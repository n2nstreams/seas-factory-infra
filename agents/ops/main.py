#!/usr/bin/env python3
"""
AIOps Agent Main Entry Point - Night 46 Implementation
FastAPI service for AI-driven operations with log streaming and Gemini-powered anomaly detection

This service provides:
- Real-time log streaming from Google Cloud Logging
- Batch processing for anomaly detection using Gemini
- Intelligent alerting and incident response
- Performance monitoring and predictive analysis
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers

# Import AIOps agent and rollback controller
from aiops_agent import (
    AIOpsAgent, LogStreamConfig, AnomalyDetectionRequest, AlertConfigUpdate,
    LogAnalyticsQuery, AlertSeverity, AnomalyType, GOOGLE_CLOUD_AVAILABLE,
    LoadTestRequest, LoadTestStatusResponse, LoadTestResult
)
from rollback_controller import (
    RollbackController, ErrorBudgetWebhookRequest, RollbackOperation,
    RollbackStatus, RollbackTrigger
)
from database_failover_agent import (
    DatabaseFailoverAgent, FailoverRequest, FailoverResponse,
    DatabaseHealthResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instances
aiops_agent: Optional[AIOpsAgent] = None
rollback_controller: Optional[RollbackController] = None
database_failover_agent: Optional[DatabaseFailoverAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global aiops_agent, rollback_controller, database_failover_agent
    
    # Startup
    logger.info("Starting AIOps Agent service with Auto-Rollback and Database Failover...")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saas-factory-prod")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    
    # Initialize agents
    aiops_agent = AIOpsAgent(project_id)
    rollback_controller = RollbackController(project_id, region)
    database_failover_agent = DatabaseFailoverAgent(project_id)
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down AIOps Agent service...")
        
        # Cancel cleanup task
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        
        # Shutdown agent
        if aiops_agent:
            await aiops_agent.shutdown()


async def periodic_cleanup():
    """Periodic cleanup of old data"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            if aiops_agent:
                await aiops_agent.cleanup_old_data(retention_days=7)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="AIOps Agent - Night 46",
    description="AI-driven operations with log streaming and Gemini-powered anomaly detection",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_aiops_agent() -> AIOpsAgent:
    """Get the global AIOps agent instance"""
    if aiops_agent is None:
        raise HTTPException(status_code=503, detail="AIOps agent not initialized")
    return aiops_agent


# API Models
class StreamResponse(BaseModel):
    """Response for starting log stream"""
    status: str
    stream_id: str
    message: str
    config: Dict


class AnomaliesResponse(BaseModel):
    """Response for anomalies list"""
    status: str
    total_anomalies: int
    anomalies: List[Dict]


class AlertsResponse(BaseModel):
    """Response for alerts list"""
    status: str
    active_alerts: int
    alerts: List[Dict]


class MetricsResponse(BaseModel):
    """Response for metrics"""
    status: str
    metrics: Dict
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    google_cloud_available: bool
    agent_initialized: bool


# API Endpoints

@app.post("/start-log-streaming", response_model=StreamResponse)
async def start_log_streaming(
    config: LogStreamConfig,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Start streaming logs from Google Cloud Logging
    
    This endpoint initiates real-time log streaming with configurable filters
    and batch processing for anomaly detection using Gemini AI.
    """
    
    try:
        # Validate Google Cloud availability
        if not GOOGLE_CLOUD_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Google Cloud libraries not available. Please install required dependencies."
            )
        
        # Log the request for tenant tracking
        await agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="log_streaming",
            agent_name="AIOpsAgent",
            stage="start_streaming",
            status="started",
            project_id=config.project_id,
            input_data=config.model_dump()
        )
        
        # Start log streaming
        stream_id = await agent.start_log_streaming(config)
        
        logger.info(f"Started log streaming {stream_id} for tenant {tenant_context.tenant_id}")
        
        return StreamResponse(
            status="success",
            stream_id=stream_id,
            message=f"Log streaming started for project {config.project_id}",
            config=config.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Failed to start log streaming for tenant {tenant_context.tenant_id}: {e}")
        
        # Log the error event
        await agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="log_streaming",
            agent_name="AIOpsAgent",
            stage="start_streaming",
            status="failed",
            project_id=config.project_id,
            error_message=str(e)
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to start log streaming: {str(e)}")


@app.post("/detect-anomalies")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Manually trigger anomaly detection for a specific service
    
    This endpoint allows manual triggering of anomaly detection analysis
    for a specific service over a configurable time range.
    """
    
    try:
        # Log the request
        await agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="anomaly_detection",
            agent_name="AIOpsAgent",
            stage="manual_detection",
            status="started",
            input_data=request.model_dump()
        )
        
        # Get anomalies for the service
        anomalies = await agent.get_anomalies(
            service=request.service,
            limit=50
        )
        
        logger.info(f"Found {len(anomalies)} anomalies for service {request.service}")
        
        return {
            "status": "success",
            "service": request.service,
            "time_range_minutes": request.time_range_minutes,
            "anomalies_found": len(anomalies),
            "anomalies": [anomaly.to_dict() for anomaly in anomalies]
        }
        
    except Exception as e:
        logger.error(f"Failed to detect anomalies for service {request.service}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect anomalies: {str(e)}")


