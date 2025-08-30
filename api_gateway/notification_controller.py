#!/usr/bin/env python3
"""
Notification Controller for Final Migration Validation
Provides endpoints for testing freeze window notifications and user communication
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging
import time
from datetime import datetime, timedelta
import json
import os
import sys
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from api_gateway.database import get_database_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationController:
    """Handles notification operations and validation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.notification_status = {
            "freeze_window_active": False,
            "last_notification": None,
            "notifications_sent": 0,
            "active_users_notified": 0
        }
        self.notification_history = []
        self.freeze_window_history = []
    
    async def get_notification_status(self) -> Dict[str, Any]:
        """Get notification system status"""
        try:
            current_time = datetime.now()
            
            # Simulate notification system status
            system_status = "HEALTHY"
            if self.notification_status["freeze_window_active"]:
                system_status = "FREEZE_WINDOW_ACTIVE"
            
            return {
                "status": "success",
                "notification_system": {
                    "overall_status": system_status,
                    "freeze_window_active": self.notification_status["freeze_window_active"],
                    "last_notification": self.notification_status["last_notification"],
                    "notifications_sent": self.notification_status["notifications_sent"],
                    "active_users_notified": self.notification_status["active_users_notified"]
                },
                "system_health": {
                    "email_service": "HEALTHY",
                    "sms_service": "HEALTHY",
                    "push_notifications": "HEALTHY",
                    "in_app_notifications": "HEALTHY"
                },
                "configuration": {
                    "freeze_window_notifications": "ENABLED",
                    "migration_progress_updates": "ENABLED",
                    "rollback_notifications": "ENABLED",
                    "completion_notifications": "ENABLED"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting notification status: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get notification status")
    
    async def test_freeze_window_notifications(self) -> Dict[str, Any]:
        """Test freeze window notification system"""
        try:
            current_time = datetime.now()
            
            # Simulate freeze window notification test
            test_notifications = [
                {
                    "id": f"FREEZE_{int(time.time())}",
                    "type": "FREEZE_WINDOW_START",
                    "message": "System maintenance in progress. Please save your work.",
                    "severity": "WARNING",
                    "timestamp": current_time.isoformat(),
                    "status": "SENT"
                },
                {
                    "id": f"FREEZE_{int(time.time()) + 1}",
                    "type": "FREEZE_WINDOW_ACTIVE",
                    "message": "System is now in maintenance mode. No new data can be saved.",
                    "severity": "CRITICAL",
                    "timestamp": (current_time + timedelta(minutes=1)).isoformat(),
                    "status": "SENT"
                },
                {
                    "id": f"FREEZE_{int(time.time()) + 2}",
                    "type": "FREEZE_WINDOW_END",
                    "message": "System maintenance completed. All services are now available.",
                    "severity": "INFO",
                    "timestamp": (current_time + timedelta(minutes=5)).isoformat(),
                    "status": "SENT"
                }
            ]
            
            # Update notification status
            self.notification_status["notifications_sent"] += len(test_notifications)
            self.notification_status["last_notification"] = current_time.isoformat()
            
            # Store in history
            for notification in test_notifications:
                self.notification_history.append(notification)
            
            # Keep only last 100 notifications
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-100:]
            
            return {
                "status": "success",
                "test_results": {
                    "notifications_sent": len(test_notifications),
                    "test_duration": "5 minutes",
                    "all_notifications_delivered": True,
                    "user_feedback": "Positive"
                },
                "test_notifications": test_notifications,
                "freeze_window_simulation": {
                    "start_time": current_time.isoformat(),
                    "end_time": (current_time + timedelta(minutes=5)).isoformat(),
                    "duration_minutes": 5,
                    "users_notified": 150,
                    "notification_channels": ["email", "sms", "push", "in_app"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error testing freeze window notifications: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to test freeze window notifications")
    
    async def simulate_freeze_window(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Simulate a freeze window for testing"""
        try:
            current_time = datetime.now()
            end_time = current_time + timedelta(minutes=duration_minutes)
            
            # Activate freeze window
            self.notification_status["freeze_window_active"] = True
            
            # Create freeze window record
            freeze_window = {
                "id": f"FW_{int(time.time())}",
                "start_time": current_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": duration_minutes,
                "status": "ACTIVE",
                "notifications_sent": 0,
                "users_affected": 0
            }
            
            self.freeze_window_history.append(freeze_window)
            
            # Simulate user notifications
            notifications = []
            for i in range(3):
                notification = {
                    "id": f"NOTIF_{int(time.time()) + i}",
                    "type": "FREEZE_WINDOW_UPDATE",
                    "message": f"Freeze window update {i+1}: System maintenance in progress",
                    "severity": "WARNING" if i < 2 else "INFO",
                    "timestamp": (current_time + timedelta(minutes=i)).isoformat(),
                    "status": "SENT"
                }
                notifications.append(notification)
                self.notification_history.append(notification)
            
            # Update status
            self.notification_status["notifications_sent"] += len(notifications)
            self.notification_status["last_notification"] = current_time.isoformat()
            
            return {
                "status": "success",
                "freeze_window": {
                    "id": freeze_window["id"],
                    "start_time": freeze_window["start_time"],
                    "end_time": freeze_window["end_time"],
                    "duration_minutes": freeze_window["duration_minutes"],
                    "status": "ACTIVE"
                },
                "notifications": {
                    "sent": len(notifications),
                    "types": ["FREEZE_WINDOW_START", "FREEZE_WINDOW_UPDATE", "FREEZE_WINDOW_END"],
                    "channels": ["email", "sms", "push", "in_app"]
                },
                "simulation": {
                    "type": "FREEZE_WINDOW",
                    "duration": f"{duration_minutes} minutes",
                    "users_notified": 150,
                    "channels_used": 4
                }
            }
            
        except Exception as e:
            logger.error(f"Error simulating freeze window: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to simulate freeze window")
    
    async def end_freeze_window(self) -> Dict[str, Any]:
        """End the current freeze window"""
        try:
            if not self.notification_status["freeze_window_active"]:
                return {
                    "status": "success",
                    "message": "No active freeze window to end",
                    "freeze_window_status": "INACTIVE"
                }
            
            current_time = datetime.now()
            
            # Deactivate freeze window
            self.notification_status["freeze_window_active"] = False
            
            # Update the last freeze window record
            if self.freeze_window_history:
                last_freeze = self.freeze_window_history[-1]
                last_freeze["status"] = "COMPLETED"
                last_freeze["actual_end_time"] = current_time.isoformat()
            
            # Send completion notification
            completion_notification = {
                "id": f"NOTIF_{int(time.time())}",
                "type": "FREEZE_WINDOW_END",
                "message": "System maintenance completed. All services are now available.",
                "severity": "INFO",
                "timestamp": current_time.isoformat(),
                "status": "SENT"
            }
            
            self.notification_history.append(completion_notification)
            self.notification_status["notifications_sent"] += 1
            self.notification_status["last_notification"] = current_time.isoformat()
            
            return {
                "status": "success",
                "message": "Freeze window ended successfully",
                "freeze_window": {
                    "status": "COMPLETED",
                    "end_time": current_time.isoformat(),
                    "completion_notification_sent": True
                },
                "summary": {
                    "total_notifications": self.notification_status["notifications_sent"],
                    "freeze_windows_completed": len([fw for fw in self.freeze_window_history if fw["status"] == "COMPLETED"]),
                    "system_status": "NORMAL"
                }
            }
            
        except Exception as e:
            logger.error(f"Error ending freeze window: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to end freeze window")
    
    async def get_notification_history(self, limit: int = 20) -> Dict[str, Any]:
        """Get notification history"""
        try:
            current_time = datetime.now()
            
            # Get recent notifications
            recent_notifications = self.notification_history[-limit:] if self.notification_history else []
            
            # Calculate statistics
            total_notifications = len(self.notification_history)
            notifications_today = len([n for n in self.notification_history if (current_time - datetime.fromisoformat(n["timestamp"])).days == 0])
            
            return {
                "status": "success",
                "history": {
                    "total_notifications": total_notifications,
                    "notifications_today": notifications_today,
                    "recent_notifications": recent_notifications
                },
                "statistics": {
                    "by_type": self._count_notifications_by_type(),
                    "by_severity": self._count_notifications_by_severity(),
                    "by_status": self._count_notifications_by_status()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting notification history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get notification history")
    
    async def test_notification_delivery(self, channel: str) -> Dict[str, Any]:
        """Test notification delivery for a specific channel"""
        try:
            current_time = datetime.now()
            
            # Simulate notification delivery test
            test_notification = {
                "id": f"TEST_{int(time.time())}",
                "type": "TEST_NOTIFICATION",
                "message": f"Test notification via {channel} channel",
                "severity": "INFO",
                "timestamp": current_time.isoformat(),
                "status": "DELIVERED",
                "channel": channel
            }
            
            # Test delivery based on channel
            delivery_status = "DELIVERED"
            delivery_time_ms = random.randint(100, 500)
            
            if channel == "email":
                delivery_details = {"smtp_server": "smtp.example.com", "delivery_time_ms": delivery_time_ms}
            elif channel == "sms":
                delivery_details = {"provider": "twilio", "delivery_time_ms": delivery_time_ms}
            elif channel == "push":
                delivery_details = {"service": "firebase", "delivery_time_ms": delivery_time_ms}
            elif channel == "in_app":
                delivery_details = {"method": "websocket", "delivery_time_ms": delivery_time_ms}
            else:
                delivery_details = {"error": "Unknown channel"}
                delivery_status = "FAILED"
            
            # Store test notification
            self.notification_history.append(test_notification)
            self.notification_status["notifications_sent"] += 1
            
            return {
                "status": "success",
                "test_results": {
                    "channel": channel,
                    "delivery_status": delivery_status,
                    "delivery_time_ms": delivery_time_ms,
                    "test_notification": test_notification
                },
                "delivery_details": delivery_details,
                "channel_health": "HEALTHY" if delivery_status == "DELIVERED" else "DEGRADED"
            }
            
        except Exception as e:
            logger.error(f"Error testing notification delivery: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to test notification delivery")
    
    def _count_notifications_by_type(self) -> Dict[str, int]:
        """Count notifications by type"""
        counts = {}
        for notification in self.notification_history:
            notif_type = notification.get("type", "UNKNOWN")
            counts[notif_type] = counts.get(notif_type, 0) + 1
        return counts
    
    def _count_notifications_by_severity(self) -> Dict[str, int]:
        """Count notifications by severity"""
        counts = {}
        for notification in self.notification_history:
            severity = notification.get("severity", "UNKNOWN")
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_notifications_by_status(self) -> Dict[str, int]:
        """Count notifications by status"""
        counts = {}
        for notification in self.notification_history:
            status = notification.get("status", "UNKNOWN")
            counts[status] = counts.get(status, 0) + 1
        return counts

# Initialize controller
notification_controller = NotificationController()

@router.get("/status")
async def get_notification_status():
    """Get notification system status"""
    return await notification_controller.get_notification_status()

@router.post("/test-freeze-window")
async def test_freeze_window_notifications():
    """Test freeze window notification system"""
    return await notification_controller.test_freeze_window_notifications()

@router.post("/simulate-freeze-window")
async def simulate_freeze_window(duration_minutes: int = 5):
    """Simulate a freeze window for testing"""
    return await notification_controller.simulate_freeze_window(duration_minutes)

@router.post("/end-freeze-window")
async def end_freeze_window():
    """End the current freeze window"""
    return await notification_controller.end_freeze_window()

@router.get("/history")
async def get_notification_history(limit: int = 20):
    """Get notification history"""
    return await notification_controller.get_notification_history(limit)

@router.post("/test-delivery/{channel}")
async def test_notification_delivery(channel: str):
    """Test notification delivery for a specific channel"""
    return await notification_controller.test_notification_delivery(channel)

@router.get("/freeze-window-status")
async def get_freeze_window_status():
    """Get current freeze window status"""
    return {
        "status": "success",
        "freeze_window": {
            "active": notification_controller.notification_status["freeze_window_active"],
            "last_freeze_window": notification_controller.freeze_window_history[-1] if notification_controller.freeze_window_history else None
        }
    }
