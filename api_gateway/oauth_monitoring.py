#!/usr/bin/env python3
"""
OAuth Monitoring and Analytics System
Tracks OAuth performance, error rates, and provides insights for production deployment
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class OAuthEvent:
    """Represents an OAuth authentication event"""
    timestamp: datetime
    provider: str  # 'google' or 'github'
    event_type: str  # 'start', 'success', 'error', 'callback'
    user_email: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class OAuthMetrics:
    """OAuth performance metrics"""
    total_attempts: int = 0
    successful_auths: int = 0
    failed_auths: int = 0
    average_response_time_ms: float = 0.0
    error_rate: float = 0.0
    last_24h_attempts: int = 0
    last_24h_successes: int = 0
    last_24h_failures: int = 0

class OAuthMonitor:
    """Monitors and tracks OAuth authentication performance"""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self.metrics: Dict[str, OAuthMetrics] = {
            'google': OAuthMetrics(),
            'github': OAuthMetrics()
        }
        self.start_time = datetime.utcnow()
        
    def record_event(self, event: OAuthEvent):
        """Record an OAuth event"""
        try:
            self.events.append(event)
            self._update_metrics(event)
            logger.info(f"OAuth event recorded: {event.provider} {event.event_type}")
        except Exception as e:
            logger.error(f"Failed to record OAuth event: {e}")
    
    def _update_metrics(self, event: OAuthEvent):
        """Update metrics based on the event"""
        provider = event.provider
        if provider not in self.metrics:
            self.metrics[provider] = OAuthMetrics()
        
        metrics = self.metrics[provider]
        
        if event.event_type == 'start':
            metrics.total_attempts += 1
            metrics.last_24h_attempts += 1
            
        elif event.event_type == 'success':
            metrics.successful_auths += 1
            metrics.last_24h_successes += 1
            
        elif event.event_type == 'error':
            metrics.failed_auths += 1
            metrics.last_24h_failures += 1
            
        # Update response time
        if event.response_time_ms:
            if metrics.average_response_time_ms == 0:
                metrics.average_response_time_ms = event.response_time_ms
            else:
                metrics.average_response_time_ms = (
                    (metrics.average_response_time_ms + event.response_time_ms) / 2
                )
        
        # Calculate error rate
        total = metrics.successful_auths + metrics.failed_auths
        if total > 0:
            metrics.error_rate = (metrics.failed_auths / total) * 100
    
    def get_provider_metrics(self, provider: str) -> Optional[OAuthMetrics]:
        """Get metrics for a specific OAuth provider"""
        return self.metrics.get(provider)
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall OAuth metrics across all providers"""
        total_attempts = sum(m.total_attempts for m in self.metrics.values())
        total_successes = sum(m.successful_auths for m in self.metrics.values())
        total_failures = sum(m.failed_auths for m in self.metrics.values())
        
        overall_error_rate = 0
        if total_attempts > 0:
            overall_error_rate = (total_failures / total_attempts) * 100
        
        avg_response_time = 0
        providers_with_time = [m for m in self.metrics.values() if m.average_response_time_ms > 0]
        if providers_with_time:
            avg_response_time = sum(m.average_response_time_ms for m in providers_with_time) / len(providers_with_time)
        
        return {
            'total_attempts': total_attempts,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'overall_error_rate': round(overall_error_rate, 2),
            'average_response_time_ms': round(avg_response_time, 2),
            'uptime_seconds': int((datetime.utcnow() - self.start_time).total_seconds()),
            'providers': {
                provider: asdict(metrics) for provider, metrics in self.metrics.items()
            }
        }
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent OAuth events"""
        recent_events = list(self.events)[-limit:]
        return [
            {
                'timestamp': event.timestamp.isoformat(),
                'provider': event.provider,
                'event_type': event.event_type,
                'user_email': event.user_email,
                'error_message': event.error_message,
                'response_time_ms': event.response_time_ms
            }
            for event in recent_events
        ]
    
    def cleanup_old_events(self, max_age_hours: int = 24):
        """Clean up events older than specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.events = deque(
            [event for event in self.events if event.timestamp > cutoff_time],
            maxlen=self.max_events
        )
        
        # Reset 24h counters
        for metrics in self.metrics.values():
            metrics.last_24h_attempts = 0
            metrics.last_24h_successes = 0
            metrics.last_24h_failures = 0

# Global OAuth monitor instance
oauth_monitor = OAuthMonitor()

def record_oauth_start(provider: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """Record the start of an OAuth flow"""
    event = OAuthEvent(
        timestamp=datetime.utcnow(),
        provider=provider,
        event_type='start',
        ip_address=ip_address,
        user_agent=user_agent
    )
    oauth_monitor.record_event(event)

def record_oauth_success(provider: str, user_email: str, response_time_ms: float, 
                        ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """Record a successful OAuth authentication"""
    event = OAuthEvent(
        timestamp=datetime.utcnow(),
        provider=provider,
        event_type='success',
        user_email=user_email,
        response_time_ms=response_time_ms,
        ip_address=ip_address,
        user_agent=user_agent
    )
    oauth_monitor.record_event(event)

def record_oauth_error(provider: str, error_message: str, response_time_ms: Optional[float] = None,
                      ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """Record an OAuth error"""
    event = OAuthEvent(
        timestamp=datetime.utcnow(),
        provider=provider,
        event_type='error',
        error_message=error_message,
        response_time_ms=response_time_ms,
        ip_address=ip_address,
        user_agent=user_agent
    )
    oauth_monitor.record_event(event)

def record_oauth_callback(provider: str, user_email: Optional[str] = None,
                         response_time_ms: Optional[float] = None):
    """Record an OAuth callback event"""
    event = OAuthEvent(
        timestamp=datetime.utcnow(),
        provider=provider,
        event_type='callback',
        user_email=user_email,
        response_time_ms=response_time_ms
    )
    oauth_monitor.record_event(event)

async def cleanup_old_events():
    """Background task to clean up old events"""
    while True:
        try:
            oauth_monitor.cleanup_old_events()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error cleaning up OAuth events: {e}")
            await asyncio.sleep(3600)

def start_cleanup_task():
    """Start the background cleanup task"""
    asyncio.create_task(cleanup_old_events())
