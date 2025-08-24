#!/usr/bin/env python3
"""
OAuth Authentication Routes for SaaS Factory
Handles Google and GitHub OAuth authentication flows
"""

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
import httpx
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from urllib.parse import urlencode
from pydantic import BaseModel

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import get_settings
from tenant_db import TenantDatabase, TenantContext
from oauth_monitoring import (
    record_oauth_start, record_oauth_success, record_oauth_error, 
    oauth_monitor
)
from dataclasses import asdict
# from access_control import get_current_user_optional  # Not used in OAuth routes

import secrets
import hashlib
import base64
import time
import json
import re
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["OAuth"])

# Initialize tenant database
tenant_db = TenantDatabase()

# OAuth configuration
settings = get_settings()

# OAuth monitoring endpoints
@router.get("/monitoring/metrics")
async def get_oauth_metrics():
    """Get OAuth performance metrics"""
    return oauth_monitor.get_overall_metrics()

@router.get("/monitoring/events")
async def get_oauth_events(limit: int = 50):
    """Get recent OAuth events"""
    return oauth_monitor.get_recent_events(limit)

@router.get("/monitoring/provider/{provider}")
async def get_provider_metrics(provider: str):
    """Get metrics for a specific OAuth provider"""
    metrics = oauth_monitor.get_provider_metrics(provider)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    return asdict(metrics)

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


# OAuth state storage - Redis for production, in-memory for development
class OAuthStateStore:
    """Production-ready OAuth state storage with Redis support"""
    
    def __init__(self):
        self.redis_enabled = settings.cache.redis_enabled
        self.redis_client = None
        self.memory_store: Dict[str, Dict] = {}
        
        if self.redis_enabled:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.Redis(
                    host=settings.cache.redis_host,
                    port=settings.cache.redis_port,
                    db=settings.cache.redis_db,
                    password=settings.cache.redis_password.get_secret_value() if settings.cache.redis_password else None,
                    decode_responses=True
                )
                logger.info("OAuth state storage: Redis enabled")
            except ImportError:
                logger.warning("Redis not available, falling back to in-memory storage")
                self.redis_enabled = False
        else:
            logger.info("OAuth state storage: In-memory mode (development)")
    
    async def set_state(self, state: str, data: Dict[str, Any], ttl: int = 600) -> bool:
        """Store OAuth state with TTL"""
        try:
            if self.redis_enabled and self.redis_client:
                # Store in Redis with TTL
                await self.redis_client.setex(
                    f"oauth_state:{state}",
                    ttl,
                    json.dumps(data)
                )
                return True
            else:
                # Fallback to in-memory with timestamp
                data['timestamp'] = datetime.utcnow()
                self.memory_store[state] = data
                return True
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
            # Fallback to in-memory
            data['timestamp'] = datetime.utcnow()
            self.memory_store[state] = data
            return False
    
    async def get_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Retrieve OAuth state"""
        try:
            if self.redis_enabled and self.redis_client:
                # Get from Redis
                data = await self.redis_client.get(f"oauth_state:{state}")
                if data:
                    return json.loads(data)
                return None
            else:
                # Get from in-memory
                return self.memory_store.get(state)
        except Exception as e:
            logger.error(f"Failed to retrieve OAuth state: {e}")
            # Fallback to in-memory
            return self.memory_store.get(state)
    
    async def delete_state(self, state: str) -> bool:
        """Delete OAuth state"""
        try:
            if self.redis_enabled and self.redis_client:
                # Delete from Redis
                await self.redis_client.delete(f"oauth_state:{state}")
                return True
            else:
                # Delete from in-memory
                self.memory_store.pop(state, None)
                return True
        except Exception as e:
            logger.error(f"Failed to delete OAuth state: {e}")
            # Fallback to in-memory
            self.memory_store.pop(state, None)
            return False
    
    async def cleanup_expired(self) -> int:
        """Clean up expired states"""
        try:
            if self.redis_enabled and self.redis_client:
                # Redis handles TTL automatically
                return 0
            else:
                # Clean up expired in-memory states
                current_time = datetime.utcnow()
                expired_states = []
                
                for state, data in self.memory_store.items():
                    if 'timestamp' in data:
                        age = (current_time - data['timestamp']).total_seconds()
                        if age > 600:  # 10 minutes
                            expired_states.append(state)
                
                for state in expired_states:
                    self.memory_store.pop(state, None)
                
                if expired_states:
                    logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")
                
                return len(expired_states)
        except Exception as e:
            logger.error(f"Failed to cleanup expired states: {e}")
            return 0

# Initialize OAuth state store
oauth_state_store = OAuthStateStore()

async def validate_and_cleanup_state(state: str, provider: str) -> bool:
    """Validate state parameter and cleanup expired states"""
    try:
        # Clean up expired states
        await oauth_state_store.cleanup_expired()
        
        # Get stored state data
        stored_state_data = await oauth_state_store.get_state(state)
        if not stored_state_data:
            return False
        
        if stored_state_data['provider'] != provider:
            return False
        
        # Check if state is expired (older than 10 minutes)
        if 'timestamp' in stored_state_data:
            age = (datetime.utcnow() - stored_state_data['timestamp']).total_seconds()
            if age > 600:  # 10 minutes
                await oauth_state_store.delete_state(state)
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating OAuth state: {e}")
        return False

# Rate limiting for OAuth endpoints
class OAuthRateLimiter:
    """Simple in-memory rate limiter for OAuth endpoints"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        current_time = time.time()
        
        # Clean up old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests allowed"""
        current_time = time.time()
        
        # Clean up old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(self.requests[identifier]))

