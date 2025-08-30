#!/usr/bin/env python3
"""
Billing Agent - Stripe Integration
Handles payment processing, subscriptions, and customer portal
"""

import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import stripe
from stripe_integration import stripe_integration, SubscriptionTier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Billing Agent",
    description="Stripe payment processing and subscription management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CreateCheckoutSessionRequest(BaseModel):
    tier: str
    billing_period: str  # "monthly" or "yearly"
    success_url: str
    cancel_url: str
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CreatePortalSessionRequest(BaseModel):
    return_url: str
    customer_id: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    tenant_id: Optional[str] = None
    created: str
    metadata: Dict[str, Any]

class SubscriptionResponse(BaseModel):
    id: str
    customer_id: str
    price_id: str
    tier: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    trial_end: Optional[str] = None
    metadata: Dict[str, Any]

class CheckoutSessionResponse(BaseModel):
    id: str
    url: str
    customer_id: str
    success_url: str
    cancel_url: str
    metadata: Dict[str, Any]

class PortalSessionResponse(BaseModel):
    id: str
    url: str
    customer_id: str
    return_url: str

# Helper function to get customer ID from request
async def get_customer_id(request: Request) -> str:
    """Extract customer ID from request headers or query params"""
    # In production, this should come from authentication middleware
    customer_id = request.headers.get("X-Customer-ID")
    if not customer_id:
        raise HTTPException(status_code=401, detail="Customer ID required")
    return customer_id

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "billing-agent"}

