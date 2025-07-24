#!/usr/bin/env python3
"""
Factory Pipeline Routes for API Gateway
Night 56: Factory monitoring and pipeline status endpoints

This module provides:
- Factory pipeline status tracking
- Real-time progress monitoring
- WebSocket event integration
- Factory orchestration status
"""

import os
import logging
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from pydantic import BaseModel, Field
import asyncpg
import httpx

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'shared'))
from tenant_db import TenantDatabase, TenantContext
from websocket_manager import get_websocket_manager, EventMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/factory", tags=["factory"])

# Database connection
tenant_db = TenantDatabase()

# WebSocket manager for real-time updates
websocket_manager = get_websocket_manager() if get_websocket_manager else None

class FactoryPipelineStatus(BaseModel):
    """Factory pipeline status model"""
    pipeline_id: str
    project_id: str
    project_name: str
    current_stage: str
    progress: float = Field(..., ge=0.0, le=100.0)
    status: str = Field(..., regex="^(queued|running|completed|failed|paused)$")
    stages: Dict[str, str] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FactoryStageUpdate(BaseModel):
    """Factory stage update model"""
    stage: str
    status: str = Field(..., regex="^(pending|running|completed|failed)$")
    progress: float = Field(..., ge=0.0, le=100.0)
    description: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class FactoryTriggerRequest(BaseModel):
    """Factory trigger request model"""
    idea_id: str
    project_name: str
    description: str
    stage: str = "idea_validation"
    priority: str = "normal"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FactoryMonitoringStats(BaseModel):
    """Factory monitoring statistics"""
    active_pipelines: int
    queued_pipelines: int
    completed_pipelines: int
    failed_pipelines: int
    total_pipelines: int
    average_completion_time: Optional[float] = None
    success_rate: float
    current_load: float

