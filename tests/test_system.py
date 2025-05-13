import pytest
from flask_socketio import SocketIOTestClient
from app import app, socketio

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_chat(client):
    socket_client = socketio.test_client(app)

    # Emit a message
    socket_client.emit('send_message', {'username': 'testuser', 'message': 'Hello!'})

    # Receive the broadcasted message
    received = socket_client.get_received()
    print("Received messages:", received)

    assert received, "No messages received"
    assert received[0]['name'] == 'receive_message'
    assert received[0]['args'][0]['message'] == 'Hello!'

    socket_client.disconnect()


def test_multiple_clients_communication():
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)

    client1.emit('send_message', {'username': 'user1', 'message': 'Hello from user1'})
    received_by_2 = client2.get_received()

    print("Client 2 received:", received_by_2)

    assert received_by_2, "Client 2 did not receive any messages"
    assert received_by_2[0]['name'] == 'receive_message'
    assert 'user1' in received_by_2[0]['args'][0]['username']

    client1.disconnect()
    client2.disconnect()

def test_disconnect_event():
    client1 = socketio.test_client(app)

    # Simulate disconnection
    client1.disconnect()

    # Should disconnect cleanly without error
    assert not client1.is_connected(), "Client did not disconnect cleanly"
