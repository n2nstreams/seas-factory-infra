"""
LangGraph dummy agent that demonstrates Agent2Agent protocol integration.
Accepts "ping" envelopes and replies with "pong-from-langgraph".
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LangGraph Dummy Agent", version="0.1.0")

class Envelope(BaseModel):
    """Agent2Agent protocol envelope"""
    type: str = "agent2agent"
    version: int = 1
    content: Any

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "lang-dummy"}

@app.post("/")
async def handle_agent_message(envelope: Envelope):
    """
    Handle incoming Agent2Agent protocol messages.
    Responds to "ping" with "pong-from-langgraph".
    """
    logger.info(f"Received envelope: {envelope}")
    
    if envelope.type != "agent2agent":
        raise HTTPException(status_code=400, detail="Invalid envelope type")
    
    if envelope.version != 1:
        raise HTTPException(status_code=400, detail="Unsupported envelope version")
    
    # Handle ping message
    if envelope.content == "ping":
        response_envelope = Envelope(
            type="agent2agent",
            version=1,
            content="pong-from-langgraph"
        )
        logger.info(f"Responding with: {response_envelope}")
        return response_envelope
    
    # Handle other messages with echo
    response_envelope = Envelope(
        type="agent2agent", 
        version=1,
        content=f"echo-from-langgraph: {envelope.content}"
    )
    logger.info(f"Echoing back: {response_envelope}")
    return response_envelope

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 