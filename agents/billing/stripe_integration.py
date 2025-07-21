#!/usr/bin/env python3
"""
Stripe Integration Module
Real implementation of Stripe payment processing for SaaS Factory
"""

import os
import logging
import stripe
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
from shared.tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")
stripe.api_version = "2023-10-16"

class SubscriptionTier(str, Enum):
    """Subscription tier definitions"""
    STARTER = "starter"
    PRO = "pro"
    GROWTH = "growth"

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"

class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"

class StripeCustomer(BaseModel):
    """Stripe customer model"""
    id: str
    email: str
    name: Optional[str] = None
    tenant_id: str
    created: datetime
    subscriptions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StripeSubscription(BaseModel):
    """Stripe subscription model"""
    id: str
    customer_id: str
    price_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaymentIntent(BaseModel):
    """Payment intent model"""
    id: str
    amount: int
    currency: str = "usd"
    status: PaymentStatus
    client_secret: str
    customer_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CheckoutSession(BaseModel):
    """Checkout session model"""
    id: str
    url: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    success_url: str
    cancel_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StripeIntegration:
    """Main Stripe integration class"""
    
    def __init__(self):
        self.api_key = os.getenv("STRIPE_API_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.public_key = os.getenv("STRIPE_PUBLIC_KEY")
        
        if not self.api_key:
            raise ValueError("STRIPE_API_KEY environment variable is required")
        
        self.tenant_db = TenantDatabase()
        
        # Price configurations for different tiers
        self.price_configs = {
            SubscriptionTier.STARTER: {
                "price_id": os.getenv("STRIPE_STARTER_PRICE_ID"),
                "amount": 2900,  # $29.00
                "projects": 1,
                "build_hours": 15
            },
            SubscriptionTier.PRO: {
                "price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
                "amount": 9900,  # $99.00
                "projects": 3,
                "build_hours": 60
            },
            SubscriptionTier.GROWTH: {
                "price_id": os.getenv("STRIPE_GROWTH_PRICE_ID"),
                "amount": 29900,  # $299.00
                "projects": 5,
                "build_hours": -1  # Unlimited
            }
        }
        
        logger.info("Stripe integration initialized")
    
    async def create_customer(self, email: str, name: Optional[str] = None, 
                            tenant_id: str = None, metadata: Dict[str, Any] = None) -> StripeCustomer:
        """Create a new Stripe customer"""
        try:
            customer_data = {
                "email": email,
                "metadata": {
                    "tenant_id": tenant_id,
                    **(metadata or {})
                }
            }
            
            if name:
                customer_data["name"] = name
            
            stripe_customer = stripe.Customer.create(**customer_data)
            
            customer = StripeCustomer(
                id=stripe_customer.id,
                email=stripe_customer.email,
                name=stripe_customer.name,
                tenant_id=tenant_id,
                created=datetime.fromtimestamp(stripe_customer.created),
                metadata=stripe_customer.metadata
            )
            
            logger.info(f"Created Stripe customer: {customer.id} for tenant: {tenant_id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[StripeCustomer]:
        """Get customer by ID"""
        try:
            stripe_customer = stripe.Customer.retrieve(customer_id)
            
            if stripe_customer.deleted:
                return None
            
            return StripeCustomer(
                id=stripe_customer.id,
                email=stripe_customer.email,
                name=stripe_customer.name,
                tenant_id=stripe_customer.metadata.get("tenant_id"),
                created=datetime.fromtimestamp(stripe_customer.created),
                metadata=stripe_customer.metadata
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer: {e}")
            return None
    
    async def create_checkout_session(self, customer_id: str, tier: SubscriptionTier,
                                    success_url: str, cancel_url: str,
                                    metadata: Dict[str, Any] = None) -> CheckoutSession:
        """Create Stripe checkout session for subscription"""
        try:
            price_config = self.price_configs.get(tier)
            if not price_config:
                raise ValueError(f"Invalid subscription tier: {tier}")
            
            price_id = price_config["price_id"]
            if not price_id:
                raise ValueError(f"Price ID not configured for tier: {tier}")
            
            session_data = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": price_id,
                    "quantity": 1,
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "tier": tier.value,
                    **(metadata or {})
                },
                "subscription_data": {
                    "metadata": {
                        "tier": tier.value,
                        **(metadata or {})
                    }
                }
            }
            
            stripe_session = stripe.checkout.Session.create(**session_data)
            
            session = CheckoutSession(
                id=stripe_session.id,
                url=stripe_session.url,
                customer_id=customer_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=stripe_session.metadata
            )
            
            logger.info(f"Created checkout session: {session.id} for customer: {customer_id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    async def get_subscription(self, subscription_id: str) -> Optional[StripeSubscription]:
        """Get subscription by ID"""
        try:
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get price information
            price_id = stripe_subscription.items.data[0].price.id
            tier = self._get_tier_from_price_id(price_id)
            
            return StripeSubscription(
                id=stripe_subscription.id,
                customer_id=stripe_subscription.customer,
                price_id=price_id,
                tier=tier,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                cancel_at_period_end=stripe_subscription.cancel_at_period_end,
                metadata=stripe_subscription.metadata
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {e}")
            return None
    
    def _get_tier_from_price_id(self, price_id: str) -> SubscriptionTier:
        """Get subscription tier from price ID"""
        for tier, config in self.price_configs.items():
            if config["price_id"] == price_id:
                return tier
        return SubscriptionTier.STARTER  # Default fallback
    
    async def cancel_subscription(self, subscription_id: str, 
                                at_period_end: bool = True) -> StripeSubscription:
        """Cancel subscription"""
        try:
            if at_period_end:
                stripe_subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe_subscription = stripe.Subscription.cancel(subscription_id)
            
            # Get price information
            price_id = stripe_subscription.items.data[0].price.id
            tier = self._get_tier_from_price_id(price_id)
            
            subscription = StripeSubscription(
                id=stripe_subscription.id,
                customer_id=stripe_subscription.customer,
                price_id=price_id,
                tier=tier,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                cancel_at_period_end=stripe_subscription.cancel_at_period_end,
                metadata=stripe_subscription.metadata
            )
            
            logger.info(f"Canceled subscription: {subscription_id}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            raise
    
    async def create_payment_intent(self, amount: int, currency: str = "usd",
                                  customer_id: Optional[str] = None,
                                  metadata: Dict[str, Any] = None) -> PaymentIntent:
        """Create payment intent for one-time payment"""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }
            
            if customer_id:
                intent_data["customer"] = customer_id
            
            stripe_intent = stripe.PaymentIntent.create(**intent_data)
            
            intent = PaymentIntent(
                id=stripe_intent.id,
                amount=stripe_intent.amount,
                currency=stripe_intent.currency,
                status=PaymentStatus(stripe_intent.status),
                client_secret=stripe_intent.client_secret,
                customer_id=customer_id,
                metadata=stripe_intent.metadata
            )
            
            logger.info(f"Created payment intent: {intent.id} for amount: {amount}")
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            if not self.webhook_secret:
                raise ValueError("STRIPE_WEBHOOK_SECRET not configured")
            
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            logger.info(f"Received Stripe webhook: {event_type}")
            
            # Handle different event types
            if event_type == "customer.subscription.created":
                return await self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.updated":
                return await self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                return await self._handle_subscription_deleted(event_data)
            elif event_type == "payment_intent.succeeded":
                return await self._handle_payment_succeeded(event_data)
            elif event_type == "payment_intent.payment_failed":
                return await self._handle_payment_failed(event_data)
            elif event_type == "checkout.session.completed":
                return await self._handle_checkout_completed(event_data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
                return {"status": "ignored", "event_type": event_type}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            raise
    
    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        subscription_id = subscription_data["id"]
        customer_id = subscription_data["customer"]
        metadata = subscription_data.get("metadata", {})
        tenant_id = metadata.get("tenant_id")
        tier = metadata.get("tier")
        try:
            if tenant_id and tier:
                await self.tenant_db.init_pool()
                async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                    await conn.execute(
                        "UPDATE tenants SET plan = $1, status = 'active', settings = settings || $2::jsonb WHERE id = $3",
                        tier,
                        json.dumps({"stripe_subscription_id": subscription_id, "stripe_customer_id": customer_id}),
                        tenant_id
                    )
            logger.info(f"Subscription created: {subscription_id} for customer: {customer_id}, tenant: {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to update tenant on subscription created: {e}")
        return {
            "status": "handled",
            "event_type": "subscription.created",
            "subscription_id": subscription_id,
            "customer_id": customer_id
        }
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        subscription_id = subscription_data["id"]
        customer_id = subscription_data["customer"]
        status = subscription_data["status"]
        metadata = subscription_data.get("metadata", {})
        tenant_id = metadata.get("tenant_id")
        tier = metadata.get("tier")
        try:
            if tenant_id and tier:
                await self.tenant_db.init_pool()
                async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                    await conn.execute(
                        "UPDATE tenants SET plan = $1, status = $2, settings = settings || $3::jsonb WHERE id = $4",
                        tier,
                        status,
                        json.dumps({"stripe_subscription_id": subscription_id, "stripe_customer_id": customer_id}),
                        tenant_id
                    )
            logger.info(f"Subscription updated: {subscription_id} status: {status}, tenant: {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to update tenant on subscription updated: {e}")
        return {
            "status": "handled",
            "event_type": "subscription.updated",
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "new_status": status
        }
    
    async def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        subscription_id = subscription_data["id"]
        customer_id = subscription_data["customer"]
        metadata = subscription_data.get("metadata", {})
        tenant_id = metadata.get("tenant_id")
        try:
            if tenant_id:
                await self.tenant_db.init_pool()
                async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                    await conn.execute(
                        "UPDATE tenants SET status = 'cancelled', settings = settings || $1::jsonb WHERE id = $2",
                        json.dumps({"stripe_subscription_id": subscription_id, "stripe_customer_id": customer_id}),
                        tenant_id
                    )
            logger.info(f"Subscription deleted: {subscription_id} for customer: {customer_id}, tenant: {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to update tenant on subscription deleted: {e}")
        return {
            "status": "handled",
            "event_type": "subscription.deleted",
            "subscription_id": subscription_id,
            "customer_id": customer_id
        }
    
    async def _handle_payment_succeeded(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event"""
        payment_id = payment_data["id"]
        amount = payment_data["amount"]
        customer_id = payment_data.get("customer")
        
        logger.info(f"Payment succeeded: {payment_id} amount: {amount}")
        
        # Send payment receipt email
        try:
            if customer_id:
                # Get customer information
                customer = await self.get_customer(customer_id)
                if customer:
                    from email_service import get_email_service, EmailRecipient, PaymentReceiptData
                    from datetime import datetime
                    
                    email_service = get_email_service()
                    recipient = EmailRecipient(email=customer.email, name=customer.name)
                    
                    # Generate invoice number
                    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{payment_id[-8:]}"
                    
                    # Create payment receipt data
                    receipt_data = PaymentReceiptData(
                        user_name=customer.name or customer.email.split('@')[0],
                        user_email=customer.email,
                        invoice_number=invoice_number,
                        invoice_date=datetime.now().strftime('%B %d, %Y'),
                        amount=amount / 100.0,  # Convert from cents
                        currency="USD",
                        plan_name="Subscription Plan",  # Will be enhanced with actual plan data
                        billing_period="Monthly"
                    )
                    
                    # Send payment receipt email
                    email_result = await email_service.send_payment_receipt_email(recipient, receipt_data)
                    logger.info(f"Payment receipt email result: {email_result}")
                    
        except Exception as e:
            logger.error(f"Error sending payment receipt email: {e}")
        
        # TODO: Update tenant database
        # - Log successful payment
        # - Update billing status
        
        return {
            "status": "handled",
            "event_type": "payment.succeeded",
            "payment_id": payment_id,
            "amount": amount,
            "customer_id": customer_id
        }
    
    async def _handle_payment_failed(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed event"""
        payment_id = payment_data["id"]
        customer_id = payment_data.get("customer")
        
        logger.error(f"Payment failed: {payment_id} for customer: {customer_id}")
        
        # TODO: Update tenant database
        # - Log failed payment
        # - Send payment failure notification
        # - Potentially suspend service
        
        return {
            "status": "handled",
            "event_type": "payment.failed",
            "payment_id": payment_id,
            "customer_id": customer_id
        }
    
    async def _handle_checkout_completed(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout session completed event"""
        session_id = session_data["id"]
        customer_id = session_data["customer"]
        subscription_id = session_data.get("subscription")
        
        logger.info(f"Checkout completed: {session_id} subscription: {subscription_id}")
        
        # Send welcome email for new subscriptions
        try:
            if customer_id and subscription_id:
                # Get customer and subscription information
                customer = await self.get_customer(customer_id)
                subscription = await self.get_subscription(subscription_id)
                
                if customer and subscription:
                    from email_service import get_email_service, EmailRecipient, WelcomeEmailData
                    
                    email_service = get_email_service()
                    recipient = EmailRecipient(email=customer.email, name=customer.name)
                    
                    # Create welcome email data
                    welcome_data = WelcomeEmailData(
                        user_name=customer.name or customer.email.split('@')[0],
                        user_email=customer.email,
                        login_url=os.getenv("LOGIN_URL", "https://app.saasfactory.com/login"),
                        dashboard_url=os.getenv("DASHBOARD_URL", "https://app.saasfactory.com/dashboard"),
                        plan_name=subscription.tier.value.title(),
                        trial_days=14
                    )
                    
                    # Send welcome email
                    email_result = await email_service.send_welcome_email(recipient, welcome_data)
                    logger.info(f"Welcome email result: {email_result}")
                    
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
        
        # TODO: Update tenant database
        # - Activate subscription
        # - Log successful signup
        
        return {
            "status": "handled",
            "event_type": "checkout.completed",
            "session_id": session_id,
            "customer_id": customer_id,
            "subscription_id": subscription_id
        }
    
    async def get_customer_subscriptions(self, customer_id: str) -> List[StripeSubscription]:
        """Get all subscriptions for a customer"""
        try:
            stripe_subscriptions = stripe.Subscription.list(
                customer=customer_id,
                limit=100
            )
            
            subscriptions = []
            for stripe_sub in stripe_subscriptions.data:
                price_id = stripe_sub.items.data[0].price.id
                tier = self._get_tier_from_price_id(price_id)
                
                subscription = StripeSubscription(
                    id=stripe_sub.id,
                    customer_id=stripe_sub.customer,
                    price_id=price_id,
                    tier=tier,
                    status=SubscriptionStatus(stripe_sub.status),
                    current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
                    current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end),
                    cancel_at_period_end=stripe_sub.cancel_at_period_end,
                    metadata=stripe_sub.metadata
                )
                
                subscriptions.append(subscription)
            
            return subscriptions
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer subscriptions: {e}")
            return []
    
    def get_tier_limits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get limits for a subscription tier"""
        config = self.price_configs.get(tier)
        if not config:
            return self.price_configs[SubscriptionTier.STARTER]
        
        return {
            "projects": config["projects"],
            "build_hours": config["build_hours"],
            "amount": config["amount"]
        }


# Global instance
stripe_integration = StripeIntegration()


def get_stripe_integration() -> StripeIntegration:
    """Get Stripe integration instance"""
    return stripe_integration 