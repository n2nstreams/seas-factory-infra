#!/usr/bin/env python3
"""
SecurityAgent - Night 41 Implementation
Security scan step: Snyk CLI in pipeline; SecurityAgent parses report.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import httpx
import json
import asyncio
import os
import tempfile
import shutil
import subprocess
import uuid
from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import yaml
import re
from enum import Enum

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from github_integration import (
    create_github_integration, ReviewComment, 
    generate_pr_title, generate_pr_body
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityScanType(str, Enum):
    """Types of security scans"""
    DEPENDENCIES = "dependencies"
    CODE = "code"
    CONTAINER = "container"
    INFRASTRUCTURE = "infrastructure"

class VulnerabilityStatus(str, Enum):
    """Status of vulnerability remediation"""
    OPEN = "open"
    IGNORED = "ignored"
    PATCHED = "patched"
    FIXED = "fixed"

# Pydantic Models
class SnykVulnerability(BaseModel):
    """Model for a Snyk vulnerability"""
    id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    language: str
    package_name: str
    package_version: Optional[str] = None
    vulnerable_versions: List[str] = Field(default_factory=list)
    patched_versions: List[str] = Field(default_factory=list)
    cve: Optional[str] = None
    cvss_score: Optional[float] = None
    exploit_maturity: Optional[str] = None
    is_patchable: bool = False
    is_upgradable: bool = False
    upgrade_path: List[str] = Field(default_factory=list)
    patch_set: Optional[str] = None
    disclosure_time: Optional[datetime] = None
    publication_time: Optional[datetime] = None
    credit: List[str] = Field(default_factory=list)
    semver: Optional[str] = None
    functions: List[str] = Field(default_factory=list)
    from_path: List[str] = Field(default_factory=list)
    identifiers: Dict[str, Any] = Field(default_factory=dict)
    references: List[str] = Field(default_factory=list)

class SnykProject(BaseModel):
    """Model for a Snyk project"""
    id: str
    name: str
    org: str
    created: datetime
    origin: str
    type: str
    is_monitored: bool = False
    total_dependencies: int = 0
    unique_count: int = 0
    open_issues: int = 0
    issues: List[SnykVulnerability] = Field(default_factory=list)

class SnykReport(BaseModel):
    """Model for a complete Snyk security report"""
    schema_version: str = "1.0.0"
    summary: Dict[str, Any] = Field(default_factory=dict)
    projects: List[SnykProject] = Field(default_factory=list)
    scan_date: datetime = Field(default_factory=datetime.utcnow)
    scan_type: SecurityScanType
    total_vulnerabilities: int = 0
    vulnerabilities_by_severity: Dict[VulnerabilitySeverity, int] = Field(default_factory=dict)
    actionable_remediation: Dict[str, Any] = Field(default_factory=dict)
    remediation_summary: Dict[str, Any] = Field(default_factory=dict)

class SecurityScanRequest(BaseModel):
    """Request model for security scanning"""
    project_id: str
    scan_type: SecurityScanType = SecurityScanType.DEPENDENCIES
    target_path: str = "."
    include_dev_dependencies: bool = False
    severity_threshold: VulnerabilitySeverity = VulnerabilitySeverity.LOW
    fail_on_issues: bool = False
    monitor_project: bool = False
    org_id: Optional[str] = None
    snyk_token: Optional[str] = None

class SecurityScanResult(BaseModel):
    """Result model for security scanning"""
    scan_id: str
    project_id: str
    status: str
    snyk_report: Optional[SnykReport] = None
    summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)
    risk_score: float = 0.0
    scan_duration_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class SecurityRecommendation(BaseModel):
    """Model for security recommendations"""
    vulnerability_id: str
    recommendation_type: str  # "upgrade", "patch", "ignore", "review"
    title: str
    description: str
    impact: str
    effort: str  # "low", "medium", "high"
    priority: int  # 1-5
    automated: bool = False
    remediation_command: Optional[str] = None
    additional_info: Optional[str] = None

class SecurityAgent:
    """Agent for security scanning and vulnerability analysis"""
    
    def __init__(self):
        self.tenant_db = TenantDatabase()
        self.github_integration = create_github_integration()
        self.dev_agent_url = os.getenv("DEV_AGENT_URL", "http://dev-agent:8083")
        self.snyk_token = os.getenv("SNYK_TOKEN")
        self.snyk_org = os.getenv("SNYK_ORG")
        
        # Security thresholds
        self.severity_weights = {
            VulnerabilitySeverity.LOW: 1,
            VulnerabilitySeverity.MEDIUM: 3,
            VulnerabilitySeverity.HIGH: 7,
            VulnerabilitySeverity.CRITICAL: 10
        }
        
        # Auto-remediation settings
        self.auto_remediation_enabled = os.getenv("ENABLE_AUTO_REMEDIATION", "false").lower() == "true"
        self.auto_upgrade_enabled = os.getenv("ENABLE_AUTO_UPGRADE", "false").lower() == "true"
        
    async def run_snyk_scan(self, request: SecurityScanRequest) -> SnykReport:
        """Run Snyk security scan"""
        logger.info(f"Starting Snyk scan for project: {request.project_id}")
        
        # Set up Snyk environment
        env = os.environ.copy()
        if request.snyk_token:
            env["SNYK_TOKEN"] = request.snyk_token
        elif self.snyk_token:
            env["SNYK_TOKEN"] = self.snyk_token
        else:
            raise ValueError("Snyk token is required")
            
        if request.org_id:
            env["SNYK_ORG"] = request.org_id
        elif self.snyk_org:
            env["SNYK_ORG"] = self.snyk_org
        
        # Build Snyk command
        snyk_cmd = ["snyk", "test", "--json"]
        
        if request.scan_type == SecurityScanType.DEPENDENCIES:
            snyk_cmd.extend(["--all-projects"])
        elif request.scan_type == SecurityScanType.CODE:
            snyk_cmd.extend(["--code"])
        elif request.scan_type == SecurityScanType.CONTAINER:
            snyk_cmd.extend(["--docker"])
        elif request.scan_type == SecurityScanType.INFRASTRUCTURE:
            snyk_cmd.extend(["--iac"])
            
        if request.include_dev_dependencies:
            snyk_cmd.append("--dev")
            
        if request.severity_threshold:
            snyk_cmd.extend(["--severity-threshold", request.severity_threshold.value])
            
        if request.org_id:
            snyk_cmd.extend(["--org", request.org_id])
            
        snyk_cmd.append(request.target_path)
        
        # Run Snyk scan
        start_time = datetime.utcnow()
        try:
            result = subprocess.run(
                snyk_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            scan_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Parse JSON output
            if result.stdout:
                try:
                    snyk_data = json.loads(result.stdout)
                    snyk_report = self._parse_snyk_output(snyk_data, request.scan_type)
                    logger.info(f"Snyk scan completed in {scan_duration:.0f}ms")
                    return snyk_report
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Snyk JSON output: {e}")
                    logger.error(f"Raw output: {result.stdout}")
                    raise
            else:
                logger.error(f"No output from Snyk scan. stderr: {result.stderr}")
                raise Exception(f"Snyk scan failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Snyk scan timed out")
            raise Exception("Snyk scan timed out after 5 minutes")
        except Exception as e:
            logger.error(f"Snyk scan failed: {e}")
            raise
    
    def _parse_snyk_output(self, snyk_data: Dict[str, Any], scan_type: SecurityScanType) -> SnykReport:
        """Parse Snyk JSON output into structured report"""
        logger.info("Parsing Snyk scan output")
        
        # Handle different output formats
        if isinstance(snyk_data, list):
            # Multiple projects
            projects = []
            for project_data in snyk_data:
                project = self._parse_snyk_project(project_data)
                projects.append(project)
        else:
            # Single project
            project = self._parse_snyk_project(snyk_data)
            projects = [project]
        
        # Calculate summary statistics
        total_vulnerabilities = sum(project.open_issues for project in projects)
        vulnerabilities_by_severity = {}
        
        for severity in VulnerabilitySeverity:
            count = sum(
                len([v for v in project.issues if v.severity == severity]) 
                for project in projects
            )
            vulnerabilities_by_severity[severity] = count
        
        # Generate summary
        summary = {
            "total_projects": len(projects),
            "total_vulnerabilities": total_vulnerabilities,
            "vulnerabilities_by_severity": vulnerabilities_by_severity,
            "scan_type": scan_type.value
        }
        
        # Generate remediation summary
        remediation_summary = self._generate_remediation_summary(projects)
        
        return SnykReport(
            summary=summary,
            projects=projects,
            scan_type=scan_type,
            total_vulnerabilities=total_vulnerabilities,
            vulnerabilities_by_severity=vulnerabilities_by_severity,
            remediation_summary=remediation_summary
        )
    
    def _parse_snyk_project(self, project_data: Dict[str, Any]) -> SnykProject:
        """Parse individual Snyk project data"""
        vulnerabilities = []
        
        # Parse vulnerabilities
        for vuln_data in project_data.get("vulnerabilities", []):
            vulnerability = SnykVulnerability(
                id=vuln_data.get("id", ""),
                title=vuln_data.get("title", ""),
                description=vuln_data.get("description", ""),
                severity=VulnerabilitySeverity(vuln_data.get("severity", "low")),
                language=vuln_data.get("language", ""),
                package_name=vuln_data.get("packageName", ""),
                package_version=vuln_data.get("version", ""),
                vulnerable_versions=vuln_data.get("semver", {}).get("vulnerable", []),
                patched_versions=vuln_data.get("semver", {}).get("patched", []),
                cve=vuln_data.get("identifiers", {}).get("CVE", [None])[0],
                cvss_score=vuln_data.get("cvssScore"),
                exploit_maturity=vuln_data.get("exploitMaturity"),
                is_patchable=vuln_data.get("isPatchable", False),
                is_upgradable=vuln_data.get("isUpgradable", False),
                upgrade_path=vuln_data.get("upgradePath", []),
                patch_set=vuln_data.get("patches", [{}])[0].get("id") if vuln_data.get("patches") else None,
                disclosure_time=self._parse_datetime(vuln_data.get("disclosureTime")),
                publication_time=self._parse_datetime(vuln_data.get("publicationTime")),
                credit=vuln_data.get("credit", []),
                semver=vuln_data.get("semver", {}).get("vulnerable", [""])[0],
                functions=vuln_data.get("functions", []),
                from_path=vuln_data.get("from", []),
                identifiers=vuln_data.get("identifiers", {}),
                references=vuln_data.get("references", [])
            )
            vulnerabilities.append(vulnerability)
        
        return SnykProject(
            id=project_data.get("projectId", str(uuid.uuid4())),
            name=project_data.get("displayTargetFile", "unknown"),
            org=project_data.get("org", ""),
            created=self._parse_datetime(project_data.get("created")) or datetime.utcnow(),
            origin=project_data.get("origin", ""),
            type=project_data.get("packageManager", ""),
            is_monitored=project_data.get("isMonitored", False),
            total_dependencies=project_data.get("dependencyCount", 0),
            unique_count=project_data.get("uniqueCount", 0),
            open_issues=len(vulnerabilities),
            issues=vulnerabilities
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Snyk output"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _generate_remediation_summary(self, projects: List[SnykProject]) -> Dict[str, Any]:
        """Generate remediation summary and recommendations"""
        total_patchable = 0
        total_upgradable = 0
        recommendations = []
        
        for project in projects:
            for vuln in project.issues:
                if vuln.is_patchable:
                    total_patchable += 1
                if vuln.is_upgradable:
                    total_upgradable += 1
                
                # Generate specific recommendation
                recommendation = self._generate_vulnerability_recommendation(vuln)
                recommendations.append(recommendation)
        
        return {
            "total_patchable": total_patchable,
            "total_upgradable": total_upgradable,
            "recommendations": recommendations,
            "auto_fixable": total_patchable + total_upgradable,
            "manual_review_required": len([r for r in recommendations if r.recommendation_type == "review"])
        }
    
    def _generate_vulnerability_recommendation(self, vulnerability: SnykVulnerability) -> SecurityRecommendation:
        """Generate specific recommendation for a vulnerability"""
        if vulnerability.is_upgradable and vulnerability.upgrade_path:
            return SecurityRecommendation(
                vulnerability_id=vulnerability.id,
                recommendation_type="upgrade",
                title=f"Upgrade {vulnerability.package_name}",
                description=f"Upgrade {vulnerability.package_name} to fix {vulnerability.title}",
                impact="Fixes vulnerability",
                effort="low" if len(vulnerability.upgrade_path) <= 2 else "medium",
                priority=self.severity_weights[vulnerability.severity],
                automated=True,
                remediation_command=f"npm install {vulnerability.package_name}@{vulnerability.upgrade_path[-1]}" if vulnerability.upgrade_path else None,
                additional_info=f"Upgrade path: {' -> '.join(vulnerability.upgrade_path)}"
            )
        elif vulnerability.is_patchable:
            return SecurityRecommendation(
                vulnerability_id=vulnerability.id,
                recommendation_type="patch",
                title=f"Apply patch for {vulnerability.package_name}",
                description=f"Apply security patch to fix {vulnerability.title}",
                impact="Fixes vulnerability",
                effort="low",
                priority=self.severity_weights[vulnerability.severity],
                automated=True,
                remediation_command=f"snyk patch {vulnerability.id}",
                additional_info=f"Patch ID: {vulnerability.patch_set}"
            )
        elif vulnerability.severity in [VulnerabilitySeverity.LOW, VulnerabilitySeverity.MEDIUM]:
            return SecurityRecommendation(
                vulnerability_id=vulnerability.id,
                recommendation_type="ignore",
                title=f"Consider ignoring {vulnerability.package_name} vulnerability",
                description=f"Low/Medium severity vulnerability may be acceptable risk",
                impact="Accepts risk",
                effort="low",
                priority=1,
                automated=False,
                remediation_command=f"snyk ignore --id={vulnerability.id}",
                additional_info="Review business impact before ignoring"
            )
        else:
            return SecurityRecommendation(
                vulnerability_id=vulnerability.id,
                recommendation_type="review",
                title=f"Manual review required for {vulnerability.package_name}",
                description=f"High/Critical vulnerability requires manual review: {vulnerability.title}",
                impact="Requires manual assessment",
                effort="high",
                priority=self.severity_weights[vulnerability.severity],
                automated=False,
                additional_info="Consider alternative packages or manual patching"
            )
    
    def calculate_risk_score(self, report: SnykReport) -> float:
        """Calculate risk score based on vulnerabilities"""
        if not report.total_vulnerabilities:
            return 0.0
        
        weighted_score = 0
        for severity, count in report.vulnerabilities_by_severity.items():
            weighted_score += self.severity_weights[severity] * count
        
        # Normalize to 0-100 scale
        max_possible_score = report.total_vulnerabilities * self.severity_weights[VulnerabilitySeverity.CRITICAL]
        risk_score = (weighted_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return min(risk_score, 100.0)
    
    async def analyze_security_report(self, report: SnykReport, tenant_context: TenantContext) -> SecurityScanResult:
        """Analyze security report and generate recommendations"""
        logger.info(f"Analyzing security report with {report.total_vulnerabilities} vulnerabilities")
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(report)
        
        # Generate high-level recommendations
        recommendations = []
        
        if report.vulnerabilities_by_severity.get(VulnerabilitySeverity.CRITICAL, 0) > 0:
            recommendations.append("🚨 CRITICAL vulnerabilities found - immediate action required")
        
        if report.vulnerabilities_by_severity.get(VulnerabilitySeverity.HIGH, 0) > 0:
            recommendations.append("⚠️ HIGH severity vulnerabilities found - review and fix soon")
        
        if report.remediation_summary.get("auto_fixable", 0) > 0:
            recommendations.append(f"✅ {report.remediation_summary['auto_fixable']} vulnerabilities can be auto-fixed")
        
        if report.remediation_summary.get("manual_review_required", 0) > 0:
            recommendations.append(f"👀 {report.remediation_summary['manual_review_required']} vulnerabilities require manual review")
        
        # Generate remediation steps
        remediation_steps = []
        
        if report.remediation_summary.get("total_upgradable", 0) > 0:
            remediation_steps.append("1. Run package updates for upgradable vulnerabilities")
        
        if report.remediation_summary.get("total_patchable", 0) > 0:
            remediation_steps.append("2. Apply security patches where available")
        
        if report.vulnerabilities_by_severity.get(VulnerabilitySeverity.CRITICAL, 0) > 0:
            remediation_steps.append("3. Prioritize fixing CRITICAL vulnerabilities immediately")
        
        remediation_steps.append("4. Review and validate all changes in staging environment")
        
        return SecurityScanResult(
            scan_id=str(uuid.uuid4()),
            project_id="",  # Will be set by caller
            status="completed",
            snyk_report=report,
            summary={
                "total_vulnerabilities": report.total_vulnerabilities,
                "vulnerabilities_by_severity": report.vulnerabilities_by_severity,
                "risk_score": risk_score,
                "auto_fixable": report.remediation_summary.get("auto_fixable", 0),
                "manual_review_required": report.remediation_summary.get("manual_review_required", 0)
            },
            recommendations=recommendations,
            remediation_steps=remediation_steps,
            risk_score=risk_score
        )
    
    async def send_security_feedback_to_dev_agent(self, scan_result: SecurityScanResult, tenant_context: TenantContext):
        """Send security feedback to DevAgent for code improvements"""
        if not scan_result.snyk_report or not scan_result.snyk_report.projects:
            return
        
        logger.info(f"Sending security feedback to DevAgent for project: {scan_result.project_id}")
        
        # Generate security feedback
        feedback = {
            "type": "security_scan_feedback",
            "project_id": scan_result.project_id,
            "scan_id": scan_result.scan_id,
            "risk_score": scan_result.risk_score,
            "summary": scan_result.summary,
            "recommendations": scan_result.recommendations,
            "remediation_steps": scan_result.remediation_steps,
            "critical_vulnerabilities": [],
            "high_vulnerabilities": [],
            "upgrade_recommendations": []
        }
        
        # Extract critical and high vulnerabilities
        for project in scan_result.snyk_report.projects:
            for vuln in project.issues:
                vuln_info = {
                    "id": vuln.id,
                    "title": vuln.title,
                    "package": vuln.package_name,
                    "severity": vuln.severity.value,
                    "is_upgradable": vuln.is_upgradable,
                    "upgrade_path": vuln.upgrade_path
                }
                
                if vuln.severity == VulnerabilitySeverity.CRITICAL:
                    feedback["critical_vulnerabilities"].append(vuln_info)
                elif vuln.severity == VulnerabilitySeverity.HIGH:
                    feedback["high_vulnerabilities"].append(vuln_info)
                
                if vuln.is_upgradable:
                    feedback["upgrade_recommendations"].append({
                        "package": vuln.package_name,
                        "current_version": vuln.package_version,
                        "recommended_version": vuln.upgrade_path[-1] if vuln.upgrade_path else "latest",
                        "vulnerability_id": vuln.id
                    })
        
        # Send to DevAgent
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.dev_agent_url}/api/security-feedback",
                    json=feedback,
                    headers={
                        "x-tenant-id": tenant_context.tenant_id,
                        "x-user-id": tenant_context.user_id or "system",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info("Security feedback sent to DevAgent successfully")
                else:
                    logger.error(f"Failed to send security feedback to DevAgent: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending security feedback to DevAgent: {e}")
    
    async def save_security_scan_result(self, scan_result: SecurityScanResult, tenant_context: TenantContext) -> str:
        """Save security scan result to database"""
        async with self.tenant_db.get_tenant_connection(tenant_context) as conn:
            await conn.execute(
                """
                INSERT INTO security_scan_results (
                    id, tenant_id, project_id, scan_type, status, risk_score,
                    total_vulnerabilities, vulnerabilities_by_severity,
                    recommendations, remediation_steps, snyk_report, 
                    scan_duration_ms, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                scan_result.scan_id,
                tenant_context.tenant_id,
                scan_result.project_id,
                scan_result.snyk_report.scan_type.value if scan_result.snyk_report else "unknown",
                scan_result.status,
                scan_result.risk_score,
                scan_result.snyk_report.total_vulnerabilities if scan_result.snyk_report else 0,
                json.dumps(scan_result.summary.get("vulnerabilities_by_severity", {})),
                json.dumps(scan_result.recommendations),
                json.dumps(scan_result.remediation_steps),
                json.dumps(scan_result.snyk_report.dict() if scan_result.snyk_report else {}),
                scan_result.scan_duration_ms,
                scan_result.created_at
            )
            
            return scan_result.scan_id
    
    async def get_security_scan_results(
        self, 
        tenant_context: TenantContext, 
        project_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get security scan results for tenant"""
        async with self.tenant_db.get_tenant_connection(tenant_context) as conn:
            query = """
                SELECT ssr.*, p.name as project_name
                FROM security_scan_results ssr
                LEFT JOIN projects p ON ssr.project_id = p.id
                WHERE ($1::UUID IS NULL OR ssr.project_id = $1)
                ORDER BY ssr.created_at DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, project_id, limit)
            return [dict(row) for row in rows]

# Initialize SecurityAgent
security_agent = SecurityAgent() 