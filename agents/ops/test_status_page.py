#!/usr/bin/env python3
"""
Test Status Page Agent - Night 79
Unit tests for status page functionality and incident management
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import the status page components
from status_page_agent import (
    StatusPageAgent,
    ServiceStatus,
    IncidentSeverity,
    IncidentStatus,
    ServiceComponent,
    Incident,
    StatusPageRequest,
    IncidentCreateRequest,
    IncidentUpdateRequest
)


class TestStatusPageAgent:
    """Test cases for Status Page Agent"""

    @pytest.fixture
    def agent(self):
        """Create a test agent instance"""
        with patch('status_page_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = StatusPageAgent("test-project")
            return agent

    def test_component_initialization(self, agent):
        """Test that components are properly initialized"""
        expected_components = [
            "orchestrator",
            "api_gateway", 
            "frontend",
            "event_relay",
            "database",
            "agents"
        ]
        
        assert len(agent.components) == len(expected_components)
        for comp_id in expected_components:
            assert comp_id in agent.components
            assert agent.components[comp_id].status == ServiceStatus.OPERATIONAL

    def test_status_determination(self, agent):
        """Test service status determination logic"""
        # Test operational status
        status = agent._determine_component_status(
            is_up=True,
            performance={"response_time_ms": 100, "error_rate": 0.001}
        )
        assert status == ServiceStatus.OPERATIONAL

        # Test degraded performance
        status = agent._determine_component_status(
            is_up=True,
            performance={"response_time_ms": 1500, "error_rate": 0.005}
        )
        assert status == ServiceStatus.DEGRADED_PERFORMANCE

        # Test partial outage
        status = agent._determine_component_status(
            is_up=True,
            performance={"response_time_ms": 500, "error_rate": 0.08}
        )
        assert status == ServiceStatus.PARTIAL_OUTAGE

        # Test major outage
        status = agent._determine_component_status(
            is_up=False,
            performance={}
        )
        assert status == ServiceStatus.MAJOR_OUTAGE

    def test_overall_status_calculation(self, agent):
        """Test overall system status calculation"""
        # All operational
        assert agent.calculate_overall_status() == ServiceStatus.OPERATIONAL

        # One degraded
        agent.components["api_gateway"].status = ServiceStatus.DEGRADED_PERFORMANCE
        assert agent.calculate_overall_status() == ServiceStatus.DEGRADED_PERFORMANCE

        # One partial outage
        agent.components["frontend"].status = ServiceStatus.PARTIAL_OUTAGE
        assert agent.calculate_overall_status() == ServiceStatus.PARTIAL_OUTAGE

        # One major outage
        agent.components["database"].status = ServiceStatus.MAJOR_OUTAGE
        assert agent.calculate_overall_status() == ServiceStatus.MAJOR_OUTAGE

    def test_uptime_calculation(self, agent):
        """Test uptime statistics calculation"""
        # Simulate uptime history
        current_time = datetime.utcnow()
        for i in range(100):
            for comp_id in agent.components.keys():
                is_operational = i < 99  # 99% uptime
                agent.uptime_history[comp_id].append({
                    "timestamp": current_time - timedelta(minutes=i),
                    "operational": is_operational
                })

        stats = agent.calculate_uptime_stats()
        
        # Should be approximately 99% for each component
        for comp_id in agent.components.keys():
            assert 0.98 <= stats[comp_id] <= 1.0
        
        # Overall should be similar
        assert 0.98 <= stats["overall"] <= 1.0

    @pytest.mark.asyncio
    async def test_incident_creation(self, agent):
        """Test incident creation"""
        request = IncidentCreateRequest(
            title="Test Incident",
            description="Testing incident creation",
            severity=IncidentSeverity.MEDIUM,
            affected_components=["api_gateway"],
            impact_description="API slowness"
        )

        incident_id = await agent.create_incident(request)
        
        assert incident_id in agent.incidents
        incident = agent.incidents[incident_id]
        assert incident.title == "Test Incident"
        assert incident.severity == IncidentSeverity.MEDIUM
        assert incident.status == IncidentStatus.INVESTIGATING
        assert "api_gateway" in incident.affected_components

    @pytest.mark.asyncio
    async def test_incident_updates(self, agent):
        """Test incident updates"""
        # Create an incident first
        request = IncidentCreateRequest(
            title="Test Incident",
            description="Testing updates",
            severity=IncidentSeverity.HIGH,
            affected_components=["database"]
        )
        incident_id = await agent.create_incident(request)

        # Update the incident
        update_request = IncidentUpdateRequest(
            status=IncidentStatus.IDENTIFIED,
            update_message="Root cause identified",
            resolved=False
        )
        
        success = await agent.update_incident(incident_id, update_request)
        assert success

        incident = agent.incidents[incident_id]
        assert incident.status == IncidentStatus.IDENTIFIED
        assert len(incident.updates) >= 2  # Initial + update

        # Resolve the incident
        resolve_request = IncidentUpdateRequest(
            update_message="Issue resolved",
            resolved=True
        )
        
        await agent.update_incident(incident_id, resolve_request)
        incident = agent.incidents[incident_id]
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolved_at is not None

    @pytest.mark.asyncio
    async def test_maintenance_mode(self, agent):
        """Test maintenance mode functionality"""
        component_ids = ["api_gateway", "frontend"]
        
        # Enable maintenance mode
        success = await agent.set_maintenance_mode(
            component_ids=component_ids,
            enabled=True,
            message="Scheduled maintenance window"
        )
        assert success

        # Check component statuses
        for comp_id in component_ids:
            assert agent.components[comp_id].status == ServiceStatus.MAINTENANCE

        # Disable maintenance mode
        await agent.set_maintenance_mode(
            component_ids=component_ids,
            enabled=False
        )

        # Check component statuses reverted
        for comp_id in component_ids:
            assert agent.components[comp_id].status == ServiceStatus.OPERATIONAL

    @pytest.mark.asyncio
    async def test_status_page_data_generation(self, agent):
        """Test status page data generation"""
        # Create a test incident
        request = IncidentCreateRequest(
            title="Active Test Incident",
            description="Testing status page data",
            severity=IncidentSeverity.LOW,
            affected_components=["event_relay"]
        )
        incident_id = await agent.create_incident(request)

        # Generate status page data
        status_request = StatusPageRequest(
            include_incidents=True,
            include_metrics=True
        )
        
        response = await agent.get_status_page_data(status_request)
        
        # Verify response structure
        assert hasattr(response, 'overall_status')
        assert hasattr(response, 'components')
        assert hasattr(response, 'active_incidents')
        assert hasattr(response, 'uptime_stats')
        
        # Check components
        assert len(response.components) == 6
        for comp in response.components:
            assert 'id' in comp
            assert 'name' in comp
            assert 'status' in comp

        # Check active incidents
        assert len(response.active_incidents) == 1
        assert response.active_incidents[0]['title'] == "Active Test Incident"

    def test_metrics_summary(self, agent):
        """Test metrics summary generation"""
        summary = agent.get_metrics_summary()
        
        expected_keys = [
            "total_components",
            "operational_components", 
            "active_incidents",
            "uptime_stats",
            "overall_status",
            "last_updated"
        ]
        
        for key in expected_keys:
            assert key in summary

        assert summary["total_components"] == 6
        assert summary["operational_components"] == 6  # All start operational
        assert summary["active_incidents"] == 0  # No incidents initially

    @pytest.mark.asyncio
    async def test_auto_incident_creation(self, agent):
        """Test automatic incident creation"""
        # Simulate a component going down
        component = agent.components["orchestrator"]
        component.status = ServiceStatus.MAJOR_OUTAGE
        
        # This would normally be called by the monitoring loop
        await agent._auto_create_incident(component, ServiceStatus.MAJOR_OUTAGE)
        
        # Check that an incident was created
        incidents = [i for i in agent.incidents.values() 
                    if "orchestrator" in i.affected_components]
        assert len(incidents) == 1
        assert incidents[0].severity == IncidentSeverity.HIGH

    @pytest.mark.asyncio 
    async def test_incident_update_messages(self, agent):
        """Test incident update message functionality"""
        # Create incident
        request = IncidentCreateRequest(
            title="Message Test",
            description="Testing update messages",
            severity=IncidentSeverity.MEDIUM,
            affected_components=["agents"]
        )
        incident_id = await agent.create_incident(request)

        # Add update messages
        await agent.add_incident_update(incident_id, "Investigation started")
        await agent.add_incident_update(incident_id, "Root cause identified")
        await agent.add_incident_update(incident_id, "Fix being deployed")

        incident = agent.incidents[incident_id]
        assert len(incident.updates) >= 4  # Initial + 3 manual updates

        # Check update content
        messages = [update["message"] for update in incident.updates]
        assert "Investigation started" in messages
        assert "Root cause identified" in messages
        assert "Fix being deployed" in messages


class TestStatusPageAPI:
    """Test cases for Status Page API endpoints"""

    def test_status_page_request_model(self):
        """Test StatusPageRequest model validation"""
        # Valid request
        request = StatusPageRequest(
            include_incidents=True,
            include_metrics=False,
            component_ids=["api_gateway", "frontend"]
        )
        assert request.include_incidents is True
        assert request.include_metrics is False
        assert request.component_ids == ["api_gateway", "frontend"]

        # Default values
        request = StatusPageRequest()
        assert request.include_incidents is True
        assert request.include_metrics is False
        assert request.component_ids is None

    def test_incident_create_request_model(self):
        """Test IncidentCreateRequest model validation"""
        request = IncidentCreateRequest(
            title="API Issues",
            description="API experiencing high latency",
            severity=IncidentSeverity.HIGH,
            affected_components=["api_gateway", "database"],
            impact_description="Users experiencing slow responses"
        )
        assert request.title == "API Issues"
        assert request.severity == IncidentSeverity.HIGH
        assert len(request.affected_components) == 2

    def test_incident_update_request_model(self):
        """Test IncidentUpdateRequest model validation"""
        request = IncidentUpdateRequest(
            status=IncidentStatus.MONITORING,
            update_message="Fix deployed, monitoring results",
            resolved=False
        )
        assert request.status == IncidentStatus.MONITORING
        assert request.resolved is False

        # Test resolution request
        resolve_request = IncidentUpdateRequest(
            update_message="Issue fully resolved",
            resolved=True
        )
        assert resolve_request.resolved is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 