@app.get("/anomalies", response_model=AnomaliesResponse)
async def get_anomalies(
    service: Optional[str] = Query(None, description="Filter by service name"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of anomalies to return"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get detected anomalies with optional filtering
    
    Returns a list of detected anomalies with optional filtering by service
    and severity. Results are sorted by detection time (newest first).
    """
    
    try:
        # Validate severity if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid severity: {severity}. Valid values: low, medium, high, critical"
                )
        
        # Get anomalies
        anomalies = await agent.get_anomalies(
            service=service,
            severity=severity_enum,
            limit=limit
        )
        
        return AnomaliesResponse(
            status="success",
            total_anomalies=len(anomalies),
            anomalies=[anomaly.to_dict() for anomaly in anomalies]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get anomalies: {str(e)}")


@app.get("/alerts", response_model=AlertsResponse)
async def get_active_alerts(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get all active alerts
    
    Returns a list of all currently active alerts with their associated
    anomalies and timing information.
    """
    
    try:
        alerts = await agent.get_active_alerts()
        
        return AlertsResponse(
            status="success",
            active_alerts=len(alerts),
            alerts=[
                {
                    "alert_id": alert.alert_id,
                    "anomaly": alert.anomaly.to_dict(),
                    "notification_channels": alert.notification_channels,
                    "created_at": alert.created_at.isoformat(),
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "duration_seconds": alert.duration.total_seconds(),
                    "is_active": alert.is_active,
                    "escalated": alert.escalated
                }
                for alert in alerts
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")


@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Acknowledge an alert
    
    Marks an alert as acknowledged, indicating that someone is aware of
    the issue and is working on it.
    """
    
    try:
        # TODO: Extract actual user ID from tenant context
        user_id = getattr(tenant_context, 'user_id', 'system')
        
        success = await agent.acknowledge_alert(alert_id, user_id)
        
        if success:
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return {"status": "success", "message": f"Alert {alert_id} acknowledged"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_note: str = Query("", description="Optional note about the resolution"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Resolve an alert
    
    Marks an alert as resolved, indicating that the underlying issue
    has been fixed.
    """
    
    try:
        # TODO: Extract actual user ID from tenant context
        user_id = getattr(tenant_context, 'user_id', 'system')
        
        success = await agent.resolve_alert(alert_id, user_id, resolution_note)
        
        if success:
            logger.info(f"Alert {alert_id} resolved by {user_id}: {resolution_note}")
            return {"status": "success", "message": f"Alert {alert_id} resolved"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get agent performance metrics
    
    Returns various performance and operational metrics about the AIOps agent,
    including logs processed, anomalies detected, and active streams.
    """
    
    try:
        metrics = agent.get_metrics()
        
        return MetricsResponse(
            status="success",
            metrics=metrics,
            timestamp=agent.tenant_db._get_current_timestamp().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.post("/cleanup")
async def cleanup_old_data(
    retention_days: int = Query(7, ge=1, le=365, description="Number of days to retain data"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Clean up old data
    
    Removes old log batches, anomalies, and resolved alerts older than
    the specified retention period.
    """
    
    try:
        await agent.cleanup_old_data(retention_days)
        
        logger.info(f"Cleaned up data older than {retention_days} days")
        
        return {
            "status": "success",
            "message": f"Cleaned up data older than {retention_days} days",
            "retention_days": retention_days
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup old data: {str(e)}")


@app.get("/streams")
async def get_active_streams(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get information about active log streams
    
    Returns a list of currently active log streams and their configuration.
    """
    
    try:
        stream_info = {
            "active_streams": len(agent.log_streams),
            "stream_ids": list(agent.log_streams.keys()),
            "total_batches": len(agent.log_batches),
            "processing_batches": len([
                b for b in agent.log_batches.values() 
                if b.status.value == "processing"
            ])
        }
        
        return {
            "status": "success",
            **stream_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get stream info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stream info: {str(e)}")


@app.delete("/streams/{stream_id}")
async def stop_log_stream(
    stream_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Stop a specific log stream
    
    Stops the specified log stream and cleans up associated resources.
    """
    
    try:
        if stream_id in agent.log_streams:
            del agent.log_streams[stream_id]
            logger.info(f"Stopped log stream {stream_id}")
            
            return {
                "status": "success",
                "message": f"Log stream {stream_id} stopped"
            }
        else:
            raise HTTPException(status_code=404, detail="Log stream not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop log stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop log stream: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the AIOps agent service and its dependencies.
    """
    
    return HealthResponse(
        status="healthy",
        timestamp=TenantDatabase()._get_current_timestamp().isoformat(),
        google_cloud_available=GOOGLE_CLOUD_AVAILABLE,
        agent_initialized=aiops_agent is not None
    )


# Auto-Rollback Webhook Endpoints (Night 47)

def get_rollback_controller() -> RollbackController:
    """Dependency to get rollback controller instance"""
    if rollback_controller is None:
        raise HTTPException(status_code=503, detail="Rollback controller not initialized")
    return rollback_controller


@app.post("/webhook/error-budget-alert")
async def error_budget_webhook(
    request: ErrorBudgetWebhookRequest,
    auth_token: str = Query(..., description="Webhook authentication token"),
    controller: RollbackController = Depends(get_rollback_controller)
):
    """
    Webhook endpoint for error budget alerts that trigger auto-rollback
    Called when error budget > 1% in 1 hour
    """
    try:
        response = await controller.handle_error_budget_webhook(request, auth_token)
        return response
    except Exception as e:
        logger.error(f"Error budget webhook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rollback/status/{rollback_id}")
async def get_rollback_status(
    rollback_id: str,
    controller: RollbackController = Depends(get_rollback_controller)
):
    """Get the status of a specific rollback operation"""
    rollback_op = controller.get_rollback_status(rollback_id)
    if not rollback_op:
        raise HTTPException(status_code=404, detail="Rollback operation not found")
    
    return {
        "rollback_id": rollback_op.rollback_id,
        "service_name": rollback_op.service_name,
        "status": rollback_op.status.value,
        "trigger": rollback_op.trigger.value,
        "created_at": rollback_op.created_at.isoformat(),
        "started_at": rollback_op.started_at.isoformat() if rollback_op.started_at else None,
        "completed_at": rollback_op.completed_at.isoformat() if rollback_op.completed_at else None,
        "target_revision": rollback_op.target_revision,
        "error_message": rollback_op.error_message
    }


@app.get("/rollback/recent")
async def get_recent_rollbacks(
    hours: int = Query(24, ge=1, le=168),
    controller: RollbackController = Depends(get_rollback_controller)
):
    """Get recent rollback operations"""
    recent_rollbacks = controller.get_recent_rollbacks(hours)
    
    return {
        "count": len(recent_rollbacks),
        "rollbacks": [
            {
                "rollback_id": rb.rollback_id,
                "service_name": rb.service_name,
                "status": rb.status.value,
                "trigger": rb.trigger.value,
                "created_at": rb.created_at.isoformat(),
                "target_revision": rb.target_revision,
                "error_message": rb.error_message
            } for rb in recent_rollbacks
        ]
    }


@app.get("/rollback/metrics")
async def get_rollback_metrics(
    controller: RollbackController = Depends(get_rollback_controller)
):
    """Get rollback controller metrics"""
    return controller.get_metrics()


@app.post("/rollback/manual/{service_name}")
async def trigger_manual_rollback(
    service_name: str,
    target_revision: Optional[str] = None,
    controller: RollbackController = Depends(get_rollback_controller)
):
    """Trigger a manual rollback for testing purposes"""
    import time
    from datetime import datetime
    
    # Create a mock alert for manual rollback
    alert = type('MockAlert', (), {
        'alert_id': f"manual-{int(time.time())}",
        'service_name': service_name,
        'error_rate': 0.05,  # 5% error rate
        'duration_minutes': 60,
        'timestamp': datetime.utcnow(),
        'alert_policy': 'manual-trigger'
    })()
    
    # Create decision for manual rollback
    decision = type('MockDecision', (), {
        'should_rollback': True,
        'reason': 'Manual rollback requested',
        'confidence': 1.0,
        'target_revision': target_revision or 'latest-stable',
        'estimated_impact': 'Manual intervention',
        'rollback_strategy': 'immediate'
    })()
    
    try:
        rollback_op = await controller._trigger_rollback(alert, decision)
        return {
            "message": "Manual rollback triggered",
            "rollback_id": rollback_op.rollback_id,
            "service_name": service_name,
            "target_revision": rollback_op.target_revision
        }
    except Exception as e:
        logger.error(f"Manual rollback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Load Testing Endpoints (Night 69)

@app.post("/load-test/start")
async def start_load_test(
    request: LoadTestRequest,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Start a k6 load test
    
    Initiates a comprehensive load test using k6 with configurable scenarios
    including spike, load, stress, and soak tests.
    """
    
    try:
        # Log the request
        await agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="load_test",
            agent_name="AIOpsAgent",
            stage="start_test",
            status="started",
            input_data=request.model_dump()
        )
        
        # Start the load test
        test_id = await agent.start_load_test(request)
        
        logger.info(f"Started load test {test_id} for tenant {tenant_context.tenant_id}")
        
        return {
            "status": "success",
            "test_id": test_id,
            "message": f"Load test started with ID {test_id}",
            "test_type": request.test_type,
            "target": request.target.name,
            "estimated_duration_minutes": request.duration_minutes
        }
        
    except ValueError as e:
        logger.error(f"Invalid load test request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start load test for tenant {tenant_context.tenant_id}: {e}")
        
        # Log the error event
        await agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="load_test",
            agent_name="AIOpsAgent",
            stage="start_test",
            status="failed",
            error_message=str(e)
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to start load test: {str(e)}")


@app.get("/load-test/{test_id}/status", response_model=LoadTestStatusResponse)
async def get_load_test_status(
    test_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get the status of a running or completed load test
    
    Returns real-time status information including progress, metrics,
    and current virtual user count.
    """
    
    try:
        status = await agent.get_load_test_status(test_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Load test not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get load test status for {test_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get load test status: {str(e)}")


@app.get("/load-test/{test_id}/result")
async def get_load_test_result(
    test_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Get detailed results of a completed load test
    
    Returns comprehensive test results including metrics, thresholds,
    anomalies detected, and Gemini analysis.
    """
    
    try:
        result = await agent.get_load_test_result(test_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Load test result not found")
        
        return {
            "status": "success",
            "result": result.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get load test result for {test_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get load test result: {str(e)}")


@app.get("/load-test/list")
async def list_load_tests(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tests to return"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    List all load tests with their basic information
    
    Returns a list of all load tests ordered by start time (newest first).
    """
    
    try:
        tests = await agent.get_all_load_tests(limit)
        
        return {
            "status": "success",
            "total_tests": len(tests),
            "tests": [test.to_dict() for test in tests]
        }
        
    except Exception as e:
        logger.error(f"Failed to list load tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list load tests: {str(e)}")


@app.post("/load-test/{test_id}/cancel")
async def cancel_load_test(
    test_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Cancel a running load test
    
    Gracefully terminates a running load test and marks it as cancelled.
    """
    
    try:
        success = await agent.cancel_load_test(test_id)
        
        if success:
            logger.info(f"Cancelled load test {test_id}")
            return {
                "status": "success",
                "message": f"Load test {test_id} cancelled successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Load test not found or not running")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel load test {test_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel load test: {str(e)}")


@app.post("/load-test/quick-stress")
async def quick_stress_test(
    target_url: str = Query(..., description="Target URL to stress test"),
    duration_minutes: int = Query(2, ge=1, le=10, description="Test duration in minutes"),
    virtual_users: int = Query(50, ge=1, le=200, description="Number of virtual users"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: AIOpsAgent = Depends(get_aiops_agent)
):
    """
    Quick stress test endpoint for immediate testing
    
    Provides a simplified way to quickly stress test a single URL
    without configuring complex test scenarios.
    """
    
    try:
        # Validate URL
        if not target_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Target URL must start with http:// or https://")
        
        # Create simplified load test request
        request = LoadTestRequest(
            test_type="stress",
            target=LoadTestTargetRequest(
                name="quick-stress",
                base_url=target_url,
                endpoints=["/", "/health", "/metrics"]
            ),
            duration_minutes=duration_minutes,
            virtual_users=virtual_users,
            ramp_up_duration_seconds=30,
            thresholds={
                "http_req_duration": ["p(95)<3000"],  # More lenient for quick tests
                "http_req_failed": ["rate<0.2"]
            }
        )
        
        test_id = await agent.start_load_test(request)
        
        return {
            "status": "success",
            "test_id": test_id,
            "message": f"Quick stress test started for {target_url}",
            "duration_minutes": duration_minutes,
            "virtual_users": virtual_users,
            "monitor_url": f"/load-test/{test_id}/status"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start quick stress test: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start quick stress test: {str(e)}")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")


# Database Failover Endpoints - Night 70

def get_database_failover_agent() -> DatabaseFailoverAgent:
    """Get the global Database Failover agent instance"""
    if database_failover_agent is None:
        raise HTTPException(status_code=503, detail="Database Failover agent not initialized")
    return database_failover_agent


@app.get("/database/health", response_model=Dict[str, Any])
async def get_database_health(
    instance_name: Optional[str] = Query(None, description="Specific instance name"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: DatabaseFailoverAgent = Depends(get_database_failover_agent)
):
    """Get database instance health status"""
    try:
        health_data = await agent.get_database_health(instance_name)
        return {
            "status": "success",
            "data": health_data,
            "tenant_id": tenant_context.tenant_id if tenant_context else "shared"
        }
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/failover", response_model=FailoverResponse)
async def trigger_database_failover(
    request: FailoverRequest,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: DatabaseFailoverAgent = Depends(get_database_failover_agent)
):
    """Trigger manual database failover"""
    try:
        logger.info(f"Manual failover requested by tenant {tenant_context.tenant_id if tenant_context else 'shared'}")
        response = await agent.trigger_manual_failover(request)
        return response
    except Exception as e:
        logger.error(f"Failed to trigger failover: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database/failover/{operation_id}")
async def get_failover_status(
    operation_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: DatabaseFailoverAgent = Depends(get_database_failover_agent)
):
    """Get status of failover operation"""
    try:
        status = await agent.get_failover_status(operation_id)
        return {
            "status": "success",
            "data": status,
            "tenant_id": tenant_context.tenant_id if tenant_context else "shared"
        }
    except Exception as e:
        logger.error(f"Failed to get failover status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database/failover/metrics")
async def get_failover_metrics(
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: DatabaseFailoverAgent = Depends(get_database_failover_agent)
):
    """Get database failover metrics and statistics"""
    try:
        metrics = await agent.get_failover_metrics()
        return {
            "status": "success",
            "data": metrics,
            "tenant_id": tenant_context.tenant_id if tenant_context else "shared"
        }
    except Exception as e:
        logger.error(f"Failed to get failover metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/failover/drill")
async def run_failover_drill(
    target_replica: Optional[str] = Query(None, description="Target replica for drill"),
    force: bool = Query(False, description="Force drill even if conditions not met"),
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    agent: DatabaseFailoverAgent = Depends(get_database_failover_agent)
):
    """Run a database failover drill"""
    try:
        logger.info(f"Failover drill requested by tenant {tenant_context.tenant_id if tenant_context else 'shared'}")
        
        drill_request = FailoverRequest(
            trigger="scheduled_drill",
            target_replica=target_replica,
            force=force,
            reason="Manual failover drill"
        )
        
        response = await agent.trigger_manual_failover(drill_request)
        return {
            "status": "success",
            "message": "Failover drill initiated",
            "data": response,
            "tenant_id": tenant_context.tenant_id if tenant_context else "shared"
        }
    except Exception as e:
        logger.error(f"Failed to run failover drill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=os.getenv("ENVIRONMENT") == "development"
    ) 