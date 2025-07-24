#!/usr/bin/env python3
"""
Admin Console API Routes
Night 54: Admin console for idea approval/rejection and tenant management

This module provides admin-specific API endpoints for:
- Managing submitted ideas (approve/reject/review)
- Tenant management and isolation upgrade
- Admin analytics and reporting
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

# Import from the shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'shared'))

from tenant_db import TenantDatabase, TenantContext
from access_control import (
    require_subscription, AccessLevel, get_tenant_subscription, 
    subscription_verifier, AccessControlError, TenantSubscription
)

from fastapi import APIRouter, Depends, HTTPException, Request
from .access_control import verify_admin_access
from google.cloud import bigquery

logger = logging.getLogger(__name__)

# Initialize router and database
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])
tenant_db = TenantDatabase()

# Security scheme
security = HTTPBearer(auto_error=False)

# Pydantic models
class IdeaReviewRequest(BaseModel):
    """Request model for idea review actions"""
    status: str = Field(..., description="New status: approved, rejected, in_review")
    admin_notes: Optional[str] = Field(None, description="Admin notes for the decision")
    reason: Optional[str] = Field(None, description="Reason for the action")

class TenantIsolationRequest(BaseModel):
    """Request model for tenant isolation upgrade"""
    tenant_id: str = Field(..., description="Tenant ID to upgrade")
    reason: Optional[str] = Field(None, description="Reason for isolation upgrade")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom settings for isolated tenant")

class AdminResponse(BaseModel):
    """Standard admin response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Dependency to verify admin access
async def verify_admin_access(
    request: Request,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: str = Header(..., description="User ID"), 
    x_user_role: str = Header(..., description="User Role")
) -> TenantContext:
    """Verify that the user has admin access"""
    
    if x_user_role != 'admin':
        raise HTTPException(
            status_code=403, 
            detail="Admin access required. Current role: " + x_user_role
        )
    
    # Create admin context
    admin_context = TenantContext(
        tenant_id=x_tenant_id,
        user_id=x_user_id,
        user_role='admin'
    )
    
    # Verify subscription and access
    subscription = await subscription_verifier.get_tenant_subscription(x_tenant_id)
    if not subscription_verifier.check_access_level(subscription, AccessLevel.PRO):
        raise AccessControlError(
            status_code=402,
            detail="Admin console requires Pro+ subscription",
            subscription_required=True,
            upgrade_url="/pricing"
        )
    
    return admin_context

# Ideas Management Endpoints

