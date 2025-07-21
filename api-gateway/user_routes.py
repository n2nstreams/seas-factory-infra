#!/usr/bin/env python3
"""
User Routes for API Gateway
Night 55: User registration with welcome email integration

This module provides:
- User registration endpoint
- User authentication
- Welcome email sending
- Integration with tenant system
"""

import os
import logging
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, validator
import asyncpg
import bcrypt

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'shared'))
from tenant_db import TenantDatabase, TenantContext
from email_service import get_email_service, EmailRecipient, WelcomeEmailData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

# Database connection
tenant_db = TenantDatabase()

class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    confirmPassword: str
    agreeToTerms: bool = False
    tenant_id: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('agreeToTerms')
    def must_agree_to_terms(cls, v):
        if not v:
            raise ValueError('You must agree to the terms of service')
        return v

class UserLoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model"""
    id: str
    tenant_id: str
    email: str
    name: str
    role: str
    status: str
    created_at: str
    plan: Optional[str] = None

async def get_or_create_tenant(email: str) -> str:
    """Get or create tenant for user"""
    try:
        await tenant_db.init_pool()
        
        # Extract domain from email for tenant slug
        domain = email.split('@')[1]
        tenant_slug = domain.replace('.', '-').lower()
        
        async with tenant_db.get_connection() as conn:
            # Check if tenant exists
            tenant = await conn.fetchrow(
                "SELECT id FROM tenants WHERE slug = $1",
                tenant_slug
            )
            
            if tenant:
                return str(tenant['id'])
            
            # Create new tenant
            tenant_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO tenants (id, name, slug, domain, plan, status, isolation_mode, settings, limits)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                tenant_id,
                f"Organization for {domain}",
                tenant_slug,
                domain,
                "starter",
                "active",
                "shared",
                '{"theme": "glassmorphism", "primary_color": "#6B7B4F"}',
                '{"max_users": 10, "max_projects": 5, "max_storage_gb": 1}'
            )
            
            logger.info(f"Created new tenant: {tenant_id} for domain: {domain}")
            return tenant_id
            
    except Exception as e:
        logger.error(f"Error getting/creating tenant: {e}")
        # Return default tenant ID as fallback
        return "default"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegistrationRequest):
    """Register a new user and send welcome email"""
    try:
        await tenant_db.init_pool()
        
        # Get or create tenant
        tenant_id = user_data.tenant_id or await get_or_create_tenant(user_data.email)
        
        async with tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
            # Check if user already exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE tenant_id = $1 AND email = $2",
                tenant_id, user_data.email.lower()
            )
            
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="User with this email already exists"
                )
            
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = hash_password(user_data.password)
            full_name = f"{user_data.firstName} {user_data.lastName}"
            
            await conn.execute(
                """
                INSERT INTO users (id, tenant_id, email, name, role, status, password_hash, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                user_id,
                tenant_id,
                user_data.email.lower(),
                full_name,
                "user",  # Default role
                "active",
                password_hash,
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            # Get tenant info for plan details
            tenant_info = await conn.fetchrow(
                "SELECT plan FROM tenants WHERE id = $1",
                tenant_id
            )
            
            plan = tenant_info['plan'] if tenant_info else "starter"
            
            # Send welcome email
            try:
                email_service = get_email_service()
                recipient = EmailRecipient(email=user_data.email, name=full_name)
                
                welcome_data = WelcomeEmailData(
                    user_name=user_data.firstName,
                    user_email=user_data.email,
                    login_url=os.getenv("LOGIN_URL", "https://app.saasfactory.com/login"),
                    dashboard_url=os.getenv("DASHBOARD_URL", "https://app.saasfactory.com/dashboard"),
                    plan_name=plan.title(),
                    trial_days=14
                )
                
                email_result = await email_service.send_welcome_email(recipient, welcome_data)
                logger.info(f"Welcome email sent to {user_data.email}: {email_result}")
                
            except Exception as e:
                logger.error(f"Error sending welcome email: {e}")
                # Don't fail registration if email fails
            
            # Return user data
            user_response = UserResponse(
                id=user_id,
                tenant_id=tenant_id,
                email=user_data.email,
                name=full_name,
                role="user",
                status="active",
                created_at=datetime.utcnow().isoformat(),
                plan=plan
            )
            
            logger.info(f"User registered successfully: {user_id}")
            return user_response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during registration"
        )

@router.post("/login")
async def login_user(login_data: UserLoginRequest):
    """Authenticate user login"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_connection() as conn:
            # Find user across all tenants (for login)
            user = await conn.fetchrow(
                """
                SELECT u.*, t.plan 
                FROM users u
                JOIN tenants t ON u.tenant_id = t.id
                WHERE u.email = $1 AND u.status = 'active'
                """,
                login_data.email.lower()
            )
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not verify_password(login_data.password, user['password_hash']):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            # Update last login
            await conn.execute(
                "UPDATE users SET last_login_at = $1 WHERE id = $2",
                datetime.utcnow(),
                user['id']
            )
            
            # Return user data (without password hash)
            user_response = UserResponse(
                id=str(user['id']),
                tenant_id=str(user['tenant_id']),
                email=user['email'],
                name=user['name'],
                role=user['role'],
                status=user['status'],
                created_at=user['created_at'].isoformat(),
                plan=user['plan']
            )
            
            logger.info(f"User logged in successfully: {user['id']}")
            return {
                "message": "Login successful",
                "user": user_response
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during login"
        )

@router.get("/profile")
async def get_user_profile(
    x_user_id: str = Header(..., description="User ID"),
    x_tenant_id: str = Header(..., description="Tenant ID")
):
    """Get current user profile"""
    try:
        await tenant_db.init_pool()
        
        async with tenant_db.get_tenant_connection(TenantContext(x_tenant_id)) as conn:
            user = await conn.fetchrow(
                """
                SELECT u.*, t.plan 
                FROM users u
                JOIN tenants t ON u.tenant_id = t.id
                WHERE u.id = $1 AND u.tenant_id = $2
                """,
                x_user_id,
                x_tenant_id
            )
            
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )
            
            user_response = UserResponse(
                id=str(user['id']),
                tenant_id=str(user['tenant_id']),
                email=user['email'],
                name=user['name'],
                role=user['role'],
                status=user['status'],
                created_at=user['created_at'].isoformat(),
                plan=user['plan']
            )
            
            return user_response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) 