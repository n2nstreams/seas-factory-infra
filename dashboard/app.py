"""
Real-time Event Dashboard Backend
FastAPI application with WebSocket support for real-time event streaming
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add agents to path for shared utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents.shared.websocket_manager import get_websocket_manager, EventMessage
    from agents.shared.event_monitor import EventMonitor
    from agents.shared.logging_cfg import setup_logging
except ImportError as e:
    print(f"Warning: Could not import shared utilities: {e}")
    # Fallback imports for development
    get_websocket_manager = None
    EventMessage = None
    EventMonitor = None
    setup_logging = None

# Setup logging
logger = logging.getLogger(__name__)
if setup_logging:
    setup_logging()

# Pydantic Models
class EventFilter(BaseModel):
    """Event filter model"""
    event_types: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    search: Optional[str] = None
    time_range: Optional[str] = None

class TestEventRequest(BaseModel):
    """Test event request model"""
    event_type: str = Field(default="test", description="Event type")
    source: str = Field(default="dashboard", description="Event source")
    priority: str = Field(default="normal", description="Event priority")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")

class WebSocketStats(BaseModel):
    """WebSocket statistics model"""
    active_connections: int
    total_connections: int
    events_sent: int
    last_activity: str

# FastAPI app
app = FastAPI(
    title="SaaS Factory Event Dashboard",
    description="Real-time event monitoring dashboard with WebSocket streaming",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global WebSocket manager
websocket_manager = get_websocket_manager() if get_websocket_manager else None

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SaaS Factory Event Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "websocket_manager": "available" if websocket_manager else "unavailable",
        "active_connections": len(active_connections)
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SaaS Factory Event Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .event { padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            .btn-primary { background-color: #007bff; color: white; }
            .btn-success { background-color: #28a745; color: white; }
            #events { max-height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <h1>SaaS Factory Event Dashboard</h1>
        
        <div id="status" class="status disconnected">
            WebSocket: Disconnected
        </div>
        
        <div class="controls">
            <button id="connect" class="btn-primary">Connect</button>
            <button id="disconnect" class="btn-primary">Disconnect</button>
            <button id="test-event" class="btn-success">Send Test Event</button>
            <button id="clear-events" class="btn-primary">Clear Events</button>
        </div>
        
        <div>
            <h3>Live Events</h3>
            <div id="events"></div>
        </div>
        
        <script>
            let ws = null;
            let eventCount = 0;
            
            const statusDiv = document.getElementById('status');
            const eventsDiv = document.getElementById('events');
            const connectBtn = document.getElementById('connect');
            const disconnectBtn = document.getElementById('disconnect');
            const testEventBtn = document.getElementById('test-event');
            const clearEventsBtn = document.getElementById('clear-events');
            
            function updateStatus(connected) {
                if (connected) {
                    statusDiv.className = 'status connected';
                    statusDiv.textContent = 'WebSocket: Connected';
                } else {
                    statusDiv.className = 'status disconnected';
                    statusDiv.textContent = 'WebSocket: Disconnected';
                }
            }
            
            function addEvent(event) {
                eventCount++;
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event';
                eventDiv.innerHTML = `
                    <strong>#${eventCount} ${event.event_type}</strong> 
                    <span style="float: right;">${event.timestamp}</span><br>
                    <em>Source: ${event.source}, Priority: ${event.priority}</em><br>
                    <code>${JSON.stringify(event.data, null, 2)}</code>
                `;
                eventsDiv.insertBefore(eventDiv, eventsDiv.firstChild);
                
                // Keep only last 50 events
                while (eventsDiv.children.length > 50) {
                    eventsDiv.removeChild(eventsDiv.lastChild);
                }
            }
            
            function connect() {
                const clientId = 'dashboard-' + Math.random().toString(36).substr(2, 9);
                ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
                
                ws.onopen = function() {
                    updateStatus(true);
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addEvent(data);
                };
                
                ws.onclose = function() {
                    updateStatus(false);
                    console.log('WebSocket disconnected');
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    updateStatus(false);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendTestEvent() {
                fetch('/api/test/publish-event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        event_type: 'test',
                        source: 'dashboard',
                        priority: 'normal',
                        data: {
                            message: 'Test event from dashboard',
                            timestamp: new Date().toISOString()
                        }
                    })
                })
                .then(response => response.json())
                .then(data => console.log('Test event sent:', data))
                .catch(error => console.error('Error sending test event:', error));
            }
            
            function clearEvents() {
                eventsDiv.innerHTML = '';
                eventCount = 0;
            }
            
            // Event listeners
            connectBtn.addEventListener('click', connect);
            disconnectBtn.addEventListener('click', disconnect);
            testEventBtn.addEventListener('click', sendTestEvent);
            clearEventsBtn.addEventListener('click', clearEvents);
            
            // Auto-connect on page load
            connect();
        </script>
    </body>
    </html>
    """
    return html_content

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time event streaming"""
    await websocket.accept()
    
    # Store connection
    active_connections[client_id] = websocket
    
    # Register with WebSocket manager if available
    if websocket_manager:
        await websocket_manager.connect_client(client_id, websocket)
    
    logger.info(f"WebSocket client {client_id} connected")
    
    try:
        # Send welcome message
        welcome_event = {
            "event_type": "connection",
            "data": {
                "message": f"Connected to dashboard as {client_id}",
                "client_id": client_id
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "dashboard",
            "priority": "info"
        }
        await websocket.send_text(json.dumps(welcome_event))
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages from client (filters, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages
                if message.get("type") == "filter":
                    filters = message.get("filters", {})
                    if websocket_manager:
                        await websocket_manager.update_client_filters(client_id, filters)
                    logger.info(f"Updated filters for client {client_id}: {filters}")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket connection for {client_id}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        # Clean up
        if client_id in active_connections:
            del active_connections[client_id]
        
        if websocket_manager:
            await websocket_manager.disconnect_client(client_id)
        
        logger.info(f"WebSocket client {client_id} cleanup completed")

# API Endpoints

@app.get("/api/metrics")
async def get_metrics():
    """Get current system metrics"""
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_connections": len(active_connections),
        "uptime": "unknown"
    }
    
    if websocket_manager:
        ws_metrics = websocket_manager.get_metrics()
        metrics.update(ws_metrics)
    
    return metrics

@app.get("/api/events/history")
async def get_event_history(limit: int = Query(default=100, ge=1, le=1000)):
    """Get event history"""
    if websocket_manager:
        return websocket_manager.get_event_history(limit)
    return []

@app.get("/api/events/flows")
async def get_event_flows():
    """Get event flow information"""
    return {
        "flows": [
            {
                "name": "Agent Communication",
                "source": "agents",
                "target": "orchestrator",
                "event_types": ["agent_request", "agent_response", "agent_error"]
            },
            {
                "name": "System Events",
                "source": "system",
                "target": "dashboard",
                "event_types": ["system_health", "metrics", "alerts"]
            }
        ]
    }

@app.get("/api/events/types")
async def get_event_types():
    """Get available event types"""
    return {
        "event_types": [
            "agent_request",
            "agent_response",
            "agent_error",
            "system_health",
            "metrics",
            "test",
            "connection"
        ]
    }

@app.get("/api/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket statistics"""
    stats = {
        "active_connections": len(active_connections),
        "total_connections": len(active_connections),
        "events_sent": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    }
    
    if websocket_manager:
        ws_metrics = websocket_manager.get_metrics()
        stats.update({
            "total_connections": ws_metrics.get("total_connections", 0),
            "events_sent": ws_metrics.get("events_sent", 0),
            "last_activity": ws_metrics.get("last_activity", stats["last_activity"])
        })
    
    return stats

