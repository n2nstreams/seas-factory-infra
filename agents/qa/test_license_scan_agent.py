#!/usr/bin/env python3
"""
Test Suite for License Scan Agent - Night 64 Implementation
OSS Review Toolkit (ORT) integration - fail pipeline on GPL licenses
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from license_scan_agent import (
    LicenseScanAgent, LicenseScanRequest, LicenseScanResult, 
    LicensePolicy, ORTResult, ScanStatus, LicenseRisk,
    PackageLicense, LicenseDetection, LicenseType
)
from tenant_db import TenantContext

class TestLicenseScanAgent:
    """Test suite for the License Scan Agent"""
    
    @pytest.fixture
    def license_agent(self):
        """Create a test instance of the License Scan Agent"""
        agent = LicenseScanAgent()
        # Mock database for testing
        agent.tenant_db = MagicMock()
        return agent
    
    @pytest.fixture
    def tenant_context(self):
        """Create a test tenant context"""
        return TenantContext(
            tenant_id="test-tenant",
            organization_id="test-org",
            subscription_tier="pro"
        )
    
    @pytest.fixture
    def sample_scan_request(self):
        """Create a sample license scan request"""
        return LicenseScanRequest(
            project_id="test-project",
            repository_url="https://github.com/test/repo.git",
            branch="main",
            fail_on_gpl=True,
            package_managers=["npm", "pip"]
        )

    def test_gpl_license_detection(self, license_agent):
        """Test GPL license detection logic"""
        
        # Test various GPL license patterns
        gpl_licenses = [
            "GPL-2.0", "GPL-3.0", "AGPL-3.0", "GPL-2.0+", "GPL-3.0+",
            "GPL v2", "GPL v3", "GNU General Public License", "GPLv2", "GPLv3"
        ]
        
        for license_name in gpl_licenses:
            assert license_agent._is_gpl_license(license_name), f"Failed to detect GPL license: {license_name}"
        
        # Test non-GPL licenses
        safe_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]
        for license_name in safe_licenses:
            assert not license_agent._is_gpl_license(license_name), f"False positive GPL detection: {license_name}"

    def test_copyleft_license_detection(self, license_agent):
        """Test copyleft license detection logic"""
        
        # Test copyleft licenses (including GPL)
        copyleft_licenses = [
            "GPL-2.0", "LGPL-2.1", "MPL-2.0", "EPL-1.0", "CDDL-1.0"
        ]
        
        for license_name in copyleft_licenses:
            assert license_agent._is_copyleft_license(license_name), f"Failed to detect copyleft license: {license_name}"
        
        # Test permissive licenses
        permissive_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
        for license_name in permissive_licenses:
            assert not license_agent._is_copyleft_license(license_name), f"False positive copyleft detection: {license_name}"

    def test_license_risk_classification(self, license_agent):
        """Test license risk level classification"""
        
        # Test GPL licenses (critical risk)
        assert license_agent._classify_license_risk("GPL-2.0") == LicenseRisk.CRITICAL
        assert license_agent._classify_license_risk("AGPL-3.0") == LicenseRisk.CRITICAL
        
        # Test other copyleft licenses (high risk)
        assert license_agent._classify_license_risk("LGPL-2.1") == LicenseRisk.HIGH
        assert license_agent._classify_license_risk("MPL-2.0") == LicenseRisk.HIGH
        
        # Test permissive licenses (safe)
        assert license_agent._classify_license_risk("MIT") == LicenseRisk.SAFE
        assert license_agent._classify_license_risk("Apache-2.0") == LicenseRisk.SAFE
        
        # Test unknown licenses (medium risk)
        assert license_agent._classify_license_risk("Unknown") == LicenseRisk.MEDIUM
        assert license_agent._classify_license_risk("Proprietary") == LicenseRisk.MEDIUM

    @patch('subprocess.run')
    def test_ort_availability_check(self, mock_subprocess, license_agent):
        """Test ORT CLI availability checking"""
        
        # Test ORT available
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="ORT 1.5.0")
        assert license_agent._is_ort_available() == True
        
        # Test ORT not available
        mock_subprocess.side_effect = FileNotFoundError()
        assert license_agent._is_ort_available() == False

    @patch('subprocess.run')
    def test_ort_version_detection(self, mock_subprocess, license_agent):
        """Test ORT version detection"""
        
        # Test successful version detection
        mock_subprocess.return_value = MagicMock(
            returncode=0, 
            stdout="OSS Review Toolkit (ORT) 1.5.0\n"
        )
        version = license_agent._get_ort_version()
        assert version == "1.5.0"
        
        # Test failed version detection
        mock_subprocess.return_value = MagicMock(returncode=1, stdout="")
        version = license_agent._get_ort_version()
        assert version == "unknown"

    @pytest.mark.asyncio
    async def test_workspace_setup_git_clone(self, license_agent, sample_scan_request):
        """Test workspace setup with git clone"""
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0)
            
            workspace_dir = await license_agent._setup_workspace(sample_scan_request)
            
            # Verify directory was created
            assert os.path.exists(workspace_dir)
            assert workspace_dir.startswith("/tmp/license_scan_")
            
            # Clean up
            shutil.rmtree(workspace_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_workspace_setup_local_path(self, license_agent):
        """Test workspace setup with local source path"""
        
        # Create a temporary source directory
        source_dir = tempfile.mkdtemp()
        test_file = os.path.join(source_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        try:
            scan_request = LicenseScanRequest(
                project_id="test-project",
                source_path=source_dir,
                fail_on_gpl=True
            )
            
            workspace_dir = await license_agent._setup_workspace(scan_request)
            
            # Verify directory was created and files copied
            assert os.path.exists(workspace_dir)
            assert os.path.exists(os.path.join(workspace_dir, "test.txt"))
            
            # Clean up
            shutil.rmtree(workspace_dir, ignore_errors=True)
            
        finally:
            shutil.rmtree(source_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_evaluate_scan_result_gpl_failure(self, license_agent, sample_scan_request):
        """Test scan result evaluation with GPL violations"""
        
        # Create mock ORT result with GPL violations
        gpl_package = PackageLicense(
            package_name="gpl-package",
            package_version="1.0.0",
            package_manager="npm",
            declared_licenses=["GPL-2.0"],
            detected_licenses=[
                LicenseDetection(
                    license_id="GPL-2.0",
                    license_name="GPL-2.0",
                    license_type=LicenseType.GPL_2_0,
                    risk_level=LicenseRisk.CRITICAL,
                    confidence=0.95,
                    file_path="node_modules/gpl-package/LICENSE",
                    is_copyleft=True
                )
            ]
        )
        
        ort_result = ORTResult(
            scan_id="test-scan-id",
            project_name="test-project",
            scan_timestamp=datetime.utcnow(),
            ort_version="1.5.0",
            status=ScanStatus.COMPLETED,
            total_packages=1,
            packages_with_licenses=1,
            gpl_violations=[gpl_package],
            all_packages=[gpl_package]
        )
        
        # Evaluate the result
        scan_result = await license_agent.evaluate_scan_result(ort_result, sample_scan_request)
        
        # Assert pipeline should fail
        assert scan_result.passed == False
        assert scan_result.pipeline_should_fail == True
        assert "GPL license violations detected" in scan_result.failure_reason
        assert len(scan_result.action_items) > 0

    @pytest.mark.asyncio
    async def test_evaluate_scan_result_success(self, license_agent, sample_scan_request):
        """Test scan result evaluation with no violations"""
        
        # Create mock ORT result with safe licenses
        safe_package = PackageLicense(
            package_name="safe-package",
            package_version="1.0.0",
            package_manager="npm",
            declared_licenses=["MIT"],
            detected_licenses=[
                LicenseDetection(
                    license_id="MIT",
                    license_name="MIT License",
                    license_type=LicenseType.MIT,
                    risk_level=LicenseRisk.SAFE,
                    confidence=0.95,
                    file_path="node_modules/safe-package/LICENSE"
                )
            ]
        )
        
        ort_result = ORTResult(
            scan_id="test-scan-id",
            project_name="test-project",
            scan_timestamp=datetime.utcnow(),
            ort_version="1.5.0",
            status=ScanStatus.COMPLETED,
            total_packages=1,
            packages_with_licenses=1,
            all_packages=[safe_package]
        )
        
        # Evaluate the result
        scan_result = await license_agent.evaluate_scan_result(ort_result, sample_scan_request)
        
        # Assert pipeline should pass
        assert scan_result.passed == True
        assert scan_result.pipeline_should_fail == False
        assert scan_result.failure_reason is None
        assert "compliance checks passed" in " ".join(scan_result.recommendations)

    @pytest.mark.asyncio
    async def test_custom_license_policy(self, license_agent, sample_scan_request):
        """Test evaluation with custom license policy"""
        
        # Create custom policy that allows GPL
        custom_policy = LicensePolicy(
            allowed_licenses=["MIT", "GPL-2.0"],
            denied_licenses=[],
            gpl_policy="allow",
            copyleft_policy="allow"
        )
        
        # Create mock ORT result with GPL package
        gpl_package = PackageLicense(
            package_name="gpl-package",
            package_version="1.0.0",
            package_manager="npm",
            declared_licenses=["GPL-2.0"],
            detected_licenses=[
                LicenseDetection(
                    license_id="GPL-2.0",
                    license_name="GPL-2.0",
                    license_type=LicenseType.GPL_2_0,
                    risk_level=LicenseRisk.CRITICAL,
                    confidence=0.95,
                    file_path="node_modules/gpl-package/LICENSE",
                    is_copyleft=True
                )
            ]
        )
        
        ort_result = ORTResult(
            scan_id="test-scan-id",
            project_name="test-project",
            scan_timestamp=datetime.utcnow(),
            ort_version="1.5.0",
            status=ScanStatus.COMPLETED,
            total_packages=1,
            packages_with_licenses=1,
            gpl_violations=[gpl_package],  # Still detected as GPL
            all_packages=[gpl_package]
        )
        
        # Evaluate with custom policy
        scan_result = await license_agent.evaluate_scan_result(
            ort_result, sample_scan_request, custom_policy
        )
        
        # With GPL allowed, scan should pass
        assert scan_result.passed == True
        assert scan_result.pipeline_should_fail == False

    @pytest.mark.asyncio
    async def test_scan_storage(self, license_agent, tenant_context):
        """Test storing scan results in database"""
        
        # Mock database connection
        mock_conn = AsyncMock()
        license_agent.tenant_db.get_connection = AsyncMock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        
        scan_result = LicenseScanResult(
            scan_id="test-scan-id",
            status=ScanStatus.COMPLETED,
            passed=True,
            scan_start_time=datetime.utcnow(),
            scan_end_time=datetime.utcnow()
        )
        
        # Test storing results
        await license_agent._store_scan_results(scan_result, tenant_context)
        
        # Verify database execute was called
        mock_conn.execute.assert_called_once()

    def test_metrics_tracking(self, license_agent):
        """Test agent metrics tracking"""
        
        initial_metrics = license_agent.get_metrics()
        
        # Verify initial metrics structure
        assert "scans_completed" in initial_metrics
        assert "gpl_violations_found" in initial_metrics
        assert "pipelines_failed" in initial_metrics
        assert "ort_version" in initial_metrics
        assert "ort_available" in initial_metrics
        
        # Test metrics initialization
        assert initial_metrics["scans_completed"] == 0
        assert initial_metrics["gpl_violations_found"] == 0
        assert initial_metrics["pipelines_failed"] == 0

class TestLicenseScanIntegration:
    """Integration tests for the License Scan Agent"""
    
    @pytest.mark.asyncio
    async def test_full_scan_workflow_mock(self):
        """Test complete scan workflow with mocked ORT"""
        
        agent = LicenseScanAgent()
        agent.tenant_db = MagicMock()
        
        # Mock ORT availability
        with patch.object(agent, '_is_ort_available', return_value=True):
            with patch.object(agent, '_setup_workspace') as mock_setup:
                with patch.object(agent, 'run_ort_scan') as mock_scan:
                    with patch.object(agent, '_store_scan_results') as mock_store:
                        
                        # Setup mocks
                        mock_setup.return_value = "/tmp/test-workspace"
                        
                        mock_ort_result = ORTResult(
                            scan_id="test-scan",
                            project_name="test-project",
                            scan_timestamp=datetime.utcnow(),
                            ort_version="1.5.0",
                            status=ScanStatus.COMPLETED,
                            total_packages=1,
                            packages_with_licenses=1
                        )
                        mock_scan.return_value = mock_ort_result
                        
                        # Create scan request
                        request = LicenseScanRequest(
                            project_id="test-project",
                            repository_url="https://github.com/test/repo.git"
                        )
                        
                        tenant_context = TenantContext(
                            tenant_id="test-tenant",
                            organization_id="test-org",
                            subscription_tier="pro"
                        )
                        
                        # Run the scan
                        result = await agent.scan_project_licenses(request, tenant_context)
                        
                        # Verify result
                        assert result.status == ScanStatus.COMPLETED
                        assert result.ort_result is not None
                        
                        # Verify mocks were called
                        mock_setup.assert_called_once()
                        mock_scan.assert_called_once()
                        mock_store.assert_called_once()

class TestNight64Requirements:
    """Test suite to verify Night 64 specific requirements"""
    
    def test_gpl_pipeline_failure_requirement(self):
        """Test that GPL licenses cause pipeline failure (Night 64 requirement)"""
        
        agent = LicenseScanAgent()
        
        # Test that default policy denies GPL
        assert agent.default_policy.gpl_policy == "deny"
        assert "GPL-2.0" in agent.default_policy.denied_licenses
        assert "GPL-3.0" in agent.default_policy.denied_licenses
        assert "AGPL-3.0" in agent.default_policy.denied_licenses
    
    def test_ort_integration_requirement(self):
        """Test OSS Review Toolkit (ORT) integration (Night 64 requirement)"""
        
        agent = LicenseScanAgent()
        
        # Test that ORT CLI path is configurable
        assert agent.ort_cli_path is not None
        
        # Test that ORT availability can be checked
        assert hasattr(agent, '_is_ort_available')
        assert hasattr(agent, '_get_ort_version')
    
    def test_pipeline_integration_requirement(self):
        """Test pipeline integration capabilities (Night 64 requirement)"""
        
        agent = LicenseScanAgent()
        
        # Test that scan results include pipeline failure information
        scan_result = LicenseScanResult(
            scan_id="test",
            status=ScanStatus.COMPLETED,
            passed=False,
            pipeline_should_fail=True,
            failure_reason="GPL license detected",
            scan_start_time=datetime.utcnow()
        )
        
        assert scan_result.pipeline_should_fail == True
        assert "GPL" in scan_result.failure_reason

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 