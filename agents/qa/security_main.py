#!/usr/bin/env python3
"""
SecurityAgent FastAPI Application - Night 41 Implementation
Security scan step: Snyk CLI in pipeline; SecurityAgent parses report.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from contextlib import asynccontextmanager
import uuid

# Import the SecurityAgent
from security_agent import (
    SecurityAgent, SecurityScanRequest, SecurityScanResult, SecurityScanType,
    VulnerabilitySeverity, SnykReport, security_agent
)

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database lifecycle"""
    logger.info("Starting SecurityAgent FastAPI application")
    await security_agent.tenant_db.init_pool()
    yield
    logger.info("Shutting down SecurityAgent FastAPI application")
    await security_agent.tenant_db.close_pool()

app = FastAPI(
    title="SecurityAgent",
    description="AI-powered security scanning and vulnerability analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SecurityScanTrigger(BaseModel):
    """Model for triggering security scans"""
    project_id: str = Field(..., description="Project ID to scan")
    scan_type: SecurityScanType = Field(default=SecurityScanType.DEPENDENCIES, description="Type of security scan")
    target_path: str = Field(default=".", description="Path to scan")
    include_dev_dependencies: bool = Field(default=False, description="Include dev dependencies")
    severity_threshold: VulnerabilitySeverity = Field(default=VulnerabilitySeverity.LOW, description="Minimum severity threshold")
    fail_on_issues: bool = Field(default=False, description="Fail build on security issues")
    notify_devagent: bool = Field(default=True, description="Send feedback to DevAgent")
    auto_remediate: bool = Field(default=False, description="Attempt automatic remediation")

class SecurityScanStatus(BaseModel):
    """Model for security scan status"""
    scan_id: str
    project_id: str
    status: str
    progress: float = Field(default=0.0, description="Progress percentage")
    current_step: str = Field(default="", description="Current step description")
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

class SecurityDashboardSummary(BaseModel):
    """Model for security dashboard summary"""
    total_scans: int
    recent_scans: List[Dict[str, Any]]
    vulnerabilities_by_severity: Dict[VulnerabilitySeverity, int]
    risk_trend: List[Dict[str, Any]]
    top_vulnerable_packages: List[Dict[str, Any]]
    remediation_stats: Dict[str, Any]

class SecurityReportSummary(BaseModel):
    """Model for security report summary"""
    scan_id: str
    project_id: str
    project_name: Optional[str] = None
    scan_type: str
    total_vulnerabilities: int
    vulnerabilities_by_severity: Dict[str, int]
    risk_score: float
    created_at: datetime
    status: str

# Dependency injection for tenant context
def get_tenant_context(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
) -> TenantContext:
    """Get tenant context from headers"""
    return TenantContext(tenant_id=x_tenant_id, user_id=x_user_id)

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SecurityAgent", "version": "1.0.0"}

@app.post("/api/scan", response_model=SecurityScanStatus)
async def trigger_security_scan(
    scan_request: SecurityScanTrigger,
    background_tasks: BackgroundTasks,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Trigger a security scan"""
    try:
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Log the scan request
        await security_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="security_scan",
            agent_name="SecurityAgent",
            stage="scan_triggered",
            status="started",
            project_id=scan_request.project_id,
            input_data=scan_request.dict()
        )
        
        # Start background scan
        background_tasks.add_task(
            run_security_scan_background,
            scan_id,
            scan_request,
            tenant_context
        )
        
        return SecurityScanStatus(
            scan_id=scan_id,
            project_id=scan_request.project_id,
            status="started",
            progress=0.0,
            current_step="Initializing security scan",
            started_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error triggering security scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/{scan_id}/status", response_model=SecurityScanStatus)
async def get_scan_status(
    scan_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get security scan status"""
    try:
        # Check scan status in database
        async with security_agent.tenant_db.get_tenant_connection(tenant_context) as conn:
            row = await conn.fetchrow(
                """
                SELECT id, project_id, status, created_at, scan_duration_ms
                FROM security_scan_results
                WHERE id = $1
                """,
                scan_id
            )
            
            if not row:
                raise HTTPException(status_code=404, detail="Scan not found")
            
            return SecurityScanStatus(
                scan_id=row['id'],
                project_id=row['project_id'],
                status=row['status'],
                progress=100.0 if row['status'] == 'completed' else 50.0,
                current_step="Completed" if row['status'] == 'completed' else "In progress",
                started_at=row['created_at']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/{scan_id}/results", response_model=SecurityScanResult)
async def get_scan_results(
    scan_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get security scan results"""
    try:
        async with security_agent.tenant_db.get_tenant_connection(tenant_context) as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM security_scan_results
                WHERE id = $1
                """,
                scan_id
            )
            
            if not row:
                raise HTTPException(status_code=404, detail="Scan results not found")
            
            # Parse stored data
            snyk_report_data = json.loads(row['snyk_report']) if row['snyk_report'] else None
            snyk_report = SnykReport(**snyk_report_data) if snyk_report_data else None
            
            return SecurityScanResult(
                scan_id=row['id'],
                project_id=row['project_id'],
                status=row['status'],
                snyk_report=snyk_report,
                summary={
                    "total_vulnerabilities": row['total_vulnerabilities'],
                    "vulnerabilities_by_severity": json.loads(row['vulnerabilities_by_severity']) if row['vulnerabilities_by_severity'] else {},
                    "risk_score": row['risk_score']
                },
                recommendations=json.loads(row['recommendations']) if row['recommendations'] else [],
                remediation_steps=json.loads(row['remediation_steps']) if row['remediation_steps'] else [],
                risk_score=row['risk_score'],
                scan_duration_ms=row['scan_duration_ms'] or 0,
                created_at=row['created_at']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/security-summary", response_model=SecurityDashboardSummary)
async def get_project_security_summary(
    project_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get security summary for a project"""
    try:
        # Get recent scans for the project
        scan_results = await security_agent.get_security_scan_results(
            tenant_context=tenant_context,
            project_id=project_id,
            limit=10
        )
        
        # Calculate summary statistics
        total_scans = len(scan_results)
        vulnerabilities_by_severity = {}
        risk_trend = []
        
        for result in scan_results:
            # Parse vulnerabilities by severity
            vuln_severity = json.loads(result['vulnerabilities_by_severity']) if result['vulnerabilities_by_severity'] else {}
            for severity, count in vuln_severity.items():
                if severity in vulnerabilities_by_severity:
                    vulnerabilities_by_severity[severity] += count
                else:
                    vulnerabilities_by_severity[severity] = count
            
            # Build risk trend
            risk_trend.append({
                "date": result['created_at'].isoformat(),
                "risk_score": result['risk_score'],
                "total_vulnerabilities": result['total_vulnerabilities']
            })
        
        # Get top vulnerable packages (mock data for now)
        top_vulnerable_packages = [
            {"name": "lodash", "vulnerabilities": 3, "severity": "HIGH"},
            {"name": "moment", "vulnerabilities": 2, "severity": "MEDIUM"},
            {"name": "axios", "vulnerabilities": 1, "severity": "LOW"}
        ]
        
        remediation_stats = {
            "auto_fixable": sum(1 for r in scan_results if r.get('auto_fixable', 0) > 0),
            "manual_review_required": sum(1 for r in scan_results if r.get('manual_review_required', 0) > 0),
            "total_recommendations": sum(len(json.loads(r['recommendations'])) for r in scan_results if r['recommendations'])
        }
        
        return SecurityDashboardSummary(
            total_scans=total_scans,
            recent_scans=[{
                "scan_id": r['id'],
                "created_at": r['created_at'].isoformat(),
                "status": r['status'],
                "risk_score": r['risk_score'],
                "total_vulnerabilities": r['total_vulnerabilities']
            } for r in scan_results[:5]],
            vulnerabilities_by_severity=vulnerabilities_by_severity,
            risk_trend=risk_trend,
            top_vulnerable_packages=top_vulnerable_packages,
            remediation_stats=remediation_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting project security summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security-reports", response_model=List[SecurityReportSummary])
async def get_security_reports(
    tenant_context: TenantContext = Depends(get_tenant_context),
    project_id: Optional[str] = None,
    limit: int = 20
):
    """Get security reports for tenant"""
    try:
        scan_results = await security_agent.get_security_scan_results(
            tenant_context=tenant_context,
            project_id=project_id,
            limit=limit
        )
        
        reports = []
        for result in scan_results:
            vuln_severity = json.loads(result['vulnerabilities_by_severity']) if result['vulnerabilities_by_severity'] else {}
            
            reports.append(SecurityReportSummary(
                scan_id=result['id'],
                project_id=result['project_id'],
                project_name=result.get('project_name'),
                scan_type=result['scan_type'],
                total_vulnerabilities=result['total_vulnerabilities'],
                vulnerabilities_by_severity=vuln_severity,
                risk_score=result['risk_score'],
                created_at=result['created_at'],
                status=result['status']
            ))
        
        return reports
        
    except Exception as e:
        logger.error(f"Error getting security reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/snyk")
async def snyk_webhook(
    webhook_data: Dict[str, Any],
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Handle Snyk webhook notifications"""
    try:
        logger.info(f"Received Snyk webhook: {webhook_data}")
        
        # Process webhook data
        project_id = webhook_data.get('project', {}).get('id')
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID not found in webhook data")
        
        # Log webhook event
        await security_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="snyk_webhook",
            agent_name="SecurityAgent",
            stage="webhook_received",
            status="completed",
            project_id=project_id,
            input_data=webhook_data
        )
        
        return {"status": "processed", "project_id": project_id}
        
    except Exception as e:
        logger.error(f"Error processing Snyk webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remediation/auto-fix")
async def auto_fix_vulnerabilities(
    scan_id: str,
    background_tasks: BackgroundTasks,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Trigger automatic vulnerability remediation"""
    try:
        # Get scan results
        scan_results = await get_scan_results(scan_id, tenant_context)
        
        if not scan_results.snyk_report:
            raise HTTPException(status_code=400, detail="No scan report available for remediation")
        
        # Start background remediation
        background_tasks.add_task(
            run_auto_remediation_background,
            scan_id,
            scan_results,
            tenant_context
        )
        
        return {"status": "started", "scan_id": scan_id, "message": "Auto-remediation started"}
        
    except Exception as e:
        logger.error(f"Error starting auto-remediation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Tasks
async def run_security_scan_background(
    scan_id: str,
    scan_request: SecurityScanTrigger,
    tenant_context: TenantContext
):
    """Run security scan in background"""
    try:
        logger.info(f"Starting background security scan: {scan_id}")
        
        # Create security scan request
        security_request = SecurityScanRequest(
            project_id=scan_request.project_id,
            scan_type=scan_request.scan_type,
            target_path=scan_request.target_path,
            include_dev_dependencies=scan_request.include_dev_dependencies,
            severity_threshold=scan_request.severity_threshold,
            fail_on_issues=scan_request.fail_on_issues
        )
        
        # Run Snyk scan
        snyk_report = await security_agent.run_snyk_scan(security_request)
        
        # Analyze results
        scan_result = await security_agent.analyze_security_report(snyk_report, tenant_context)
        scan_result.scan_id = scan_id
        scan_result.project_id = scan_request.project_id
        
        # Save results
        await security_agent.save_security_scan_result(scan_result, tenant_context)
        
        # Send feedback to DevAgent if requested
        if scan_request.notify_devagent:
            await security_agent.send_security_feedback_to_dev_agent(scan_result, tenant_context)
        
        # Log completion
        await security_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="security_scan",
            agent_name="SecurityAgent",
            stage="scan_completed",
            status="completed",
            project_id=scan_request.project_id,
            output_data=scan_result.dict()
        )
        
        logger.info(f"Security scan completed: {scan_id}")
        
    except Exception as e:
        logger.error(f"Error in background security scan: {e}")
        
        # Log error
        await security_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="security_scan",
            agent_name="SecurityAgent",
            stage="scan_failed",
            status="failed",
            project_id=scan_request.project_id,
            error_message=str(e)
        )

async def run_auto_remediation_background(
    scan_id: str,
    scan_results: SecurityScanResult,
    tenant_context: TenantContext
):
    """Run automatic remediation in background"""
    try:
        logger.info(f"Starting auto-remediation for scan: {scan_id}")
        
        # TODO: Implement automatic remediation logic
        # This would involve:
        # 1. Analyzing remediation recommendations
        # 2. Applying automatic fixes (upgrades, patches)
        # 3. Creating PR with fixes
        # 4. Updating scan results
        
        # For now, just log the attempt
        await security_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="auto_remediation",
            agent_name="SecurityAgent",
            stage="remediation_started",
            status="started",
            project_id=scan_results.project_id,
            input_data={"scan_id": scan_id}
        )
        
        logger.info(f"Auto-remediation completed for scan: {scan_id}")
        
    except Exception as e:
        logger.error(f"Error in auto-remediation: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085) 