@app.post("/api/events/filter")
async def apply_event_filter(filter_data: EventFilter):
    """Apply event filter to all connections"""
    applied_count = 0
    
    if websocket_manager:
        filter_dict = filter_data.dict(exclude_none=True)
        for client_id in active_connections.keys():
            success = await websocket_manager.update_client_filters(client_id, filter_dict)
            if success:
                applied_count += 1
    
    return {
        "message": f"Filter applied to {applied_count} connections",
        "filter": filter_data.dict(exclude_none=True)
    }

@app.get("/api/agents/status")
async def get_agent_status():
    """Get agent status information"""
    return {
        "agents": [
            {
                "name": "requirements_agent",
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat()
            },
            {
                "name": "idea_agent",
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat()
            },
            {
                "name": "market_agent",
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

@app.post("/api/test/publish-event")
async def publish_test_event(event_request: TestEventRequest):
    """Publish a test event for testing purposes"""
    if not websocket_manager:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")
    
    # Create test event
    event = EventMessage(
        event_type=event_request.event_type,
        data=event_request.data,
        timestamp=datetime.now(timezone.utc),
        source=event_request.source,
        priority=event_request.priority
    )
    
    # Broadcast to all connections
    sent_count = await websocket_manager.broadcast_event(event)
    
    return {
        "message": "Test event published",
        "event": event.to_dict(),
        "sent_to": sent_count
    }

# Background task to simulate events (for testing)
async def simulate_events():
    """Background task to simulate events for testing"""
    import random
    
    while True:
        if websocket_manager and active_connections:
            # Simulate random events
            event_types = ["agent_request", "agent_response", "system_health", "metrics"]
            sources = ["requirements_agent", "idea_agent", "market_agent", "system"]
            priorities = ["low", "normal", "high"]
            
            event = EventMessage(
                event_type=random.choice(event_types),
                data={
                    "message": f"Simulated {random.choice(event_types)} event",
                    "value": random.randint(1, 100),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timestamp=datetime.now(timezone.utc),
                source=random.choice(sources),
                priority=random.choice(priorities)
            )
            
            await websocket_manager.broadcast_event(event)
        
        # Wait 30 seconds between simulated events
        await asyncio.sleep(30)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting SaaS Factory Event Dashboard")
    
    # Start background task for simulated events (comment out for production)
    # asyncio.create_task(simulate_events())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down SaaS Factory Event Dashboard")
    
    # Close all WebSocket connections
    for client_id, websocket in active_connections.items():
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket for {client_id}: {e}")
    
    # Cleanup WebSocket manager
    if websocket_manager:
        await websocket_manager.cleanup()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 