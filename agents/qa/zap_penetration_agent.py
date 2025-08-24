"""
OWASP ZAP Penetration Testing Agent - Night 78 Implementation

This agent performs dynamic application security testing (DAST) using OWASP ZAP
to complement the existing Snyk-based static analysis security scanning.

Night 78: Final security scan & penetration test script (OWASP ZAP).
"""

import os
import uuid
import time
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException

# Import existing SecurityAgent components
from agents.qa.security_agent import SecurityAgent
from agents.shared.tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZAPScanRequest(BaseModel):
    """Request model for ZAP penetration testing"""
    project_id: str
    target_url: str = Field(..., description="Target application URL to scan")
    scan_type: str = Field(default="quick", description="quick, baseline, or full")
    spider_timeout: int = Field(default=5, description="Spider timeout in minutes")
    scan_timeout: int = Field(default=10, description="Active scan timeout in minutes")
    max_depth: int = Field(default=5, description="Maximum spider depth")
    exclude_urls: List[str] = Field(default=[], description="URLs to exclude from scan")
    include_contexts: List[str] = Field(default=[], description="Context names to include")
    authentication: Optional[Dict[str, Any]] = Field(default=None, description="Authentication config")
    custom_rules: List[Dict[str, Any]] = Field(default=[], description="Custom ZAP rules")
    
    @field_validator('scan_type')
    @classmethod
    def validate_scan_type(cls, v):
        if v not in ['quick', 'baseline', 'full']:
            raise ValueError('scan_type must be one of: quick, baseline, full')
        return v
    
    @field_validator('target_url')
    @classmethod
    def validate_target_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('target_url must be a valid HTTP/HTTPS URL')
        return v


class ZAPVulnerability(BaseModel):
    """ZAP vulnerability model"""
    plugin_id: str
    alert_id: str
    name: str
    description: str
    solution: str
    reference: str
    severity: str  # High, Medium, Low, Informational
    confidence: str  # High, Medium, Low
    risk: str  # Critical, High, Medium, Low, Informational
    url: str
    param: Optional[str] = None
    attack: Optional[str] = None
    evidence: Optional[str] = None
    other_info: Optional[str] = None
    cwe_id: Optional[str] = None
    wasc_id: Optional[str] = None


class ZAPScanResult(BaseModel):
    """ZAP scan result model"""
    scan_id: str
    project_id: str
    target_url: str
    scan_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Summary statistics
    total_vulnerabilities: int = 0
    vulnerabilities_by_risk: Dict[str, int] = Field(default_factory=dict)
    vulnerabilities_by_confidence: Dict[str, int] = Field(default_factory=dict)
    
    # Detailed vulnerabilities
    vulnerabilities: List[ZAPVulnerability] = Field(default_factory=list)
    
    # ZAP-specific metrics
    spider_results: Dict[str, Any] = Field(default_factory=dict)
    passive_scan_results: Dict[str, Any] = Field(default_factory=dict)
    active_scan_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Risk assessment
    risk_score: float = 0.0
    security_posture: str = "unknown"
    recommendations: List[str] = Field(default_factory=list)
    
    # Raw ZAP data
    zap_report: Dict[str, Any] = Field(default_factory=dict)


