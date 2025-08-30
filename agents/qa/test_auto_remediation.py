#!/usr/bin/env python3
"""
Test Auto-Remediation Module - Security Agent Implementation
Comprehensive testing for auto-remediation functionality including:
- Vulnerability analysis and prioritization
- Automatic fix application
- PR creation
- Rollback capabilities
"""

import pytest
from unittest.mock import patch
from datetime import datetime

# Import the modules to test
from auto_remediation import (
    AutoRemediationEngine, 
    RemediationAction, 
    RemediationResult,
    RemediationType, 
    RemediationStatus
)

# Mock tenant context
class MockTenantContext:
    def __init__(self, tenant_id="test-tenant", user_id="test-user"):
        self.tenant_id = tenant_id
        self.user_id = user_id

# Mock GitHub integration
class MockGitHubIntegration:
    def __init__(self):
        self.token = "mock-token"
        self.repo = "test/repo"

# Test data
MOCK_VULNERABILITIES = [
    {
        "id": "vuln-1",
        "title": "SQL Injection in lodash",
        "package_name": "lodash",
        "package_version": "4.17.15",
        "severity": "high",
        "is_upgradable": True,
        "is_patchable": False,
        "upgrade_path": ["4.17.16", "4.17.17"],
        "patched_versions": [],
        "type": "dependency"
    },
    {
        "id": "vuln-2",
        "title": "XSS in moment",
        "package_name": "moment",
        "package_version": "2.29.1",
        "severity": "medium",
        "is_upgradable": True,
        "is_patchable": False,
        "upgrade_path": ["2.29.2", "2.29.3"],
        "patched_versions": [],
        "type": "dependency"
    },
    {
        "id": "vuln-3",
        "title": "Path traversal in axios",
        "package_name": "axios",
        "package_version": "0.21.1",
        "severity": "low",
        "is_upgradable": True,
        "is_patchable": False,
        "upgrade_path": ["0.21.2", "0.21.3"],
        "patched_versions": [],
        "type": "dependency"
    }
]

MOCK_SCAN_DATA = {
    "vulnerabilities": MOCK_VULNERABILITIES,
    "project_id": "test-project",
    "scan_type": "dependencies"
}

