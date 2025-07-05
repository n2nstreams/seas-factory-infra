#!/usr/bin/env python3
"""
Event Relay Service - Receives Pub/Sub messages and stores them in Firestore
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response
from google.cloud import firestore
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Event Relay Service", version="1.0.0")

# Initialize Firestore client
PROJECT_ID = os.getenv("PROJECT_ID", "summer-nexus-463503-e1")
db = firestore.Client(project=PROJECT_ID)

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "event-relay", "timestamp": time.time()}

@app.post("/")
async def receive_pubsub_message(request: Request):
    """Receive Pub/Sub push messages and store them in Firestore"""
    try:
        # Parse the Pub/Sub message
        body = await request.body()
        envelope = json.loads(body.decode("utf-8"))
        
        # Extract the message data
        pubsub_message = envelope.get("message", {})
        message_data = pubsub_message.get("data", "")
        
        # Decode the base64 message data
        import base64
        decoded_data = base64.b64decode(message_data).decode("utf-8")
        event_data = json.loads(decoded_data)
        
        # Add metadata
        event_document = {
            **event_data,
            "message_id": pubsub_message.get("messageId"),
            "publish_time": pubsub_message.get("publishTime"),
            "received_at": firestore.SERVER_TIMESTAMP
        }
        
        # Store in Firestore
        doc_ref = db.collection("events").document()
        doc_ref.set(event_document)
        
        logger.info(f"Stored event: {event_data.get('type', 'unknown')} - {event_data.get('stage', 'unknown')}")
        
        return Response(status_code=200, content="OK")
        
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {str(e)}")
        return Response(status_code=500, content=f"Error: {str(e)}")

@app.get("/events")
async def get_events(limit: int = 100):
    """Get the most recent events from Firestore"""
    try:
        # Query events ordered by received_at (most recent first)
        events_ref = db.collection("events").order_by("received_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        events = []
        for doc in events_ref.stream():
            event_data = doc.to_dict()
            # Convert Firestore timestamp to ISO string for JSON serialization
            if "received_at" in event_data:
                event_data["received_at"] = event_data["received_at"].isoformat()
            events.append(event_data)
        
        return {
            "events": events,
            "count": len(events),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/events/stream")
async def stream_events():
    """Stream events in real-time (placeholder for SSE)"""
    # This would be implemented with Server-Sent Events in a real scenario
    return {"message": "Real-time streaming not implemented yet"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 