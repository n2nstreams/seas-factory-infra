"""
AIOps Agent - Night 46 Implementation
AI-driven operations with log streaming and Gemini-powered anomaly detection

This agent implements:
- Real-time log streaming from Google Cloud Logging
- Batch processing for anomaly detection using Gemini
- Intelligent alerting and incident response
- Performance monitoring and predictive analysis
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
import uuid

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Google Cloud imports
try:
    from google.cloud import logging as cloud_logging
    from google.cloud import monitoring_v3
    from google.cloud import error_reporting
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud libraries not available")

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    ERROR_SPIKE = "error_spike"
    LATENCY_INCREASE = "latency_increase"
    UNUSUAL_PATTERN = "unusual_pattern"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_INCIDENT = "security_incident"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class LogProcessingStatus(Enum):
    """Status of log processing batches"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LogEntry:
    """Structured log entry from Google Cloud Logging"""
    timestamp: datetime
    severity: str
    service: str
    message: str
    labels: Dict[str, str]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    http_request: Optional[Dict[str, Any]] = None
    operation: Optional[Dict[str, Any]] = None
    source_location: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "service": self.service,
            "message": self.message,
            "labels": self.labels,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "http_request": self.http_request,
            "operation": self.operation,
            "source_location": self.source_location
        }


@dataclass
class LogBatch:
    """Batch of logs for processing"""
    batch_id: str
    logs: List[LogEntry]
    created_at: datetime
    service_filter: Optional[str] = None
    time_window: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    status: LogProcessingStatus = LogProcessingStatus.PENDING
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    @property
    def log_count(self) -> int:
        return len(self.logs)
    
    @property
    def error_count(self) -> int:
        return sum(1 for log in self.logs if log.severity in ['ERROR', 'CRITICAL'])
    
    @property
    def warning_count(self) -> int:
        return sum(1 for log in self.logs if log.severity == 'WARNING')


