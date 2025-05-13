"""Flask web application for a multiplayer game with chat and leaderboard."""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# ------------------ DB Setup ------------------

def init_db():
    """Initializes the SQLite database with required tables."""
    if not os.path.exists('database.db'):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE leaderboard (player TEXT, wins INTEGER)''')
        cursor.execute('''CREATE TABLE chat (username TEXT, message TEXT)''')
        cursor.execute('''CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT)''')
        connection.commit()
        connection.close()

# ------------------ Auth Routes ------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            return "Username already taken!"
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        connection.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user[1], password):
            session['username'] = username
            return redirect('/')
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('username', None)
    return redirect('/login')

# ------------------ Game Routes ------------------

@app.route('/')
def index():
    """Displays the main game interface."""
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'])

@app.route('/leaderboard')
def leaderboard():
    """Returns the top 10 players on the leaderboard."""
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM leaderboard ORDER BY wins DESC LIMIT 10")
    data = cursor.fetchall()
    connection.close()
    return jsonify(data)

@app.route('/add-win', methods=['POST'])
def add_win():
    """Adds a win to the specified player's record."""
    player = request.json['player']
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM leaderboard WHERE player=?", (player,))
    if cursor.fetchone():
        cursor.execute("UPDATE leaderboard SET wins = wins + 1 WHERE player=?", (player,))
    else:
        cursor.execute("INSERT INTO leaderboard VALUES (?, ?)", (player, 1))
    connection.commit()
    connection.close()
    return jsonify({"status": "success"})

# ------------------ Chat ------------------

@socketio.on('send_message')
def handle_send_message(data):
    """Handles incoming chat messages and broadcasts them."""
    username = data['username']
    message = data['message']
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO chat VALUES (?, ?)", (username, message))
    connection.commit()
    connection.close()
    emit('receive_message', data, broadcast=True)

@socketio.on('connect')
def on_connect():
    """Logs a message when a client connects."""
    print("Client connected")

# ------------------ Start ------------------

if __name__ == '__main__':
    init_db()
    socketio.run(app, host="0.0.0.0", port=8001, debug=True, allow_unsafe_werkzeug=True)