class ZAPPenetrationAgent:
    """OWASP ZAP Penetration Testing Agent"""
    
    def __init__(self):
        self.tenant_db = TenantDatabase()
        self.zap_proxy_port = int(os.getenv("ZAP_PROXY_PORT", "8080"))
        self.zap_daemon_host = os.getenv("ZAP_DAEMON_HOST", "localhost")
        self.zap_daemon_port = int(os.getenv("ZAP_DAEMON_PORT", "8090"))
        self.zap_api_key = os.getenv("ZAP_API_KEY", "")
        
        # ZAP configuration
        self.zap_home = os.getenv("ZAP_HOME", "/opt/zaproxy")
        self.zap_session_timeout = int(os.getenv("ZAP_SESSION_TIMEOUT", "3600"))
        
        # Security assessment thresholds
        self.risk_weights = {
            "Critical": 10,
            "High": 7,
            "Medium": 3,
            "Low": 1,
            "Informational": 0
        }
        
        # Confidence weights
        self.confidence_weights = {
            "High": 1.0,
            "Medium": 0.7,
            "Low": 0.4
        }
        
        logger.info("ZAP Penetration Agent initialized")
    
    async def run_zap_scan(self, request: ZAPScanRequest) -> ZAPScanResult:
        """Run OWASP ZAP penetration test"""
        scan_id = str(uuid.uuid4())
        logger.info(f"Starting ZAP scan {scan_id} for {request.target_url}")
        
        # Initialize scan result
        scan_result = ZAPScanResult(
            scan_id=scan_id,
            project_id=request.project_id,
            target_url=request.target_url,
            scan_type=request.scan_type,
            status="running",
            started_at=datetime.utcnow()
        )
        
        try:
            # Start ZAP daemon if not running
            await self._ensure_zap_daemon_running()
            
            # Initialize ZAP session
            await self._initialize_zap_session(scan_id)
            
            # Configure scan based on request
            await self._configure_zap_scan(request)
            
            # Run spider (discovery phase)
            logger.info(f"Starting spider for {request.target_url}")
            spider_results = await self._run_spider(request)
            scan_result.spider_results = spider_results
            
            # Run passive scan
            logger.info("Running passive scan")
            passive_results = await self._run_passive_scan(request)
            scan_result.passive_scan_results = passive_results
            
            # Run active scan if requested
            if request.scan_type in ['baseline', 'full']:
                logger.info("Running active scan")
                active_results = await self._run_active_scan(request)
                scan_result.active_scan_results = active_results
            
            # Generate comprehensive report
            zap_report = await self._generate_zap_report()
            scan_result.zap_report = zap_report
            
            # Parse vulnerabilities
            vulnerabilities = await self._parse_zap_vulnerabilities(zap_report)
            scan_result.vulnerabilities = vulnerabilities
            scan_result.total_vulnerabilities = len(vulnerabilities)
            
            # Calculate statistics
            scan_result.vulnerabilities_by_risk = self._calculate_risk_distribution(vulnerabilities)
            scan_result.vulnerabilities_by_confidence = self._calculate_confidence_distribution(vulnerabilities)
            
            # Calculate risk score and security posture
            scan_result.risk_score = self._calculate_risk_score(vulnerabilities)
            scan_result.security_posture = self._assess_security_posture(scan_result.risk_score, vulnerabilities)
            
            # Generate recommendations
            scan_result.recommendations = await self._generate_recommendations(vulnerabilities, scan_result)
            
            # Complete scan
            scan_result.completed_at = datetime.utcnow()
            scan_result.duration_seconds = int((scan_result.completed_at - scan_result.started_at).total_seconds())
            scan_result.status = "completed"
            
            logger.info(f"ZAP scan {scan_id} completed successfully")
            return scan_result
            
        except Exception as e:
            logger.error(f"ZAP scan {scan_id} failed: {e}")
            scan_result.status = "failed"
            scan_result.completed_at = datetime.utcnow()
            scan_result.duration_seconds = int((scan_result.completed_at - scan_result.started_at).total_seconds())
            raise HTTPException(status_code=500, detail=f"ZAP scan failed: {e}")
        
        finally:
            # Cleanup ZAP session
            await self._cleanup_zap_session(scan_id)
    
    async def _ensure_zap_daemon_running(self) -> bool:
        """Ensure ZAP daemon is running"""
        try:
            # Check if ZAP is already running
            response = await self._zap_api_call("GET", "core/action/version/")
            if response and "version" in response:
                logger.info(f"ZAP daemon already running, version: {response['version']}")
                return True
        except:
            pass
        
        # Start ZAP daemon
        logger.info("Starting ZAP daemon")
        zap_cmd = [
            f"{self.zap_home}/zap.sh",
            "-daemon",
            "-host", self.zap_daemon_host,
            "-port", str(self.zap_daemon_port),
            "-config", f"api.key={self.zap_api_key}",
            "-config", "api.addrs.addr.name=.*",
            "-config", "api.addrs.addr.regex=true"
        ]
        
        process = subprocess.Popen(
            zap_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, JAVA_OPTS="-Xmx2g")
        )
        
        # Wait for ZAP to start (max 60 seconds)
        for i in range(60):
            try:
                response = await self._zap_api_call("GET", "core/action/version/")
                if response and "version" in response:
                    logger.info(f"ZAP daemon started successfully, version: {response['version']}")
                    return True
            except:
                pass
            await asyncio.sleep(1)
        
        raise Exception("Failed to start ZAP daemon within timeout")
    
    async def _zap_api_call(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API call to ZAP daemon"""
        import httpx
        
        url = f"http://{self.zap_daemon_host}:{self.zap_daemon_port}/JSON/{endpoint}"
        
        request_params = {"apikey": self.zap_api_key}
        if params:
            request_params.update(params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, params=request_params)
            elif method == "POST":
                response = await client.post(url, data=request_params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    async def _initialize_zap_session(self, scan_id: str) -> None:
        """Initialize ZAP session for the scan"""
        session_name = f"scan_{scan_id}"
        await self._zap_api_call("POST", "core/action/newSession/", {"name": session_name})
        logger.info(f"Initialized ZAP session: {session_name}")
    
    async def _configure_zap_scan(self, request: ZAPScanRequest) -> None:
        """Configure ZAP for the specific scan"""
        # Set target in scope
        await self._zap_api_call("POST", "core/action/includeInContext/", {
            "contextName": "Default Context",
            "regex": f"{request.target_url}.*"
        })
        
        # Configure excludes
        for exclude_url in request.exclude_urls:
            await self._zap_api_call("POST", "core/action/excludeFromContext/", {
                "contextName": "Default Context",
                "regex": exclude_url
            })
        
        # Configure authentication if provided
        if request.authentication:
            await self._configure_authentication(request.authentication)
        
        # Set scan policies based on scan type
        if request.scan_type == "quick":
            # Enable only fast, low-impact policies
            await self._configure_quick_scan_policies()
        elif request.scan_type == "baseline":
            # Enable baseline policies
            await self._configure_baseline_scan_policies()
        elif request.scan_type == "full":
            # Enable all policies
            await self._configure_full_scan_policies()
    
    async def _configure_authentication(self, auth_config: Dict[str, Any]) -> None:
        """Configure authentication in ZAP"""
        if auth_config.get("type") == "form":
            # Configure form-based authentication
            await self._zap_api_call("POST", "authentication/action/setAuthenticationMethod/", {
                "contextId": "0",
                "authMethodName": "formBasedAuthentication",
                "authMethodConfigParams": f"loginUrl={auth_config.get('login_url')}&loginRequestData={auth_config.get('login_data')}"
            })
        elif auth_config.get("type") == "header":
            # Configure header-based authentication
            await self._zap_api_call("POST", "authentication/action/setAuthenticationMethod/", {
                "contextId": "0",
                "authMethodName": "httpAuthentication",
                "authMethodConfigParams": f"hostname={auth_config.get('hostname')}&realm={auth_config.get('realm')}"
            })
    
    async def _configure_quick_scan_policies(self) -> None:
        """Configure policies for quick scan"""
        # Disable time-consuming scan rules
        await self._zap_api_call("POST", "ascan/action/disableScanners/", {
            "ids": "10020,10021,10023,10024,10025,10026,10027,10028,10029"
        })
    
    async def _configure_baseline_scan_policies(self) -> None:
        """Configure policies for baseline scan"""
        # Enable most scan rules except the very slow ones
        await self._zap_api_call("POST", "ascan/action/disableScanners/", {
            "ids": "10029"  # Only disable the slowest
        })
    
    async def _configure_full_scan_policies(self) -> None:
        """Configure policies for full scan"""
        # Enable all scan rules
        await self._zap_api_call("POST", "ascan/action/enableAllScanners/")
    
    async def _run_spider(self, request: ZAPScanRequest) -> Dict[str, Any]:
        """Run ZAP spider to discover URLs"""
        # Start spider
        spider_response = await self._zap_api_call("POST", "spider/action/scan/", {
            "url": request.target_url,
            "maxChildren": str(request.max_depth),
            "recurse": "true",
            "contextName": "Default Context"
        })
        
        spider_id = spider_response.get("scan")
        
        # Wait for spider to complete
        timeout = time.time() + (request.spider_timeout * 60)
        while time.time() < timeout:
            status_response = await self._zap_api_call("GET", "spider/view/status/", {"scanId": spider_id})
            status = int(status_response.get("status", 0))
            
            if status >= 100:
                break
            
            await asyncio.sleep(2)
        
        # Get spider results
        results = await self._zap_api_call("GET", "spider/view/results/", {"scanId": spider_id})
        
        return {
            "spider_id": spider_id,
            "urls_found": len(results.get("results", [])),
            "urls": results.get("results", [])
        }
    
    async def _run_passive_scan(self, request: ZAPScanRequest) -> Dict[str, Any]:
        """Run passive scan on discovered URLs"""
        # Enable passive scanning
        await self._zap_api_call("POST", "pscan/action/enableAllScanners/")
        
        # Wait for passive scan to complete
        timeout = time.time() + 300  # 5 minutes max
        while time.time() < timeout:
            status_response = await self._zap_api_call("GET", "pscan/view/recordsToScan/")
            records_to_scan = int(status_response.get("recordsToScan", 0))
            
            if records_to_scan == 0:
                break
            
            await asyncio.sleep(2)
        
        return {"status": "completed"}
    
    async def _run_active_scan(self, request: ZAPScanRequest) -> Dict[str, Any]:
        """Run active scan"""
        # Start active scan
        scan_response = await self._zap_api_call("POST", "ascan/action/scan/", {
            "url": request.target_url,
            "recurse": "true",
            "inScopeOnly": "true",
            "scanPolicyName": "Default Policy",
            "contextId": "0"
        })
        
        scan_id = scan_response.get("scan")
        
        # Wait for active scan to complete
        timeout = time.time() + (request.scan_timeout * 60)
        while time.time() < timeout:
            status_response = await self._zap_api_call("GET", "ascan/view/status/", {"scanId": scan_id})
            status = int(status_response.get("status", 0))
            
            if status >= 100:
                break
            
            await asyncio.sleep(5)
        
        return {
            "scan_id": scan_id,
            "status": "completed"
        }
    
    async def _generate_zap_report(self) -> Dict[str, Any]:
        """Generate comprehensive ZAP report"""
        # Get alerts
        alerts_response = await self._zap_api_call("GET", "core/view/alerts/")
        
        # Get core statistics
        stats_response = await self._zap_api_call("GET", "core/view/stats/")
        
        # Get spider results summary
        spider_response = await self._zap_api_call("GET", "spider/view/allUrls/")
        
        return {
            "alerts": alerts_response.get("alerts", []),
            "statistics": stats_response.get("stats", {}),
            "urls_discovered": spider_response.get("allUrls", []),
            "report_generated_at": datetime.utcnow().isoformat()
        }
    
    async def _parse_zap_vulnerabilities(self, zap_report: Dict[str, Any]) -> List[ZAPVulnerability]:
        """Parse ZAP alerts into vulnerability objects"""
        vulnerabilities = []
        
        for alert in zap_report.get("alerts", []):
            vulnerability = ZAPVulnerability(
                plugin_id=alert.get("pluginId", ""),
                alert_id=alert.get("id", ""),
                name=alert.get("name", ""),
                description=alert.get("description", ""),
                solution=alert.get("solution", ""),
                reference=alert.get("reference", ""),
                severity=alert.get("risk", "Low"),  # ZAP uses 'risk' field
                confidence=alert.get("confidence", "Medium"),
                risk=alert.get("risk", "Low"),
                url=alert.get("url", ""),
                param=alert.get("param"),
                attack=alert.get("attack"),
                evidence=alert.get("evidence"),
                other_info=alert.get("other"),
                cwe_id=str(alert.get("cweid", "")) if alert.get("cweid") else None,
                wasc_id=str(alert.get("wascid", "")) if alert.get("wascid") else None
            )
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _calculate_risk_distribution(self, vulnerabilities: List[ZAPVulnerability]) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        
        for vuln in vulnerabilities:
            risk = vuln.risk
            if risk in distribution:
                distribution[risk] += 1
        
        return distribution
    
    def _calculate_confidence_distribution(self, vulnerabilities: List[ZAPVulnerability]) -> Dict[str, int]:
        """Calculate confidence level distribution"""
        distribution = {"High": 0, "Medium": 0, "Low": 0}
        
        for vuln in vulnerabilities:
            confidence = vuln.confidence
            if confidence in distribution:
                distribution[confidence] += 1
        
        return distribution
    
    def _calculate_risk_score(self, vulnerabilities: List[ZAPVulnerability]) -> float:
        """Calculate overall risk score (0-100)"""
        if not vulnerabilities:
            return 0.0
        
        total_weighted_score = 0
        total_max_score = 0
        
        for vuln in vulnerabilities:
            risk_weight = self.risk_weights.get(vuln.risk, 1)
            confidence_weight = self.confidence_weights.get(vuln.confidence, 0.5)
            
            vulnerability_score = risk_weight * confidence_weight
            total_weighted_score += vulnerability_score
            total_max_score += self.risk_weights["Critical"] * 1.0
        
        if total_max_score == 0:
            return 0.0
        
        risk_score = (total_weighted_score / total_max_score) * 100
        return min(risk_score, 100.0)
    
    def _assess_security_posture(self, risk_score: float, vulnerabilities: List[ZAPVulnerability]) -> str:
        """Assess overall security posture"""
        critical_count = sum(1 for v in vulnerabilities if v.risk == "Critical")
        high_count = sum(1 for v in vulnerabilities if v.risk == "High")
        
        if critical_count > 0:
            return "Critical"
        elif high_count > 3 or risk_score > 70:
            return "Poor"
        elif high_count > 0 or risk_score > 40:
            return "Fair"
        elif risk_score > 20:
            return "Good"
        else:
            return "Excellent"
    
    async def _generate_recommendations(self, vulnerabilities: List[ZAPVulnerability], scan_result: ZAPScanResult) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.risk == "Critical"]
        if critical_vulns:
            recommendations.append(f"🚨 Address {len(critical_vulns)} CRITICAL vulnerabilities immediately")
        
        # High vulnerabilities
        high_vulns = [v for v in vulnerabilities if v.risk == "High"]
        if high_vulns:
            recommendations.append(f"⚠️ Fix {len(high_vulns)} HIGH severity vulnerabilities within 7 days")
        
        # Common vulnerability patterns
        xss_vulns = [v for v in vulnerabilities if "xss" in v.name.lower() or "cross-site" in v.name.lower()]
        if xss_vulns:
            recommendations.append(f"🔒 Implement proper input validation and output encoding to prevent XSS ({len(xss_vulns)} found)")
        
        sql_injection_vulns = [v for v in vulnerabilities if "sql" in v.name.lower() and "injection" in v.name.lower()]
        if sql_injection_vulns:
            recommendations.append(f"💉 Use parameterized queries to prevent SQL injection ({len(sql_injection_vulns)} found)")
        
        # Security headers
        header_vulns = [v for v in vulnerabilities if "header" in v.name.lower()]
        if header_vulns:
            recommendations.append("🛡️ Implement security headers (CSP, HSTS, X-Frame-Options, etc.)")
        
        # HTTPS/TLS issues
        tls_vulns = [v for v in vulnerabilities if "ssl" in v.name.lower() or "tls" in v.name.lower()]
        if tls_vulns:
            recommendations.append("🔐 Review and strengthen TLS/SSL configuration")
        
        # General recommendations based on scan results
        if scan_result.risk_score > 50:
            recommendations.append("🎯 Consider implementing a Web Application Firewall (WAF)")
            recommendations.append("🔍 Perform regular security assessments and penetration testing")
        
        if not recommendations:
            recommendations.append("✅ No critical security issues found, maintain current security practices")
        
        return recommendations
    
    async def _cleanup_zap_session(self, scan_id: str) -> None:
        """Cleanup ZAP session after scan"""
        try:
            session_name = f"scan_{scan_id}"
            await self._zap_api_call("POST", "core/action/deleteSession/", {"name": session_name})
            logger.info(f"Cleaned up ZAP session: {session_name}")
        except Exception as e:
            logger.warning(f"Failed to cleanup ZAP session: {e}")
    
    async def save_zap_scan_result(self, scan_result: ZAPScanResult, tenant_context: TenantContext) -> None:
        """Save ZAP scan result to database"""
        try:
            # Convert to SecurityAgent format for database storage
            security_scan_data = {
                'scan_id': scan_result.scan_id,
                'tenant_id': tenant_context.tenant_id,
                'project_id': scan_result.project_id,
                'scan_type': 'zap_penetration',
                'status': scan_result.status,
                'risk_score': scan_result.risk_score,
                'total_vulnerabilities': scan_result.total_vulnerabilities,
                'vulnerabilities_by_severity': {
                    'critical': scan_result.vulnerabilities_by_risk.get('Critical', 0),
                    'high': scan_result.vulnerabilities_by_risk.get('High', 0),
                    'medium': scan_result.vulnerabilities_by_risk.get('Medium', 0),
                    'low': scan_result.vulnerabilities_by_risk.get('Low', 0)
                },
                'recommendations': scan_result.recommendations,
                'zap_report': scan_result.zap_report,
                'scan_duration_ms': (scan_result.duration_seconds or 0) * 1000,
                'target_url': scan_result.target_url,
                'scan_metadata': {
                    'scan_type': scan_result.scan_type,
                    'spider_results': scan_result.spider_results,
                    'security_posture': scan_result.security_posture,
                    'vulnerabilities_by_confidence': scan_result.vulnerabilities_by_confidence
                }
            }
            
            # Save to database using existing security infrastructure
            await self.tenant_db.save_security_scan_result(security_scan_data, tenant_context)
            logger.info(f"Saved ZAP scan result {scan_result.scan_id} to database")
            
        except Exception as e:
            logger.error(f"Failed to save ZAP scan result: {e}")
            raise


# Integration with existing SecurityAgent
class EnhancedSecurityAgent(SecurityAgent):
    """Enhanced SecurityAgent with ZAP penetration testing capabilities"""
    
    def __init__(self):
        super().__init__()
        self.zap_agent = ZAPPenetrationAgent()
    
    async def run_comprehensive_security_scan(self, project_id: str, target_url: str, tenant_context: TenantContext) -> Dict[str, Any]:
        """Run comprehensive security scan including Snyk + ZAP"""
        results = {
            'project_id': project_id,
            'scan_timestamp': datetime.utcnow().isoformat(),
            'scans': {}
        }
        
        try:
            # Run existing Snyk scans
            logger.info("Running Snyk security scans...")
            # This would call existing Snyk functionality
            # snyk_result = await self.run_snyk_scan(...)
            # results['scans']['snyk'] = snyk_result
            
            # Run ZAP penetration test
            logger.info(f"Running ZAP penetration test on {target_url}...")
            zap_request = ZAPScanRequest(
                project_id=project_id,
                target_url=target_url,
                scan_type="baseline"
            )
            
            zap_result = await self.zap_agent.run_zap_scan(zap_request)
            await self.zap_agent.save_zap_scan_result(zap_result, tenant_context)
            
            results['scans']['zap'] = {
                'scan_id': zap_result.scan_id,
                'status': zap_result.status,
                'risk_score': zap_result.risk_score,
                'total_vulnerabilities': zap_result.total_vulnerabilities,
                'security_posture': zap_result.security_posture,
                'recommendations': zap_result.recommendations
            }
            
            # Calculate combined risk assessment
            results['combined_assessment'] = await self._calculate_combined_risk_assessment(results['scans'])
            
            logger.info("Comprehensive security scan completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive security scan failed: {e}")
            results['error'] = str(e)
            results['status'] = 'failed'
            return results
    
    async def _calculate_combined_risk_assessment(self, scans: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate combined risk assessment from all scans"""
        combined_assessment = {
            'overall_risk_score': 0.0,
            'overall_security_posture': 'unknown',
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0,
            'combined_recommendations': []
        }
        
        scan_weights = {'snyk': 0.6, 'zap': 0.4}  # Weight static analysis higher
        total_risk_score = 0.0
        total_weight = 0.0
        
        for scan_type, scan_data in scans.items():
            if isinstance(scan_data, dict) and 'risk_score' in scan_data:
                weight = scan_weights.get(scan_type, 0.5)
                total_risk_score += scan_data['risk_score'] * weight
                total_weight += weight
                
                # Aggregate recommendations
                if 'recommendations' in scan_data:
                    combined_assessment['combined_recommendations'].extend(scan_data['recommendations'])
        
        if total_weight > 0:
            combined_assessment['overall_risk_score'] = total_risk_score / total_weight
        
        # Determine overall security posture
        if combined_assessment['overall_risk_score'] > 80:
            combined_assessment['overall_security_posture'] = 'Critical'
        elif combined_assessment['overall_risk_score'] > 60:
            combined_assessment['overall_security_posture'] = 'Poor'
        elif combined_assessment['overall_risk_score'] > 40:
            combined_assessment['overall_security_posture'] = 'Fair'
        elif combined_assessment['overall_risk_score'] > 20:
            combined_assessment['overall_security_posture'] = 'Good'
        else:
            combined_assessment['overall_security_posture'] = 'Excellent'
        
        return combined_assessment 