@dataclass
class Anomaly:
    """Detected anomaly with Gemini analysis"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    service: str
    description: str
    gemini_analysis: str
    evidence: List[LogEntry]
    metrics: Dict[str, float]
    detected_at: datetime
    confidence_score: float  # 0.0 to 1.0
    recommended_actions: List[str]
    affected_resources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "service": self.service,
            "description": self.description,
            "gemini_analysis": self.gemini_analysis,
            "evidence_count": len(self.evidence),
            "metrics": self.metrics,
            "detected_at": self.detected_at.isoformat(),
            "confidence_score": self.confidence_score,
            "recommended_actions": self.recommended_actions,
            "affected_resources": self.affected_resources
        }


@dataclass
class Alert:
    """Alert generated from anomaly"""
    alert_id: str
    anomaly: Anomaly
    notification_channels: List[str]
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalated: bool = False
    
    @property
    def is_active(self) -> bool:
        return self.resolved_at is None
    
    @property
    def duration(self) -> timedelta:
        end_time = self.resolved_at or datetime.utcnow()
        return end_time - self.created_at


# Pydantic models for API
class LogStreamConfig(BaseModel):
    """Configuration for log streaming"""
    project_id: str
    services: List[str] = Field(default_factory=list)
    severity_filter: List[str] = Field(default=["ERROR", "WARNING", "INFO"])
    batch_size: int = Field(default=100, ge=10, le=1000)
    batch_timeout_seconds: int = Field(default=300, ge=60, le=3600)
    enable_gemini_analysis: bool = Field(default=True)


class AnomalyDetectionRequest(BaseModel):
    """Request for manual anomaly detection"""
    service: str
    time_range_minutes: int = Field(default=60, ge=5, le=1440)
    severity_threshold: str = Field(default="WARNING")


class AlertConfigUpdate(BaseModel):
    """Update alert configuration"""
    notification_channels: List[str]
    severity_threshold: AlertSeverity
    auto_escalation_enabled: bool = Field(default=True)
    escalation_delay_minutes: int = Field(default=30)


class LogAnalyticsQuery(BaseModel):
    """Query for log analytics"""
    service: Optional[str] = None
    start_time: datetime
    end_time: datetime
    anomaly_types: List[AnomalyType] = Field(default_factory=list)
    severity_levels: List[AlertSeverity] = Field(default_factory=list)


class AIOpsAgent:
    """
    Advanced AIOps Agent with Gemini-powered anomaly detection
    Implements Night 46: Stream logs, detect anomalies using Gemini on log batches
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Google Cloud clients
        if GOOGLE_CLOUD_AVAILABLE:
            self.logging_client = cloud_logging.Client(project=project_id)
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.error_reporting_client = error_reporting.Client(project=project_id)
            
            # Initialize Vertex AI for Gemini
            vertexai.init(project=project_id, location="us-central1")
            self.gemini_model = GenerativeModel("gemini-1.5-pro")
        else:
            self.logging_client = None
            self.monitoring_client = None
            self.error_reporting_client = None
            self.gemini_model = None
        
        # Internal state
        self.tenant_db = TenantDatabase()
        self.log_batches: Dict[str, LogBatch] = {}
        self.active_anomalies: Dict[str, Anomaly] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.log_streams: Dict[str, AsyncGenerator] = {}
        
        # Configuration
        self.default_batch_size = 100
        self.default_batch_timeout = 300  # 5 minutes
        self.anomaly_detection_enabled = True
        self.gemini_analysis_enabled = True
        
        # Performance tracking
        self.metrics = {
            "logs_processed": 0,
            "batches_created": 0,
            "anomalies_detected": 0,
            "alerts_generated": 0,
            "gemini_api_calls": 0
        }
        
        # Background tasks
        self._background_tasks = set()
        self._shutdown_event = asyncio.Event()
    
    async def start_log_streaming(self, config: LogStreamConfig) -> str:
        """
        Start streaming logs from Google Cloud Logging
        
        Args:
            config: Log streaming configuration
            
        Returns:
            stream_id: Unique identifier for the log stream
        """
        if not GOOGLE_CLOUD_AVAILABLE:
            raise HTTPException(status_code=500, detail="Google Cloud libraries not available")
        
        stream_id = f"stream-{uuid.uuid4()}"
        
        self.logger.info(f"Starting log stream {stream_id} for project {self.project_id}")
        
        # Create log stream
        log_stream = self._create_log_stream(config)
        self.log_streams[stream_id] = log_stream
        
        # Start background processing
        task = asyncio.create_task(self._process_log_stream(stream_id, log_stream, config))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        return stream_id
    
    def _create_log_stream(self, config: LogStreamConfig) -> AsyncGenerator[LogEntry, None]:
        """Create async generator for log streaming"""
        
        async def log_generator():
            """Async generator that yields log entries"""
            
            # Build filter string
            filters = []
            
            if config.services:
                service_filter = " OR ".join([f'resource.labels.service_name="{svc}"' for svc in config.services])
                filters.append(f"({service_filter})")
            
            if config.severity_filter:
                severity_filter = " OR ".join([f'severity="{sev}"' for sev in config.severity_filter])
                filters.append(f"({severity_filter})")
            
            # Add timestamp filter for recent logs
            timestamp_filter = f'timestamp >= "{(datetime.utcnow() - timedelta(minutes=5)).isoformat()}Z"'
            filters.append(timestamp_filter)
            
            filter_str = " AND ".join(filters)
            
            self.logger.info(f"Log filter: {filter_str}")
            
            try:
                # Use tail mode for real-time streaming
                entries = self.logging_client.list_entries(
                    filter_=filter_str,
                    order_by=cloud_logging.DESCENDING,
                    page_size=config.batch_size
                )
                
                for entry in entries:
                    log_entry = self._convert_cloud_log_entry(entry)
                    if log_entry:
                        yield log_entry
                        await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
                        
            except Exception as e:
                self.logger.error(f"Error in log streaming: {e}")
                raise
        
        return log_generator()
    
    def _convert_cloud_log_entry(self, entry) -> Optional[LogEntry]:
        """Convert Google Cloud Log entry to internal LogEntry format"""
        try:
            # Extract service name from resource labels
            service = "unknown"
            if hasattr(entry, 'resource') and entry.resource.labels:
                service = entry.resource.labels.get('service_name', 
                         entry.resource.labels.get('container_name',
                         entry.resource.labels.get('function_name', 'unknown')))
            
            # Extract labels
            labels = {}
            if hasattr(entry, 'labels') and entry.labels:
                labels = dict(entry.labels)
            
            # Extract HTTP request data
            http_request = None
            if hasattr(entry, 'http_request') and entry.http_request:
                http_request = {
                    "method": getattr(entry.http_request, 'request_method', None),
                    "url": getattr(entry.http_request, 'request_url', None),
                    "status": getattr(entry.http_request, 'status', None),
                    "response_size": getattr(entry.http_request, 'response_size', None),
                    "latency": getattr(entry.http_request, 'latency', None)
                }
            
            # Extract operation data
            operation = None
            if hasattr(entry, 'operation') and entry.operation:
                operation = {
                    "id": getattr(entry.operation, 'id', None),
                    "producer": getattr(entry.operation, 'producer', None),
                    "first": getattr(entry.operation, 'first', False),
                    "last": getattr(entry.operation, 'last', False)
                }
            
            # Extract source location
            source_location = None
            if hasattr(entry, 'source_location') and entry.source_location:
                source_location = {
                    "file": getattr(entry.source_location, 'file', None),
                    "line": getattr(entry.source_location, 'line', None),
                    "function": getattr(entry.source_location, 'function', None)
                }
            
            return LogEntry(
                timestamp=entry.timestamp or datetime.utcnow(),
                severity=entry.severity or "INFO",
                service=service,
                message=str(entry.payload) if entry.payload else "",
                labels=labels,
                trace_id=getattr(entry, 'trace', None),
                span_id=getattr(entry, 'span_id', None),
                http_request=http_request,
                operation=operation,
                source_location=source_location
            )
            
        except Exception as e:
            self.logger.error(f"Error converting log entry: {e}")
            return None
    
    async def _process_log_stream(self, stream_id: str, log_stream: AsyncGenerator, config: LogStreamConfig):
        """Process log stream and create batches for analysis"""
        
        current_batch_logs = []
        batch_start_time = datetime.utcnow()
        
        try:
            async for log_entry in log_stream:
                if self._shutdown_event.is_set():
                    break
                
                current_batch_logs.append(log_entry)
                self.metrics["logs_processed"] += 1
                
                # Check if batch is ready for processing
                batch_ready = (
                    len(current_batch_logs) >= config.batch_size or
                    (datetime.utcnow() - batch_start_time).total_seconds() >= config.batch_timeout_seconds
                )
                
                if batch_ready:
                    # Create batch
                    batch = LogBatch(
                        batch_id=f"batch-{uuid.uuid4()}",
                        logs=current_batch_logs.copy(),
                        created_at=datetime.utcnow(),
                        service_filter=",".join(config.services) if config.services else None
                    )
                    
                    self.log_batches[batch.batch_id] = batch
                    self.metrics["batches_created"] += 1
                    
                    # Process batch asynchronously
                    if config.enable_gemini_analysis:
                        task = asyncio.create_task(self._analyze_log_batch(batch))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    
                    # Reset for next batch
                    current_batch_logs = []
                    batch_start_time = datetime.utcnow()
                    
        except Exception as e:
            self.logger.error(f"Error processing log stream {stream_id}: {e}")
        finally:
            # Clean up stream
            if stream_id in self.log_streams:
                del self.log_streams[stream_id]
    
    async def _analyze_log_batch(self, batch: LogBatch):
        """Analyze log batch using Gemini for anomaly detection"""
        
        batch.status = LogProcessingStatus.PROCESSING
        batch.processing_started_at = datetime.utcnow()
        
        try:
            self.logger.info(f"Analyzing batch {batch.batch_id} with {batch.log_count} logs")
            
            # Quick statistical analysis
            stats = self._calculate_batch_statistics(batch)
            
            # Check for obvious anomalies first
            quick_anomalies = self._detect_quick_anomalies(batch, stats)
            
            # Use Gemini for deeper analysis if enabled
            if self.gemini_analysis_enabled and self.gemini_model:
                gemini_anomalies = await self._analyze_with_gemini(batch, stats)
                all_anomalies = quick_anomalies + gemini_anomalies
            else:
                all_anomalies = quick_anomalies
            
            # Process detected anomalies
            for anomaly in all_anomalies:
                await self._handle_detected_anomaly(anomaly)
            
            batch.status = LogProcessingStatus.COMPLETED
            batch.processing_completed_at = datetime.utcnow()
            
            self.logger.info(f"Completed analysis of batch {batch.batch_id}, found {len(all_anomalies)} anomalies")
            
        except Exception as e:
            self.logger.error(f"Error analyzing batch {batch.batch_id}: {e}")
            batch.status = LogProcessingStatus.FAILED
            batch.processing_completed_at = datetime.utcnow()
    
    def _calculate_batch_statistics(self, batch: LogBatch) -> Dict[str, Any]:
        """Calculate statistical metrics for the log batch"""
        
        stats = {
            "total_logs": batch.log_count,
            "error_count": batch.error_count,
            "warning_count": batch.warning_count,
            "error_rate": batch.error_count / batch.log_count if batch.log_count > 0 else 0,
            "services": defaultdict(int),
            "severities": defaultdict(int),
            "unique_messages": len(set(log.message for log in batch.logs)),
            "time_span": (max(log.timestamp for log in batch.logs) - 
                         min(log.timestamp for log in batch.logs)).total_seconds() if batch.logs else 0
        }
        
        for log in batch.logs:
            stats["services"][log.service] += 1
            stats["severities"][log.severity] += 1
        
        return stats
    
    def _detect_quick_anomalies(self, batch: LogBatch, stats: Dict[str, Any]) -> List[Anomaly]:
        """Detect obvious anomalies using rule-based analysis"""
        
        anomalies = []
        
        # High error rate anomaly
        if stats["error_rate"] > 0.1:  # More than 10% errors
            anomaly = Anomaly(
                anomaly_id=f"anomaly-{uuid.uuid4()}",
                anomaly_type=AnomalyType.ERROR_SPIKE,
                severity=AlertSeverity.HIGH if stats["error_rate"] > 0.3 else AlertSeverity.MEDIUM,
                service=max(stats["services"], key=stats["services"].get) if stats["services"] else "unknown",
                description=f"High error rate detected: {stats['error_rate']:.1%} ({stats['error_count']}/{stats['total_logs']} logs)",
                gemini_analysis="Rule-based detection: Error rate threshold exceeded",
                evidence=[log for log in batch.logs if log.severity in ['ERROR', 'CRITICAL']][:10],
                metrics={"error_rate": stats["error_rate"], "error_count": stats["error_count"]},
                detected_at=datetime.utcnow(),
                confidence_score=0.8,
                recommended_actions=[
                    "Investigate recent deployments or configuration changes",
                    "Check service health and resource utilization",
                    "Review error logs for common patterns"
                ]
            )
            anomalies.append(anomaly)
        
        # Repeated error pattern anomaly
        error_messages = [log.message for log in batch.logs if log.severity in ['ERROR', 'CRITICAL']]
        if error_messages:
            message_counts = defaultdict(int)
            for msg in error_messages:
                message_counts[msg] += 1
            
            repeated_errors = [(msg, count) for msg, count in message_counts.items() if count >= 5]
            if repeated_errors:
                most_common_error, count = max(repeated_errors, key=lambda x: x[1])
                
                anomaly = Anomaly(
                    anomaly_id=f"anomaly-{uuid.uuid4()}",
                    anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                    severity=AlertSeverity.MEDIUM,
                    service=max(stats["services"], key=stats["services"].get) if stats["services"] else "unknown",
                    description=f"Repeated error pattern detected: '{most_common_error[:100]}...' occurred {count} times",
                    gemini_analysis="Rule-based detection: Repeated error pattern threshold exceeded",
                    evidence=[log for log in batch.logs if log.message == most_common_error][:5],
                    metrics={"pattern_count": count, "unique_errors": len(message_counts)},
                    detected_at=datetime.utcnow(),
                    confidence_score=0.7,
                    recommended_actions=[
                        "Investigate the root cause of the repeated error",
                        "Check if this is a known issue with existing remediation",
                        "Consider implementing circuit breaker pattern if applicable"
                    ]
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _analyze_with_gemini(self, batch: LogBatch, stats: Dict[str, Any]) -> List[Anomaly]:
        """Use Gemini AI to analyze log batch for complex anomalies"""
        
        try:
            self.metrics["gemini_api_calls"] += 1
            
            # Prepare log sample for Gemini analysis (limit size to avoid token limits)
            log_sample = batch.logs[:50]  # Take first 50 logs
            
            # Create analysis prompt
            prompt = self._create_gemini_analysis_prompt(log_sample, stats)
            
            # Call Gemini
            response = await self._call_gemini_async(prompt)
            
            # Parse Gemini response
            anomalies = self._parse_gemini_response(response, batch)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error in Gemini analysis: {e}")
            return []
    
    def _create_gemini_analysis_prompt(self, logs: List[LogEntry], stats: Dict[str, Any]) -> str:
        """Create analysis prompt for Gemini"""
        
        log_sample_text = "\n".join([
            f"[{log.timestamp}] {log.severity} {log.service}: {log.message[:200]}"
            for log in logs[:20]  # Show only first 20 logs in prompt
        ])
        
        prompt = f"""
        Analyze the following log batch for anomalies and unusual patterns:

        BATCH STATISTICS:
        - Total logs: {stats['total_logs']}
        - Error rate: {stats['error_rate']:.1%}
        - Services: {list(stats['services'].keys())}
        - Time span: {stats['time_span']:.1f} seconds

        LOG SAMPLE:
        {log_sample_text}

        Please analyze this log data and identify any anomalies. Look for:
        1. Unusual error patterns or spikes
        2. Performance degradation indicators
        3. Security-related issues
        4. Resource exhaustion signs
        5. Service reliability problems

        For each anomaly found, provide:
        - Type of anomaly (error_spike, latency_increase, unusual_pattern, resource_exhaustion, security_incident, performance_degradation)
        - Severity level (low, medium, high, critical)
        - Detailed description
        - Confidence score (0.0 to 1.0)
        - Specific affected service
        - Recommended actions

        Format your response as JSON with the following structure:
        {{
            "anomalies": [
                {{
                    "type": "anomaly_type",
                    "severity": "severity_level",
                    "service": "service_name",
                    "description": "detailed description",
                    "confidence": 0.0,
                    "recommended_actions": ["action1", "action2"],
                    "analysis": "detailed analysis explanation"
                }}
            ]
        }}

        If no significant anomalies are found, return {{"anomalies": []}}.
        """
        
        return prompt
    
    async def _call_gemini_async(self, prompt: str) -> str:
        """Call Gemini API asynchronously"""
        
        try:
            # Run Gemini call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _parse_gemini_response(self, response: str, batch: LogBatch) -> List[Anomaly]:
        """Parse Gemini response and create Anomaly objects"""
        
        try:
            # Clean response (remove any markdown formatting)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            # Parse JSON response
            data = json.loads(clean_response)
            
            anomalies = []
            for anomaly_data in data.get("anomalies", []):
                try:
                    anomaly = Anomaly(
                        anomaly_id=f"anomaly-{uuid.uuid4()}",
                        anomaly_type=AnomalyType(anomaly_data["type"]),
                        severity=AlertSeverity(anomaly_data["severity"]),
                        service=anomaly_data["service"],
                        description=anomaly_data["description"],
                        gemini_analysis=anomaly_data.get("analysis", ""),
                        evidence=batch.logs[:10],  # Include some log evidence
                        metrics={"confidence": anomaly_data.get("confidence", 0.5)},
                        detected_at=datetime.utcnow(),
                        confidence_score=anomaly_data.get("confidence", 0.5),
                        recommended_actions=anomaly_data.get("recommended_actions", [])
                    )
                    anomalies.append(anomaly)
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"Invalid anomaly data from Gemini: {e}")
                    continue
            
            return anomalies
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini response as JSON: {e}")
            self.logger.debug(f"Raw response: {response}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing Gemini response: {e}")
            return []
    
    async def _handle_detected_anomaly(self, anomaly: Anomaly):
        """Handle a detected anomaly (create alerts, notifications, etc.)"""
        
        self.active_anomalies[anomaly.anomaly_id] = anomaly
        self.metrics["anomalies_detected"] += 1
        
        self.logger.warning(f"Anomaly detected: {anomaly.description}")
        
        # Create alert if severity warrants it
        if anomaly.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            alert = Alert(
                alert_id=f"alert-{uuid.uuid4()}",
                anomaly=anomaly,
                notification_channels=["email", "slack"],  # Default channels
                created_at=datetime.utcnow()
            )
            
            self.active_alerts[alert.alert_id] = alert
            self.metrics["alerts_generated"] += 1
            
            # Trigger notifications
            await self._send_alert_notifications(alert)
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send notifications for alerts"""
        
        try:
            # Log alert to Cloud Logging
            if self.logging_client:
                self.logging_client.logger("aiops-alerts").log_struct({
                    "alert_id": alert.alert_id,
                    "anomaly": alert.anomaly.to_dict(),
                    "severity": alert.anomaly.severity.value,
                    "service": alert.anomaly.service,
                    "timestamp": alert.created_at.isoformat()
                })
            
            # Report to Error Reporting for critical alerts
            if alert.anomaly.severity == AlertSeverity.CRITICAL and self.error_reporting_client:
                self.error_reporting_client.report_exception()
            
            # TODO: Add email/Slack/PagerDuty integrations here
            self.logger.info(f"Alert notifications sent for {alert.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert notifications: {e}")
    
    async def get_anomalies(self, 
                           service: Optional[str] = None,
                           severity: Optional[AlertSeverity] = None,
                           limit: int = 100) -> List[Anomaly]:
        """Get detected anomalies with optional filtering"""
        
        anomalies = list(self.active_anomalies.values())
        
        # Apply filters
        if service:
            anomalies = [a for a in anomalies if a.service == service]
        
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        # Sort by detection time (newest first)
        anomalies.sort(key=lambda a: a.detected_at, reverse=True)
        
        return anomalies[:limit]
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.active_alerts.values() if alert.is_active]
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged_at = datetime.utcnow()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_note: str = "") -> bool:
        """Resolve an alert"""
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.utcnow()
            
            self.logger.info(f"Alert {alert_id} resolved by {resolved_by}: {resolution_note}")
            return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        
        return {
            **self.metrics,
            "active_streams": len(self.log_streams),
            "active_anomalies": len(self.active_anomalies),
            "active_alerts": len([a for a in self.active_alerts.values() if a.is_active]),
            "pending_batches": len([b for b in self.log_batches.values() if b.status == LogProcessingStatus.PENDING]),
            "processing_batches": len([b for b in self.log_batches.values() if b.status == LogProcessingStatus.PROCESSING])
        }
    
    async def cleanup_old_data(self, retention_days: int = 7):
        """Clean up old batches, anomalies, and alerts"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
        
        # Clean up old batches
        old_batches = [bid for bid, batch in self.log_batches.items() 
                      if batch.created_at < cutoff_time]
        for bid in old_batches:
            del self.log_batches[bid]
        
        # Clean up old anomalies
        old_anomalies = [aid for aid, anomaly in self.active_anomalies.items() 
                        if anomaly.detected_at < cutoff_time]
        for aid in old_anomalies:
            del self.active_anomalies[aid]
        
        # Clean up resolved alerts older than retention period
        old_alerts = [aid for aid, alert in self.active_alerts.items() 
                     if alert.resolved_at and alert.resolved_at < cutoff_time]
        for aid in old_alerts:
            del self.active_alerts[aid]
        
        self.logger.info(f"Cleaned up {len(old_batches)} batches, {len(old_anomalies)} anomalies, {len(old_alerts)} alerts")
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        
        self.logger.info("Shutting down AIOps Agent...")
        
        # Signal shutdown to background tasks
        self._shutdown_event.set()
        
        # Wait for background tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Clear streams
        self.log_streams.clear()
        
        self.logger.info("AIOps Agent shutdown complete")