class TestAutoRemediationEngine:
    """Test cases for AutoRemediationEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance"""
        tenant_context = MockTenantContext()
        engine = AutoRemediationEngine(tenant_context)
        return engine
    
    @pytest.fixture
    def mock_github_integration(self):
        """Mock GitHub integration"""
        return MockGitHubIntegration()
    
    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine.tenant_context is not None
        assert engine.max_concurrent_remediations == 3
        assert engine.auto_approve_low_risk is True
        assert engine.require_manual_approval_high_risk is True
        assert len(engine.risk_thresholds) == 4
        assert engine.risk_thresholds["critical"] == 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_vulnerabilities_for_remediation(self, engine):
        """Test vulnerability analysis and remediation action generation"""
        actions = await engine.analyze_vulnerabilities_for_remediation(MOCK_SCAN_DATA)
        
        assert len(actions) == 3
        
        # Check that actions are sorted by priority (high severity first)
        assert actions[0].risk_level == "high"
        assert actions[0].package_name == "lodash"
        assert actions[1].risk_level == "medium"
        assert actions[1].package_name == "moment"
        assert actions[2].risk_level == "low"
        assert actions[2].package_name == "axios"
        
        # Check action details
        lodash_action = actions[0]
        assert lodash_action.remediation_type == RemediationType.PACKAGE_UPGRADE
        assert lodash_action.target_version == "4.17.17"
        assert lodash_action.automated is False  # High severity requires approval
        assert lodash_action.requires_approval is True
    
    @pytest.mark.asyncio
    async def test_create_remediation_action(self, engine):
        """Test individual remediation action creation"""
        vuln = MOCK_VULNERABILITIES[0]  # High severity lodash vulnerability
        
        action = await engine._create_remediation_action(vuln)
        
        assert action is not None
        assert action.vulnerability_id == "vuln-1"
        assert action.package_name == "lodash"
        assert action.current_version == "4.17.15"
        assert action.target_version == "4.17.17"
        assert action.remediation_type == RemediationType.PACKAGE_UPGRADE
        assert action.risk_level == "high"
        assert action.estimated_effort == "low"
        assert action.automated is False
        assert action.requires_approval is True
    
    def test_determine_remediation_type(self, engine):
        """Test remediation type determination"""
        # Test upgradable package
        vuln = {"is_upgradable": True, "is_patchable": False}
        assert engine._determine_remediation_type(vuln) == RemediationType.PACKAGE_UPGRADE
        
        # Test patchable package
        vuln = {"is_upgradable": False, "is_patchable": True}
        assert engine._determine_remediation_type(vuln) == RemediationType.SECURITY_PATCH
        
        # Test configuration issue
        vuln = {"type": "configuration"}
        assert engine._determine_remediation_type(vuln) == RemediationType.CONFIGURATION_FIX
        
        # Test dev dependency
        vuln = {"is_dev_dependency": True}
        assert engine._determine_remediation_type(vuln) == RemediationType.DEPENDENCY_REMOVAL
        
        # Test default case
        vuln = {}
        assert engine._determine_remediation_type(vuln) == RemediationType.MANUAL_REVIEW
    
    def test_generate_remediation_command(self, engine):
        """Test remediation command generation"""
        # Test package upgrade
        vuln = {"package_name": "lodash", "upgrade_path": ["4.17.16", "4.17.17"]}
        command = engine._generate_remediation_command(vuln, RemediationType.PACKAGE_UPGRADE)
        assert "npm update lodash@4.17.17" in command
        
        # Test security patch
        vuln = {"id": "patch-123"}
        command = engine._generate_remediation_command(vuln, RemediationType.SECURITY_PATCH)
        assert "snyk patch patch-123" in command
        
        # Test configuration fix
        vuln = {"package_name": "config"}
        command = engine._generate_remediation_command(vuln, RemediationType.CONFIGURATION_FIX)
        assert "Configuration fix for config" in command
        
        # Test dependency removal
        vuln = {"package_name": "unused-pkg"}
        command = engine._generate_remediation_command(vuln, RemediationType.DEPENDENCY_REMOVAL)
        assert "npm uninstall unused-pkg" in command
    
    def test_get_target_version(self, engine):
        """Test target version extraction"""
        # Test upgrade path
        vuln = {"upgrade_path": ["1.0.1", "1.0.2", "1.0.3"]}
        assert engine._get_target_version(vuln) == "1.0.3"
        
        # Test patched versions
        vuln = {"patched_versions": ["2.0.0", "2.0.1"]}
        assert engine._get_target_version(vuln) == "2.0.0"
        
        # Test default
        vuln = {}
        assert engine._get_target_version(vuln) == "latest"
    
    def test_generate_description(self, engine):
        """Test description generation"""
        vuln = {
            "title": "SQL Injection",
            "package_name": "lodash",
            "upgrade_path": ["4.17.16", "4.17.17"]
        }
        
        description = engine._generate_description(vuln, RemediationType.PACKAGE_UPGRADE)
        assert "Upgrade lodash to 4.17.17" in description
        assert "SQL Injection" in description
    
    def test_estimate_effort(self, engine):
        """Test effort estimation"""
        assert engine._estimate_effort(RemediationType.PACKAGE_UPGRADE, {}) == "low"
        assert engine._estimate_effort(RemediationType.SECURITY_PATCH, {}) == "low"
        assert engine._estimate_effort(RemediationType.CONFIGURATION_FIX, {}) == "medium"
        assert engine._estimate_effort(RemediationType.MANUAL_REVIEW, {}) == "high"
    
    def test_can_automate_remediation(self, engine):
        """Test automation capability determination"""
        # High severity should not be automated
        vuln = {"severity": "high"}
        assert engine._can_automate_remediation(vuln, RemediationType.PACKAGE_UPGRADE) is False
        
        # Low severity should be automated
        vuln = {"severity": "low"}
        assert engine._can_automate_remediation(vuln, RemediationType.PACKAGE_UPGRADE) is True
        
        # Manual review types cannot be automated
        assert engine._can_automate_remediation({}, RemediationType.MANUAL_REVIEW) is False
        
        # Configuration fixes cannot be automated
        assert engine._can_automate_remediation({}, RemediationType.CONFIGURATION_FIX) is False
    
    def test_requires_approval(self, engine):
        """Test approval requirement determination"""
        # High severity requires approval
        assert engine._requires_approval("high", RemediationType.PACKAGE_UPGRADE) is True
        
        # Critical severity requires approval
        assert engine._requires_approval("critical", RemediationType.PACKAGE_UPGRADE) is True
        
        # Low severity with auto-approval enabled
        assert engine._requires_approval("low", RemediationType.PACKAGE_UPGRADE) is False
        
        # Manual review types require approval
        assert engine._requires_approval("low", RemediationType.MANUAL_REVIEW) is True
    
    def test_risk_and_effort_scoring(self, engine):
        """Test risk and effort scoring for sorting"""
        assert engine._get_risk_score("low") == 0.1
        assert engine._get_risk_score("medium") == 0.3
        assert engine._get_risk_score("high") == 0.7
        assert engine._get_risk_score("critical") == 1.0
        
        assert engine._get_effort_score("low") == 0.1
        assert engine._get_effort_score("medium") == 0.5
        assert engine._get_effort_score("high") == 1.0
    
    @pytest.mark.asyncio
    async def test_execute_remediation_actions(self, engine):
        """Test remediation action execution"""
        # Create test actions
        actions = [
            RemediationAction(
                vulnerability_id="vuln-1",
                package_name="lodash",
                current_version="4.17.15",
                target_version="4.17.17",
                remediation_type=RemediationType.PACKAGE_UPGRADE,
                command="npm update lodash@4.17.17",
                description="Upgrade lodash",
                risk_level="high",
                estimated_effort="low",
                automated=True,
                requires_approval=False
            )
        ]
        
        # Mock the command execution
        with patch.object(engine, '_run_remediation_command', return_value=("Success", None)):
            results = await engine.execute_remediation_actions(actions, "/tmp/test")
            
            assert len(results) == 1
            assert results[0].success is True
            assert results[0].status == RemediationStatus.SUCCESS
            assert results[0].rollback_available is True
    
    @pytest.mark.asyncio
    async def test_run_remediation_command(self, engine):
        """Test remediation command execution"""
        # Test successful command
        output, error = await engine._run_remediation_command("echo 'success'", "/tmp")
        assert "success" in output
        assert error is None
        
        # Test command that starts with # (comment)
        output, error = await engine._run_remediation_command("# Manual action required", "/tmp")
        assert "Skipped - manual action required" in output
        assert error is None
    
    def test_can_rollback(self, engine):
        """Test rollback capability determination"""
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        # Package upgrades can be rolled back
        assert engine._can_rollback(action) is True
        
        # Security patches can be rolled back
        action.remediation_type = RemediationType.SECURITY_PATCH
        assert engine._can_rollback(action) is True
        
        # Configuration fixes cannot be rolled back
        action.remediation_type = RemediationType.CONFIGURATION_FIX
        assert engine._can_rollback(action) is False
    
    @pytest.mark.asyncio
    async def test_create_remediation_pr(self, engine):
        """Test PR creation"""
        actions = [
            RemediationAction(
                vulnerability_id="vuln-1",
                package_name="lodash",
                current_version="4.17.15",
                target_version="4.17.17",
                remediation_type=RemediationType.PACKAGE_UPGRADE,
                command="npm update lodash@4.17.17",
                description="Upgrade lodash",
                risk_level="high",
                estimated_effort="low",
                automated=True,
                requires_approval=False
            )
        ]
        
        results = [
            RemediationResult(
                action=actions[0],
                status=RemediationStatus.SUCCESS,
                success=True,
                output="Success",
                execution_time=1.0,
                timestamp=datetime.now(),
                rollback_available=True
            )
        ]
        
        pr_id = await engine.create_remediation_pr(actions, results, "test-project", "main")
        assert pr_id is not None
        assert "PR-" in pr_id
    
    def test_generate_pr_body(self, engine):
        """Test PR body generation"""
        actions = [
            RemediationAction(
                vulnerability_id="vuln-1",
                package_name="lodash",
                current_version="4.17.15",
                target_version="4.17.17",
                remediation_type=RemediationType.PACKAGE_UPGRADE,
                command="npm update lodash@4.17.17",
                description="Upgrade lodash",
                risk_level="high",
                estimated_effort="low",
                automated=True,
                requires_approval=False
            )
        ]
        
        results = [
            RemediationResult(
                action=actions[0],
                status=RemediationStatus.SUCCESS,
                success=True,
                output="Success",
                execution_time=1.0,
                timestamp=datetime.now(),
                rollback_available=True
            )
        ]
        
        body = engine._generate_pr_body(actions, results)
        
        assert "🔒 Security Auto-Remediation" in body
        assert "📊 Summary" in body
        assert "✅ Successful Remediations" in body
        assert "lodash" in body
        assert "🔄 Rollback Available" in body
    
    @pytest.mark.asyncio
    async def test_rollback_remediation(self, engine):
        """Test remediation rollback"""
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        result = RemediationResult(
            action=action,
            status=RemediationStatus.SUCCESS,
            success=True,
            output="Success",
            execution_time=1.0,
            timestamp=datetime.now(),
            rollback_available=True
        )
        
        # Mock the command execution
        with patch.object(engine, '_run_remediation_command', return_value=("Rollback success", None)):
            success = await engine.rollback_remediation(result, "/tmp/test")
            assert success is True
            assert result.status == RemediationStatus.ROLLED_BACK
            assert result.rollback_available is False
    
    def test_generate_rollback_command(self, engine):
        """Test rollback command generation"""
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        # Test package upgrade rollback
        rollback_cmd = engine._generate_rollback_command(action)
        assert "npm install lodash@4.17.15" in rollback_cmd
        
        # Test security patch rollback
        action.remediation_type = RemediationType.SECURITY_PATCH
        rollback_cmd = engine._generate_rollback_command(action)
        assert "manual intervention required" in rollback_cmd
    
    def test_get_remediation_summary(self, engine):
        """Test remediation summary generation"""
        # Add some test results to history
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        result = RemediationResult(
            action=action,
            status=RemediationStatus.SUCCESS,
            success=True,
            output="Success",
            execution_time=1.0,
            timestamp=datetime.now(),
            rollback_available=True
        )
        
        engine.remediation_history.append(result)
        
        summary = engine.get_remediation_summary()
        
        assert summary["total_actions"] == 1
        assert summary["successful"] == 1
        assert summary["failed"] == 0
        assert summary["success_rate"] == 100.0
        assert summary["last_activity"] is not None

