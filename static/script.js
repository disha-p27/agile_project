const socket = io();
let board = ['', '', '', '', '', '', '', '', ''];
let currentPlayer = 'X';
let vsAI = false;
let aiDifficulty = 'hard';
let gameOver = false;

window.onload = () => {
    createBoard();
    loadLeaderboard();
};

function createBoard() {
    const boardEl = document.getElementById('board');
    boardEl.innerHTML = '';
    board.forEach((cell, i) => {
        const div = document.createElement('div');
        div.className = 'cell';
        div.textContent = cell;
        div.onclick = () => handleMove(i);
        boardEl.appendChild(div);
    });
}

function handleMove(index) {
    if (board[index] !== '' || gameOver) return;
    board[index] = currentPlayer;
    createBoard();
    checkWinner();

    if (vsAI && !gameOver) {
        currentPlayer = 'O';

        let aiMove;
        if (aiDifficulty === 'easy') {
            aiMove = getRandomMove();
        } else if (aiDifficulty === 'medium') {
            aiMove = Math.random() < 0.5 ? getRandomMove() : getBestMove();
        } else {
            aiMove = getBestMove();
        }

        board[aiMove] = currentPlayer;
        createBoard();
        checkWinner();
        currentPlayer = 'X';
    } else {
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        document.getElementById('status').textContent = `Player ${currentPlayer}'s Turn`;
    }
}

function getRandomMove() {
    const available = board.map((val, idx) => val === '' ? idx : null).filter(val => val !== null);
    return available[Math.floor(Math.random() * available.length)];
}

function getBestMove() {
    let bestScore = -Infinity;
    let move;
    board.forEach((cell, i) => {
        if (cell === '') {
            board[i] = 'O';
            let score = minimax(board, 0, false);
            board[i] = '';
            if (score > bestScore) {
                bestScore = score;
                move = i;
            }
        }
    });
    return move;
}

function minimax(newBoard, depth, isMaximizing) {
    const scores = { O: 1, X: -1, tie: 0 };
    let result = checkWinnerRaw();
    if (result !== null) return scores[result];

    if (isMaximizing) {
        let best = -Infinity;
        newBoard.forEach((cell, i) => {
            if (cell === '') {
                newBoard[i] = 'O';
                let score = minimax(newBoard, depth + 1, false);
                newBoard[i] = '';
                best = Math.max(score, best);
            }
        });
        return best;
    } else {
        let best = Infinity;
        newBoard.forEach((cell, i) => {
            if (cell === '') {
                newBoard[i] = 'X';
                let score = minimax(newBoard, depth + 1, true);
                newBoard[i] = '';
                best = Math.min(score, best);
            }
        });
        return best;
    }
}

function checkWinnerRaw() {
    const wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ];
    for (let combo of wins) {
        let [a, b, c] = combo;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) return board[a];
    }
    if (!board.includes('')) return 'tie';
    return null;
}

function checkWinner() {
    const result = checkWinnerRaw();
    if (result) {
        gameOver = true;
        document.getElementById('status').textContent = result === 'tie' ? 'It\'s a tie!' : `Player ${result} wins!`;

        if (result !== 'tie') {
            fetch('/add-win', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player: result })
            }).then(() => loadLeaderboard());

            showCelebration(result);
        }
    }
}

function startVsAI() {
    vsAI = true;
    aiDifficulty = document.getElementById('difficulty').value;
    resetGame();
}

function startMultiplayer() {
    hideDifficultyOptions(); // Hides difficulty options
    vsAI = false;
    resetGame();
}


function resetGame() {
    board = ['', '', '', '', '', '', '', '', ''];
    currentPlayer = 'X';
    gameOver = false;
    createBoard();
    document.getElementById('status').textContent = `Player ${currentPlayer}'s Turn`;
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}

function loadLeaderboard() {
    fetch('/leaderboard')
        .then(res => res.json())
        .then(data => {
            const ul = document.getElementById('leaderboard-list');
            ul.innerHTML = '';
            data.forEach(row => {
                const li = document.createElement('li');
                li.textContent = `${row[0]} - ${row[1]} Wins`;
                ul.appendChild(li);
            });
        });
}

// --- Chat Section ---
function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message) {
        socket.emit('send_message', {
            username: 'Player',
            message: message
        });
        input.value = '';
    }
}

socket.on('receive_message', (data) => {
    const chatBox = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.textContent = `${data.username}: ${data.message}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// --- Celebration 🎉 ---
function showCelebration(winner) {
    document.getElementById('winner-name').textContent = winner;
    document.getElementById('celebration').style.display = 'flex';
    startConfetti();

    setTimeout(() => {
        stopConfetti();
        document.getElementById('celebration').style.display = 'none';
    }, 5000);
}

function startConfetti() {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1000 };

    const interval = setInterval(function () {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        confetti(Object.assign({}, defaults, { particleCount, origin: { x: Math.random(), y: Math.random() - 0.2 } }));
    }, 250);
}

function stopConfetti() {
    // No cleanup needed for canvas-confetti
}
function showDifficultyOptions() {
    document.getElementById('difficulty-controls').style.display = 'flex';
}
function hideDifficultyOptions() {
    document.getElementById('difficulty-controls').style.display = 'none';
}
