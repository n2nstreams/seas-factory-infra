#!/usr/bin/env python3
"""
OAuth Authentication Routes for SaaS Factory
Handles Google and GitHub OAuth authentication flows
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
import httpx
import logging
import os
from typing import Optional
from datetime import datetime, timedelta
import jwt
from urllib.parse import urlencode
from pydantic import BaseModel

from config.settings import get_settings
from shared.tenant_db import TenantDatabase, TenantContext
from shared.access_control import get_current_user_optional

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["OAuth"])

# Initialize tenant database
tenant_db = TenantDatabase()

# OAuth configuration
settings = get_settings()

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# GitHub OAuth endpoints
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


@router.get("/google")
async def google_oauth_start():
    """Start Google OAuth flow"""
    if not settings.security.google_oauth_enabled:
        raise HTTPException(status_code=400, detail="Google OAuth is not enabled")
    
    if not settings.security.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth client ID not configured")
    
    # Build OAuth authorization URL
    params = {
        'client_id': settings.security.google_client_id,
        'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.google_redirect_uri}",
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Starting Google OAuth flow: {auth_url}")
    
    return RedirectResponse(url=auth_url)


@router.get("/callback/google")
async def google_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle Google OAuth callback"""
    if error:
        logger.error(f"Google OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': settings.security.google_client_id,
            'client_secret': settings.security.google_client_secret.get_secret_value(),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.google_redirect_uri}"
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            # Get user information
            headers = {'Authorization': f'Bearer {access_token}'}
            user_response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # Extract user data
            email = user_info.get('email')
            name = user_info.get('name', '')
            google_id = user_info.get('id')
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not provided by Google")
            
            logger.info(f"Google OAuth user info: {email} ({google_id})")
            
            # Create or get user
            user = await create_or_get_oauth_user(
                email=email,
                name=name,
                provider='google',
                provider_id=google_id
            )
            
            # Generate JWT token
            token = create_jwt_token(user)
            
            # Redirect to frontend with token
            frontend_url = f"{settings.services.api_gateway_url.replace('api', 'app')}/auth/success?token={token}"
            return RedirectResponse(url=frontend_url)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Google OAuth HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=400, detail="Failed to complete OAuth flow")
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal OAuth error")


@router.get("/github")
async def github_oauth_start():
    """Start GitHub OAuth flow"""
    if not settings.security.github_oauth_enabled:
        raise HTTPException(status_code=400, detail="GitHub OAuth is not enabled")
    
    if not settings.security.github_client_id:
        raise HTTPException(status_code=500, detail="GitHub OAuth client ID not configured")
    
    # Build OAuth authorization URL
    params = {
        'client_id': settings.security.github_client_id,
        'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.github_redirect_uri}",
        'scope': 'user:email',
        'response_type': 'code'
    }
    
    auth_url = f"{GITHUB_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Starting GitHub OAuth flow: {auth_url}")
    
    return RedirectResponse(url=auth_url)


@router.get("/callback/github")
async def github_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle GitHub OAuth callback"""
    if error:
        logger.error(f"GitHub OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': settings.security.github_client_id,
            'client_secret': settings.security.github_client_secret.get_secret_value(),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.github_redirect_uri}"
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                GITHUB_TOKEN_URL, 
                data=token_data,
                headers={'Accept': 'application/json'}
            )
            token_response.raise_for_status()
            token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            # Get user information
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            user_response = await client.get(GITHUB_USERINFO_URL, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # Get user emails
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            emails_response.raise_for_status()
            emails = emails_response.json()
            
            # Find primary email
            primary_email = next((email['email'] for email in emails if email['primary']), None)
            if not primary_email:
                raise HTTPException(status_code=400, detail="Primary email not found")
            
            # Extract user data
            name = user_info.get('name', user_info.get('login', ''))
            github_id = user_info.get('id')
            
            logger.info(f"GitHub OAuth user info: {primary_email} ({github_id})")
            
            # Create or get user
            user = await create_or_get_oauth_user(
                email=primary_email,
                name=name,
                provider='github',
                provider_id=github_id
            )
            
            # Generate JWT token
            token = create_jwt_token(user)
            
            # Redirect to frontend with token
            frontend_url = f"{settings.services.api_gateway_url.replace('api', 'app')}/auth/success?token={token}"
            return RedirectResponse(url=frontend_url)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"GitHub OAuth HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=400, detail="Failed to complete OAuth flow")
    except Exception as e:
        logger.error(f"GitHub OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal OAuth error")


async def create_or_get_oauth_user(email: str, name: str, provider: str, provider_id: str):
    """Create or get OAuth user with tenant isolation"""
    try:
        await tenant_db.init_pool()
        
        # Use default tenant for OAuth users (can be upgraded later)
        default_tenant_id = "5aff78c7-413b-4e0e-bbfb-090765835bab"
        
        async with tenant_db.get_tenant_connection(TenantContext(default_tenant_id)) as conn:
            # Check if user already exists
            existing_user = await conn.fetchrow(
                """
                SELECT u.*, t.plan 
                FROM users u
                JOIN tenants t ON u.tenant_id = t.id
                WHERE u.email = $1 AND u.status = 'active'
                """,
                email.lower()
            )
            
            if existing_user:
                # Update last login
                await conn.execute(
                    "UPDATE users SET last_login_at = $1 WHERE id = $2",
                    datetime.utcnow(),
                    existing_user['id']
                )
                
                logger.info(f"OAuth user logged in: {email}")
                return {
                    'id': str(existing_user['id']),
                    'tenant_id': str(existing_user['tenant_id']),
                    'email': existing_user['email'],
                    'name': existing_user['name'],
                    'role': existing_user['role'],
                    'status': existing_user['status'],
                    'created_at': existing_user['created_at'].isoformat(),
                    'plan': existing_user['plan']
                }
            
            # Create new user
            user_id = await conn.fetchval(
                """
                INSERT INTO users (tenant_id, email, name, password_hash, role, status, created_at, last_login_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                default_tenant_id,
                email.lower(),
                name,
                f"oauth_{provider}_{provider_id}",  # Placeholder password for OAuth users
                'user',
                'active',
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            # Get tenant plan
            tenant = await conn.fetchrow("SELECT plan FROM tenants WHERE id = $1", default_tenant_id)
            
            logger.info(f"Created new OAuth user: {email} ({user_id})")
            
            return {
                'id': str(user_id),
                'tenant_id': default_tenant_id,
                'email': email.lower(),
                'name': name,
                'role': 'user',
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'plan': tenant['plan'] if tenant else 'starter'
            }
            
    except Exception as e:
        logger.error(f"Error creating/getting OAuth user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user account")


def create_jwt_token(user: dict) -> str:
    """Create JWT token for authenticated user"""
    payload = {
        'user_id': user['id'],
        'tenant_id': user['tenant_id'],
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=settings.security.jwt_expiration_hours)
    }
    
    token = jwt.encode(
        payload,
        settings.security.jwt_secret_key.get_secret_value(),
        algorithm=settings.security.jwt_algorithm
    )
    
    return token


@router.get("/status")
async def oauth_status():
    """Get OAuth configuration status"""
    return {
        "google_oauth_enabled": settings.security.google_oauth_enabled,
        "github_oauth_enabled": settings.security.github_oauth_enabled,
        "google_client_id_configured": bool(settings.security.google_client_id),
        "github_client_id_configured": bool(settings.security.github_client_id)
    }
