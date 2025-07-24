#!/usr/bin/env python3
"""
API Gateway for SaaS Factory
Routes requests to appropriate agent services and handles cross-cutting concerns.
"""

from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
import json
import os
from typing import Optional, Dict, Any
import httpx
from datetime import datetime
from google.cloud import bigquery

# Import admin routes
from admin_routes import admin_router
from user_routes import router as user_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SaaS Factory API Gateway",
    description="Central API gateway routing requests to SaaS Factory agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add admin routes
app.include_router(admin_router)
app.include_router(user_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
        "version": "1.0.0"
    }

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "SaaS Factory API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "admin": "/api/admin/*",
            "orchestrator": "/api/orchestrate",
            "agents": "/api/{agent_type}/*"
        },
        "documentation": "/docs"
    }

# Orchestrator endpoint (existing)
@app.post("/api/orchestrate")
async def orchestrate_request(
    request: Request,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Route requests to the orchestrator"""
    try:
        body = await request.json()
        
        # Add tenant context to the request
        body["tenant_context"] = {
            "tenant_id": x_tenant_id,
            "user_id": x_user_id
        }
        
        # For now, return a mock response
        # In production, this would route to the actual orchestrator
        logger.info(f"Orchestrator request for tenant {x_tenant_id}: {body}")
        
        return {
            "status": "accepted",
            "message": "Request submitted to orchestrator",
            "tenant_id": x_tenant_id,
            "stage": body.get("stage", "unknown"),
            "request_id": f"req_{int(datetime.utcnow().timestamp())}"
        }
        
    except Exception as e:
        logger.error(f"Error in orchestrator request: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestrator request failed: {str(e)}")

# Agent proxy endpoints
@app.api_route("/api/{agent_type}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_agent(
    agent_type: str,
    path: str,
    request: Request,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Proxy requests to specific agent services"""
    try:
        # Agent service URLs (in production, these would be from service discovery)
        agent_urls = {
            "techstack": "http://localhost:8081",
            "design": "http://localhost:8082", 
            "dev": "http://localhost:8083",
            "qa": "http://localhost:8084",
            "ops": "http://localhost:8085"
        }
        
        if agent_type not in agent_urls:
            raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")
        
        base_url = agent_urls[agent_type]
        target_url = f"{base_url}/{path}"
        
        # Prepare headers
        headers = dict(request.headers)
        headers["x-tenant-id"] = x_tenant_id
        if x_user_id:
            headers["x-user-id"] = x_user_id
        
        # Get request body if present
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
        
        # Make request to agent service
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
            
    except httpx.RequestError as e:
        logger.error(f"Error proxying to {agent_type}: {e}")
        raise HTTPException(status_code=503, detail=f"Agent service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Error in agent proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 