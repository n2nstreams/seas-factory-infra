"""
ZAP Penetration Testing Service - Night 78 Implementation

FastAPI service for OWASP ZAP penetration testing that integrates with
the existing SecurityAgent infrastructure.

Night 78: Final security scan & penetration test script (OWASP ZAP).
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import ZAP agent components
from agents.qa.zap_penetration_agent import (
    ZAPPenetrationAgent, 
    ZAPScanRequest, 
    ZAPScanResult,
    EnhancedSecurityAgent
)

# Import existing security infrastructure
from agents.shared.tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZAPScanTrigger(BaseModel):
    """Request model for triggering ZAP scans"""
    project_id: str
    target_url: str
    scan_type: str = "baseline"
    spider_timeout: int = 5
    scan_timeout: int = 10
    max_depth: int = 5
    exclude_urls: List[str] = []
    authentication: Optional[Dict[str, Any]] = None
    notify_devagent: bool = True


class ZAPScanStatus(BaseModel):
    """ZAP scan status response"""
    scan_id: str
    project_id: str
    target_url: str
    status: str
    progress: float = 0.0
    current_step: str = ""
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ComprehensiveScanRequest(BaseModel):
    """Request for comprehensive security scan (Snyk + ZAP)"""
    project_id: str
    target_url: str
    include_snyk: bool = True
    include_zap: bool = True
    zap_scan_type: str = "baseline"


# Global instances
zap_agent = None
enhanced_security_agent = None
tenant_db = None


# Dependency injection for tenant context
def get_tenant_context(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
) -> TenantContext:
    """Get tenant context from headers"""
    return TenantContext(tenant_id=x_tenant_id, user_id=x_user_id)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global zap_agent, enhanced_security_agent, tenant_db
    
    logger.info("Starting ZAP Penetration Testing Service...")
    
    # Initialize components
    zap_agent = ZAPPenetrationAgent()
    enhanced_security_agent = EnhancedSecurityAgent()
    tenant_db = TenantDatabase()
    
    logger.info("ZAP Penetration Testing Service started successfully")
    
    yield
    
    logger.info("ZAP Penetration Testing Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="ZAP Penetration Testing Service",
    description="OWASP ZAP penetration testing service for comprehensive security scanning",
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "zap-penetration-testing",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/zap/scan", response_model=ZAPScanStatus)
async def trigger_zap_scan(
    scan_request: ZAPScanTrigger,
    background_tasks: BackgroundTasks,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Trigger a ZAP penetration test"""
    try:
        # Log the scan request
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="zap_penetration_scan",
            agent_name="ZAPPenetrationAgent",
            stage="scan_triggered",
            status="started",
            project_id=scan_request.project_id,
            input_data=scan_request.dict()
        )
        
        # Create ZAP scan request
        zap_request = ZAPScanRequest(
            project_id=scan_request.project_id,
            target_url=scan_request.target_url,
            scan_type=scan_request.scan_type,
            spider_timeout=scan_request.spider_timeout,
            scan_timeout=scan_request.scan_timeout,
            max_depth=scan_request.max_depth,
            exclude_urls=scan_request.exclude_urls,
            authentication=scan_request.authentication
        )
        
        # Start background scan
        background_tasks.add_task(
            run_zap_scan_background,
            zap_request,
            tenant_context,
            scan_request.notify_devagent
        )
        
        return ZAPScanStatus(
            scan_id="pending",  # Will be generated in background task
            project_id=scan_request.project_id,
            target_url=scan_request.target_url,
            status="started",
            progress=0.0,
            current_step="Initializing ZAP penetration test",
            started_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error triggering ZAP scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comprehensive-scan")
async def trigger_comprehensive_scan(
    scan_request: ComprehensiveScanRequest,
    background_tasks: BackgroundTasks,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Trigger comprehensive security scan (Snyk + ZAP)"""
    try:
        # Log the comprehensive scan request
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="comprehensive_security_scan",
            agent_name="EnhancedSecurityAgent",
            stage="scan_triggered",
            status="started",
            project_id=scan_request.project_id,
            input_data=scan_request.dict()
        )
        
        # Start background comprehensive scan
        background_tasks.add_task(
            run_comprehensive_scan_background,
            scan_request,
            tenant_context
        )
        
        return {
            "project_id": scan_request.project_id,
            "status": "started",
            "message": "Comprehensive security scan initiated",
            "scans": {
                "snyk": scan_request.include_snyk,
                "zap": scan_request.include_zap
            },
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering comprehensive scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zap/scan/{scan_id}")
async def get_zap_scan_status(
    scan_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get ZAP scan status and results"""
    try:
        # Query database for scan results
        scan_result = await tenant_db.get_security_scan_result(scan_id, tenant_context)
        
        if not scan_result:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return {
            "scan_id": scan_result.get("scan_id"),
            "project_id": scan_result.get("project_id"),
            "status": scan_result.get("status"),
            "risk_score": scan_result.get("risk_score"),
            "total_vulnerabilities": scan_result.get("total_vulnerabilities"),
            "vulnerabilities_by_severity": scan_result.get("vulnerabilities_by_severity"),
            "recommendations": scan_result.get("recommendations"),
            "created_at": scan_result.get("created_at"),
            "updated_at": scan_result.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zap/scans")
async def list_zap_scans(
    project_id: Optional[str] = None,
    limit: int = 50,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """List ZAP penetration test scans for tenant"""
    try:
        scans = await tenant_db.list_security_scans(
            tenant_context=tenant_context,
            project_id=project_id,
            scan_type="zap_penetration",
            limit=limit
        )
        
        return {
            "scans": scans,
            "total": len(scans),
            "tenant_id": tenant_context.tenant_id
        }
        
    except Exception as e:
        logger.error(f"Error listing ZAP scans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zap/demo")
async def run_zap_demo(
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Run ZAP penetration test demo on DVWA or similar test target"""
    try:
        # Demo target (DVWA or similar vulnerable app)
        demo_target = os.getenv("ZAP_DEMO_TARGET", "http://dvwa.local")
        
        demo_request = ZAPScanRequest(
            project_id="demo-project",
            target_url=demo_target,
            scan_type="quick",
            spider_timeout=2,
            scan_timeout=5,
            max_depth=3
        )
        
        logger.info(f"Running ZAP demo scan on {demo_target}")
        scan_result = await zap_agent.run_zap_scan(demo_request)
        await zap_agent.save_zap_scan_result(scan_result, tenant_context)
        
        return {
            "demo_completed": True,
            "scan_id": scan_result.scan_id,
            "target_url": demo_target,
            "status": scan_result.status,
            "risk_score": scan_result.risk_score,
            "total_vulnerabilities": scan_result.total_vulnerabilities,
            "security_posture": scan_result.security_posture,
            "recommendations": scan_result.recommendations[:5]  # First 5 recommendations
        }
        
    except Exception as e:
        logger.error(f"ZAP demo failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {e}")


# Background Tasks

async def run_zap_scan_background(
    zap_request: ZAPScanRequest,
    tenant_context: TenantContext,
    notify_devagent: bool = False
):
    """Run ZAP scan in background"""
    try:
        logger.info(f"Starting background ZAP scan for {zap_request.target_url}")
        
        # Run ZAP scan
        scan_result = await zap_agent.run_zap_scan(zap_request)
        
        # Save results to database
        await zap_agent.save_zap_scan_result(scan_result, tenant_context)
        
        # Send feedback to DevAgent if requested
        if notify_devagent and scan_result.total_vulnerabilities > 0:
            await send_zap_feedback_to_dev_agent(scan_result, tenant_context)
        
        # Log completion
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="zap_penetration_scan",
            agent_name="ZAPPenetrationAgent",
            stage="scan_completed",
            status="completed",
            project_id=zap_request.project_id,
            output_data={
                "scan_id": scan_result.scan_id,
                "risk_score": scan_result.risk_score,
                "total_vulnerabilities": scan_result.total_vulnerabilities,
                "security_posture": scan_result.security_posture
            }
        )
        
        logger.info(f"ZAP scan {scan_result.scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background ZAP scan failed: {e}")
        
        # Log failure
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="zap_penetration_scan",
            agent_name="ZAPPenetrationAgent",
            stage="scan_failed",
            status="failed",
            project_id=zap_request.project_id,
            output_data={"error": str(e)}
        )


async def run_comprehensive_scan_background(
    scan_request: ComprehensiveScanRequest,
    tenant_context: TenantContext
):
    """Run comprehensive security scan in background"""
    try:
        logger.info(f"Starting comprehensive security scan for {scan_request.target_url}")
        
        # Run comprehensive scan using enhanced security agent
        results = await enhanced_security_agent.run_comprehensive_security_scan(
            project_id=scan_request.project_id,
            target_url=scan_request.target_url,
            tenant_context=tenant_context
        )
        
        # Log completion
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="comprehensive_security_scan",
            agent_name="EnhancedSecurityAgent",
            stage="scan_completed",
            status="completed",
            project_id=scan_request.project_id,
            output_data=results
        )
        
        logger.info(f"Comprehensive security scan completed for project {scan_request.project_id}")
        
    except Exception as e:
        logger.error(f"Comprehensive security scan failed: {e}")
        
        # Log failure
        await tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="comprehensive_security_scan",
            agent_name="EnhancedSecurityAgent",
            stage="scan_failed",
            status="failed",
            project_id=scan_request.project_id,
            output_data={"error": str(e)}
        )


async def send_zap_feedback_to_dev_agent(scan_result: ZAPScanResult, tenant_context: TenantContext):
    """Send ZAP scan feedback to DevAgent"""
    try:
        import httpx
        
        dev_agent_url = os.getenv("DEV_AGENT_URL", "http://dev-agent:8083")
        
        # Prepare feedback data
        feedback_data = {
            "type": "zap_penetration_feedback",
            "scan_id": scan_result.scan_id,
            "project_id": scan_result.project_id,
            "target_url": scan_result.target_url,
            "risk_score": scan_result.risk_score,
            "security_posture": scan_result.security_posture,
            "critical_vulnerabilities": [
                {
                    "name": v.name,
                    "description": v.description,
                    "solution": v.solution,
                    "url": v.url
                } for v in scan_result.vulnerabilities if v.risk == "Critical"
            ],
            "high_vulnerabilities": [
                {
                    "name": v.name,
                    "description": v.description,
                    "solution": v.solution,
                    "url": v.url
                } for v in scan_result.vulnerabilities if v.risk == "High"
            ],
            "recommendations": scan_result.recommendations,
            "scan_timestamp": scan_result.started_at.isoformat()
        }
        
        # Send feedback to DevAgent
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{dev_agent_url}/api/feedback/security",
                json=feedback_data,
                headers={"X-Tenant-ID": tenant_context.tenant_id}
            )
            response.raise_for_status()
        
        logger.info(f"Sent ZAP feedback to DevAgent for scan {scan_result.scan_id}")
        
    except Exception as e:
        logger.warning(f"Failed to send ZAP feedback to DevAgent: {e}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8085))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "zap_main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 