#!/usr/bin/env python3
"""
Security Middleware for SaaS Factory API Gateway
Implements comprehensive security headers and security features
"""

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging
from typing import Optional
import secrets
import time

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for API Gateway"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.security_headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Strict referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Feature restriction policy
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https: wss:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Cache control for security
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            
            # Additional security headers
            "X-Download-Options": "noopen",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Requested-With": "XMLHttpRequest",
        }
        
        # Rate limiting configuration
        self.rate_limit_requests = 100  # requests per window
        self.rate_limit_window = 60     # seconds
        self.rate_limit_store = {}      # In production, use Redis
        
        # Security monitoring
        self.security_events = []
        self.max_events = 1000
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with security enhancements"""
        start_time = time.time()
        
        # Generate request ID for tracking
        request_id = secrets.token_urlsafe(16)
        request.state.request_id = request_id
        
        # Rate limiting check
        if not self._check_rate_limit(request):
            logger.warning(f"Rate limit exceeded for {request.client.host}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.rate_limit_window)}
            )
        
        # Security validation
        security_violations = self._validate_security(request)
        if security_violations:
            logger.warning(f"Security violations detected: {security_violations}")
            self._log_security_event("security_violation", request, security_violations)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Add request tracking headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(round((time.time() - start_time) * 1000, 2))
            
            # Log successful request
            self._log_security_event("request_success", request, None)
            
            return response
            
        except Exception as e:
            # Log security event for errors
            self._log_security_event("request_error", request, str(e))
            logger.error(f"Request processing error: {e}")
            raise
    
    def _check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limits"""
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_rate_limit_store(current_time)
        
        # Check rate limit
        if client_ip in self.rate_limit_store:
            requests = self.rate_limit_store[client_ip]
            # Remove old requests outside the window
            requests = [req_time for req_time in requests if current_time - req_time < self.rate_limit_window]
            
            if len(requests) >= self.rate_limit_requests:
                return False
            
            requests.append(current_time)
            self.rate_limit_store[client_ip] = requests
        else:
            self.rate_limit_store[client_ip] = [current_time]
        
        return True
    
    def _cleanup_rate_limit_store(self, current_time: float):
        """Clean up old rate limit entries"""
        cutoff_time = current_time - self.rate_limit_window
        for client_ip in list(self.rate_limit_store.keys()):
            requests = self.rate_limit_store[client_ip]
            requests = [req_time for req_time in requests if req_time > cutoff_time]
            if not requests:
                del self.rate_limit_store[client_ip]
            else:
                self.rate_limit_store[client_ip] = requests
    
    def _validate_security(self, request: Request) -> list:
        """Validate request for security issues"""
        violations = []
        
        # Check for suspicious headers
        suspicious_headers = [
            "X-Forwarded-For", "X-Real-IP", "X-Client-IP",
            "X-Forwarded-Host", "X-Original-URL", "X-Rewrite-URL"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                violations.append(f"Suspicious header: {header}")
        
        # Check for SQL injection patterns in query parameters
        sql_patterns = ["'", "/*", "*/", "--", "xp_", "sp_", "exec", "union", "select"]
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                for pattern in sql_patterns:
                    if pattern.lower() in param_value.lower():
                        violations.append(f"Potential SQL injection in {param_name}")
                        break
        
        # Check for XSS patterns
        xss_patterns = ["<script", "javascript:", "onload=", "onerror=", "onclick="]
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                for pattern in xss_patterns:
                    if pattern.lower() in param_value.lower():
                        violations.append(f"Potential XSS in {param_name}")
                        break
        
        # Check for path traversal
        if ".." in request.url.path or "//" in request.url.path:
            violations.append("Potential path traversal attack")
        
        return violations
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers to response"""
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
    
    def _log_security_event(self, event_type: str, request: Request, details: Optional[str]):
        """Log security events for monitoring"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "client_ip": request.client.host,
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "details": details
        }
        
        self.security_events.append(event)
        
        # Keep only recent events
        if len(self.security_events) > self.max_events:
            self.security_events = self.security_events[-self.max_events:]
        
        # Log to application logs
        if event_type in ["security_violation", "request_error"]:
            logger.warning(f"Security event: {event}")
        else:
            logger.info(f"Security event: {event_type}")
    
    def get_security_metrics(self) -> dict:
        """Get security metrics for monitoring"""
        current_time = time.time()
        recent_events = [e for e in self.security_events if current_time - e["timestamp"] < 3600]
        
        return {
            "total_events": len(self.security_events),
            "recent_events_1h": len(recent_events),
            "event_types": {
                event_type: len([e for e in recent_events if e["event_type"] == event_type])
                for event_type in set(e["event_type"] for e in recent_events)
            },
            "rate_limit_store_size": len(self.rate_limit_store),
            "active_clients": len([
                client for client, requests in self.rate_limit_store.items()
                if requests and time.time() - requests[-1] < self.rate_limit_window
            ])
        }


def create_security_middleware(app):
    """Create and configure security middleware"""
    return SecurityMiddleware(app)
