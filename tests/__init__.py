# tests/__init__.py
import pytest
from app import app, init_db

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()  # Setup the test database
        yield client