# FastAPI application
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler"""
    # Startup
    logger.info("Starting AIOps Agent service...")
    yield
    # Shutdown
    logger.info("Shutting down AIOps Agent service...")


app = FastAPI(
    title="AIOps Agent - Night 46",
    description="AI-driven operations with log streaming and Gemini-powered anomaly detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[AIOpsAgent] = None


def get_aiops_agent() -> AIOpsAgent:
    """Get the global AIOps agent instance"""
    global agent
    if agent is None:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saas-factory-prod")
        agent = AIOpsAgent(project_id)
    return agent


@app.post("/start-log-streaming")
async def start_log_streaming(
    config: LogStreamConfig,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Start streaming logs from Google Cloud Logging"""
    
    try:
        stream_id = await aiops_agent.start_log_streaming(config)
        
        return {
            "status": "success",
            "stream_id": stream_id,
            "message": f"Log streaming started for project {config.project_id}",
            "config": config.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Failed to start log streaming: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start log streaming: {str(e)}")


@app.post("/detect-anomalies")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Manually trigger anomaly detection for a service"""
    
    # This endpoint would trigger manual analysis of recent logs
    # For now, return the current anomalies
    anomalies = await aiops_agent.get_anomalies(
        service=request.service,
        limit=50
    )
    
    return {
        "status": "success",
        "service": request.service,
        "anomalies_found": len(anomalies),
        "anomalies": [anomaly.to_dict() for anomaly in anomalies]
    }


@app.get("/anomalies")
async def get_anomalies(
    service: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Get detected anomalies"""
    
    severity_enum = None
    if severity:
        try:
            severity_enum = AlertSeverity(severity.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    anomalies = await aiops_agent.get_anomalies(
        service=service,
        severity=severity_enum,
        limit=limit
    )
    
    return {
        "status": "success",
        "total_anomalies": len(anomalies),
        "anomalies": [anomaly.to_dict() for anomaly in anomalies]
    }


@app.get("/alerts")
async def get_active_alerts(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Get active alerts"""
    
    alerts = await aiops_agent.get_active_alerts()
    
    return {
        "status": "success",
        "active_alerts": len(alerts),
        "alerts": [
            {
                "alert_id": alert.alert_id,
                "anomaly": alert.anomaly.to_dict(),
                "created_at": alert.created_at.isoformat(),
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "duration_seconds": alert.duration.total_seconds()
            }
            for alert in alerts
        ]
    }


@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Acknowledge an alert"""
    
    success = await aiops_agent.acknowledge_alert(alert_id, "user")  # TODO: Get actual user from context
    
    if success:
        return {"status": "success", "message": f"Alert {alert_id} acknowledged"}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_note: str = "",
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Resolve an alert"""
    
    success = await aiops_agent.resolve_alert(alert_id, "user", resolution_note)  # TODO: Get actual user
    
    if success:
        return {"status": "success", "message": f"Alert {alert_id} resolved"}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")


@app.get("/metrics")
async def get_metrics(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Get agent performance metrics"""
    
    metrics = aiops_agent.get_metrics()
    
    return {
        "status": "success",
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/cleanup")
async def cleanup_old_data(
    retention_days: int = 7,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    aiops_agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """Clean up old data"""
    
    await aiops_agent.cleanup_old_data(retention_days)
    
    return {
        "status": "success",
        "message": f"Cleaned up data older than {retention_days} days"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "google_cloud_available": GOOGLE_CLOUD_AVAILABLE
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8086)),
        log_level="info"
    )
