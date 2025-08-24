"""
Rollback Controller - Night 47 Implementation
Handles error budget monitoring and triggers Cloud Deploy auto-rollbacks

This module:
- Receives webhook alerts when error budget > 1% in 1 hour
- Interfaces with Cloud Deploy API for automated rollbacks
- Tracks rollback history and status
- Provides rollback decision logic
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid

# Google Cloud imports
try:
    from google.cloud import deploy_v1
    from google.cloud import monitoring_v3
    from google.cloud import logging as cloud_logging
    import googleapiclient.discovery
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud libraries not available")

# FastAPI imports
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RollbackStatus(Enum):
    """Status of rollback operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RollbackTrigger(Enum):
    """What triggered the rollback"""
    ERROR_BUDGET_EXCEEDED = "error_budget_exceeded"
    MANUAL = "manual"
    HEALTH_CHECK_FAILED = "health_check_failed"
    SLO_VIOLATION = "slo_violation"


@dataclass
class ErrorBudgetAlert:
    """Error budget alert from monitoring"""
    alert_id: str
    service_name: str
    error_rate: float
    duration_minutes: int
    timestamp: datetime
    alert_policy: str
    raw_alert: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackDecision:
    """Decision about whether to proceed with rollback"""
    should_rollback: bool
    reason: str
    confidence: float
    target_revision: Optional[str] = None
    estimated_impact: str = ""
    rollback_strategy: str = "immediate"


@dataclass
class RollbackOperation:
    """Details of a rollback operation"""
    rollback_id: str
    service_name: str
    trigger: RollbackTrigger
    status: RollbackStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    source_revision: Optional[str] = None
    target_revision: Optional[str] = None
    deployment_id: Optional[str] = None
    error_message: Optional[str] = None
    decision: Optional[RollbackDecision] = None


# Webhook request model
class ErrorBudgetWebhookRequest(BaseModel):
    """Model for error budget webhook requests"""
    incident: Dict[str, Any] = Field(..., description="Alert incident data")
    version: str = Field(default="1.2", description="Webhook version")


