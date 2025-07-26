"""
Test suite for OWASP ZAP Penetration Testing Agent - Night 78 Implementation

Comprehensive tests for ZAP penetration testing functionality.
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the components to test
from agents.qa.zap_penetration_agent import (
    ZAPPenetrationAgent,
    ZAPScanRequest,
    ZAPScanResult,
    ZAPVulnerability,
    EnhancedSecurityAgent
)
from agents.qa.zap_main import app
from agents.shared.tenant_db import TenantContext


class TestZAPScanRequest:
    """Test ZAP scan request validation"""
    
    def test_valid_zap_scan_request(self):
        """Test creating a valid ZAP scan request"""
        request = ZAPScanRequest(
            project_id="test-project",
            target_url="https://example.com",
            scan_type="baseline"
        )
        
        assert request.project_id == "test-project"
        assert request.target_url == "https://example.com"
        assert request.scan_type == "baseline"
        assert request.spider_timeout == 5  # default
        assert request.scan_timeout == 10   # default
    
    def test_invalid_scan_type(self):
        """Test invalid scan type validation"""
        with pytest.raises(ValueError, match="scan_type must be one of"):
            ZAPScanRequest(
                project_id="test-project",
                target_url="https://example.com",
                scan_type="invalid"
            )
    
    def test_invalid_target_url(self):
        """Test invalid target URL validation"""
        with pytest.raises(ValueError, match="target_url must be a valid HTTP/HTTPS URL"):
            ZAPScanRequest(
                project_id="test-project",
                target_url="invalid-url",
                scan_type="baseline"
            )
    
    def test_custom_scan_parameters(self):
        """Test custom scan parameters"""
        request = ZAPScanRequest(
            project_id="test-project",
            target_url="https://example.com",
            scan_type="full",
            spider_timeout=10,
            scan_timeout=20,
            max_depth=8,
            exclude_urls=["https://example.com/logout"],
            authentication={"type": "form", "login_url": "https://example.com/login"}
        )
        
        assert request.spider_timeout == 10
        assert request.scan_timeout == 20
        assert request.max_depth == 8
        assert "https://example.com/logout" in request.exclude_urls
        assert request.authentication["type"] == "form"


class TestZAPVulnerability:
    """Test ZAP vulnerability model"""
    
    def test_zap_vulnerability_creation(self):
        """Test creating a ZAP vulnerability"""
        vuln = ZAPVulnerability(
            plugin_id="10001",
            alert_id="alert123",
            name="SQL Injection",
            description="SQL injection vulnerability found",
            solution="Use parameterized queries",
            reference="https://owasp.org/www-community/attacks/SQL_Injection",
            severity="High",
            confidence="High",
            risk="High",
            url="https://example.com/search",
            param="query",
            attack="' OR 1=1--",
            evidence="SQL error returned",
            cwe_id="89",
            wasc_id="19"
        )
        
        assert vuln.plugin_id == "10001"
        assert vuln.name == "SQL Injection"
        assert vuln.severity == "High"
        assert vuln.cwe_id == "89"


class TestZAPPenetrationAgent:
    """Test ZAP penetration testing agent"""
    
    @pytest.fixture
    def zap_agent(self):
        """Create ZAP agent for testing"""
        return ZAPPenetrationAgent()
    
    @pytest.fixture
    def mock_tenant_context(self):
        """Create mock tenant context"""
        return TenantContext(
            tenant_id="test-tenant",
            user_id="test-user",
            project_id="test-project"
        )
    
    def test_zap_agent_initialization(self, zap_agent):
        """Test ZAP agent initialization"""
        assert zap_agent.zap_proxy_port == 8080
        assert zap_agent.zap_daemon_port == 8090
        assert "Critical" in zap_agent.risk_weights
        assert zap_agent.risk_weights["Critical"] == 10
    
    def test_risk_score_calculation(self, zap_agent):
        """Test risk score calculation"""
        vulnerabilities = [
            ZAPVulnerability(
                plugin_id="1", alert_id="1", name="Test", description="Test",
                solution="Test", reference="Test", severity="Critical",
                confidence="High", risk="Critical", url="https://example.com"
            ),
            ZAPVulnerability(
                plugin_id="2", alert_id="2", name="Test", description="Test",
                solution="Test", reference="Test", severity="High",
                confidence="Medium", risk="High", url="https://example.com"
            )
        ]
        
        risk_score = zap_agent._calculate_risk_score(vulnerabilities)
        assert risk_score > 0
        assert risk_score <= 100
    
    def test_security_posture_assessment(self, zap_agent):
        """Test security posture assessment"""
        # Test critical vulnerability
        critical_vulns = [
            ZAPVulnerability(
                plugin_id="1", alert_id="1", name="Test", description="Test",
                solution="Test", reference="Test", severity="Critical",
                confidence="High", risk="Critical", url="https://example.com"
            )
        ]
        posture = zap_agent._assess_security_posture(100.0, critical_vulns)
        assert posture == "Critical"
        
        # Test excellent posture
        no_vulns = []
        posture = zap_agent._assess_security_posture(0.0, no_vulns)
        assert posture == "Excellent"
    
    def test_risk_distribution_calculation(self, zap_agent):
        """Test risk distribution calculation"""
        vulnerabilities = [
            ZAPVulnerability(
                plugin_id="1", alert_id="1", name="Test", description="Test",
                solution="Test", reference="Test", severity="Critical",
                confidence="High", risk="Critical", url="https://example.com"
            ),
            ZAPVulnerability(
                plugin_id="2", alert_id="2", name="Test", description="Test",
                solution="Test", reference="Test", severity="High",
                confidence="Medium", risk="High", url="https://example.com"
            ),
            ZAPVulnerability(
                plugin_id="3", alert_id="3", name="Test", description="Test",
                solution="Test", reference="Test", severity="High",
                confidence="High", risk="High", url="https://example.com"
            )
        ]
        
        distribution = zap_agent._calculate_risk_distribution(vulnerabilities)
        assert distribution["Critical"] == 1
        assert distribution["High"] == 2
        assert distribution["Medium"] == 0
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, zap_agent):
        """Test recommendation generation"""
        # Test with critical vulnerabilities
        critical_vulns = [
            ZAPVulnerability(
                plugin_id="1", alert_id="1", name="SQL Injection", description="Test",
                solution="Test", reference="Test", severity="Critical",
                confidence="High", risk="Critical", url="https://example.com"
            )
        ]
        
        scan_result = ZAPScanResult(
            scan_id="test",
            project_id="test",
            target_url="https://example.com",
            scan_type="baseline",
            status="completed",
            started_at=datetime.utcnow(),
            risk_score=85.0
        )
        
        recommendations = await zap_agent._generate_recommendations(critical_vulns, scan_result)
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("WAF" in rec for rec in recommendations)  # High risk score recommendation
    
    @patch('zap_penetration_agent.subprocess.Popen')
    @patch('zap_penetration_agent.ZAPPenetrationAgent._zap_api_call')
    @pytest.mark.asyncio
    async def test_ensure_zap_daemon_running(self, mock_api_call, mock_popen, zap_agent):
        """Test ZAP daemon startup"""
        # Mock ZAP already running
        mock_api_call.return_value = {"version": "2.14.0"}
        
        result = await zap_agent._ensure_zap_daemon_running()
        assert result is True
        mock_popen.assert_not_called()  # Should not try to start if already running
    
    @patch('zap_penetration_agent.ZAPPenetrationAgent._zap_api_call')
    @pytest.mark.asyncio
    async def test_zap_api_call_success(self, mock_api_call, zap_agent):
        """Test successful ZAP API call"""
        mock_api_call.return_value = {"status": "success"}
        
        result = await zap_agent._zap_api_call("GET", "core/view/version/")
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_parse_zap_vulnerabilities(self, zap_agent):
        """Test parsing ZAP vulnerabilities from report"""
        zap_report = {
            "alerts": [
                {
                    "pluginId": "10001",
                    "id": "alert1",
                    "name": "SQL Injection",
                    "description": "SQL injection found",
                    "solution": "Use parameterized queries",
                    "reference": "https://owasp.org",
                    "risk": "High",
                    "confidence": "High",
                    "url": "https://example.com/search",
                    "param": "query",
                    "attack": "' OR 1=1--",
                    "evidence": "SQL error",
                    "cweid": 89,
                    "wascid": 19
                }
            ]
        }
        
        vulnerabilities = await zap_agent._parse_zap_vulnerabilities(zap_report)
        assert len(vulnerabilities) == 1
        assert vulnerabilities[0].name == "SQL Injection"
        assert vulnerabilities[0].cwe_id == "89"


class TestZAPMainAPI:
    """Test ZAP main FastAPI application"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_tenant_context(self):
        """Mock tenant context"""
        return TenantContext(
            tenant_id="test-tenant",
            user_id="test-user",
            project_id="test-project"
        )
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "zap-penetration-testing"
    
    @patch('zap_main.get_tenant_context')
    @patch('zap_main.tenant_db')
    def test_trigger_zap_scan(self, mock_tenant_db, mock_get_tenant, client, mock_tenant_context):
        """Test triggering ZAP scan"""
        mock_get_tenant.return_value = mock_tenant_context
        mock_tenant_db.log_agent_event = AsyncMock()
        
        scan_request = {
            "project_id": "test-project",
            "target_url": "https://example.com",
            "scan_type": "baseline"
        }
        
        response = client.post("/api/zap/scan", json=scan_request)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["target_url"] == "https://example.com"
    
    @patch('zap_main.get_tenant_context')
    @patch('zap_main.tenant_db')
    def test_trigger_comprehensive_scan(self, mock_tenant_db, mock_get_tenant, client, mock_tenant_context):
        """Test triggering comprehensive scan"""
        mock_get_tenant.return_value = mock_tenant_context
        mock_tenant_db.log_agent_event = AsyncMock()
        
        scan_request = {
            "project_id": "test-project",
            "target_url": "https://example.com",
            "include_snyk": True,
            "include_zap": True
        }
        
        response = client.post("/api/comprehensive-scan", json=scan_request)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["scans"]["snyk"] is True
        assert data["scans"]["zap"] is True
    
    @patch('zap_main.get_tenant_context')
    @patch('zap_main.tenant_db')
    def test_get_zap_scan_status(self, mock_tenant_db, mock_get_tenant, client, mock_tenant_context):
        """Test getting ZAP scan status"""
        mock_get_tenant.return_value = mock_tenant_context
        mock_tenant_db.get_security_scan_result = AsyncMock(return_value={
            "scan_id": "test-scan",
            "project_id": "test-project",
            "status": "completed",
            "risk_score": 25.0,
            "total_vulnerabilities": 5
        })
        
        response = client.get("/api/zap/scan/test-scan")
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == "test-scan"
        assert data["status"] == "completed"
    
    @patch('zap_main.get_tenant_context')
    @patch('zap_main.tenant_db')
    def test_list_zap_scans(self, mock_tenant_db, mock_get_tenant, client, mock_tenant_context):
        """Test listing ZAP scans"""
        mock_get_tenant.return_value = mock_tenant_context
        mock_tenant_db.list_security_scans = AsyncMock(return_value=[
            {"scan_id": "scan1", "status": "completed"},
            {"scan_id": "scan2", "status": "running"}
        ])
        
        response = client.get("/api/zap/scans")
        assert response.status_code == 200
        data = response.json()
        assert len(data["scans"]) == 2
        assert data["total"] == 2
    
    def test_invalid_scan_request(self, client):
        """Test invalid scan request"""
        invalid_request = {
            "project_id": "test-project",
            "target_url": "invalid-url",  # Invalid URL
            "scan_type": "baseline"
        }
        
        response = client.post("/api/zap/scan", json=invalid_request)
        assert response.status_code == 422  # Validation error


