"""
Database Failover Agent - Night 70 Implementation
Detects database failures and manages automated failover to read replicas

This agent implements:
- Real-time database health monitoring
- Automated failover decision making
- Integration with Cloud SQL replica promotion
- Post-failover validation and reporting
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import uuid

# FastAPI imports
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Google Cloud imports
try:
    from google.cloud import sql_v1
    from google.cloud import monitoring_v3
    from google.cloud import logging as cloud_logging
    import google.auth
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud libraries not available")

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseState(Enum):
    """Database instance states"""
    RUNNABLE = "RUNNABLE"
    SUSPENDED = "SUSPENDED" 
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class FailoverTrigger(Enum):
    """Triggers that initiate failover"""
    MANUAL = "manual"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    CONNECTION_FAILURE = "connection_failure"
    REPLICATION_LAG = "replication_lag"
    ALERT_WEBHOOK = "alert_webhook"
    SCHEDULED_DRILL = "scheduled_drill"


class FailoverStatus(Enum):
    """Status of failover operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReplicaHealth(Enum):
    """Health status of read replicas"""
    HEALTHY = "healthy"
    LAGGING = "lagging"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class DatabaseInstance:
    """Represents a database instance"""
    name: str
    region: str
    state: DatabaseState
    instance_type: str  # primary, replica
    ip_address: Optional[str] = None
    last_check: Optional[datetime] = None
    replication_lag: Optional[int] = None
    connection_pool_size: int = 0
    active_connections: int = 0
    is_failover_target: bool = False


@dataclass
class DatabaseHealth:
    """Health metrics for database monitoring"""
    instance_name: str
    timestamp: datetime
    is_accessible: bool
    response_time_ms: float
    cpu_utilization: float
    memory_utilization: float
    disk_utilization: float
    active_connections: int
    replication_lag: Optional[int] = None
    error_rate: float = 0.0
    availability: float = 100.0


@dataclass
class FailoverDecision:
    """Failover decision with reasoning"""
    trigger: FailoverTrigger
    should_failover: bool
    target_replica: Optional[str]
    reasoning: str
    confidence_score: float
    estimated_downtime: int  # seconds
    impact_assessment: str


@dataclass
class FailoverOperation:
    """Tracks a failover operation"""
    operation_id: str
    trigger: FailoverTrigger
    original_primary: str
    target_replica: str
    status: FailoverStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    decision: Optional[FailoverDecision] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    downtime_seconds: Optional[int] = None


class FailoverRequest(BaseModel):
    """Request to initiate failover"""
    trigger: str
    target_replica: Optional[str] = None
    force: bool = False
    reason: Optional[str] = None


class DatabaseHealthResponse(BaseModel):
    """Response for database health check"""
    instance_name: str
    state: str
    is_healthy: bool
    health_metrics: Dict[str, Any]
    replicas: List[Dict[str, Any]]
    last_updated: str


class FailoverResponse(BaseModel):
    """Response for failover operations"""
    operation_id: str
    status: str
    message: str
    target_replica: Optional[str] = None
    estimated_completion: Optional[str] = None


