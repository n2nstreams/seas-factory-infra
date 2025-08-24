#!/usr/bin/env python3
"""
Slack Integration Module
Real implementation of Slack notifications for SaaS Factory
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackMessageType(str, Enum):
    """Slack message types"""
    ALERT = "alert"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

class SlackAttachment(BaseModel):
    """Slack message attachment"""
    color: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    fields: List[Dict[str, str]] = Field(default_factory=list)
    footer: Optional[str] = None
    ts: Optional[int] = None

class SlackMessage(BaseModel):
    """Slack message model"""
    channel: str
    text: str
    username: Optional[str] = "SaaS Factory"
    icon_emoji: Optional[str] = ":robot_face:"
    icon_url: Optional[str] = None
    attachments: List[SlackAttachment] = Field(default_factory=list)
    thread_ts: Optional[str] = None
    unfurl_links: bool = False
    unfurl_media: bool = False

class SlackIntegration:
    """Main Slack integration class"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.default_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "#alerts")
        self.app_name = os.getenv("APP_NAME", "SaaS Factory")
        
        # Message color mapping
        self.message_colors = {
            SlackMessageType.ALERT: "#ff0000",      # Red
            SlackMessageType.SUCCESS: "#36a64f",    # Green
            SlackMessageType.WARNING: "#ff9900",    # Orange
            SlackMessageType.ERROR: "#ff0000",      # Red
            SlackMessageType.INFO: "#439fe0"        # Blue
        }
        
        # Emoji mapping
        self.message_emojis = {
            SlackMessageType.ALERT: ":rotating_light:",
            SlackMessageType.SUCCESS: ":white_check_mark:",
            SlackMessageType.WARNING: ":warning:",
            SlackMessageType.ERROR: ":x:",
            SlackMessageType.INFO: ":information_source:"
        }
        
        logger.info("Slack integration initialized")
    
    async def send_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Send message to Slack"""
        try:
            if self.webhook_url:
                return await self._send_webhook_message(message)
            elif self.bot_token:
                return await self._send_api_message(message)
            else:
                logger.warning("No Slack webhook URL or bot token configured")
                return {"status": "error", "message": "No Slack configuration found"}
        
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_webhook_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Send message via webhook"""
        try:
            payload = {
                "channel": message.channel,
                "text": message.text,
                "username": message.username,
                "icon_emoji": message.icon_emoji,
                "attachments": [att.dict(exclude_none=True) for att in message.attachments],
                "unfurl_links": message.unfurl_links,
                "unfurl_media": message.unfurl_media
            }
            
            if message.icon_url:
                payload["icon_url"] = message.icon_url
                del payload["icon_emoji"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {"status": "success", "message": "Message sent successfully"}
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
        
        except Exception as e:
            logger.error(f"Webhook message error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_api_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Send message via Slack API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "channel": message.channel,
                "text": message.text,
                "username": message.username,
                "icon_emoji": message.icon_emoji,
                "attachments": [att.dict(exclude_none=True) for att in message.attachments],
                "unfurl_links": message.unfurl_links,
                "unfurl_media": message.unfurl_media
            }
            
            if message.thread_ts:
                payload["thread_ts"] = message.thread_ts
            
            if message.icon_url:
                payload["icon_url"] = message.icon_url
                del payload["icon_emoji"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                response_data = response.json()
                
                if response_data.get("ok"):
                    return {
                        "status": "success",
                        "message": "Message sent successfully",
                        "ts": response_data.get("ts"),
                        "channel": response_data.get("channel")
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Slack API error: {response_data.get('error')}"
                    }
        
        except Exception as e:
            logger.error(f"API message error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_alert(self, title: str, message: str, channel: Optional[str] = None,
                        fields: Optional[List[Dict[str, str]]] = None,
                        thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send alert message"""
        return await self.send_typed_message(
            SlackMessageType.ALERT, title, message, channel, fields, thread_ts
        )
    
    async def send_success(self, title: str, message: str, channel: Optional[str] = None,
                          fields: Optional[List[Dict[str, str]]] = None,
                          thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send success message"""
        return await self.send_typed_message(
            SlackMessageType.SUCCESS, title, message, channel, fields, thread_ts
        )
    
    async def send_warning(self, title: str, message: str, channel: Optional[str] = None,
                          fields: Optional[List[Dict[str, str]]] = None,
                          thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send warning message"""
        return await self.send_typed_message(
            SlackMessageType.WARNING, title, message, channel, fields, thread_ts
        )
    
    async def send_error(self, title: str, message: str, channel: Optional[str] = None,
                        fields: Optional[List[Dict[str, str]]] = None,
                        thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send error message"""
        return await self.send_typed_message(
            SlackMessageType.ERROR, title, message, channel, fields, thread_ts
        )
    
    async def send_info(self, title: str, message: str, channel: Optional[str] = None,
                       fields: Optional[List[Dict[str, str]]] = None,
                       thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send info message"""
        return await self.send_typed_message(
            SlackMessageType.INFO, title, message, channel, fields, thread_ts
        )
    
    async def send_typed_message(self, message_type: SlackMessageType, title: str, 
                               message: str, channel: Optional[str] = None,
                               fields: Optional[List[Dict[str, str]]] = None,
                               thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send typed message with formatting"""
        
        channel = channel or self.default_channel
        color = self.message_colors.get(message_type, "#cccccc")
        emoji = self.message_emojis.get(message_type, ":robot_face:")
        
        attachment = SlackAttachment(
            color=color,
            title=title,
            text=message,
            fields=fields or [],
            footer=self.app_name,
            ts=int(datetime.now().timestamp())
        )
        
        slack_message = SlackMessage(
            channel=channel,
            text=f"{emoji} {title}",
            attachments=[attachment],
            thread_ts=thread_ts
        )
        
        return await self.send_message(slack_message)
    
    async def send_deployment_notification(self, service_name: str, version: str,
                                         status: str, environment: str,
                                         channel: Optional[str] = None) -> Dict[str, Any]:
        """Send deployment notification"""
        
        title = f"Deployment {status.title()}: {service_name}"
        message = f"Service `{service_name}` version `{version}` deployment {status} in `{environment}`"
        
        fields = [
            {"title": "Service", "value": service_name, "short": True},
            {"title": "Version", "value": version, "short": True},
            {"title": "Environment", "value": environment, "short": True},
            {"title": "Status", "value": status.title(), "short": True}
        ]
        
        if status.lower() == "success":
            return await self.send_success(title, message, channel, fields)
        elif status.lower() == "failed":
            return await self.send_error(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def send_agent_notification(self, agent_name: str, event_type: str,
                                    status: str, project_id: Optional[str] = None,
                                    details: Optional[Dict[str, Any]] = None,
                                    channel: Optional[str] = None) -> Dict[str, Any]:
        """Send agent event notification"""
        
        title = f"Agent Event: {agent_name}"
        message = f"Agent `{agent_name}` {event_type} - Status: {status}"
        
        fields = [
            {"title": "Agent", "value": agent_name, "short": True},
            {"title": "Event", "value": event_type, "short": True},
            {"title": "Status", "value": status, "short": True}
        ]
        
        if project_id:
            fields.append({"title": "Project ID", "value": project_id, "short": True})
        
        if details:
            for key, value in details.items():
                if len(fields) < 10:  # Slack limit
                    fields.append({"title": key.title(), "value": str(value), "short": True})
        
        if status.lower() in ["success", "completed"]:
            return await self.send_success(title, message, channel, fields)
        elif status.lower() in ["failed", "error"]:
            return await self.send_error(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def send_cost_alert(self, current_cost: float, budget_limit: float,
                            percentage_used: float, project_id: str,
                            channel: Optional[str] = None) -> Dict[str, Any]:
        """Send cost monitoring alert"""
        
        title = f"Cost Alert: Budget {percentage_used:.1f}% Used"
        message = f"Project `{project_id}` has used ${current_cost:.2f} of ${budget_limit:.2f} budget"
        
        fields = [
            {"title": "Current Cost", "value": f"${current_cost:.2f}", "short": True},
            {"title": "Budget Limit", "value": f"${budget_limit:.2f}", "short": True},
            {"title": "Percentage Used", "value": f"{percentage_used:.1f}%", "short": True},
            {"title": "Project ID", "value": project_id, "short": True}
        ]
        
        if percentage_used >= 90:
            return await self.send_alert(title, message, channel, fields)
        elif percentage_used >= 75:
            return await self.send_warning(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def send_security_alert(self, vulnerability_type: str, severity: str,
                                file_path: str, project_id: str,
                                details: Optional[Dict[str, Any]] = None,
                                channel: Optional[str] = None) -> Dict[str, Any]:
        """Send security vulnerability alert"""
        
        title = f"Security Alert: {vulnerability_type}"
        message = f"Security vulnerability detected in `{file_path}` - Severity: {severity}"
        
        fields = [
            {"title": "Vulnerability", "value": vulnerability_type, "short": True},
            {"title": "Severity", "value": severity, "short": True},
            {"title": "File", "value": file_path, "short": False},
            {"title": "Project ID", "value": project_id, "short": True}
        ]
        
        if details:
            for key, value in details.items():
                if len(fields) < 10:  # Slack limit
                    fields.append({"title": key.title(), "value": str(value), "short": True})
        
        if severity.lower() in ["critical", "high"]:
            return await self.send_alert(title, message, channel, fields)
        elif severity.lower() == "medium":
            return await self.send_warning(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def send_monitoring_alert(self, service_name: str, alert_type: str,
                                  metric_name: str, current_value: float,
                                  threshold: float, unit: str = "",
                                  channel: Optional[str] = None) -> Dict[str, Any]:
        """Send monitoring alert"""
        
        title = f"Monitoring Alert: {service_name}"
        message = f"Alert triggered for `{service_name}` - {metric_name}: {current_value}{unit}"
        
        fields = [
            {"title": "Service", "value": service_name, "short": True},
            {"title": "Alert Type", "value": alert_type, "short": True},
            {"title": "Metric", "value": metric_name, "short": True},
            {"title": "Current Value", "value": f"{current_value}{unit}", "short": True},
            {"title": "Threshold", "value": f"{threshold}{unit}", "short": True},
            {"title": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True}
        ]
        
        if alert_type.lower() in ["critical", "error"]:
            return await self.send_alert(title, message, channel, fields)
        elif alert_type.lower() == "warning":
            return await self.send_warning(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def send_build_notification(self, build_id: str, status: str,
                                    project_id: str, branch: str,
                                    commit_hash: str, duration: Optional[float] = None,
                                    channel: Optional[str] = None) -> Dict[str, Any]:
        """Send build notification"""
        
        title = f"Build {status.title()}: {project_id}"
        message = f"Build `{build_id}` {status} for project `{project_id}`"
        
        fields = [
            {"title": "Build ID", "value": build_id, "short": True},
            {"title": "Project", "value": project_id, "short": True},
            {"title": "Branch", "value": branch, "short": True},
            {"title": "Commit", "value": commit_hash[:8], "short": True},
            {"title": "Status", "value": status.title(), "short": True}
        ]
        
        if duration:
            fields.append({"title": "Duration", "value": f"{duration:.1f}s", "short": True})
        
        if status.lower() == "success":
            return await self.send_success(title, message, channel, fields)
        elif status.lower() == "failed":
            return await self.send_error(title, message, channel, fields)
        else:
            return await self.send_info(title, message, channel, fields)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack connection"""
        try:
            test_message = SlackMessage(
                channel=self.default_channel,
                text="🧪 Test message from SaaS Factory",
                attachments=[SlackAttachment(
                    color="#36a64f",
                    title="Connection Test",
                    text="If you can see this message, Slack integration is working correctly!",
                    footer=self.app_name,
                    ts=int(datetime.now().timestamp())
                )]
            )
            
            result = await self.send_message(test_message)
            
            if result["status"] == "success":
                logger.info("Slack connection test successful")
            else:
                logger.error(f"Slack connection test failed: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Slack connection test error: {e}")
            return {"status": "error", "message": str(e)}


# Global instance
slack_integration = SlackIntegration()


def get_slack_integration() -> SlackIntegration:
    """Get Slack integration instance"""
    return slack_integration


# Convenience functions
async def send_alert(title: str, message: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send alert message (convenience function)"""
    return await slack_integration.send_alert(title, message, channel, **kwargs)

async def send_success(title: str, message: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send success message (convenience function)"""
    return await slack_integration.send_success(title, message, channel, **kwargs)

async def send_warning(title: str, message: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send warning message (convenience function)"""
    return await slack_integration.send_warning(title, message, channel, **kwargs)

async def send_error(title: str, message: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send error message (convenience function)"""
    return await slack_integration.send_error(title, message, channel, **kwargs)

async def send_info(title: str, message: str, channel: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send info message (convenience function)"""
    return await slack_integration.send_info(title, message, channel, **kwargs) 