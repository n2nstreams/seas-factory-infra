#!/usr/bin/env python3
"""
Simple Test Script for Auto-Remediation Module
Tests core functionality without pytest dependencies
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

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

async def test_auto_remediation_engine():
    """Test the auto-remediation engine"""
    print("🧪 Testing Auto-Remediation Engine...")
    
    # Create engine
    tenant_context = MockTenantContext()
    engine = AutoRemediationEngine(tenant_context)
    
    print("✅ Engine initialized successfully")
    
    # Test vulnerability analysis
    print("\n🔍 Testing vulnerability analysis...")
    actions = await engine.analyze_vulnerabilities_for_remediation(MOCK_SCAN_DATA)
    
    assert len(actions) == 3, f"Expected 3 actions, got {len(actions)}"
    print(f"✅ Generated {len(actions)} remediation actions")
    
    # Check action details
    lodash_action = actions[0]
    assert lodash_action.risk_level == "high", f"Expected high risk, got {lodash_action.risk_level}"
    assert lodash_action.package_name == "lodash", f"Expected lodash package, got {lodash_action.package_name}"
    assert lodash_action.remediation_type == RemediationType.PACKAGE_UPGRADE
    assert lodash_action.automated is False  # High severity requires approval
    assert lodash_action.requires_approval is True
    
    print("✅ High severity action correctly configured")
    
    # Test action execution (mocked)
    print("\n⚡ Testing action execution...")
    
    # Create test actions for execution
    test_actions = [
        RemediationAction(
            vulnerability_id="vuln-3",
            package_name="axios",
            current_version="0.21.1",
            target_version="0.21.3",
            remediation_type=RemediationType.PACKAGE_UPGRADE,
            command="npm update axios@0.21.3",
            description="Upgrade axios to fix vulnerability",
            risk_level="low",
            estimated_effort="low",
            automated=True,
            requires_approval=False
        )
    ]
    
    # Mock command execution by patching the method
    original_method = engine._run_remediation_command
    
    async def mock_run_command(command, project_path):
        if "npm update" in command:
            return "axios@0.21.3 installed successfully", None
        return "Command executed", None
    
    engine._run_remediation_command = mock_run_command
    
    try:
        results = await engine.execute_remediation_actions(test_actions, "/tmp/test")
        
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0].success is True, "Expected successful execution"
        assert results[0].status == RemediationStatus.SUCCESS
        assert results[0].rollback_available is True
        
        print("✅ Action execution successful")
        
    finally:
        # Restore original method
        engine._run_remediation_command = original_method
    
    # Test PR creation
    print("\n📝 Testing PR creation...")
    pr_id = await engine.create_remediation_pr(actions, results, "test-project", "main")
    
    # GitHub integration is disabled in test environment, so we expect None
    if pr_id is None:
        print("ℹ️  PR creation skipped (GitHub integration disabled)")
    else:
        assert "PR-" in pr_id, f"Expected PR ID format, got {pr_id}"
        print("✅ PR creation successful")
    
    # Test rollback capability
    print("\n🔄 Testing rollback capability...")
    
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
        timestamp=engine.remediation_history[0].timestamp,
        rollback_available=True
    )
    
    # Mock rollback command execution
    async def mock_rollback_command(command, project_path):
        if "npm install" in command:
            return "lodash@4.17.15 installed successfully", None
        return "Rollback command executed", None
    
    engine._run_remediation_command = mock_rollback_command
    
    try:
        success = await engine.rollback_remediation(result, "/tmp/test")
        
        assert success is True, "Expected successful rollback"
        assert result.status == RemediationStatus.ROLLED_BACK
        assert result.rollback_available is False
        
        print("✅ Rollback capability working")
        
    finally:
        # Restore original method
        engine._run_remediation_command = original_method
    
    # Test summary generation
    print("\n📊 Testing summary generation...")
    summary = engine.get_remediation_summary()
    
    assert summary["total_actions"] > 0, "Expected actions in history"
    assert "success_rate" in summary, "Expected success rate in summary"
    
    print("✅ Summary generation working")
    
    print("\n🎉 All tests passed successfully!")

def test_remediation_models():
    """Test the Pydantic models"""
    print("🧪 Testing Remediation Models...")
    
    # Test RemediationAction
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
    assert action.remediation_type == RemediationType.PACKAGE_UPGRADE
    
    print("✅ RemediationAction model working")
    
    # Test RemediationResult
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
    assert result.rollback_available is True
    
    print("✅ RemediationResult model working")
    
    print("🎉 Model tests passed successfully!")

if __name__ == "__main__":
    print("🚀 Starting Auto-Remediation Tests...\n")
    
    try:
        # Test models first
        test_remediation_models()
        
        # Test async functionality
        asyncio.run(test_auto_remediation_engine())
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Auto-remediation module is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
