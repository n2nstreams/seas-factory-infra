"""
WebSocket Manager for Real-time Event Streaming
Handles WebSocket connections, broadcasting, and client management
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client"""
    client_id: str
    websocket: Any
    connected_at: datetime
    last_ping: datetime
    filters: Dict[str, Any]
    
    def __post_init__(self):
        if isinstance(self.connected_at, str):
            self.connected_at = datetime.fromisoformat(self.connected_at.replace('Z', '+00:00'))
        if isinstance(self.last_ping, str):
            self.last_ping = datetime.fromisoformat(self.last_ping.replace('Z', '+00:00'))

@dataclass
class EventMessage:
    """Represents an event message to be sent via WebSocket"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: str = "normal"
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority
        }

class WebSocketManager:
    """
    Manages WebSocket connections and real-time event broadcasting
    
    Features:
    - Client connection lifecycle management
    - Real-time event broadcasting with filtering
    - Health monitoring and metrics
    - Background tasks for metrics and health checks
    """
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.event_history: List[EventMessage] = []
        self.metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "events_sent": 0,
            "last_activity": datetime.now(timezone.utc)
        }
        self.max_history_size = 1000
        self.max_clients = 100
        self._background_tasks: Set[asyncio.Task] = set()
        logger.info("WebSocketManager initialized")
    
    async def connect_client(self, client_id: str, websocket: Any, filters: Dict[str, Any] = None) -> bool:
        """
        Connect a new WebSocket client
        
        Args:
            client_id: Unique identifier for the client
            websocket: WebSocket connection object
            filters: Optional filters for event filtering
            
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if len(self.clients) >= self.max_clients:
            logger.warning(f"Maximum clients ({self.max_clients}) reached, rejecting connection")
            return False
        
        if client_id in self.clients:
            logger.warning(f"Client {client_id} already connected, replacing connection")
            await self.disconnect_client(client_id)
        
        client = WebSocketClient(
            client_id=client_id,
            websocket=websocket,
            connected_at=datetime.now(timezone.utc),
            last_ping=datetime.now(timezone.utc),
            filters=filters or {}
        )
        
        self.clients[client_id] = client
        self.metrics["total_connections"] += 1
        self.metrics["active_connections"] = len(self.clients)
        self.metrics["last_activity"] = datetime.now(timezone.utc)
        
        logger.info(f"Client {client_id} connected, total active: {len(self.clients)}")
        
        # Start background tasks if this is the first client
        if len(self.clients) == 1:
            await self._start_background_tasks()
        
        return True
    
    async def disconnect_client(self, client_id: str) -> bool:
        """
        Disconnect a WebSocket client
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            bool: True if disconnected successfully, False if client not found
        """
        if client_id not in self.clients:
            logger.warning(f"Client {client_id} not found for disconnection")
            return False
        
        client = self.clients[client_id]
        
        try:
            if hasattr(client.websocket, 'close'):
                await client.websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket for client {client_id}: {e}")
        
        del self.clients[client_id]
        self.metrics["active_connections"] = len(self.clients)
        self.metrics["last_activity"] = datetime.now(timezone.utc)
        
        logger.info(f"Client {client_id} disconnected, total active: {len(self.clients)}")
        
        # Stop background tasks if no clients remain
        if len(self.clients) == 0:
            await self._stop_background_tasks()
        
        return True
    
    async def broadcast_event(self, event: EventMessage) -> int:
        """
        Broadcast an event to all connected clients
        
        Args:
            event: Event message to broadcast
            
        Returns:
            int: Number of clients that received the event
        """
        if not self.clients:
            return 0
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Prepare message
        message = json.dumps(event.to_dict())
        successful_sends = 0
        clients_to_remove = []
        
        # Send to all connected clients
        for client_id, client in self.clients.items():
            try:
                # Apply client filters if any
                if self._should_send_to_client(event, client):
                    if hasattr(client.websocket, 'send'):
                        await client.websocket.send(message)
                    successful_sends += 1
                    
            except ConnectionClosed:
                logger.info(f"Client {client_id} connection closed during broadcast")
                clients_to_remove.append(client_id)
            except WebSocketException as e:
                logger.error(f"WebSocket error for client {client_id}: {e}")
                clients_to_remove.append(client_id)
            except Exception as e:
                logger.error(f"Unexpected error broadcasting to client {client_id}: {e}")
                clients_to_remove.append(client_id)
        
        # Remove disconnected clients
        for client_id in clients_to_remove:
            await self.disconnect_client(client_id)
        
        self.metrics["events_sent"] += successful_sends
        self.metrics["last_activity"] = datetime.now(timezone.utc)
        
        if successful_sends > 0:
            logger.debug(f"Broadcast event to {successful_sends} clients")
        
        return successful_sends
    
    def _should_send_to_client(self, event: EventMessage, client: WebSocketClient) -> bool:
        """
        Check if an event should be sent to a specific client based on filters
        
        Args:
            event: Event message to check
            client: Client to check against
            
        Returns:
            bool: True if event should be sent to client
        """
        if not client.filters:
            return True
        
        # Check event type filter
        if "event_types" in client.filters:
            if event.event_type not in client.filters["event_types"]:
                return False
        
        # Check source filter
        if "sources" in client.filters:
            if event.source not in client.filters["sources"]:
                return False
        
        # Check priority filter
        if "priority" in client.filters:
            if event.priority not in client.filters["priority"]:
                return False
        
        return True
    
    async def update_client_filters(self, client_id: str, filters: Dict[str, Any]) -> bool:
        """
        Update filters for a specific client
        
        Args:
            client_id: Unique identifier for the client
            filters: New filters to apply
            
        Returns:
            bool: True if updated successfully, False if client not found
        """
        if client_id not in self.clients:
            return False
        
        self.clients[client_id].filters = filters
        logger.info(f"Updated filters for client {client_id}")
        return True
    
    async def ping_client(self, client_id: str) -> bool:
        """
        Send a ping to a specific client
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            bool: True if ping sent successfully, False otherwise
        """
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        
        try:
            if hasattr(client.websocket, 'ping'):
                await client.websocket.ping()
            client.last_ping = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"Error pinging client {client_id}: {e}")
            await self.disconnect_client(client_id)
            return False
    
    async def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific client
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Optional[Dict]: Client information or None if not found
        """
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id]
        return {
            "client_id": client.client_id,
            "connected_at": client.connected_at.isoformat(),
            "last_ping": client.last_ping.isoformat(),
            "filters": client.filters
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current WebSocket metrics
        
        Returns:
            Dict: Current metrics
        """
        return {
            **self.metrics,
            "last_activity": self.metrics["last_activity"].isoformat(),
            "event_history_size": len(self.event_history)
        }
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent event history
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List[Dict]: Recent events
        """
        return [event.to_dict() for event in self.event_history[-limit:]]
    
    async def _start_background_tasks(self):
        """Start background tasks for metrics and health checks"""
        # Metrics broadcasting task (every 10 seconds)
        metrics_task = asyncio.create_task(self._metrics_broadcast_task())
        self._background_tasks.add(metrics_task)
        
        # Health check task (every 30 seconds)
        health_task = asyncio.create_task(self._health_check_task())
        self._background_tasks.add(health_task)
        
        logger.info("Background tasks started")
    
    async def _stop_background_tasks(self):
        """Stop all background tasks"""
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
        logger.info("Background tasks stopped")
    
    async def _metrics_broadcast_task(self):
        """Background task to broadcast metrics every 10 seconds"""
        while True:
            try:
                if self.clients:
                    metrics_event = EventMessage(
                        event_type="metrics",
                        data=self.get_metrics(),
                        timestamp=datetime.now(timezone.utc),
                        source="websocket_manager",
                        priority="low"
                    )
                    await self.broadcast_event(metrics_event)
                
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics broadcast task: {e}")
                await asyncio.sleep(10)
    
    async def _health_check_task(self):
        """Background task to check client health every 30 seconds"""
        while True:
            try:
                if self.clients:
                    disconnected_clients = []
                    for client_id in list(self.clients.keys()):
                        success = await self.ping_client(client_id)
                        if not success:
                            disconnected_clients.append(client_id)
                    
                    if disconnected_clients:
                        logger.info(f"Health check removed {len(disconnected_clients)} inactive clients")
                
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check task: {e}")
                await asyncio.sleep(30)
    
    async def cleanup(self):
        """Clean up resources and close all connections"""
        logger.info("Cleaning up WebSocketManager")
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.disconnect_client(client_id)
        
        # Clear history
        self.event_history.clear()
        
        logger.info("WebSocketManager cleanup completed")

# Global instance
_websocket_manager = None

def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager

async def create_websocket_manager() -> WebSocketManager:
    """Create a new WebSocket manager instance"""
    return WebSocketManager() 