import os
import logging
import sys
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from stripe_integration import get_stripe_integration, SubscriptionTier
from shared.tenant_db import TenantDatabase
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from access_control import (
    get_subscription_status, refresh_subscription_cache, 
    subscription_verifier, AccessLevel
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Billing Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tenant_db = TenantDatabase()
stripe_integration = get_stripe_integration()

class CreateCustomerRequest(BaseModel):
    email: str
    name: Optional[str] = None
    tenant_id: str
    metadata: Optional[Dict[str, Any]] = None

class CreateCheckoutSessionRequest(BaseModel):
    customer_id: str
    tier: SubscriptionTier
    success_url: str
    cancel_url: str
    metadata: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup():
    await tenant_db.init_pool()

@app.on_event("shutdown")
async def shutdown():
    await tenant_db.close_pool()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/create-customer")
async def create_customer(req: CreateCustomerRequest):
    try:
        customer = await stripe_integration.create_customer(
            email=req.email,
            name=req.name,
            tenant_id=req.tenant_id,
            metadata=req.metadata
        )
        return customer.dict()
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-checkout-session")
async def create_checkout_session(req: CreateCheckoutSessionRequest):
    try:
        session = await stripe_integration.create_checkout_session(
            customer_id=req.customer_id,
            tier=req.tier,
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata=req.metadata
        )
        return session.dict()
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    try:
        payload = await request.body()
        result = await stripe_integration.handle_webhook(payload, stripe_signature)
        return result
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Subscription Verification Endpoints (Night 53)

@app.get("/subscription/status/{tenant_id}")
async def get_tenant_subscription_status(tenant_id: str):
    """Get detailed subscription status for a tenant"""
    try:
        status = await get_subscription_status(tenant_id)
        return status
    except Exception as e:
        logger.error(f"Error getting subscription status for {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription/status")
async def get_current_tenant_subscription_status(
    x_tenant_id: str = Header(..., description="Tenant ID")
):
    """Get subscription status for current tenant from headers"""
    try:
        status = await get_subscription_status(x_tenant_id)
        return status
    except Exception as e:
        logger.error(f"Error getting subscription status for {x_tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscription/refresh/{tenant_id}")
async def refresh_tenant_subscription_cache(tenant_id: str):
    """Force refresh subscription cache for a tenant"""
    try:
        subscription = await refresh_subscription_cache(tenant_id)
        return {
            "tenant_id": tenant_id,
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "refreshed_at": subscription.last_checked.isoformat() if subscription.last_checked else None
        }
    except Exception as e:
        logger.error(f"Error refreshing subscription cache for {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription/limits/{tenant_id}")
async def get_tenant_limits(tenant_id: str):
    """Get subscription limits and usage for a tenant"""
    try:
        subscription = await subscription_verifier.get_tenant_subscription(tenant_id)
        limits_check = subscription_verifier.check_usage_limits(subscription)
        tier_limits = subscription_verifier.tier_limits.get(subscription.tier, {})
        
        return {
            "tenant_id": tenant_id,
            "tier": subscription.tier.value,
            "limits": {
                "projects": {
                    "max": tier_limits.get('max_projects', -1),
                    "used": subscription.projects_used,
                    "remaining": max(0, tier_limits.get('max_projects', 0) - subscription.projects_used) 
                               if tier_limits.get('max_projects', -1) > 0 else -1,
                    "within_limit": limits_check.get('projects_within_limit', True)
                },
                "build_hours": {
                    "max": tier_limits.get('max_build_hours', -1),
                    "used": subscription.build_hours_used,
                    "remaining": max(0, tier_limits.get('max_build_hours', 0) - subscription.build_hours_used)
                               if tier_limits.get('max_build_hours', -1) > 0 else -1,
                    "within_limit": limits_check.get('build_hours_within_limit', True)
                }
            },
            "features": tier_limits.get('features', [])
        }
    except Exception as e:
        logger.error(f"Error getting limits for {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscription/verify-access")
async def verify_subscription_access(
    request_data: Dict[str, Any],
    x_tenant_id: str = Header(..., description="Tenant ID")
):
    """Verify if tenant has access to specific feature or tier"""
    try:
        required_tier = request_data.get('required_tier', 'starter')
        feature = request_data.get('feature')
        
        subscription = await subscription_verifier.get_tenant_subscription(x_tenant_id)
        
        # Check tier access
        tier_access = subscription_verifier.check_access_level(
            subscription, AccessLevel(required_tier)
        )
        
        # Check feature access if specified
        feature_access = True
        if feature:
            feature_access = subscription_verifier.check_feature_access(subscription, feature)
        
        # Check usage limits
        limits_check = subscription_verifier.check_usage_limits(subscription)
        
        return {
            "tenant_id": x_tenant_id,
            "has_access": tier_access and feature_access and all(limits_check.values()),
            "tier_access": tier_access,
            "feature_access": feature_access,
            "within_limits": limits_check,
            "current_tier": subscription.tier.value,
            "subscription_status": subscription.status.value
        }
    except Exception as e:
        logger.error(f"Error verifying access for {x_tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 