@router.get("/status", response_model=FactoryMonitoringStats)
async def get_factory_status(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get overall factory status and statistics"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            # Get pipeline statistics
            stats_query = """
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'running') as active_pipelines,
                    COUNT(*) FILTER (WHERE status = 'queued') as queued_pipelines,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_pipelines,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_pipelines,
                    COUNT(*) as total_pipelines,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) FILTER (WHERE status = 'completed') as avg_completion_time
                FROM factory_pipelines 
                WHERE tenant_id = $1
            """
            
            stats_row = await conn.fetchrow(stats_query, x_tenant_id)
            
            if not stats_row:
                # Return default stats if no pipelines exist
                return FactoryMonitoringStats(
                    active_pipelines=0,
                    queued_pipelines=0,
                    completed_pipelines=0,
                    failed_pipelines=0,
                    total_pipelines=0,
                    success_rate=0.0,
                    current_load=0.0
                )
            
            total = stats_row['total_pipelines'] or 0
            completed = stats_row['completed_pipelines'] or 0
            active = stats_row['active_pipelines'] or 0
            
            success_rate = (completed / total * 100) if total > 0 else 0.0
            current_load = (active / 10 * 100)  # Assuming max 10 concurrent pipelines
            
            return FactoryMonitoringStats(
                active_pipelines=stats_row['active_pipelines'] or 0,
                queued_pipelines=stats_row['queued_pipelines'] or 0,
                completed_pipelines=completed,
                failed_pipelines=stats_row['failed_pipelines'] or 0,
                total_pipelines=total,
                average_completion_time=stats_row['avg_completion_time'],
                success_rate=success_rate,
                current_load=min(current_load, 100.0)
            )
            
    except Exception as e:
        logger.error(f"Error getting factory status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get factory status: {str(e)}")

@router.get("/pipelines", response_model=List[FactoryPipelineStatus])
async def get_factory_pipelines(
    limit: int = 20,
    status: Optional[str] = None,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get factory pipelines for tenant"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            # Build query with optional status filter
            where_clause = "WHERE tenant_id = $1"
            params = [x_tenant_id]
            
            if status:
                where_clause += " AND status = $2"
                params.append(status)
            
            query = f"""
                SELECT 
                    pipeline_id, project_id, project_name, current_stage, progress, 
                    status, stages, started_at, updated_at, completed_at, 
                    error_message, metadata
                FROM factory_pipelines 
                {where_clause}
                ORDER BY started_at DESC 
                LIMIT ${"2" if not status else "3"}
            """
            
            if not status:
                params.append(limit)
            else:
                params.append(limit)
            
            rows = await conn.fetch(query, *params)
            
            pipelines = []
            for row in rows:
                pipeline = FactoryPipelineStatus(
                    pipeline_id=str(row['pipeline_id']),
                    project_id=str(row['project_id']),
                    project_name=row['project_name'],
                    current_stage=row['current_stage'],
                    progress=float(row['progress']),
                    status=row['status'],
                    stages=json.loads(row['stages']) if row['stages'] else {},
                    started_at=row['started_at'],
                    updated_at=row['updated_at'],
                    completed_at=row['completed_at'],
                    error_message=row['error_message'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                pipelines.append(pipeline)
            
            return pipelines
            
    except Exception as e:
        logger.error(f"Error getting factory pipelines: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get factory pipelines: {str(e)}")

@router.get("/pipelines/{pipeline_id}", response_model=FactoryPipelineStatus)
async def get_factory_pipeline(
    pipeline_id: str,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get specific factory pipeline status"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            query = """
                SELECT 
                    pipeline_id, project_id, project_name, current_stage, progress, 
                    status, stages, started_at, updated_at, completed_at, 
                    error_message, metadata
                FROM factory_pipelines 
                WHERE pipeline_id = $1 AND tenant_id = $2
            """
            
            row = await conn.fetchrow(query, pipeline_id, x_tenant_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Factory pipeline not found")
            
            return FactoryPipelineStatus(
                pipeline_id=str(row['pipeline_id']),
                project_id=str(row['project_id']),
                project_name=row['project_name'],
                current_stage=row['current_stage'],
                progress=float(row['progress']),
                status=row['status'],
                stages=json.loads(row['stages']) if row['stages'] else {},
                started_at=row['started_at'],
                updated_at=row['updated_at'],
                completed_at=row['completed_at'],
                error_message=row['error_message'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting factory pipeline {pipeline_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get factory pipeline: {str(e)}")

@router.post("/pipelines/{pipeline_id}/update")
async def update_factory_pipeline(
    pipeline_id: str,
    stage_update: FactoryStageUpdate,
    background_tasks: BackgroundTasks,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Update factory pipeline stage progress"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            # Get current pipeline
            current_pipeline = await conn.fetchrow(
                "SELECT * FROM factory_pipelines WHERE pipeline_id = $1 AND tenant_id = $2",
                pipeline_id, x_tenant_id
            )
            
            if not current_pipeline:
                raise HTTPException(status_code=404, detail="Factory pipeline not found")
            
            # Update stages
            stages = json.loads(current_pipeline['stages']) if current_pipeline['stages'] else {}
            stages[stage_update.stage] = stage_update.status
            
            # Determine overall status
            overall_status = "running"
            if stage_update.status == "failed":
                overall_status = "failed"
            elif stage_update.progress >= 100.0 and all(s in ["completed", "skipped"] for s in stages.values()):
                overall_status = "completed"
            
            # Update pipeline
            update_query = """
                UPDATE factory_pipelines 
                SET 
                    current_stage = $3,
                    progress = $4,
                    status = $5,
                    stages = $6,
                    updated_at = $7,
                    completed_at = $8,
                    error_message = $9
                WHERE pipeline_id = $1 AND tenant_id = $2
            """
            
            completed_at = datetime.now(timezone.utc) if overall_status == "completed" else None
            
            await conn.execute(
                update_query,
                pipeline_id,
                x_tenant_id,
                stage_update.stage,
                stage_update.progress,
                overall_status,
                json.dumps(stages),
                datetime.now(timezone.utc),
                completed_at,
                stage_update.error_message
            )
            
            # Send WebSocket event
            background_tasks.add_task(
                send_factory_update_event,
                pipeline_id,
                current_pipeline['project_name'],
                stage_update
            )
            
            logger.info(f"Updated factory pipeline {pipeline_id}: {stage_update.stage} -> {stage_update.status}")
            
            return {
                "status": "success",
                "pipeline_id": pipeline_id,
                "stage": stage_update.stage,
                "progress": stage_update.progress,
                "overall_status": overall_status
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating factory pipeline {pipeline_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update factory pipeline: {str(e)}")

@router.post("/trigger")
async def trigger_factory_pipeline(
    trigger_request: FactoryTriggerRequest,
    background_tasks: BackgroundTasks,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Trigger a new factory pipeline"""
    try:
        await tenant_db.init_pool()
        
        # Generate pipeline ID
        pipeline_id = f"pipeline_{int(datetime.now().timestamp())}"
        
        # Initialize pipeline stages
        stages = {
            "idea_validation": "pending",
            "tech_stack": "pending",
            "design": "pending", 
            "development": "pending",
            "qa": "pending",
            "deployment": "pending"
        }
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            # Create pipeline record
            insert_query = """
                INSERT INTO factory_pipelines (
                    pipeline_id, tenant_id, project_id, project_name, current_stage,
                    progress, status, stages, started_at, updated_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """
            
            await conn.execute(
                insert_query,
                pipeline_id,
                x_tenant_id,
                trigger_request.idea_id,  # Using idea_id as project_id for now
                trigger_request.project_name,
                trigger_request.stage,
                0.0,
                "queued",
                json.dumps(stages),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                json.dumps(trigger_request.metadata)
            )
        
        # Send WebSocket event
        background_tasks.add_task(
            send_factory_trigger_event,
            pipeline_id,
            trigger_request.project_name,
            trigger_request.stage
        )
        
        # Trigger actual orchestration (would call orchestrator service)
        background_tasks.add_task(
            trigger_orchestrator,
            pipeline_id,
            trigger_request,
            x_tenant_id,
            x_user_id
        )
        
        logger.info(f"Triggered factory pipeline {pipeline_id} for project: {trigger_request.project_name}")
        
        return {
            "status": "success",
            "pipeline_id": pipeline_id,
            "project_name": trigger_request.project_name,
            "stage": trigger_request.stage,
            "message": "Factory pipeline triggered successfully"
        }
        
    except Exception as e:
        logger.error(f"Error triggering factory pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger factory pipeline: {str(e)}")

# Background task functions

async def send_factory_update_event(
    pipeline_id: str,
    project_name: str,
    stage_update: FactoryStageUpdate
):
    """Send WebSocket event for factory update"""
    if not websocket_manager:
        return
    
    try:
        event = EventMessage(
            event_type="factory_progress",
            data={
                "pipeline_id": pipeline_id,
                "project_name": project_name,
                "stage": stage_update.stage,
                "progress": stage_update.progress,
                "status": stage_update.status,
                "description": stage_update.description,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timestamp=datetime.now(timezone.utc),
            source="factory_orchestrator",
            priority="normal"
        )
        
        await websocket_manager.broadcast_event(event)
        logger.debug(f"Sent factory update event for pipeline {pipeline_id}")
        
    except Exception as e:
        logger.error(f"Error sending factory update event: {e}")

async def send_factory_trigger_event(
    pipeline_id: str,
    project_name: str,
    stage: str
):
    """Send WebSocket event for factory trigger"""
    if not websocket_manager:
        return
    
    try:
        event = EventMessage(
            event_type="factory_triggered",
            data={
                "pipeline_id": pipeline_id,
                "project_name": project_name,
                "stage": stage,
                "message": f"Factory pipeline started for {project_name}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timestamp=datetime.now(timezone.utc),
            source="factory_orchestrator",
            priority="normal"
        )
        
        await websocket_manager.broadcast_event(event)
        logger.debug(f"Sent factory trigger event for pipeline {pipeline_id}")
        
    except Exception as e:
        logger.error(f"Error sending factory trigger event: {e}")

async def trigger_orchestrator(
    pipeline_id: str,
    trigger_request: FactoryTriggerRequest,
    tenant_id: str,
    user_id: Optional[str]
):
    """Trigger the actual orchestrator service"""
    try:
        orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8001")
        
        orchestration_data = {
            "pipeline_id": pipeline_id,
            "stage": trigger_request.stage,
            "payload": {
                "idea_id": trigger_request.idea_id,
                "project_name": trigger_request.project_name,
                "description": trigger_request.description,
                "priority": trigger_request.priority,
                "metadata": trigger_request.metadata
            },
            "tenant_context": {
                "tenant_id": tenant_id,
                "user_id": user_id
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{orchestrator_url}/orchestrator",
                json=orchestration_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully triggered orchestrator for pipeline {pipeline_id}")
            else:
                logger.error(f"Orchestrator trigger failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error triggering orchestrator for pipeline {pipeline_id}: {e}") 