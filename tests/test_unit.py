import pytest
import sqlite3
from app import app, init_db

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Initialize database for testing
        init_db()
        yield client  # This allows test functions to use the `client` fixture

# Test the database initialization function
def test_init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    
    assert ('leaderboard',) in tables
    assert ('chat',) in tables
    assert ('users',) in tables

# Test user registration
def test_register(client):
    # Simulate user registration
    response = client.post('/register', data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302  # Redirect to login
    assert b'login' in response.data

# Test adding a win to the leaderboard
def test_add_win(client):
    response = client.post('/add-win', json={'player': 'testuser'})
    assert response.status_code == 200
    assert b'{"status":"success"}' in response.data