@admin_router.get("/ideas", response_model=Dict[str, Any])
async def get_all_ideas(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get all ideas across all tenants (admin only)"""
    try:
        await tenant_db.init_pool()
        
        ideas = await tenant_db.get_all_ideas(
            admin_context=admin_context,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset
        )
        
        # Get statistics
        stats = await tenant_db.get_idea_statistics(admin_context)
        
        return {
            "ideas": ideas,
            "statistics": stats,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(ideas)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching ideas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ideas: {str(e)}")

@admin_router.get("/ideas/{idea_id}", response_model=Dict[str, Any])
async def get_idea_details(
    idea_id: str,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get detailed information about a specific idea"""
    try:
        await tenant_db.init_pool()
        
        # Get idea details
        ideas = await tenant_db.get_all_ideas(
            admin_context=admin_context,
            limit=1
        )
        
        idea = next((i for i in ideas if str(i['id']) == idea_id), None)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        return {
            "idea": idea,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching idea details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch idea: {str(e)}")

@admin_router.put("/ideas/{idea_id}/review", response_model=AdminResponse)
async def review_idea(
    idea_id: str,
    review_request: IdeaReviewRequest,
    request: Request,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Review an idea (approve, reject, or mark in review)"""
    try:
        await tenant_db.init_pool()
        
        # Validate status
        valid_statuses = ['approved', 'rejected', 'in_review', 'pending']
        if review_request.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update idea status
        success = await tenant_db.update_idea_status(
            admin_context=admin_context,
            idea_id=idea_id,
            status=review_request.status,
            admin_notes=review_request.admin_notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        # Log admin action with request context
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        await tenant_db.log_admin_action(
            admin_context=admin_context,
            action_type='idea_review',
            target_type='idea',
            target_id=idea_id,
            action_data={
                'old_status': 'pending',  # We could fetch this if needed
                'new_status': review_request.status,
                'admin_notes': review_request.admin_notes
            },
            reason=review_request.reason,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return AdminResponse(
            success=True,
            message=f"Idea {review_request.status} successfully",
            data={"idea_id": idea_id, "new_status": review_request.status}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to review idea: {str(e)}")

@admin_router.post("/ideas/{idea_id}/promote", response_model=AdminResponse)
async def promote_idea_to_project(
    idea_id: str,
    request: Request,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Promote an approved idea to a project"""
    try:
        await tenant_db.init_pool()
        
        project_id = await tenant_db.promote_idea_to_project(
            admin_context=admin_context,
            idea_id=idea_id
        )
        
        if not project_id:
            raise HTTPException(
                status_code=400, 
                detail="Idea not found or not approved. Only approved ideas can be promoted."
            )
        
        # Log admin action
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        await tenant_db.log_admin_action(
            admin_context=admin_context,
            action_type='idea_promoted',
            target_type='idea',
            target_id=idea_id,
            action_data={'project_id': project_id},
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return AdminResponse(
            success=True,
            message="Idea promoted to project successfully",
            data={"idea_id": idea_id, "project_id": project_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error promoting idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to promote idea: {str(e)}")

# Tenant Management Endpoints

@admin_router.get("/tenants", response_model=Dict[str, Any])
async def get_all_tenants(
    status: Optional[str] = None,
    isolation_mode: Optional[str] = None,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get all tenants with their statistics (admin only)"""
    try:
        await tenant_db.init_pool()
        
        tenants = await tenant_db.get_all_tenants(
            admin_context=admin_context,
            status=status,
            isolation_mode=isolation_mode
        )
        
        return {
            "tenants": tenants,
            "total": len(tenants),
            "summary": {
                "shared": sum(1 for t in tenants if t.get('isolation_mode') == 'shared'),
                "isolated": sum(1 for t in tenants if t.get('isolation_mode') == 'isolated'),
                "active": sum(1 for t in tenants if t.get('status') == 'active'),
                "total_projects": sum(t.get('project_count', 0) for t in tenants),
                "total_ideas": sum(t.get('idea_count', 0) for t in tenants)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching tenants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenants: {str(e)}")

@admin_router.get("/tenants/{tenant_id}", response_model=Dict[str, Any])
async def get_tenant_details(
    tenant_id: str,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get detailed information about a specific tenant"""
    try:
        await tenant_db.init_pool()
        
        # Get tenant details
        tenants = await tenant_db.get_all_tenants(admin_context=admin_context)
        tenant = next((t for t in tenants if str(t['id']) == tenant_id), None)
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get tenant's ideas
        tenant_context = TenantContext(tenant_id=tenant_id, user_id=admin_context.user_id, user_role='admin')
        ideas = await tenant_db.get_tenant_ideas(tenant_context=tenant_context, limit=10)
        projects = await tenant_db.get_tenant_projects(tenant_context=tenant_context)
        
        return {
            "tenant": tenant,
            "ideas": ideas,
            "projects": projects,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tenant details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenant: {str(e)}")

@admin_router.post("/tenants/{tenant_id}/isolate", response_model=AdminResponse)
async def upgrade_tenant_to_isolated(
    tenant_id: str,
    isolation_request: TenantIsolationRequest,
    request: Request,
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Upgrade a tenant to isolated infrastructure"""
    try:
        await tenant_db.init_pool()
        
        # Get tenant info first
        tenants = await tenant_db.get_all_tenants(admin_context=admin_context)
        tenant = next((t for t in tenants if str(t['id']) == tenant_id), None)
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        if tenant.get('isolation_mode') == 'isolated':
            raise HTTPException(status_code=400, detail="Tenant is already isolated")
        
        # Prepare isolation settings
        isolation_settings = {
            'isolation': {
                'upgraded_at': datetime.utcnow().isoformat(),
                'upgraded_by': admin_context.user_id,
                'reason': isolation_request.reason,
                'custom_settings': isolation_request.custom_settings or {}
            }
        }
        
        # Update tenant to isolated mode
        success = await tenant_db.update_tenant_isolation(
            admin_context=admin_context,
            tenant_id=tenant_id,
            isolation_mode='isolated',
            settings_update=isolation_settings
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update tenant isolation status")
        
        # Log admin action
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        await tenant_db.log_admin_action(
            admin_context=admin_context,
            action_type='tenant_isolation_upgrade',
            target_type='tenant',
            target_id=tenant_id,
            action_data={
                'old_isolation_mode': 'shared',
                'new_isolation_mode': 'isolated',
                'reason': isolation_request.reason,
                'custom_settings': isolation_request.custom_settings
            },
            reason=isolation_request.reason,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return AdminResponse(
            success=True,
            message=f"Tenant {tenant.get('name', tenant_id)} upgraded to isolated infrastructure",
            data={
                "tenant_id": tenant_id,
                "isolation_mode": "isolated",
                "note": "Infrastructure promotion will be processed asynchronously"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading tenant {tenant_id} to isolated: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upgrade tenant: {str(e)}")

# Analytics and Reporting Endpoints

@admin_router.get("/analytics/ideas", response_model=Dict[str, Any])
async def get_idea_analytics(
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get idea submission and approval analytics"""
    try:
        await tenant_db.init_pool()
        
        stats = await tenant_db.get_idea_statistics(admin_context)
        
        # Additional analytics
        all_ideas = await tenant_db.get_all_ideas(admin_context=admin_context, limit=1000)
        
        # Category breakdown
        category_stats = {}
        for idea in all_ideas:
            category = idea.get('category', 'Unknown')
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'approved': 0, 'rejected': 0, 'pending': 0}
            category_stats[category]['total'] += 1
            category_stats[category][idea['status']] += 1
        
        # Recent activity (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_ideas = [i for i in all_ideas if i['created_at'] > thirty_days_ago]
        
        return {
            "overall_statistics": stats,
            "category_breakdown": category_stats,
            "recent_activity": {
                "last_30_days": len(recent_ideas),
                "ideas": recent_ideas[:10]  # Latest 10
            },
            "trends": {
                "approval_rate": (stats.get('approved_ideas', 0) / max(stats.get('total_ideas', 1), 1)) * 100,
                "avg_review_time_days": stats.get('avg_review_time_days', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching idea analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@admin_router.get("/analytics/tenants", response_model=Dict[str, Any])
async def get_tenant_analytics(
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Get tenant usage and growth analytics"""
    try:
        await tenant_db.init_pool()
        
        all_tenants = await tenant_db.get_all_tenants(admin_context=admin_context)
        
        # Plan distribution
        plan_stats = {}
        isolation_stats = {'shared': 0, 'isolated': 0}
        
        for tenant in all_tenants:
            plan = tenant.get('plan', 'free')
            if plan not in plan_stats:
                plan_stats[plan] = 0
            plan_stats[plan] += 1
            
            isolation_mode = tenant.get('isolation_mode', 'shared')
            isolation_stats[isolation_mode] += 1
        
        # Growth metrics
        total_projects = sum(tenant.get('project_count', 0) for tenant in all_tenants)
        total_ideas = sum(tenant.get('idea_count', 0) for tenant in all_tenants)
        total_users = sum(tenant.get('user_count', 0) for tenant in all_tenants)
        
        return {
            "tenant_summary": {
                "total_tenants": len(all_tenants),
                "active_tenants": sum(1 for t in all_tenants if t.get('status') == 'active'),
                "total_projects": total_projects,
                "total_ideas": total_ideas,
                "total_users": total_users
            },
            "plan_distribution": plan_stats,
            "isolation_distribution": isolation_stats,
            "averages": {
                "projects_per_tenant": total_projects / max(len(all_tenants), 1),
                "ideas_per_tenant": total_ideas / max(len(all_tenants), 1),
                "users_per_tenant": total_users / max(len(all_tenants), 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching tenant analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@admin_router.get("/analytics/experiment/{experiment_key}")
async def get_experiment_analytics(request: Request, experiment_key: str, admin_user: dict = Depends(verify_admin_access)):
    """
    Retrieves and aggregates analytics data for a specific experiment from BigQuery.
    """
    bq_client = request.app.state.bq_client
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not configured.")

    query = f"""
        SELECT
            variation_id,
            COUNT(DISTINCT user_id) as users,
            COUNTIF(event_name = 'cta-click') as conversions
        FROM
            `saas-factory-experiments.experiment_events`
        WHERE
            experiment_key = @experiment_key
        GROUP BY
            variation_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("experiment_key", "STRING", experiment_key),
        ]
    )

    try:
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        return results.to_dict("records")
    except Exception as e:
        logger.error(f"Error querying BigQuery for experiment analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve experiment analytics.")

# Health and Status Endpoints

@admin_router.get("/health", response_model=Dict[str, Any])
async def admin_health_check(
    admin_context: TenantContext = Depends(verify_admin_access)
):
    """Admin console health check"""
    try:
        await tenant_db.init_pool()
        
        # Test database connectivity
        stats = await tenant_db.get_idea_statistics(admin_context)
        
        return {
            "status": "healthy",
            "admin_user": admin_context.user_id,
            "database": "connected",
            "idea_count": stats.get('total_ideas', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Admin health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Export router
__all__ = ['admin_router'] 