import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from stripe_integration import get_stripe_integration, SubscriptionTier
from shared.tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from pydantic import BaseModel
from typing import Optional, Dict, Any

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