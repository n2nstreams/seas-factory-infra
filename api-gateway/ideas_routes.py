"""
Ideas Routes for SaaS Factory API Gateway
Handles user idea submission and management
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel, validator
import httpx
import os

from tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/ideas", tags=["ideas"])

# Get database instance
tenant_db = TenantDatabase()

class IdeaSubmissionRequest(BaseModel):
    """Request model for idea submission"""
    title: str
    description: str
    category: Optional[str] = "general"
    
    # Step 2: Problem & Solution
    problem: Optional[str] = None
    solution: Optional[str] = None
    target_audience: Optional[str] = None
    
    # Step 3: Business Details
    key_features: Optional[List[str]] = []
    business_model: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required')
        return v.strip()
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description is required')
        return v.strip()

class IdeaResponse(BaseModel):
    """Response model for submitted ideas"""
    id: str
    title: str
    description: str
    status: str
    created_at: str
    submission_id: str

@router.post("/submit", response_model=IdeaResponse)
async def submit_idea(
    idea_data: IdeaSubmissionRequest,
    background_tasks: BackgroundTasks,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: str = Header(..., description="User ID")
):
    """Submit a new idea for AI processing"""
    try:
        await tenant_db.init_pool()
        
        # Create tenant context
        tenant_context = TenantContext(x_tenant_id)
        
        # Generate unique IDs
        idea_id = str(uuid.uuid4())
        submission_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        async with tenant_db.get_tenant_connection(tenant_context) as conn:
            # Insert the idea into the database
            await conn.execute(
                """
                INSERT INTO ideas (
                    id, tenant_id, submitted_by, project_name, description, category,
                    problem, solution, target_audience, key_features,
                    business_model, timeline, budget, status,
                    created_at, updated_at, submission_data
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                """,
                idea_id,
                x_tenant_id,
                x_user_id,
                idea_data.title,
                idea_data.description,
                idea_data.category,
                idea_data.problem,
                idea_data.solution,
                idea_data.target_audience,
                str(idea_data.key_features or []),
                idea_data.business_model,
                idea_data.timeline,
                idea_data.budget_range,
                "pending",  # Initial status per schema
                now,
                now,
                json.dumps({"submission_id": submission_id})  # Store submission_id as JSON string
            )
            
            logger.info(f"Idea submitted successfully: {idea_id} by user {x_user_id}")
            
            # Trigger factory pipeline in the background
            background_tasks.add_task(
                trigger_factory_pipeline,
                idea_id,
                idea_data,
                x_tenant_id,
                x_user_id
            )
            
            # Return the submitted idea
            return IdeaResponse(
                id=idea_id,
                title=idea_data.title,
                description=idea_data.description,
                status="pending",
                created_at=now.isoformat(),
                submission_id=submission_id
            )
            
    except Exception as e:
        logger.error(f"Error submitting idea: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit idea: {str(e)}"
        )

@router.get("/status/{submission_id}")
async def get_idea_status(
    submission_id: str,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: str = Header(..., description="User ID")
):
    """Get the status of a submitted idea"""
    try:
        await tenant_db.init_pool()
        tenant_context = TenantContext(x_tenant_id)
        
        async with tenant_db.get_tenant_connection(tenant_context) as conn:
            idea = await conn.fetchrow(
                """
                SELECT id, title, status, created_at, updated_at
                FROM ideas 
                WHERE submission_id = $1 AND user_id = $2 AND tenant_id = $3
                """,
                submission_id, x_user_id, x_tenant_id
            )
            
            if not idea:
                raise HTTPException(status_code=404, detail="Idea not found")
            
            return {
                "id": str(idea['id']),
                "title": idea['title'],
                "status": idea['status'],
                "created_at": idea['created_at'].isoformat(),
                "updated_at": idea['updated_at'].isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching idea status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch idea status: {str(e)}"
        )

@router.get("/my-ideas")
async def get_my_ideas(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: str = Header(..., description="User ID"),
    limit: int = 20,
    offset: int = 0
):
    """Get all ideas submitted by the current user"""
    try:
        await tenant_db.init_pool()
        tenant_context = TenantContext(x_tenant_id)
        
        async with tenant_db.get_tenant_connection(tenant_context) as conn:
            ideas = await conn.fetch(
                """
                SELECT 
                    id, project_name, description, status, created_at, updated_at,
                    problem, solution, target_audience, business_model, timeline, budget
                FROM ideas 
                WHERE submitted_by = $1 AND tenant_id = $2
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
                """,
                x_user_id, x_tenant_id, limit, offset
            )
            
            # Return array directly (not wrapped in object) for frontend compatibility
            return [
                {
                    "id": str(idea['id']),
                    "project_name": idea['project_name'],
                    "title": idea['project_name'],  # Alias for compatibility
                    "description": idea['description'],
                    "status": idea['status'],
                    "created_at": idea['created_at'].isoformat() if idea['created_at'] else None,
                    "updated_at": idea['updated_at'].isoformat() if idea['updated_at'] else None,
                    "problem": idea['problem'],
                    "solution": idea['solution'],
                    "target_audience": idea['target_audience'],
                    "business_model": idea['business_model'],
                    "timeline": idea['timeline'],
                    "budget": idea['budget']
                }
                for idea in ideas
            ]
            
    except Exception as e:
        logger.error(f"Error fetching user ideas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ideas: {str(e)}"
        )


async def trigger_factory_pipeline(
    idea_id: str,
    idea_data: IdeaSubmissionRequest,
    tenant_id: str,
    user_id: str
):
    """Trigger factory pipeline for a new idea"""
    try:
        factory_url = os.getenv("FACTORY_URL", "http://localhost:8000")
        
        # Prepare factory trigger request
        factory_trigger = {
            "idea_id": idea_id,
            "project_name": idea_data.title,
            "description": idea_data.description,
            "stage": "idea_validation",
            "priority": "normal",
            "metadata": {
                "category": idea_data.category,
                "problem": idea_data.problem,
                "solution": idea_data.solution,
                "target_audience": idea_data.target_audience,
                "key_features": idea_data.key_features,
                "business_model": idea_data.business_model,
                "timeline": idea_data.timeline,
                "budget": idea_data.budget_range
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{factory_url}/api/factory/trigger",
                json=factory_trigger,
                headers={
                    "X-Tenant-Id": tenant_id,
                    "X-User-Id": user_id
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Factory pipeline triggered for idea {idea_id}: {result['pipeline_id']}")
            else:
                logger.error(f"Failed to trigger factory pipeline: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error triggering factory pipeline for idea {idea_id}: {e}")
        # Don't raise - this is a background task 