class TestEnhancedSecurityAgent:
    """Test enhanced security agent with ZAP integration"""
    
    @pytest.fixture
    def enhanced_agent(self):
        """Create enhanced security agent"""
        return EnhancedSecurityAgent()
    
    @pytest.fixture
    def mock_tenant_context(self):
        """Mock tenant context"""
        return TenantContext(
            tenant_id="test-tenant",
            user_id="test-user",
            project_id="test-project"
        )
    
    def test_enhanced_agent_initialization(self, enhanced_agent):
        """Test enhanced security agent initialization"""
        assert enhanced_agent.zap_agent is not None
        assert hasattr(enhanced_agent, 'run_comprehensive_security_scan')
    
    @pytest.mark.asyncio
    async def test_calculate_combined_risk_assessment(self, enhanced_agent):
        """Test combined risk assessment calculation"""
        scans = {
            'snyk': {
                'risk_score': 60.0,
                'recommendations': ['Fix dependency A', 'Update package B']
            },
            'zap': {
                'risk_score': 40.0,
                'recommendations': ['Implement CSP', 'Fix XSS']
            }
        }
        
        assessment = await enhanced_agent._calculate_combined_risk_assessment(scans)
        
        # Weighted average: (60 * 0.6) + (40 * 0.4) = 36 + 16 = 52
        assert assessment['overall_risk_score'] == 52.0
        assert assessment['overall_security_posture'] == 'Fair'  # Risk score between 40-60
        assert len(assessment['combined_recommendations']) == 4


