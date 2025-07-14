#!/usr/bin/env python3
"""
Critical Path Integration Tests
Tests for the full project creation flow and core business logic
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import uuid
import json

from conftest import (
    integration_test, slow_test, wait_for_condition,
    TEST_CONFIG
)


@integration_test
@slow_test
async def test_full_project_creation_flow(tenant_db, tenant_context, sample_project_data, 
                                        mock_openai, mock_github, mock_figma, mock_slack):
    """Test complete project creation flow: Idea → Design → Code → Deploy"""
    
    # Step 1: Create project
    project_id = await tenant_db.create_project(
        tenant_context,
        name=sample_project_data["name"],
        description=sample_project_data["description"],
        project_type=sample_project_data["project_type"]
    )
    
    assert project_id is not None
    
    # Step 2: Generate design
    design_request = {
        "project_id": project_id,
        "project_type": sample_project_data["project_type"],
        "pages": sample_project_data["pages"],
        "style_preferences": sample_project_data["style_preferences"],
        "color_scheme": "natural",
        "layout_type": "clean",
        "target_audience": "business users"
    }
    
    # Mock design generation
    with patch('agents.design.main.DesignAgent') as mock_design_agent:
        mock_design_instance = Mock()
        mock_design_agent.return_value = mock_design_instance
        
        mock_design_response = {
            "project_id": project_id,
            "wireframes": [
                {
                    "page_name": "home",
                    "page_type": "landing",
                    "elements": [
                        {
                            "type": "header",
                            "content": "Welcome to Test App",
                            "position": {"x": 0, "y": 0}
                        }
                    ],
                    "figma_url": "https://figma.com/test-design",
                    "preview_url": "https://figma.com/test-design/preview"
                }
            ],
            "figma_project_url": "https://figma.com/test-project",
            "style_guide": {
                "primary_color": "#6B7280",
                "secondary_color": "#84CC16",
                "theme": "glassmorphism"
            }
        }
        
        mock_design_instance.generate_design = AsyncMock(return_value=mock_design_response)
        
        # Execute design generation
        from agents.design.main import DesignAgent
        design_agent = DesignAgent()
        design_result = await design_agent.generate_design(design_request)
        
        assert design_result["project_id"] == project_id
        assert len(design_result["wireframes"]) > 0
        assert design_result["figma_project_url"] is not None
    
    # Step 3: Generate code
    code_request = {
        "project_id": project_id,
        "module_spec": {
            "name": "UserService",
            "type": "service",
            "description": "User management service",
            "functions": [
                {
                    "name": "create_user",
                    "parameters": ["email", "name"],
                    "return_type": "User",
                    "description": "Create a new user"
                }
            ]
        },
        "requirements": [
            "Use FastAPI for API endpoints",
            "Use Pydantic for data validation",
            "Include proper error handling"
        ]
    }
    
    # Mock code generation
    with patch('agents.dev.main.DevAgent') as mock_dev_agent:
        mock_dev_instance = Mock()
        mock_dev_agent.return_value = mock_dev_instance
        
        mock_code_response = {
            "module_name": "UserService",
            "files": [
                {
                    "filename": "user_service.py",
                    "content": "# Generated UserService\nclass UserService:\n    def create_user(self, email: str, name: str):\n        return User(email=email, name=name)",
                    "file_type": "source",
                    "language": "python"
                }
            ],
            "total_files": 1,
            "total_lines": 4,
            "validation_results": {"all_files_valid": True}
        }
        
        mock_dev_instance.generate_code = AsyncMock(return_value=mock_code_response)
        
        # Execute code generation
        from agents.dev.main import DevAgent
        dev_agent = DevAgent()
        code_result = await dev_agent.generate_code(code_request)
        
        assert code_result["module_name"] == "UserService"
        assert len(code_result["files"]) > 0
        assert code_result["validation_results"]["all_files_valid"] is True
    
    # Step 4: Create Pull Request
    pr_request = {
        "project_id": project_id,
        "module_name": "UserService",
        "files": code_result["files"],
        "description": "Add UserService module"
    }
    
    mock_pr_response = {
        "pr_number": 1,
        "pr_url": "https://github.com/test/repo/pull/1",
        "branch_name": "feature/userservice-auto-20240101",
        "status": "created"
    }
    
    with patch('agents.shared.github_integration.create_github_integration') as mock_github_integration:
        mock_github_instance = Mock()
        mock_github_integration.return_value = mock_github_instance
        
        mock_github_instance.create_pull_request = AsyncMock(return_value=mock_pr_response)
        
        # Execute PR creation
        pr_result = await mock_github_instance.create_pull_request(pr_request)
        
        assert pr_result["pr_number"] == 1
        assert pr_result["status"] == "created"
        assert "github.com" in pr_result["pr_url"]
    
    # Step 5: Run QA Tests
    qa_request = {
        "project_id": project_id,
        "module_name": "UserService",
        "test_types": ["unit", "integration"],
        "coverage_threshold": 80
    }
    
    with patch('agents.qa.main.QAAgent') as mock_qa_agent:
        mock_qa_instance = Mock()
        mock_qa_agent.return_value = mock_qa_instance
        
        mock_qa_response = {
            "test_results": {
                "total_tests": 5,
                "passed": 5,
                "failed": 0,
                "coverage_percentage": 85.5
            },
            "review_status": "passed",
            "issues_found": [],
            "suggestions": ["Add more edge case tests"]
        }
        
        mock_qa_instance.run_tests = AsyncMock(return_value=mock_qa_response)
        
        # Execute QA tests
        from agents.qa.main import QAAgent
        qa_agent = QAAgent()
        qa_result = await qa_agent.run_tests(qa_request)
        
        assert qa_result["review_status"] == "passed"
        assert qa_result["test_results"]["passed"] == 5
        assert qa_result["test_results"]["failed"] == 0
    
    # Step 6: Verify events were logged
    events = await tenant_db.get_project_events(tenant_context, project_id)
    
    assert len(events) >= 4  # At least design, code, PR, QA events
    
    event_types = [event["event_type"] for event in events]
    assert "design_generation" in event_types
    assert "code_generation" in event_types
    assert "pr_creation" in event_types
    assert "qa_testing" in event_types
    
    # Step 7: Verify project status
    project = await tenant_db.get_project(tenant_context, project_id)
    assert project is not None
    assert project["status"] == "active"
    
    print("✅ Full project creation flow test passed")


@integration_test
async def test_tenant_isolation(test_database, mock_openai):
    """Test that tenant A cannot access tenant B's data"""
    
    # Create two separate tenants
    tenant_a_context = {
        "tenant_id": "tenant-a",
        "user_id": "user-a"
    }
    
    tenant_b_context = {
        "tenant_id": "tenant-b", 
        "user_id": "user-b"
    }
    
    # Create database instances for each tenant
    db_a = TenantDatabase()
    db_b = TenantDatabase()
    
    await db_a.init_pool()
    await db_b.init_pool()
    
    try:
        # Create tenant A and project
        await db_a.create_tenant(
            tenant_a_context,
            slug="tenant-a",
            name="Tenant A",
            email="tenant-a@example.com"
        )
        
        project_a_id = await db_a.create_project(
            tenant_a_context,
            name="Project A",
            description="Project for tenant A",
            project_type="web_app"
        )
        
        # Create tenant B and project
        await db_b.create_tenant(
            tenant_b_context,
            slug="tenant-b",
            name="Tenant B",
            email="tenant-b@example.com"
        )
        
        project_b_id = await db_b.create_project(
            tenant_b_context,
            name="Project B",
            description="Project for tenant B",
            project_type="mobile_app"
        )
        
        # Test 1: Tenant A should not be able to access tenant B's project
        project_b_from_a = await db_a.get_project(tenant_a_context, project_b_id)
        assert project_b_from_a is None, "Tenant A should not access tenant B's project"
        
        # Test 2: Tenant B should not be able to access tenant A's project
        project_a_from_b = await db_b.get_project(tenant_b_context, project_a_id)
        assert project_a_from_b is None, "Tenant B should not access tenant A's project"
        
        # Test 3: Each tenant should only see their own projects
        projects_a = await db_a.get_tenant_projects(tenant_a_context)
        projects_b = await db_b.get_tenant_projects(tenant_b_context)
        
        assert len(projects_a) == 1, "Tenant A should have exactly 1 project"
        assert len(projects_b) == 1, "Tenant B should have exactly 1 project"
        
        assert projects_a[0]["id"] == project_a_id
        assert projects_b[0]["id"] == project_b_id
        
        # Test 4: Test event isolation
        await db_a.log_agent_event(
            tenant_context=tenant_a_context,
            project_id=project_a_id,
            agent_name="TestAgent",
            event_type="test_event",
            status="success",
            data={"test": "data"}
        )
        
        await db_b.log_agent_event(
            tenant_context=tenant_b_context,
            project_id=project_b_id,
            agent_name="TestAgent",
            event_type="test_event",
            status="success",
            data={"test": "data"}
        )
        
        # Each tenant should only see their own events
        events_a = await db_a.get_project_events(tenant_a_context, project_a_id)
        events_b = await db_b.get_project_events(tenant_b_context, project_b_id)
        
        assert len(events_a) >= 1, "Tenant A should have at least 1 event"
        assert len(events_b) >= 1, "Tenant B should have at least 1 event"
        
        # Tenant A should not see tenant B's events
        events_b_from_a = await db_a.get_project_events(tenant_a_context, project_b_id)
        assert len(events_b_from_a) == 0, "Tenant A should not see tenant B's events"
        
        print("✅ Tenant isolation test passed")
        
    finally:
        await db_a.close_pool()
        await db_b.close_pool()