# Customer management endpoints
@app.post("/customers", response_model=CustomerResponse)
async def create_customer(
    email: str,
    name: Optional[str] = None,
    tenant_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Create a new Stripe customer"""
    try:
        customer = await stripe_integration.create_customer(
            email=email,
            name=name,
            tenant_id=tenant_id,
            metadata=metadata
        )
        
        return CustomerResponse(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            tenant_id=customer.tenant_id,
            created=customer.created.isoformat(),
            metadata=customer.metadata
        )
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """Get customer by ID"""
    try:
        customer = await stripe_integration.get_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return CustomerResponse(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            tenant_id=customer.tenant_id,
            created=customer.created.isoformat(),
            metadata=customer.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Checkout session endpoints
@app.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(req: CreateCheckoutSessionRequest):
    """Create a Stripe checkout session for subscription"""
    try:
        # Validate tier
        try:
            tier = SubscriptionTier(req.tier)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {req.tier}")
        
        # Validate billing period
        if req.billing_period not in ["monthly", "yearly"]:
            raise HTTPException(status_code=400, detail="Billing period must be 'monthly' or 'yearly'")
        
        session = await stripe_integration.create_checkout_session(
            customer_id=req.customer_id,
            tier=tier,
            billing_period=req.billing_period,
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata=req.metadata
        )
        
        return CheckoutSessionResponse(
            id=session.id,
            url=session.url,
            customer_id=session.customer_id,
            success_url=session.success_url,
            cancel_url=session.cancel_url,
            metadata=session.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Customer portal endpoints
@app.post("/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(req: CreatePortalSessionRequest):
    """Create a customer portal session for managing subscriptions"""
    try:
        # Get customer ID from request if not provided
        customer_id = req.customer_id
        if not customer_id:
            # In production, this should come from authentication
            raise HTTPException(status_code=400, detail="Customer ID required")
        
        session = await stripe_integration.create_customer_portal_session(
            customer_id=customer_id,
            return_url=req.return_url
        )
        
        return PortalSessionResponse(
            id=session.id,
            url=session.url,
            customer_id=session.customer_id,
            return_url=session.return_url
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook endpoint
@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        result = await stripe_integration.handle_webhook(payload, stripe_signature)
        return result
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Subscription management endpoints
@app.get("/subscription/status/{customer_id}", response_model=SubscriptionResponse)
async def get_customer_subscription_status(customer_id: str):
    """Get detailed subscription status for a customer"""
    try:
        subscriptions = await stripe_integration.get_customer_subscriptions(customer_id)
        
        if not subscriptions:
            raise HTTPException(status_code=404, detail="No subscription found for customer")
        
        # Return the most recent active subscription
        active_subscription = None
        for sub in subscriptions:
            if sub.status in ["active", "trialing"]:
                active_subscription = sub
                break
        
        if not active_subscription:
            # Return the most recent subscription regardless of status
            active_subscription = subscriptions[0]
        
        return SubscriptionResponse(
            id=active_subscription.id,
            customer_id=active_subscription.customer_id,
            price_id=active_subscription.price_id,
            tier=active_subscription.tier.value,
            status=active_subscription.status.value,
            current_period_start=active_subscription.current_period_start.isoformat(),
            current_period_end=active_subscription.current_period_end.isoformat(),
            cancel_at_period_end=active_subscription.cancel_at_period_end,
            trial_end=active_subscription.trial_end.isoformat() if active_subscription.trial_end else None,
            metadata=active_subscription.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: str):
    """Get subscription by ID"""
    try:
        subscription = await stripe_integration.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return SubscriptionResponse(
            id=subscription.id,
            customer_id=subscription.customer_id,
            price_id=subscription.price_id,
            tier=subscription.tier.value,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
            trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
            metadata=subscription.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Payment intent endpoints
@app.post("/create-payment-intent")
async def create_payment_intent(
    amount: int,
    currency: str = "usd",
    customer_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Create a payment intent for one-time payments"""
    try:
        payment_intent = await stripe_integration.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            metadata=metadata
        )
        
        return {
            "id": payment_intent.id,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "status": payment_intent.status.value,
            "customer_id": payment_intent.customer_id,
            "metadata": payment_intent.metadata
        }
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Plan information endpoints
@app.get("/plans/{tier}/limits")
async def get_plan_limits(tier: str):
    """Get plan limits for a specific tier"""
    try:
        try:
            subscription_tier = SubscriptionTier(tier)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
        
        limits = stripe_integration.get_tier_limits(subscription_tier)
        return {
            "tier": tier,
            "limits": limits
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    try:
        plans = {}
        for tier in SubscriptionTier:
            if tier != SubscriptionTier.FREE:
                limits = stripe_integration.get_tier_limits(tier)
                plans[tier.value] = {
                    "name": tier.value.title(),
                    "limits": limits
                }
        
        return {
            "plans": plans,
            "free_plan": {
                "name": "Free",
                "limits": {
                    "projects": 1,
                    "build_hours": 5,
                    "storage_gb": 1,
                    "embeddings_mb": 100
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting available plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Feature access check endpoint
@app.post("/check-feature-access")
async def check_feature_access(
    feature: str,
    customer_id: str
):
    """Check if a customer has access to a specific feature"""
    try:
        subscriptions = await stripe_integration.get_customer_subscriptions(customer_id)
        
        if not subscriptions:
            return {
                "has_access": False,
                "reason": "No active subscription"
            }
        
        # Check if any subscription grants access to the feature
        for subscription in subscriptions:
            if subscription.status in ["active", "trialing"]:
                has_access = stripe_integration.has_feature_access(subscription, feature)
                if has_access:
                    return {
                        "has_access": True,
                        "subscription_id": subscription.id,
                        "tier": subscription.tier.value
                    }
        
        return {
            "has_access": False,
            "reason": "Feature not available on current plan"
        }
    except Exception as e:
        logger.error(f"Error checking feature access: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Usage limits check endpoint
@app.post("/check-usage-limits")
async def check_usage_limits(
    customer_id: str,
    usage: Dict[str, int]
):
    """Check if customer usage is within plan limits"""
    try:
        subscriptions = await stripe_integration.get_customer_subscriptions(customer_id)
        
        if not subscriptions:
            return {
                "within_limits": False,
                "exceeded_features": ["subscription"],
                "remaining": {"projects": 0, "build_hours": 0, "storage_gb": 0}
            }
        
        # Check usage against the most recent active subscription
        for subscription in subscriptions:
            if subscription.status in ["active", "trialing"]:
                result = stripe_integration.check_usage_limits(subscription, usage)
                return result
        
        return {
            "within_limits": False,
            "exceeded_features": ["subscription"],
            "remaining": {"projects": 0, "build_hours": 0, "storage_gb": 0}
        }
    except Exception as e:
        logger.error(f"Error checking usage limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 