import os
import sqlite3
import pytest
from app import app, init_db

DB_PATH = 'database.db'

@pytest.fixture(scope='module')
def client():
    # Ensure a clean database before tests
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # if using CSRF
    with app.test_client() as client:
        yield client

def test_init_db():
    """Test if required tables are created properly."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = set(row[0] for row in cursor.fetchall())
    conn.close()

    assert 'leaderboard' in tables
    assert 'chat' in tables
    assert 'users' in tables

def test_register(client):
    """Test registration of a new user."""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'login' in response.data or b'Login' in response.data

def test_login_success(client):
    """Test login with correct credentials."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'testuser' in response.data or b'Welcome' in response.data

def test_add_win(client):
    """Test updating/adding a win for a player."""
    response = client.post('/add-win', json={'player': 'testuser'})
    assert response.status_code == 200
    assert b'"status": "success"' in response.data or b'"status":"success"' in response.data

def test_leaderboard_retrieval(client):
    """Test if leaderboard returns data correctly."""
    response = client.get('/leaderboard')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(player[0] == 'testuser' for player in data)
