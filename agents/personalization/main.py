import base64
import json
import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from google.cloud import pubsub_v1
from config.settings import get_settings, Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personalization Agent",
    description="Consumes user events and generates feature embeddings for personalization.",
    version="1.0.0"
)

# Load settings
settings = get_settings()

# Load sentence transformer model
# Using a smaller, efficient model suitable for generating embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

class PubSubMessage(BaseModel):
    message: dict
    subscription: str

def get_db_connection():
    """Establishes and returns a database connection."""
    conn = psycopg2.connect(settings.database.url)
    register_vector(conn)
    return conn

@app.on_event("startup")
async def startup_event():
    """Initializes the Pub/Sub subscriber on application startup."""
    if settings.google_cloud.project_id and settings.google_cloud.personalization_subscription:
        try:
            subscriber = pubsub_v1.SubscriberClient()
            subscription_path = subscriber.subscription_path(
                settings.google_cloud.project_id,
                settings.google_cloud.personalization_subscription
            )
            streaming_pull_future = subscriber.subscribe(subscription_path, callback=message_callback)
            logger.info(f"Listening for messages on {subscription_path}...")
            # Keep the future alive to continue receiving messages
            app.state.streaming_pull_future = streaming_pull_future
        except Exception as e:
            logger.error(f"Failed to subscribe to Pub/Sub: {e}")
    else:
        logger.warning("Pub/Sub subscription not configured. Skipping.")

def message_callback(message):
    """Callback function to process incoming Pub/Sub messages."""
    try:
        data = json.loads(message.data.decode("utf-8"))
        logger.info(f"Received message: {data}")

        user_id = data.get("user_id")
        feature_name = data.get("feature_name")
        feature_value = data.get("feature_value")

        if not all([user_id, feature_name, feature_value]):
            logger.error("Missing required fields in message")
            message.nack()
            return

        # Generate embedding
        embedding = model.encode(feature_value)

        # Store embedding in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            execute_values(
                cursor,
                "INSERT INTO user_feature_embeddings (user_id, feature_name, embedding) VALUES %s ON CONFLICT (user_id, feature_name) DO UPDATE SET embedding = EXCLUDED.embedding, updated_at = CURRENT_TIMESTAMP",
                [(user_id, feature_name, embedding)]
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Successfully stored embedding for user {user_id} and feature {feature_name}")
            message.ack()
        except Exception as e:
            logger.error(f"Database error: {e}")
            message.nack()

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        message.nack()

@app.post("/pubsub/push")
async def pubsub_push(data: PubSubMessage):
    """
    HTTP endpoint to receive push-based Pub/Sub messages.
    This is an alternative to the pull-based subscriber for different deployment models.
    """
    try:
        # The actual message is base64-encoded in the 'data' field of the message.
        message_data = base64.b64decode(data.message['data']).decode('utf-8')
        message_json = json.loads(message_data)
        
        # Manually create a message-like object for the callback
        class MockMessage:
            def __init__(self, data):
                self.data = data
            def ack(self):
                logger.info("Message acknowledged.")
            def nack(self):
                logger.warning("Message not acknowledged.")

        mock_message = MockMessage(message_data.encode('utf-8'))
        message_callback(mock_message)

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in pubsub_push: {e}")
        raise HTTPException(status_code=400, detail="Invalid Pub/Sub message format")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Add a personalization_subscription to the settings for local testing
    settings.google_cloud.personalization_subscription = "user-events-subscription"
    uvicorn.run(app, host=settings.host, port=settings.port) 