class RollbackController:
    """
    Rollback Controller for automated Cloud Deploy rollbacks
    Implements Night 47: Auto-rollback when error budget > 1% in 1 hour
    """
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Google Cloud clients
        if GOOGLE_CLOUD_AVAILABLE:
            self.deploy_client = deploy_v1.CloudDeployClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.logging_client = cloud_logging.Client(project=project_id)
        else:
            self.deploy_client = None
            self.monitoring_client = None
            self.logging_client = None
        
        # Internal state
        self.active_rollbacks: Dict[str, RollbackOperation] = {}
        self.rollback_history: List[RollbackOperation] = []
        
        # Configuration
        self.pipeline_name = f"projects/{project_id}/locations/{region}/deliveryPipelines/api-backend-pipeline"
        self.target_name = f"projects/{project_id}/locations/{region}/targets/production"
        self.error_budget_threshold = 0.01  # 1%
        self.rollback_enabled = True
        
        # Rollback decision parameters
        self.min_confidence_threshold = 0.8
        self.cooldown_period_minutes = 30
        self.max_rollbacks_per_hour = 3
        
        # Metrics
        self.metrics = {
            "webhook_alerts_received": 0,
            "rollbacks_triggered": 0,
            "rollbacks_successful": 0,
            "rollbacks_failed": 0,
            "decisions_skipped": 0
        }
    
    async def handle_error_budget_webhook(self, request: ErrorBudgetWebhookRequest, auth_token: str) -> Dict[str, Any]:
        """
        Handle incoming error budget alert webhook
        
        Args:
            request: The webhook request data
            auth_token: Authentication token for verification
            
        Returns:
            Dict: Response indicating action taken
        """
        self.metrics["webhook_alerts_received"] += 1
        self.logger.info("Received error budget alert webhook")
        
        try:
            # Verify webhook token
            if not self._verify_webhook_token(auth_token):
                raise HTTPException(status_code=401, detail="Invalid webhook token")
            
            # Parse alert data
            alert = self._parse_error_budget_alert(request.incident)
            
            # Log the alert
            self._log_alert_received(alert)
            
            # Make rollback decision
            decision = await self._make_rollback_decision(alert)
            
            response = {
                "alert_id": alert.alert_id,
                "received_at": datetime.utcnow().isoformat(),
                "action": "none"
            }
            
            if decision.should_rollback:
                # Trigger rollback
                rollback_op = await self._trigger_rollback(alert, decision)
                response.update({
                    "action": "rollback_triggered",
                    "rollback_id": rollback_op.rollback_id,
                    "reason": decision.reason
                })
                
                self.logger.warning(f"Auto-rollback triggered: {rollback_op.rollback_id}")
            else:
                response.update({
                    "action": "rollback_skipped",
                    "reason": decision.reason
                })
                
                self.metrics["decisions_skipped"] += 1
                self.logger.info(f"Rollback skipped: {decision.reason}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")
    
    def _verify_webhook_token(self, token: str) -> bool:
        """Verify the webhook authentication token"""
        # In production, compare with token from Secret Manager
        expected_token = os.getenv("ERROR_BUDGET_WEBHOOK_TOKEN", "development-token")
        return token == expected_token
    
    def _parse_error_budget_alert(self, incident_data: Dict[str, Any]) -> ErrorBudgetAlert:
        """Parse the error budget alert from monitoring webhook"""
        
        # Extract key information from Cloud Monitoring alert
        alert_id = incident_data.get("incident_id", str(uuid.uuid4()))
        policy_name = incident_data.get("policy_name", "unknown")
        
        # Parse service name from alert (default to api-backend)
        service_name = "api-backend"
        if "condition" in incident_data:
            condition = incident_data["condition"]
            if "displayName" in condition and "api-backend" in condition["displayName"]:
                service_name = "api-backend"
        
        # Extract error rate and duration from alert
        error_rate = 0.01  # Default to 1% if not parsed
        duration_minutes = 60  # Default to 1 hour
        
        # Try to extract actual values from condition
        if "condition" in incident_data:
            threshold_value = incident_data["condition"].get("thresholdValue", 0.01)
            error_rate = float(threshold_value)
        
        return ErrorBudgetAlert(
            alert_id=alert_id,
            service_name=service_name,
            error_rate=error_rate,
            duration_minutes=duration_minutes,
            timestamp=datetime.utcnow(),
            alert_policy=policy_name,
            raw_alert=incident_data
        )
    
    def _log_alert_received(self, alert: ErrorBudgetAlert):
        """Log the alert to Cloud Logging"""
        if self.logging_client:
            self.logging_client.logger("rollback-controller").log_struct({
                "event": "error_budget_alert_received",
                "alert_id": alert.alert_id,
                "service_name": alert.service_name,
                "error_rate": alert.error_rate,
                "duration_minutes": alert.duration_minutes,
                "timestamp": alert.timestamp.isoformat(),
                "severity": "WARNING"
            })
    
    async def _make_rollback_decision(self, alert: ErrorBudgetAlert) -> RollbackDecision:
        """
        Make intelligent decision about whether to rollback
        
        Args:
            alert: The error budget alert
            
        Returns:
            RollbackDecision: Decision with reasoning
        """
        self.logger.info(f"Making rollback decision for alert {alert.alert_id}")
        
        # Check if rollbacks are enabled
        if not self.rollback_enabled:
            return RollbackDecision(
                should_rollback=False,
                reason="Rollbacks disabled",
                confidence=1.0
            )
        
        # Check error rate threshold
        if alert.error_rate <= self.error_budget_threshold:
            return RollbackDecision(
                should_rollback=False,
                reason=f"Error rate {alert.error_rate:.3f} below threshold {self.error_budget_threshold}",
                confidence=0.9
            )
        
        # Check for recent rollbacks (cooldown period)
        recent_rollbacks = self._get_recent_rollbacks(alert.service_name, minutes=self.cooldown_period_minutes)
        if recent_rollbacks:
            return RollbackDecision(
                should_rollback=False,
                reason=f"Rollback in cooldown period ({len(recent_rollbacks)} recent rollbacks)",
                confidence=0.8
            )
        
        # Check hourly rollback limit
        hourly_rollbacks = self._get_recent_rollbacks(alert.service_name, minutes=60)
        if len(hourly_rollbacks) >= self.max_rollbacks_per_hour:
            return RollbackDecision(
                should_rollback=False,
                reason=f"Hourly rollback limit exceeded ({len(hourly_rollbacks)}/{self.max_rollbacks_per_hour})",
                confidence=0.9
            )
        
        # Get target revision for rollback
        target_revision = await self._get_last_known_good_revision(alert.service_name)
        if not target_revision:
            return RollbackDecision(
                should_rollback=False,
                reason="No known good revision available",
                confidence=0.7
            )
        
        # Calculate confidence based on alert severity and duration
        confidence = min(0.95, 0.7 + (alert.error_rate - self.error_budget_threshold) * 10)
        confidence = min(confidence, 0.7 + (alert.duration_minutes / 60) * 0.2)
        
        if confidence < self.min_confidence_threshold:
            return RollbackDecision(
                should_rollback=False,
                reason=f"Confidence too low ({confidence:.2f} < {self.min_confidence_threshold})",
                confidence=confidence
            )
        
        # Decision: proceed with rollback
        return RollbackDecision(
            should_rollback=True,
            reason=f"Error rate {alert.error_rate:.3f} exceeds threshold for {alert.duration_minutes}min",
            confidence=confidence,
            target_revision=target_revision,
            estimated_impact="Moderate - rolling back to last known good revision",
            rollback_strategy="immediate"
        )
    
    def _get_recent_rollbacks(self, service_name: str, minutes: int) -> List[RollbackOperation]:
        """Get recent rollbacks for a service within the specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        recent_rollbacks = [
            rb for rb in self.rollback_history
            if rb.service_name == service_name and rb.created_at > cutoff_time
        ]
        
        return recent_rollbacks
    
    async def _get_last_known_good_revision(self, service_name: str) -> Optional[str]:
        """Get the last known good revision for rollback target"""
        
        if not self.deploy_client:
            # Mock for development
            return "previous-revision-abc123"
        
        try:
            # Query Cloud Deploy for recent successful deployments
            request = deploy_v1.ListReleasesRequest(
                parent=self.pipeline_name,
                page_size=10,
                order_by="create_time desc"
            )
            
            releases = self.deploy_client.list_releases(request=request)
            
            for release in releases:
                if release.deploy_parameters and release.deploy_parameters.get("success", False):
                    # Found a successful release
                    return release.name.split("/")[-1]
            
            # Fallback: use a default revision identifier
            return "stable-revision"
            
        except Exception as e:
            self.logger.error(f"Error getting last known good revision: {e}")
            return None
    
    async def _trigger_rollback(self, alert: ErrorBudgetAlert, decision: RollbackDecision) -> RollbackOperation:
        """
        Trigger the actual rollback via Cloud Deploy
        
        Args:
            alert: The alert that triggered the rollback
            decision: The rollback decision
            
        Returns:
            RollbackOperation: The rollback operation details
        """
        rollback_id = f"auto-rollback-{int(time.time())}"
        
        rollback_op = RollbackOperation(
            rollback_id=rollback_id,
            service_name=alert.service_name,
            trigger=RollbackTrigger.ERROR_BUDGET_EXCEEDED,
            status=RollbackStatus.PENDING,
            created_at=datetime.utcnow(),
            target_revision=decision.target_revision,
            decision=decision
        )
        
        self.active_rollbacks[rollback_id] = rollback_op
        self.metrics["rollbacks_triggered"] += 1
        
        try:
            # Execute the rollback
            await self._execute_cloud_deploy_rollback(rollback_op)
            
            rollback_op.status = RollbackStatus.IN_PROGRESS
            rollback_op.started_at = datetime.utcnow()
            
            # Log rollback initiation
            self._log_rollback_initiated(rollback_op)
            
            # Start monitoring rollback progress in background
            asyncio.create_task(self._monitor_rollback_progress(rollback_op))
            
        except Exception as e:
            rollback_op.status = RollbackStatus.FAILED
            rollback_op.error_message = str(e)
            self.metrics["rollbacks_failed"] += 1
            
            self.logger.error(f"Failed to trigger rollback {rollback_id}: {e}")
        
        return rollback_op
    
    async def _execute_cloud_deploy_rollback(self, rollback_op: RollbackOperation):
        """Execute the actual Cloud Deploy rollback operation"""
        
        if not self.deploy_client:
            # Simulate rollback for development
            self.logger.info(f"Simulating rollback for {rollback_op.rollback_id}")
            return
        
        try:
            # Create a rollback request to Cloud Deploy
            request = deploy_v1.RollbackTargetRequest(
                name=self.target_name,
                target_id=rollback_op.target_revision,
                rollback_id=rollback_op.rollback_id
            )
            
            # Execute the rollback
            operation = self.deploy_client.rollback_target(request=request)
            rollback_op.deployment_id = operation.name
            
            self.logger.info(f"Cloud Deploy rollback initiated: {operation.name}")
            
        except Exception as e:
            self.logger.error(f"Cloud Deploy rollback failed: {e}")
            raise
    
    def _log_rollback_initiated(self, rollback_op: RollbackOperation):
        """Log rollback initiation to Cloud Logging"""
        if self.logging_client:
            self.logging_client.logger("rollback-controller").log_struct({
                "event": "auto_rollback_initiated",
                "rollback_id": rollback_op.rollback_id,
                "service_name": rollback_op.service_name,
                "trigger": rollback_op.trigger.value,
                "target_revision": rollback_op.target_revision,
                "timestamp": rollback_op.created_at.isoformat(),
                "severity": "WARNING"
            })
    
    async def _monitor_rollback_progress(self, rollback_op: RollbackOperation):
        """Monitor rollback progress and update status"""
        
        max_wait_time = 600  # 10 minutes
        check_interval = 30  # 30 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time and rollback_op.status == RollbackStatus.IN_PROGRESS:
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
            
            # Check rollback status
            success = await self._check_rollback_success(rollback_op)
            
            if success:
                rollback_op.status = RollbackStatus.COMPLETED
                rollback_op.completed_at = datetime.utcnow()
                self.metrics["rollbacks_successful"] += 1
                
                self.logger.info(f"Rollback {rollback_op.rollback_id} completed successfully")
                break
            elif success is False:  # Explicitly failed
                rollback_op.status = RollbackStatus.FAILED
                rollback_op.completed_at = datetime.utcnow()
                self.metrics["rollbacks_failed"] += 1
                
                self.logger.error(f"Rollback {rollback_op.rollback_id} failed")
                break
        
        if elapsed_time >= max_wait_time and rollback_op.status == RollbackStatus.IN_PROGRESS:
            rollback_op.status = RollbackStatus.FAILED
            rollback_op.error_message = "Rollback timeout"
            rollback_op.completed_at = datetime.utcnow()
            self.metrics["rollbacks_failed"] += 1
        
        # Move to history
        self.rollback_history.append(rollback_op)
        if rollback_op.rollback_id in self.active_rollbacks:
            del self.active_rollbacks[rollback_op.rollback_id]
    
    async def _check_rollback_success(self, rollback_op: RollbackOperation) -> Optional[bool]:
        """
        Check if rollback was successful
        
        Returns:
            True if successful, False if failed, None if still in progress
        """
        
        if not self.deploy_client:
            # Simulate success for development
            return True
        
        try:
            # Check deployment operation status
            if rollback_op.deployment_id:
                operation = self.deploy_client.get_operation(name=rollback_op.deployment_id)
                
                if operation.done:
                    if operation.error:
                        return False
                    else:
                        return True
                else:
                    return None  # Still in progress
                    
        except Exception as e:
            self.logger.error(f"Error checking rollback status: {e}")
            return False
        
        return None
    
    def get_rollback_status(self, rollback_id: str) -> Optional[RollbackOperation]:
        """Get the status of a specific rollback operation"""
        return self.active_rollbacks.get(rollback_id) or next(
            (rb for rb in self.rollback_history if rb.rollback_id == rollback_id),
            None
        )
    
    def get_recent_rollbacks(self, hours: int = 24) -> List[RollbackOperation]:
        """Get recent rollback operations"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent = [
            rb for rb in self.rollback_history
            if rb.created_at > cutoff_time
        ]
        
        # Include active rollbacks
        recent.extend(self.active_rollbacks.values())
        
        return sorted(recent, key=lambda x: x.created_at, reverse=True)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get rollback controller metrics"""
        return {
            **self.metrics,
            "active_rollbacks": len(self.active_rollbacks),
            "total_rollbacks": len(self.rollback_history),
            "rollback_enabled": self.rollback_enabled
        } 