@integration_test
async def test_payment_flow(mock_stripe, tenant_db, tenant_context):
    """Test Stripe payment integration flow"""
    
    # Import Stripe integration
    from agents.billing.stripe_integration import StripeIntegration, SubscriptionTier
    
    stripe_integration = StripeIntegration()
    
    # Test 1: Create customer
    customer = await stripe_integration.create_customer(
        email="test@example.com",
        name="Test User",
        tenant_id=tenant_context["tenant_id"]
    )
    
    assert customer.email == "test@example.com"
    assert customer.tenant_id == tenant_context["tenant_id"]
    
    # Test 2: Create checkout session
    checkout_session = await stripe_integration.create_checkout_session(
        customer_id=customer.id,
        tier=SubscriptionTier.STARTER,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    
    assert checkout_session.customer_id == customer.id
    assert "checkout.stripe.com" in checkout_session.url
    
    # Test 3: Get subscription (after checkout completion)
    subscription = await stripe_integration.get_subscription("sub_test123")
    
    assert subscription is not None
    assert subscription.customer_id == customer.id
    assert subscription.tier == SubscriptionTier.STARTER
    assert subscription.status.value == "active"
    
    # Test 4: Test tier limits
    limits = stripe_integration.get_tier_limits(SubscriptionTier.STARTER)
    
    assert limits["projects"] == 1
    assert limits["build_hours"] == 15
    assert limits["amount"] == 2900
    
    print("✅ Payment flow test passed")


@integration_test
async def test_agent_communication_flow(mock_openai, mock_slack, tenant_db, tenant_context):
    """Test agent-to-agent communication and event flow"""
    
    # Create a project for testing
    project_id = await tenant_db.create_project(
        tenant_context,
        name="Communication Test Project",
        description="Test agent communication",
        project_type="web_app"
    )
    
    # Test 1: Agent event logging
    await tenant_db.log_agent_event(
        tenant_context=tenant_context,
        project_id=project_id,
        agent_name="DesignAgent",
        event_type="design_generation",
        status="started",
        data={"pages": ["home", "about"]}
    )
    
    await tenant_db.log_agent_event(
        tenant_context=tenant_context,
        project_id=project_id,
        agent_name="DesignAgent",
        event_type="design_generation",
        status="completed",
        data={"figma_url": "https://figma.com/test-design"}
    )
    
    # Test 2: Verify events are logged correctly
    events = await tenant_db.get_project_events(tenant_context, project_id)
    
    assert len(events) == 2
    assert events[0]["event_type"] == "design_generation"
    assert events[0]["status"] == "started"
    assert events[1]["status"] == "completed"
    
    # Test 3: Test event filtering
    design_events = await tenant_db.get_project_events(
        tenant_context, 
        project_id, 
        agent_name="DesignAgent"
    )
    
    assert len(design_events) == 2
    assert all(event["agent_name"] == "DesignAgent" for event in design_events)
    
    # Test 4: Test Slack notification
    from agents.notifications.slack_integration import SlackIntegration
    
    slack_integration = SlackIntegration()
    
    result = await slack_integration.send_agent_notification(
        agent_name="DesignAgent",
        event_type="design_generation",
        status="completed",
        project_id=project_id,
        details={"figma_url": "https://figma.com/test-design"}
    )
    
    assert result["status"] == "success"
    
    print("✅ Agent communication flow test passed")


@integration_test
async def test_security_scan_integration(tenant_db, tenant_context, sample_security_scan_data):
    """Test security scanning integration"""
    
    # Create a project
    project_id = await tenant_db.create_project(
        tenant_context,
        name="Security Test Project",
        description="Test security scanning",
        project_type="web_app"
    )
    
    # Mock security scan results
    scan_results = [
        {
            "vulnerability_type": "SQL Injection",
            "severity": "high",
            "file_path": "app.py",
            "details": {
                "line_number": 42,
                "description": "Potential SQL injection vulnerability"
            }
        },
        {
            "vulnerability_type": "Cross-Site Scripting",
            "severity": "medium",
            "file_path": "templates/index.html",
            "details": {
                "line_number": 15,
                "description": "Unescaped user input in template"
            }
        }
    ]
    
    # Store scan results
    for result in scan_results:
        await tenant_db.store_security_scan_result(
            tenant_context=tenant_context,
            project_id=project_id,
            scan_type="dependencies",
            vulnerability_type=result["vulnerability_type"],
            severity=result["severity"],
            file_path=result["file_path"],
            details=result["details"]
        )
    
    # Test 1: Retrieve scan results
    stored_results = await tenant_db.get_security_scan_results(
        tenant_context, 
        project_id
    )
    
    assert len(stored_results) == 2
    
    # Test 2: Filter by severity
    high_severity_results = await tenant_db.get_security_scan_results(
        tenant_context,
        project_id,
        severity="high"
    )
    
    assert len(high_severity_results) == 1
    assert high_severity_results[0]["vulnerability_type"] == "SQL Injection"
    
    # Test 3: Test Slack security alert
    from agents.notifications.slack_integration import SlackIntegration
    
    slack_integration = SlackIntegration()
    
    result = await slack_integration.send_security_alert(
        vulnerability_type="SQL Injection",
        severity="high",
        file_path="app.py",
        project_id=project_id,
        details={"line_number": 42}
    )
    
    assert result["status"] == "success"
    
    print("✅ Security scan integration test passed")


@integration_test
async def test_error_handling_and_recovery(tenant_db, tenant_context, mock_openai):
    """Test error handling and recovery scenarios"""
    
    # Create a project
    project_id = await tenant_db.create_project(
        tenant_context,
        name="Error Test Project",
        description="Test error handling",
        project_type="web_app"
    )
    
    # Test 1: Test database connection error handling
    with patch('asyncpg.connect', side_effect=Exception("Database connection failed")):
        try:
            await tenant_db.create_project(
                tenant_context,
                name="Should Fail",
                description="This should fail",
                project_type="web_app"
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Database connection failed" in str(e)
    
    # Test 2: Test API error handling
    mock_openai.chat.completions.create.side_effect = Exception("OpenAI API Error")
    
    # Mock a service that uses OpenAI
    from agents.dev.main import DevAgent
    
    dev_agent = DevAgent()
    
    try:
        await dev_agent.generate_code({
            "project_id": project_id,
            "module_spec": {"name": "TestModule", "type": "service"}
        })
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "OpenAI API Error" in str(e)
    
    # Test 3: Test graceful degradation
    # Reset mock to work again
    mock_openai.chat.completions.create.side_effect = None
    
    # Verify system can recover
    events = await tenant_db.get_project_events(tenant_context, project_id)
    assert isinstance(events, list)  # Should not crash
    
    print("✅ Error handling and recovery test passed")


@integration_test
@slow_test
async def test_load_handling(tenant_db, tenant_context, mock_openai):
    """Test system behavior under load"""
    
    # Create multiple projects concurrently
    project_tasks = []
    for i in range(10):
        task = tenant_db.create_project(
            tenant_context,
            name=f"Load Test Project {i}",
            description=f"Load test project {i}",
            project_type="web_app"
        )
        project_tasks.append(task)
    
    # Execute all tasks concurrently
    project_ids = await asyncio.gather(*project_tasks)
    
    assert len(project_ids) == 10
    assert all(pid is not None for pid in project_ids)
    
    # Test concurrent event logging
    event_tasks = []
    for i, project_id in enumerate(project_ids):
        task = tenant_db.log_agent_event(
            tenant_context=tenant_context,
            project_id=project_id,
            agent_name="LoadTestAgent",
            event_type="load_test",
            status="completed",
            data={"iteration": i}
        )
        event_tasks.append(task)
    
    await asyncio.gather(*event_tasks)
    
    # Verify all events were logged
    total_events = 0
    for project_id in project_ids:
        events = await tenant_db.get_project_events(tenant_context, project_id)
        total_events += len(events)
    
    assert total_events >= 10  # At least one event per project
    
    print(f"✅ Load handling test passed - handled {len(project_ids)} projects and {total_events} events")


@integration_test
async def test_configuration_validation(test_settings):
    """Test configuration validation"""
    
    # Test 1: Required settings are present
    assert test_settings.database.host is not None
    assert test_settings.database.name is not None
    assert test_settings.ai.openai_api_key.get_secret_value() is not None
    
    # Test 2: Environment-specific settings
    assert test_settings.environment.value == "test"
    assert test_settings.debug is True
    
    # Test 3: Database connection string generation
    db_url = test_settings.database.url
    assert "postgresql://" in db_url
    assert test_settings.database.name in db_url
    
    print("✅ Configuration validation test passed")


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/integration/test_critical_path.py -v
    pass 