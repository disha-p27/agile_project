import pytest
import sqlite3
from app import app, init_db

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Initialize DB and ensure no lingering users
        init_db()
        yield client

# Test user registration and login
def test_register_and_login(client):
    # Register a new user
    client.post('/register', data={'username': 'testuser', 'password': 'password123'})
    
    # Attempt login with the same credentials
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302  # Should redirect to the main page

# Test invalid login
def test_invalid_login(client):
    response = client.post('/login', data={'username': 'wronguser', 'password': 'wrongpass'})
    assert b'Invalid credentials!' in response.data

# Test adding and retrieving wins
def test_leaderboard(client):
    client.post('/add-win', json={'player': 'testuser'})
    response = client.get('/leaderboard')
    assert response.status_code == 200
    assert b'testuser' in response.data