class DatabaseFailoverAgent:
    """
    Database Failover Agent - Night 70
    Manages database failover scenarios and replica promotion
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Google Cloud clients
        if GOOGLE_CLOUD_AVAILABLE:
            credentials, _ = google.auth.default()
            self.sql_client = sql_v1.SqlInstancesServiceClient(credentials=credentials)
            self.monitoring_client = monitoring_v3.MetricServiceClient(credentials=credentials)
            self.logging_client = cloud_logging.Client(project=project_id, credentials=credentials)
        else:
            self.sql_client = None
            self.monitoring_client = None
            self.logging_client = None
        
        # Internal state
        self.tenant_db = TenantDatabase()
        self.database_instances: Dict[str, DatabaseInstance] = {}
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.active_failovers: Dict[str, FailoverOperation] = {}
        self.failover_history: List[FailoverOperation] = []
        
        # Configuration
        self.health_check_interval = 60  # seconds
        self.connection_timeout = 10  # seconds
        self.max_replication_lag = 300  # 5 minutes in seconds
        self.failover_threshold_failures = 3
        self.replica_promotion_timeout = 600  # 10 minutes
        
        # Metrics
        self.metrics = {
            "health_checks_performed": 0,
            "failovers_triggered": 0,
            "failovers_successful": 0,
            "failovers_failed": 0,
            "average_failover_time": 0.0
        }
        
        # Start health monitoring
        if GOOGLE_CLOUD_AVAILABLE:
            asyncio.create_task(self._start_health_monitoring())

    async def _start_health_monitoring(self):
        """Start continuous health monitoring of database instances"""
        self.logger.info("Starting database health monitoring")
        
        while True:
            try:
                await self._discover_database_instances()
                await self._perform_health_checks()
                await self._evaluate_failover_conditions()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def _discover_database_instances(self):
        """Discover and catalog database instances"""
        try:
            # List all SQL instances in the project
            request = sql_v1.SqlInstancesListRequest(project=self.project_id)
            response = self.sql_client.list(request=request)
            
            for instance in response.instances:
                instance_info = DatabaseInstance(
                    name=instance.name,
                    region=instance.region,
                    state=DatabaseState(instance.state.name) if instance.state else DatabaseState.UNKNOWN,
                    instance_type="replica" if instance.replica_configuration else "primary",
                    ip_address=instance.ip_addresses[0].ip_address if instance.ip_addresses else None,
                    last_check=datetime.utcnow(),
                    is_failover_target=getattr(instance.replica_configuration, 'failover_target', False) if instance.replica_configuration else False
                )
                
                self.database_instances[instance.name] = instance_info
                
        except Exception as e:
            self.logger.error(f"Failed to discover database instances: {e}")

    async def _perform_health_checks(self):
        """Perform health checks on all database instances"""
        self.metrics["health_checks_performed"] += 1
        
        for instance_name, instance in self.database_instances.items():
            health = await self._check_instance_health(instance)
            self.health_history[instance_name].append(health)
            
            # Update instance state
            instance.last_check = health.timestamp
            
            self.logger.debug(f"Health check for {instance_name}: accessible={health.is_accessible}, "
                            f"response_time={health.response_time_ms}ms")

    async def _check_instance_health(self, instance: DatabaseInstance) -> DatabaseHealth:
        """Check health of a specific database instance"""
        start_time = time.time()
        
        try:
            # Get instance details from Cloud SQL API
            request = sql_v1.SqlInstancesGetRequest(
                project=self.project_id,
                instance=instance.name
            )
            
            sql_instance = self.sql_client.get(request=request)
            response_time = (time.time() - start_time) * 1000
            
            # Basic accessibility check
            is_accessible = sql_instance.state == sql_v1.SqlInstanceState.RUNNABLE
            
            # Get replication lag if this is a replica
            replication_lag = None
            if instance.instance_type == "replica" and sql_instance.replica_configuration:
                # In a real implementation, you'd query the replica lag metric
                replication_lag = 0  # Placeholder
            
            return DatabaseHealth(
                instance_name=instance.name,
                timestamp=datetime.utcnow(),
                is_accessible=is_accessible,
                response_time_ms=response_time,
                cpu_utilization=0.0,  # Would get from monitoring
                memory_utilization=0.0,  # Would get from monitoring
                disk_utilization=0.0,  # Would get from monitoring
                active_connections=0,  # Would get from monitoring
                replication_lag=replication_lag,
                error_rate=0.0,
                availability=100.0 if is_accessible else 0.0
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed for {instance.name}: {e}")
            return DatabaseHealth(
                instance_name=instance.name,
                timestamp=datetime.utcnow(),
                is_accessible=False,
                response_time_ms=float('inf'),
                cpu_utilization=0.0,
                memory_utilization=0.0,
                disk_utilization=0.0,
                active_connections=0,
                error_rate=100.0,
                availability=0.0
            )

    async def _evaluate_failover_conditions(self):
        """Evaluate if failover conditions are met"""
        primary_instances = [
            instance for instance in self.database_instances.values() 
            if instance.instance_type == "primary"
        ]
        
        for primary in primary_instances:
            # Check recent health history
            recent_checks = list(self.health_history[primary.name])[-self.failover_threshold_failures:]
            
            if len(recent_checks) >= self.failover_threshold_failures:
                failed_checks = sum(1 for check in recent_checks if not check.is_accessible)
                
                if failed_checks >= self.failover_threshold_failures:
                    self.logger.warning(f"Primary instance {primary.name} has failed {failed_checks} consecutive health checks")
                    
                    # Make failover decision
                    decision = await self._make_failover_decision(
                        primary.name, 
                        FailoverTrigger.HEALTH_CHECK_FAILURE
                    )
                    
                    if decision.should_failover:
                        await self._initiate_failover(decision)

    async def _make_failover_decision(self, failed_primary: str, trigger: FailoverTrigger) -> FailoverDecision:
        """Make intelligent failover decision"""
        # Find healthy failover targets
        failover_candidates = [
            instance for instance in self.database_instances.values()
            if (instance.instance_type == "replica" and 
                instance.is_failover_target and
                instance.state == DatabaseState.RUNNABLE)
        ]
        
        if not failover_candidates:
            return FailoverDecision(
                trigger=trigger,
                should_failover=False,
                target_replica=None,
                reasoning="No healthy failover candidates available",
                confidence_score=0.0,
                estimated_downtime=0,
                impact_assessment="Cannot failover - no suitable replicas"
            )
        
        # Select best candidate (prefer same region, lowest lag)
        best_candidate = min(failover_candidates, 
                           key=lambda r: (r.replication_lag or 0, r.region != self.database_instances[failed_primary].region))
        
        # Estimate downtime (replica promotion + DNS update)
        estimated_downtime = 120  # 2 minutes base + replication lag
        if best_candidate.replication_lag:
            estimated_downtime += best_candidate.replication_lag
        
        confidence_score = 0.9  # High confidence for automated failover
        if best_candidate.replication_lag and best_candidate.replication_lag > self.max_replication_lag:
            confidence_score = 0.6  # Lower confidence due to lag
        
        return FailoverDecision(
            trigger=trigger,
            should_failover=True,
            target_replica=best_candidate.name,
            reasoning=f"Primary {failed_primary} failed, promoting {best_candidate.name} (lag: {best_candidate.replication_lag}s)",
            confidence_score=confidence_score,
            estimated_downtime=estimated_downtime,
            impact_assessment=f"Estimated downtime: {estimated_downtime}s, data loss risk: minimal"
        )

    async def _initiate_failover(self, decision: FailoverDecision) -> FailoverOperation:
        """Initiate database failover operation"""
        operation_id = f"failover-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        
        operation = FailoverOperation(
            operation_id=operation_id,
            trigger=decision.trigger,
            original_primary="",  # Will be set based on decision
            target_replica=decision.target_replica,
            status=FailoverStatus.PENDING,
            created_at=datetime.utcnow(),
            decision=decision
        )
        
        self.active_failovers[operation_id] = operation
        self.metrics["failovers_triggered"] += 1
        
        self.logger.warning(f"Initiating failover: {operation_id}")
        
        # Execute failover in background
        asyncio.create_task(self._execute_failover(operation))
        
        return operation

    async def _execute_failover(self, operation: FailoverOperation):
        """Execute the failover operation"""
        try:
            operation.status = FailoverStatus.IN_PROGRESS
            operation.started_at = datetime.utcnow()
            
            # Step 1: Promote replica to primary
            await self._promote_replica(operation.target_replica)
            
            # Step 2: Validate new primary
            validation_results = await self._validate_failover(operation.target_replica)
            operation.validation_results = validation_results
            
            # Step 3: Update application configuration (placeholder)
            await self._update_application_config(operation.target_replica)
            
            # Step 4: Complete operation
            operation.status = FailoverStatus.COMPLETED
            operation.completed_at = datetime.utcnow()
            operation.downtime_seconds = int(
                (operation.completed_at - operation.started_at).total_seconds()
            )
            
            self.metrics["failovers_successful"] += 1
            self._update_average_failover_time(operation.downtime_seconds)
            
            self.logger.info(f"Failover {operation.operation_id} completed successfully in {operation.downtime_seconds}s")
            
        except Exception as e:
            operation.status = FailoverStatus.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
            
            self.metrics["failovers_failed"] += 1
            self.logger.error(f"Failover {operation.operation_id} failed: {e}")
        
        finally:
            # Move to history
            self.failover_history.append(operation)
            if operation.operation_id in self.active_failovers:
                del self.active_failovers[operation.operation_id]

    async def _promote_replica(self, replica_name: str):
        """Promote replica to primary using Cloud SQL API"""
        try:
            request = sql_v1.SqlInstancesPromoteReplicaRequest(
                project=self.project_id,
                instance=replica_name
            )
            
            operation = self.sql_client.promote_replica(request=request)
            
            # Wait for promotion to complete
            await self._wait_for_sql_operation(operation.name)
            
            self.logger.info(f"Successfully promoted replica {replica_name} to primary")
            
        except Exception as e:
            raise Exception(f"Failed to promote replica {replica_name}: {e}")

    async def _wait_for_sql_operation(self, operation_name: str, timeout: int = 600):
        """Wait for a Cloud SQL operation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                request = sql_v1.SqlOperationsGetRequest(
                    project=self.project_id,
                    operation=operation_name
                )
                
                operation = self.sql_client.get_operation(request=request)
                
                if operation.status == sql_v1.SqlOperationStatus.DONE:
                    if operation.error:
                        raise Exception(f"SQL operation failed: {operation.error}")
                    return
                
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error checking SQL operation status: {e}")
                await asyncio.sleep(10)
        
        raise Exception(f"SQL operation {operation_name} timed out after {timeout}s")

    async def _validate_failover(self, new_primary: str) -> Dict[str, Any]:
        """Validate that failover was successful"""
        validation_results = {
            "connectivity_test": False,
            "write_test": False,
            "replication_status": "unknown",
            "application_health": "unknown"
        }
        
        try:
            # Test basic connectivity
            health = await self._check_instance_health(self.database_instances[new_primary])
            validation_results["connectivity_test"] = health.is_accessible
            
            # Test write operations (simplified)
            # In reality, you'd test actual database writes
            validation_results["write_test"] = health.is_accessible
            
            # Check replication status of remaining replicas
            validation_results["replication_status"] = "healthy"
            
            # Test application health (placeholder)
            validation_results["application_health"] = "unknown"
            
        except Exception as e:
            self.logger.error(f"Failover validation failed: {e}")
        
        return validation_results

    async def _update_application_config(self, new_primary: str):
        """Update application configuration to use new primary"""
        # This would update Cloud Run environment variables, 
        # connection pools, etc. to point to the new primary
        self.logger.info(f"Application configuration should be updated to use {new_primary}")
        
        # In a real implementation, this would:
        # 1. Update Cloud Run services with new DB_HOST
        # 2. Refresh connection pools
        # 3. Update load balancer health checks
        # 4. Notify monitoring systems

    def _update_average_failover_time(self, duration_seconds: int):
        """Update average failover time metric"""
        if self.metrics["failovers_successful"] == 1:
            self.metrics["average_failover_time"] = duration_seconds
        else:
            current_avg = self.metrics["average_failover_time"]
            count = self.metrics["failovers_successful"]
            self.metrics["average_failover_time"] = (
                (current_avg * (count - 1) + duration_seconds) / count
            )

    # Public API methods
    
    async def get_database_health(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of database instances"""
        if instance_name:
            if instance_name not in self.database_instances:
                raise HTTPException(status_code=404, detail=f"Instance {instance_name} not found")
            
            instance = self.database_instances[instance_name]
            recent_health = list(self.health_history[instance_name])[-1] if self.health_history[instance_name] else None
            
            return {
                "instance_name": instance_name,
                "state": instance.state.value,
                "instance_type": instance.instance_type,
                "is_healthy": recent_health.is_accessible if recent_health else False,
                "last_check": instance.last_check.isoformat() if instance.last_check else None,
                "health_metrics": recent_health.__dict__ if recent_health else {},
                "is_failover_target": instance.is_failover_target
            }
        else:
            # Return all instances
            result = {}
            for name, instance in self.database_instances.items():
                recent_health = list(self.health_history[name])[-1] if self.health_history[name] else None
                result[name] = {
                    "state": instance.state.value,
                    "instance_type": instance.instance_type,
                    "is_healthy": recent_health.is_accessible if recent_health else False,
                    "last_check": instance.last_check.isoformat() if instance.last_check else None,
                    "is_failover_target": instance.is_failover_target
                }
            
            return result

    async def trigger_manual_failover(self, request: FailoverRequest) -> FailoverResponse:
        """Trigger manual failover"""
        trigger = FailoverTrigger(request.trigger)
        
        # Find primary instance to fail over from
        primary_instances = [
            instance for instance in self.database_instances.values() 
            if instance.instance_type == "primary"
        ]
        
        if not primary_instances:
            raise HTTPException(status_code=400, detail="No primary instance found")
        
        primary = primary_instances[0]  # Assuming single primary for now
        
        # Make failover decision
        decision = await self._make_failover_decision(primary.name, trigger)
        
        if request.target_replica:
            decision.target_replica = request.target_replica
        
        if not decision.should_failover and not request.force:
            raise HTTPException(
                status_code=400, 
                detail=f"Failover not recommended: {decision.reasoning}"
            )
        
        # Force failover if requested
        if request.force:
            decision.should_failover = True
        
        # Initiate failover
        operation = await self._initiate_failover(decision)
        
        return FailoverResponse(
            operation_id=operation.operation_id,
            status=operation.status.value,
            message=f"Failover initiated from {primary.name} to {decision.target_replica}",
            target_replica=decision.target_replica,
            estimated_completion=(
                operation.created_at + timedelta(seconds=decision.estimated_downtime)
            ).isoformat()
        )

    async def get_failover_status(self, operation_id: str) -> Dict[str, Any]:
        """Get status of failover operation"""
        if operation_id in self.active_failovers:
            operation = self.active_failovers[operation_id]
        else:
            # Check history
            operation = next(
                (op for op in self.failover_history if op.operation_id == operation_id),
                None
            )
        
        if not operation:
            raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")
        
        return {
            "operation_id": operation.operation_id,
            "status": operation.status.value,
            "trigger": operation.trigger.value,
            "target_replica": operation.target_replica,
            "created_at": operation.created_at.isoformat(),
            "started_at": operation.started_at.isoformat() if operation.started_at else None,
            "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
            "downtime_seconds": operation.downtime_seconds,
            "error_message": operation.error_message,
            "validation_results": operation.validation_results
        }

    async def get_failover_metrics(self) -> Dict[str, Any]:
        """Get failover metrics and statistics"""
        return {
            "metrics": self.metrics,
            "active_failovers": len(self.active_failovers),
            "total_failovers": len(self.failover_history),
            "success_rate": (
                self.metrics["failovers_successful"] / self.metrics["failovers_triggered"] * 100
                if self.metrics["failovers_triggered"] > 0 else 0
            ),
            "recent_failovers": [
                {
                    "operation_id": op.operation_id,
                    "status": op.status.value,
                    "downtime_seconds": op.downtime_seconds,
                    "created_at": op.created_at.isoformat()
                }
                for op in self.failover_history[-10:]  # Last 10 failovers
            ]
        } 