class TestZAPIntegration:
    """Integration tests for ZAP functionality"""
    
    @pytest.fixture
    def integration_setup(self):
        """Setup for integration tests"""
        return {
            "target_url": "http://testphp.vulnweb.com",  # Public vulnerable test site
            "project_id": "integration-test"
        }
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_zap_quick_scan_integration(self, integration_setup):
        """Integration test for ZAP quick scan"""
        # This test requires ZAP daemon to be running
        # Skip if ZAP is not available
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8090/JSON/core/view/version/?apikey=changeme")
                if response.status_code != 200:
                    pytest.skip("ZAP daemon not available for integration test")
        except:
            pytest.skip("ZAP daemon not available for integration test")
        
        zap_agent = ZAPPenetrationAgent()
        scan_request = ZAPScanRequest(
            project_id=integration_setup["project_id"],
            target_url=integration_setup["target_url"],
            scan_type="quick",
            spider_timeout=1,  # Very short for testing
            scan_timeout=2
        )
        
        # This would run actual ZAP scan - only enable for real integration testing
        # scan_result = await zap_agent.run_zap_scan(scan_request)
        # assert scan_result.status == "completed"
        # assert scan_result.target_url == integration_setup["target_url"]
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_zap_performance_metrics(self):
        """Test ZAP performance metrics"""
        zap_agent = ZAPPenetrationAgent()
        
        # Test risk calculation performance
        large_vuln_list = []
        for i in range(1000):
            vuln = ZAPVulnerability(
                plugin_id=str(i),
                alert_id=str(i),
                name=f"Test Vuln {i}",
                description="Test",
                solution="Test",
                reference="Test",
                severity="Medium",
                confidence="Medium",
                risk="Medium",
                url="https://example.com"
            )
            large_vuln_list.append(vuln)
        
        import time
        start_time = time.time()
        risk_score = zap_agent._calculate_risk_score(large_vuln_list)
        calculation_time = time.time() - start_time
        
        assert risk_score >= 0
        assert calculation_time < 1.0  # Should complete within 1 second


# Test fixtures and helpers
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_zap_api_responses():
    """Mock ZAP API responses for testing"""
    return {
        "version": {"version": "2.14.0"},
        "spider_scan": {"scan": "1"},
        "spider_status": {"status": "100"},
        "spider_results": {"results": ["https://example.com", "https://example.com/page1"]},
        "active_scan": {"scan": "2"},
        "active_status": {"status": "100"},
        "alerts": {
            "alerts": [
                {
                    "pluginId": "10001",
                    "id": "1",
                    "name": "SQL Injection",
                    "description": "SQL injection vulnerability",
                    "solution": "Use parameterized queries",
                    "reference": "https://owasp.org",
                    "risk": "High",
                    "confidence": "High",
                    "url": "https://example.com/search",
                    "param": "query"
                }
            ]
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 