# Initialize rate limiters
oauth_rate_limiter = OAuthRateLimiter(
    max_requests=settings.security.rate_limit_requests if settings.security.rate_limit_enabled else 1000,
    window_seconds=settings.security.rate_limit_window if settings.security.rate_limit_enabled else 60
)

def check_rate_limit(identifier: str) -> bool:
    """Check rate limit for OAuth endpoint"""
    if not settings.security.rate_limit_enabled:
        return True
    
    if not oauth_rate_limiter.is_allowed(identifier):
        logger.warning(f"Rate limit exceeded for OAuth endpoint: {identifier}")
        return False
    
    return True

def validate_oauth_input(code: str, state: Optional[str], provider: str) -> bool:
    """Validate OAuth input parameters"""
    # Validate authorization code
    if not code or not re.match(r'^[A-Za-z0-9_-]+$', code):
        logger.warning(f"Invalid authorization code format for {provider}")
        return False
    
    # Validate state parameter
    if state and not re.match(r'^[A-Za-z0-9_-]+$', state):
        logger.warning(f"Invalid state parameter format for {provider}")
        return False
    
    return True

def sanitize_oauth_input(value: str) -> str:
    """Sanitize OAuth input values"""
    if not value:
        return ""
    
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[^A-Za-z0-9_-]', '', value)
    return sanitized[:100]  # Limit length

