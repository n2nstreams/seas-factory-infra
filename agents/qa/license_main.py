#!/usr/bin/env python3
"""
License Scan Agent - Main FastAPI Application
Night 64: OSS Review Toolkit (ORT) integration - fail pipeline on GPL licenses
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
import sys
from typing import Optional

# Import shared components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, get_tenant_context_from_headers

# Import the License Scan Agent
from license_scan_agent import (
    LicenseScanAgent, LicenseScanRequest, LicenseScanResult, 
    LicensePolicy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
license_agent: Optional[LicenseScanAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    global license_agent
    
    # Startup
    logger.info("🚀 License Scan Agent starting up...")
    
    try:
        # Initialize the license scan agent
        license_agent = LicenseScanAgent()
        
        # Verify ORT installation
        if license_agent._is_ort_available():
            ort_version = license_agent._get_ort_version()
            logger.info(f"✅ OSS Review Toolkit (ORT) v{ort_version} detected")
        else:
            logger.warning("⚠️  OSS Review Toolkit (ORT) not found - some features may be limited")
        
        # Test database connectivity
        tenant_db = TenantDatabase()
        logger.info("✅ Database connection established")
        
        logger.info("🎯 License Scan Agent ready for Night 64 - GPL license detection!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize License Scan Agent: {str(e)}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("🛑 License Scan Agent shutting down...")

# Create FastAPI app
app = FastAPI(
    title="License Scan Agent",
    description="OSS Review Toolkit (ORT) integration for license compliance scanning - Night 64 Implementation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    return {
        "status": "healthy",
        "service": "license-scan-agent",
        "version": "1.0.0",
        "ort_available": license_agent._is_ort_available(),
        "ort_version": license_agent._get_ort_version(),
        "metrics": license_agent.get_metrics()
    }

# Main license scanning endpoint
@app.post("/scan", response_model=LicenseScanResult)
async def scan_licenses(
    request: LicenseScanRequest,
    background_tasks: BackgroundTasks,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """
    Scan project dependencies for license compliance using OSS Review Toolkit (ORT)
    
    This endpoint implements Night 64: fail pipeline on GPL licenses detected
    """
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    logger.info(f"🔍 Starting license scan for project {request.project_id} (tenant: {tenant_context.tenant_id})")
    
    try:
        # Run the license scan
        scan_result = await license_agent.scan_project_licenses(request, tenant_context)
        
        # Log the result
        if scan_result.pipeline_should_fail:
            logger.warning(
                f"🚨 License scan FAILED for project {request.project_id}: {scan_result.failure_reason}"
            )
        else:
            logger.info(f"✅ License scan PASSED for project {request.project_id}")
        
        return scan_result
        
    except Exception as e:
        logger.error(f"❌ License scan failed for project {request.project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"License scan failed: {str(e)}"
        )

# Async scan endpoint for long-running scans
@app.post("/scan/async")
async def scan_licenses_async(
    request: LicenseScanRequest,
    background_tasks: BackgroundTasks,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """
    Start an asynchronous license scan and return immediately with scan ID
    """
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    # Generate scan ID
    import uuid
    scan_id = str(uuid.uuid4())
    
    logger.info(f"🔄 Starting async license scan {scan_id} for project {request.project_id}")
    
    # Add the scan to background tasks
    background_tasks.add_task(
        _run_async_scan, 
        scan_id, 
        request, 
        tenant_context
    )
    
    return {
        "scan_id": scan_id,
        "status": "started",
        "message": f"License scan started for project {request.project_id}",
        "check_status_url": f"/scan/{scan_id}/status"
    }

async def _run_async_scan(scan_id: str, request: LicenseScanRequest, tenant_context):
    """Background task to run async license scan"""
    global license_agent
    
    try:
        logger.info(f"🏃 Executing async license scan {scan_id}")
        
        # Run the scan
        scan_result = await license_agent.scan_project_licenses(request, tenant_context)
        
        # Update scan result with our scan_id
        scan_result.scan_id = scan_id
        
        # Store the result (already handled in scan_project_licenses)
        logger.info(f"✅ Async license scan {scan_id} completed")
        
    except Exception as e:
        logger.error(f"❌ Async license scan {scan_id} failed: {str(e)}")

# Get scan status/results
@app.get("/scan/{scan_id}/status")
async def get_scan_status(
    scan_id: str,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """Get the status and results of a license scan"""
    try:
        tenant_db = TenantDatabase()
        
        async with tenant_db.get_connection(tenant_context) as conn:
            result = await conn.fetchrow("""
                SELECT scan_id, project_id, status, passed, pipeline_should_fail, 
                       failure_reason, scan_start_time, scan_end_time, 
                       ort_result, recommendations, action_items
                FROM license_scan_results 
                WHERE scan_id = $1 AND tenant_id = $2
            """, scan_id, tenant_context.tenant_id)
            
            if not result:
                raise HTTPException(
                    status_code=404, 
                    detail=f"License scan {scan_id} not found"
                )
            
            # Parse JSON fields
            import json
            ort_result = json.loads(result['ort_result']) if result['ort_result'] else None
            recommendations = json.loads(result['recommendations']) if result['recommendations'] else []
            action_items = json.loads(result['action_items']) if result['action_items'] else []
            
            return {
                "scan_id": result['scan_id'],
                "project_id": result['project_id'],
                "status": result['status'],
                "passed": result['passed'],
                "pipeline_should_fail": result['pipeline_should_fail'],
                "failure_reason": result['failure_reason'],
                "scan_start_time": result['scan_start_time'],
                "scan_end_time": result['scan_end_time'],
                "ort_result": ort_result,
                "recommendations": recommendations,
                "action_items": action_items
            }
            
    except Exception as e:
        logger.error(f"Error retrieving scan status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve scan status: {str(e)}"
        )

# List scans for a project
@app.get("/project/{project_id}/scans")
async def list_project_scans(
    project_id: str,
    limit: int = 20,
    offset: int = 0,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """List license scans for a specific project"""
    try:
        tenant_db = TenantDatabase()
        
        async with tenant_db.get_connection(tenant_context) as conn:
            results = await conn.fetch("""
                SELECT scan_id, project_id, status, passed, pipeline_should_fail,
                       failure_reason, scan_start_time, scan_end_time
                FROM license_scan_results 
                WHERE project_id = $1 AND tenant_id = $2
                ORDER BY scan_start_time DESC
                LIMIT $3 OFFSET $4
            """, project_id, tenant_context.tenant_id, limit, offset)
            
            return {
                "project_id": project_id,
                "scans": [dict(row) for row in results],
                "total_count": len(results),
                "limit": limit,
                "offset": offset
            }
            
    except Exception as e:
        logger.error(f"Error listing project scans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list project scans: {str(e)}"
        )

# Get agent metrics
@app.get("/metrics")
async def get_metrics():
    """Get License Scan Agent performance metrics"""
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    return license_agent.get_metrics()

# License policy endpoints
@app.get("/policy/default")
async def get_default_policy():
    """Get the default license policy configuration"""
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    return license_agent.default_policy.dict()

@app.post("/scan/with-policy", response_model=LicenseScanResult)
async def scan_with_custom_policy(
    request: LicenseScanRequest,
    policy: LicensePolicy,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """
    Scan project with custom license policy
    """
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    logger.info(f"🔍 Starting license scan with custom policy for project {request.project_id}")
    
    try:
        # Set up workspace
        workspace_dir = await license_agent._setup_workspace(request)
        
        try:
            # Run ORT scan
            ort_result = await license_agent.run_ort_scan(workspace_dir, request)
            
            # Evaluate with custom policy
            scan_result = await license_agent.evaluate_scan_result(ort_result, request, policy)
            
            # Store results
            await license_agent._store_scan_results(scan_result, tenant_context)
            
            return scan_result
            
        finally:
            # Clean up workspace
            import shutil
            if workspace_dir and os.path.exists(workspace_dir):
                shutil.rmtree(workspace_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"❌ License scan with custom policy failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"License scan failed: {str(e)}"
        )

# Cloud Build webhook endpoint
@app.post("/webhook/cloudbuild")
async def cloudbuild_webhook(
    request: Request,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """
    Webhook endpoint for Cloud Build integration
    Triggered when Cloud Build completes ORT license scan
    """
    try:
        payload = await request.json()
        
        build_id = payload.get("build_id")
        project_name = payload.get("project_name")
        status = payload.get("status", "unknown")
        
        logger.info(f"📥 Received Cloud Build webhook for build {build_id}, project {project_name}")
        
        # Process the Cloud Build results
        # In production, you would download and parse the ORT results from Cloud Storage
        
        return {
            "status": "received",
            "build_id": build_id,
            "project_name": project_name,
            "message": "Cloud Build webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing Cloud Build webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )

# Pipeline integration endpoint
@app.post("/pipeline/check")
async def pipeline_license_check(
    project_id: str,
    repository_url: str,
    branch: str = "main",
    fail_build: bool = True,
    tenant_context=Depends(get_tenant_context_from_headers)
):
    """
    Pipeline integration endpoint - designed to be called from CI/CD
    Returns appropriate exit codes for pipeline success/failure
    """
    global license_agent
    
    if license_agent is None:
        raise HTTPException(status_code=503, detail="License Scan Agent not initialized")
    
    logger.info(f"🔧 Pipeline license check for {project_id} on branch {branch}")
    
    try:
        # Create scan request
        scan_request = LicenseScanRequest(
            project_id=project_id,
            repository_url=repository_url,
            branch=branch,
            fail_on_gpl=fail_build
        )
        
        # Run the scan
        scan_result = await license_agent.scan_project_licenses(scan_request, tenant_context)
        
        # For pipeline integration, return appropriate status codes
        if scan_result.pipeline_should_fail and fail_build:
            # Return 422 to indicate pipeline should fail
            return JSONResponse(
                status_code=422,
                content={
                    "pipeline_status": "FAILED",
                    "reason": scan_result.failure_reason,
                    "scan_id": scan_result.scan_id,
                    "recommendations": scan_result.recommendations,
                    "action_items": scan_result.action_items
                }
            )
        else:
            # Return 200 for success
            return {
                "pipeline_status": "PASSED",
                "scan_id": scan_result.scan_id,
                "message": "License compliance check passed",
                "summary": scan_result.ort_result.license_summary if scan_result.ort_result else {}
            }
            
    except Exception as e:
        logger.error(f"❌ Pipeline license check failed: {str(e)}")
        
        if fail_build:
            return JSONResponse(
                status_code=500,
                content={
                    "pipeline_status": "ERROR",
                    "reason": f"License scan failed: {str(e)}"
                }
            )
        else:
            return {
                "pipeline_status": "WARNING",
                "reason": f"License scan failed: {str(e)}"
            }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8087"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting License Scan Agent on {host}:{port}")
    
    uvicorn.run(
        "license_main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    ) 