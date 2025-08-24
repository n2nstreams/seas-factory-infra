import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import base64

# It's important to set the environment before importing the app
import os
os.environ['ENVIRONMENT'] = 'test'
os.environ['DB_PASSWORD'] = 'test'
os.environ['OPENAI_API_KEY'] = 'test'


from agents.personalization.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    """Create a TestClient instance for the FastAPI app."""
    with TestClient(app) as c:
        yield c

def test_health_check(test_app):
    """Test the health check endpoint."""
    response = test_app.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('agents.personalization.main.get_db_connection')
@patch('agents.personalization.main.model')
def test_pubsub_push_endpoint(mock_model, mock_get_db_connection, test_app):
    """Test the /pubsub/push endpoint with a valid message."""
    # Mock the sentence transformer model
    mock_model.encode.return_value = [0.1, 0.2, 0.3] * 128 # 384 dimensions

    # Mock the database connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Prepare the test Pub/Sub message
    message_data = {
        "user_id": "test_user_123",
        "feature_name": "test_feature",
        "feature_value": "This is a test feature."
    }
    message_bytes = json.dumps(message_data).encode('utf-8')
    base64_encoded_message = base64.b64encode(message_bytes).decode('utf-8')

    pubsub_message = {
        "message": {
            "data": base64_encoded_message,
            "messageId": "1234567890",
            "publishTime": "2024-01-01T00:00:00Z"
        },
        "subscription": "projects/test-project/subscriptions/test-subscription"
    }

    # Make the request
    response = test_app.post("/pubsub/push", json=pubsub_message)

    # Assert the response
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Assert that the model was called correctly
    mock_model.encode.assert_called_once_with("This is a test feature.")

    # Assert that the database connection was handled correctly
    mock_get_db_connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once() # Simplified check for execute_values
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('agents.personalization.main.get_db_connection')
def test_pubsub_push_missing_fields(mock_get_db_connection, test_app):
    """Test the /pubsub/push endpoint with missing fields in the message."""
    # Prepare a message with missing fields
    message_data = {
        "user_id": "test_user_123"
        # feature_name and feature_value are missing
    }
    message_bytes = json.dumps(message_data).encode('utf-8')
    base64_encoded_message = base64.b64encode(message_bytes).decode('utf-8')

    pubsub_message = {
        "message": {
            "data": base64_encoded_message,
        },
        "subscription": "projects/test-project/subscriptions/test-subscription"
    }

    # We don't expect the DB to be called, so no need to mock it extensively
    # but the callback will be triggered. The nack will be logged.
    response = test_app.post("/pubsub/push", json=pubsub_message)
    assert response.status_code == 200 # The endpoint itself succeeds
    
    # Check that the database was not called
    mock_get_db_connection.assert_not_called()

def test_pubsub_push_invalid_format(test_app):
    """Test the /pubsub/push endpoint with an invalid message format."""
    response = test_app.post("/pubsub/push", json={"invalid": "payload"})
    assert response.status_code == 400
    assert "Invalid Pub/Sub message format" in response.json()["detail"]