def add_security_headers(response: RedirectResponse) -> RedirectResponse:
    """Add security headers to OAuth responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

@router.get("/google")
async def google_oauth_start(request: Request):
    """Start Google OAuth flow with enhanced security"""
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"google_start:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    if not settings.security.google_oauth_enabled:
        raise HTTPException(status_code=400, detail="Google OAuth is not enabled")
    
    if not settings.security.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth client ID not configured")
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Generate PKCE code verifier and challenge for additional security
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge_b64 = base64.urlsafe_b64encode(code_challenge).decode().rstrip('=')
    
    # Record OAuth start
    record_oauth_start('google', 
                      ip_address=client_ip,
                      user_agent=request.headers.get('user-agent'))
    
    # Build OAuth authorization URL with enhanced security
    params = {
        'client_id': settings.security.google_client_id,
        'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.google_redirect_uri}",
        'response_type': 'code',
        'scope': ' '.join(settings.security.google_scopes),
        'access_type': settings.security.google_access_type,
        'prompt': settings.security.google_prompt,
        'state': state,
        'code_challenge': code_challenge_b64,
        'code_challenge_method': 'S256'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Starting Google OAuth flow with PKCE: {auth_url}")
    
    # Store state and PKCE verifier in memory store for validation
    await oauth_state_store.set_state(state, {
        'provider': 'google',
        'code_verifier': code_verifier,
        'timestamp': datetime.utcnow()
    })
    
    response = RedirectResponse(url=auth_url)
    return add_security_headers(response)


@router.get("/callback/google")
async def google_oauth_callback(
    request: Request,
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle Google OAuth callback"""
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"google_callback:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    if error:
        logger.error(f"Google OAuth error: {error}")
        record_oauth_error('google', f"OAuth error: {error}")
        # Redirect to frontend with error
        frontend_url = f"{settings.services.frontend_url}/auth/error?error={error}&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    if not code:
        logger.error("Google OAuth callback: No authorization code provided")
        record_oauth_error('google', "No authorization code provided")
        # Redirect to frontend with error
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_code&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Input validation and sanitization
    if not validate_oauth_input(code, state, 'google'):
        logger.error("Google OAuth callback: Invalid input parameters")
        record_oauth_error('google', "Invalid input parameters")
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=invalid_input&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Sanitize inputs
    sanitized_code = sanitize_oauth_input(code)
    sanitized_state = sanitize_oauth_input(state) if state else None
    
    # Validate state parameter for CSRF protection
    if not await validate_and_cleanup_state(sanitized_state, 'google'):
        logger.error("Google OAuth callback: Invalid state parameter")
        record_oauth_error('google', "Invalid state parameter")
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=invalid_state&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Get stored state data before clearing
    stored_state_data = await oauth_state_store.get_state(sanitized_state)
    
    # Validate PKCE code challenge
    code_verifier = stored_state_data.get('code_verifier')
    if not code_verifier:
        logger.error("Google OAuth callback: Code verifier not found in state")
        record_oauth_error('google', "Code verifier not found")
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=code_verifier_missing&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Clear the stored state
    await oauth_state_store.delete_state(sanitized_state)
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': settings.security.google_client_id,
            'client_secret': settings.security.google_client_secret.get_secret_value(),
            'code': sanitized_code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.google_redirect_uri}",
            'code_verifier': code_verifier
        }
        
        logger.info(f"Exchanging Google OAuth code for token: {code[:10]}...")
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            
            if not token_response.is_success:
                error_msg = f"Google token exchange failed: {token_response.status_code} - {token_response.text}"
                logger.error(error_msg)
                record_oauth_error('google', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=token_exchange_failed&provider=google"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            refresh_token = token_info.get('refresh_token')  # Google provides refresh tokens
            expires_in = token_info.get('expires_in', 3600)  # Default to 1 hour
            
            if not access_token:
                error_msg = "Google OAuth: No access token in response"
                logger.error(error_msg)
                record_oauth_error('google', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_access_token&provider=google"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            logger.info(f"Google OAuth: Successfully obtained access token, expires in {expires_in}s")
            if refresh_token:
                logger.info("Google OAuth: Refresh token also received")
            
            # Get user information
            headers = {'Authorization': f'Bearer {access_token}'}
            user_response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
            
            if not user_response.is_success:
                error_msg = f"Failed to get Google user info: {user_response.status_code} - {user_response.text}"
                logger.error(error_msg)
                record_oauth_error('google', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=user_info_failed&provider=google"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            user_info = user_response.json()
            
            # Extract user data
            email = user_info.get('email')
            name = user_info.get('name', '')
            google_id = user_info.get('id')
            email_verified = user_info.get('verified_email', False)
            
            if not email:
                error_msg = "Google OAuth: No email provided"
                logger.error(error_msg)
                record_oauth_error('google', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_email&provider=google"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            if not email_verified:
                logger.warning(f"Google OAuth: Email {email} is not verified")
            
            logger.info(f"Google OAuth user info: {email} ({google_id}), verified: {email_verified}")
            
            # Create or get user with refresh token
            user = await create_or_get_oauth_user(
                email=email,
                name=name,
                provider='google',
                provider_id=google_id,
                refresh_token=refresh_token,
                access_token_expires_in=expires_in
            )
            
            # Generate JWT token
            token = create_jwt_token(user)
            
            # Record successful OAuth
            record_oauth_success('google', email, 0,  # Response time not tracked for Google
                               ip_address=request.client.host if request.client else None,
                               user_agent=request.headers.get('user-agent'))
            
            # Redirect to frontend with token
            frontend_url = f"{settings.services.frontend_url}/auth/callback/google?token={token}"
            logger.info(f"Google OAuth successful, redirecting to: {frontend_url}")
            response = RedirectResponse(url=frontend_url)
            return add_security_headers(response)
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Google OAuth HTTP error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        record_oauth_error('google', error_msg)
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=http_error&provider=google&details={e.response.status_code}"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    except Exception as e:
        error_msg = f"Google OAuth error: {str(e)}"
        logger.error(error_msg)
        record_oauth_error('google', error_msg)
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=internal_error&provider=google"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)


@router.get("/scopes/google")
async def get_google_oauth_scopes():
    """Get available Google OAuth scopes and their descriptions"""
    if not settings.security.google_oauth_enabled:
        raise HTTPException(status_code=400, detail="Google OAuth is not enabled")
    
    available_scopes = {
        "openid": {
            "description": "OpenID Connect authentication",
            "required": True,
            "category": "authentication"
        },
        "email": {
            "description": "Access to user's email address",
            "required": True,
            "category": "profile"
        },
        "profile": {
            "description": "Access to user's basic profile information",
            "required": True,
            "category": "profile"
        },
        "https://www.googleapis.com/auth/userinfo.profile": {
            "description": "Access to user's profile information",
            "required": False,
            "category": "profile"
        },
        "https://www.googleapis.com/auth/userinfo.email": {
            "description": "Access to user's email address",
            "required": False,
            "category": "profile"
        },
        "https://www.googleapis.com/auth/plus.me": {
            "description": "Access to Google+ profile information",
            "required": False,
            "category": "social"
        }
    }
    
    current_scopes = settings.security.google_scopes
    configured_scopes = {}
    
    for scope in current_scopes:
        if scope in available_scopes:
            configured_scopes[scope] = available_scopes[scope]
        else:
            configured_scopes[scope] = {
                "description": "Custom scope",
                "required": False,
                "category": "custom"
            }
    
    return {
        "available_scopes": available_scopes,
        "configured_scopes": configured_scopes,
        "current_configuration": {
            "scopes": current_scopes,
            "prompt": settings.security.google_prompt,
            "access_type": settings.security.google_access_type
        }
    }


@router.post("/validate/google")
async def validate_google_token(request: Request):
    """Validate Google OAuth access token"""
    if not settings.security.google_oauth_enabled:
        raise HTTPException(status_code=400, detail="Google OAuth is not enabled")
    
    try:
        # Get access token from request body
        body = await request.json()
        access_token = body.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Validate token with Google
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with httpx.AsyncClient() as client:
            # Check token info endpoint
            token_info_url = "https://oauth2.googleapis.com/tokeninfo"
            token_response = await client.get(f"{token_info_url}?access_token={access_token}")
            
            if not token_response.is_success:
                return {
                    'valid': False,
                    'error': 'Invalid or expired token'
                }
            
            token_info = token_response.json()
            
            # Check if token is expired
            expires_at = token_info.get('exp')
            if expires_at:
                current_time = int(time.time())
                if current_time >= expires_at:
                    return {
                        'valid': False,
                        'error': 'Token has expired'
                    }
            
            return {
                'valid': True,
                'user_id': token_info.get('user_id'),
                'email': token_info.get('email'),
                'scope': token_info.get('scope'),
                'expires_at': expires_at
            }
            
    except Exception as e:
        error_msg = f"Google OAuth token validation error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Internal token validation error")


@router.post("/refresh/google")
async def refresh_google_token(request: Request):
    """Refresh Google OAuth access token using refresh token"""
    if not settings.security.google_oauth_enabled:
        raise HTTPException(status_code=400, detail="Google OAuth is not enabled")
    
    try:
        # Get refresh token from request body
        body = await request.json()
        refresh_token = body.get('refresh_token')
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        # Exchange refresh token for new access token
        token_data = {
            'client_id': settings.security.google_client_id,
            'client_secret': settings.security.google_client_secret.get_secret_value(),
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        logger.info("Refreshing Google OAuth access token")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            
            if not token_response.is_success:
                error_msg = f"Google token refresh failed: {token_response.status_code} - {token_response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail="Failed to refresh token")
            
            token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            expires_in = token_info.get('expires_in', 3600)
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token in refresh response")
            
            logger.info(f"Google OAuth token refreshed successfully, expires in {expires_in}s")
            
            return {
                'access_token': access_token,
                'expires_in': expires_in,
                'token_type': 'Bearer'
            }
            
    except Exception as e:
        error_msg = f"Google OAuth token refresh error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Internal token refresh error")


@router.get("/github")
async def github_oauth_start(request: Request):
    """Start GitHub OAuth flow with enhanced security"""
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"github_start:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    if not settings.security.github_oauth_enabled:
        raise HTTPException(status_code=400, detail="GitHub OAuth is not enabled")
    
    if not settings.security.github_client_id:
        raise HTTPException(status_code=500, detail="GitHub OAuth client ID not configured")
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Record OAuth start
    record_oauth_start('github', 
                      ip_address=client_ip,
                      user_agent=request.headers.get('user-agent'))
    
    # Build OAuth authorization URL
    params = {
        'client_id': settings.security.github_client_id,
        'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.github_redirect_uri}",
        'scope': 'user:email',
        'response_type': 'code',
        'state': state
    }
    
    auth_url = f"{GITHUB_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Starting GitHub OAuth flow: {auth_url}")
    
    # Store state in memory store for validation
    await oauth_state_store.set_state(state, {
        'provider': 'github',
        'timestamp': datetime.utcnow()
    })
    
    response = RedirectResponse(url=auth_url)
    return add_security_headers(response)


@router.get("/callback/github")
async def github_oauth_callback(
    request: Request,
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle GitHub OAuth callback"""
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"github_callback:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    if error:
        logger.error(f"GitHub OAuth error: {error}")
        record_oauth_error('github', f"OAuth error: {error}")
        # Redirect to frontend with error
        frontend_url = f"{settings.services.frontend_url}/auth/error?error={error}&provider=github"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    if not code:
        logger.error("GitHub OAuth callback: No authorization code provided")
        record_oauth_error('github', "No authorization code provided")
        # Redirect to frontend with error
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_code&provider=github"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Validate state parameter for CSRF protection
    if not await validate_and_cleanup_state(state, 'github'):
        logger.error("GitHub OAuth callback: Invalid state parameter")
        record_oauth_error('github', "Invalid state parameter")
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=invalid_state&provider=github"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    
    # Clear the stored state
    await oauth_state_store.delete_state(state)
    
    start_time = datetime.utcnow()
    try:
        # Exchange code for access token
        token_data = {
            'client_id': settings.security.github_client_id,
            'client_secret': settings.security.github_client_secret.get_secret_value(),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{settings.services.api_gateway_url}{settings.security.github_redirect_uri}"
        }
        
        logger.info(f"Exchanging GitHub OAuth code for token: {code[:10]}...")
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                GITHUB_TOKEN_URL, 
                data=token_data,
                headers={'Accept': 'application/json'}
            )
            
            if not token_response.is_success:
                error_msg = f"GitHub token exchange failed: {token_response.status_code} - {token_response.text}"
                logger.error(error_msg)
                record_oauth_error('github', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=token_exchange_failed&provider=github"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            if not access_token:
                error_msg = "GitHub OAuth: No access token in response"
                logger.error(error_msg)
                record_oauth_error('github', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_access_token&provider=github"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            logger.info("GitHub OAuth: Successfully obtained access token")
            
            # Get user information
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            user_response = await client.get(GITHUB_USERINFO_URL, headers=headers)
            if not user_response.is_success:
                error_msg = f"Failed to get GitHub user info: {user_response.status_code} - {user_response.text}"
                logger.error(error_msg)
                record_oauth_error('github', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=user_info_failed&provider=github"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            user_info = user_response.json()
            
            # Get user emails
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            if not emails_response.is_success:
                error_msg = f"Failed to get GitHub user emails: {emails_response.status_code} - {emails_response.text}"
                logger.error(error_msg)
                record_oauth_error('github', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=emails_failed&provider=github"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
            emails = emails_response.json()
            
            # Find primary email
            primary_email = next((email['email'] for email in emails if email['primary']), None)
            if not primary_email:
                error_msg = "GitHub OAuth: No primary email found"
                logger.error(error_msg)
                record_oauth_error('github', error_msg)
                frontend_url = f"{settings.services.frontend_url}/auth/error?error=no_primary_email&provider=github"
                response = RedirectResponse(url=frontend_url)
                return add_security_headers(response)
            
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
            
            # Record successful OAuth
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            record_oauth_success('github', primary_email, response_time,
                               ip_address=request.client.host if request.client else None,
                               user_agent=request.headers.get('user-agent'))
            
            # Redirect to frontend with token
            frontend_url = f"{settings.services.frontend_url}/auth/callback/github?token={token}"
            logger.info(f"GitHub OAuth successful, redirecting to: {frontend_url}")
            response = RedirectResponse(url=frontend_url)
            return add_security_headers(response)
            
    except httpx.HTTPStatusError as e:
        error_msg = f"GitHub OAuth HTTP error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        record_oauth_error('github', error_msg)
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=http_error&provider=github&details={e.response.status_code}"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)
    except Exception as e:
        error_msg = f"GitHub OAuth error: {str(e)}"
        logger.error(error_msg)
        record_oauth_error('github', error_msg)
        frontend_url = f"{settings.services.frontend_url}/auth/error?error=internal_error&provider=github"
        response = RedirectResponse(url=frontend_url)
        return add_security_headers(response)


async def create_or_get_oauth_user(email: str, name: str, provider: str, provider_id: str, refresh_token: Optional[str] = None, access_token_expires_in: int = 3600):
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
        "github_client_id_configured": bool(settings.security.github_client_id),
        "features": {
            "pkce_enabled": True,
            "refresh_tokens": True,
            "state_validation": True,
            "csrf_protection": True
        }
    }