class TestRemediationAction:
    """Test cases for RemediationAction model"""
    
    def test_remediation_action_creation(self):
        """Test RemediationAction model creation"""
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash to fix vulnerability",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        assert action.vulnerability_id == "vuln-1"
        assert action.package_name == "lodash"
        assert action.current_version == "4.17.15"
        assert action.target_version == "4.17.17"
        assert action.remediation_type == RemediationType.PACKAGE_UPGRADE
        assert action.command == "npm update lodash@4.17.17"
        assert action.description == "Upgrade lodash to fix vulnerability"
        assert action.risk_level == "high"
        assert action.estimated_effort == "low"
        assert action.automated is True
        assert action.requires_approval is False

class TestRemediationResult:
    """Test cases for RemediationResult model"""
    
    def test_remediation_result_creation(self):
        """Test RemediationResult model creation"""
        action = RemediationAction(
            vulnerability_id="vuln-1",
            package_name="lodash",
            current_version="4.17.15",
            target_version="4.17.17",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update lodash@4.17.17",
            description="Upgrade lodash",
            risk_level="high",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
        
        result = RemediationResult(
            action=action,
            status=RemediationStatus.SUCCESS,
            success=True,
            output="Successfully updated lodash",
            error_message=None,
            execution_time=2.5,
            timestamp=datetime.now(),
            rollback_available=True
        )
        
        assert result.action == action
        assert result.status == RemediationStatus.SUCCESS
        assert result.success is True
        assert result.output == "Successfully updated lodash"
        assert result.error_message is None
        assert result.execution_time == 2.5
        assert result.rollback_available is True

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
