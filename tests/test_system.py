import pytest
from flask_socketio import SocketIOTestClient
from app import app, socketio

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Set up the test client for Socket.IO
        socketio.test_client(app)
        yield client

def test_chat(client):
    socket_client = socketio.test_client(app)

    # Emit a message
    socket_client.emit('send_message', {'username': 'testuser', 'message': 'Hello!'})

    # Receive the broadcasted message
    received = socket_client.get_received()

    # Debug: print received to understand structure
    print("Received messages:", received)

    assert received, "No messages received"
    assert received[0]['name'] == 'receive_message'
    assert received[0]['args'][0]['message'] == 'Hello!'

    # Disconnect the client
    socket_client.disconnect()

