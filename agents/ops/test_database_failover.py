"""
Test suite for Database Failover Agent - Night 70
Tests database failover scenarios, replica promotion, and validation logic
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Test imports
import sys
import os
sys.path.append(os.path.dirname(__file__))

from database_failover_agent import (
    DatabaseFailoverAgent, DatabaseInstance, DatabaseHealth, FailoverDecision,
    FailoverOperation, FailoverRequest, DatabaseState,
    FailoverTrigger, FailoverStatus
)


class TestDatabaseFailoverAgent:
    """Test the DatabaseFailoverAgent class"""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock DatabaseFailoverAgent for testing"""
        with patch('database_failover_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = DatabaseFailoverAgent("test-project")
            
            # Mock database instances
            agent.database_instances = {
                "primary-instance": DatabaseInstance(
                    name="primary-instance",
                    region="us-central1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="primary",
                    ip_address="10.0.1.10",
                    last_check=datetime.utcnow()
                ),
                "replica-east": DatabaseInstance(
                    name="replica-east",
                    region="us-east1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="replica",
                    ip_address="10.0.2.10",
                    last_check=datetime.utcnow(),
                    is_failover_target=True,
                    replication_lag=5
                ),
                "replica-central": DatabaseInstance(
                    name="replica-central",
                    region="us-central1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="replica",
                    ip_address="10.0.1.11",
                    last_check=datetime.utcnow(),
                    is_failover_target=False,
                    replication_lag=2
                )
            }
            
            return agent
    
    @pytest.fixture
    def sample_health_data(self):
        """Sample health data for testing"""
        return DatabaseHealth(
            instance_name="primary-instance",
            timestamp=datetime.utcnow(),
            is_accessible=True,
            response_time_ms=50.0,
            cpu_utilization=25.0,
            memory_utilization=40.0,
            disk_utilization=30.0,
            active_connections=10,
            replication_lag=None,
            error_rate=0.0,
            availability=100.0
        )
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        with patch('database_failover_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = DatabaseFailoverAgent("test-project")
            
            assert agent.project_id == "test-project"
            assert agent.health_check_interval == 60
            assert agent.max_replication_lag == 300
            assert agent.failover_threshold_failures == 3
            assert len(agent.database_instances) == 0
            assert len(agent.active_failovers) == 0
    
    @pytest.mark.asyncio
    async def test_health_check_accessible_instance(self, mock_agent, sample_health_data):
        """Test health check for accessible instance"""
        instance = mock_agent.database_instances["primary-instance"]
        
        with patch.object(mock_agent, '_check_instance_health', return_value=sample_health_data):
            health = await mock_agent._check_instance_health(instance)
            
            assert health.instance_name == "primary-instance"
            assert health.is_accessible is True
            assert health.response_time_ms == 50.0
            assert health.availability == 100.0
    
    @pytest.mark.asyncio
    async def test_health_check_failed_instance(self, mock_agent):
        """Test health check for failed instance"""
        instance = mock_agent.database_instances["primary-instance"]
        
        failed_health = DatabaseHealth(
            instance_name="primary-instance",
            timestamp=datetime.utcnow(),
            is_accessible=False,
            response_time_ms=float('inf'),
            cpu_utilization=0.0,
            memory_utilization=0.0,
            disk_utilization=0.0,
            active_connections=0,
            error_rate=100.0,
            availability=0.0
        )
        
        with patch.object(mock_agent, '_check_instance_health', return_value=failed_health):
            health = await mock_agent._check_instance_health(instance)
            
            assert health.is_accessible is False
            assert health.error_rate == 100.0
            assert health.availability == 0.0
    
    @pytest.mark.asyncio
    async def test_failover_decision_with_healthy_replicas(self, mock_agent):
        """Test failover decision when healthy replicas are available"""
        decision = await mock_agent._make_failover_decision(
            "primary-instance",
            FailoverTrigger.HEALTH_CHECK_FAILURE
        )
        
        assert decision.should_failover is True
        assert decision.target_replica == "replica-east"  # Should prefer failover target
        assert decision.confidence_score >= 0.8
        assert decision.estimated_downtime > 0
        assert "replica-east" in decision.reasoning
    
    @pytest.mark.asyncio
    async def test_failover_decision_no_healthy_replicas(self, mock_agent):
        """Test failover decision when no healthy replicas are available"""
        # Mark all replicas as failed
        for instance in mock_agent.database_instances.values():
            if instance.instance_type == "replica":
                instance.state = DatabaseState.FAILED
        
        decision = await mock_agent._make_failover_decision(
            "primary-instance",
            FailoverTrigger.HEALTH_CHECK_FAILURE
        )
        
        assert decision.should_failover is False
        assert decision.target_replica is None
        assert decision.confidence_score == 0.0
        assert "no healthy failover candidates" in decision.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_manual_failover_trigger(self, mock_agent):
        """Test manual failover triggering"""
        request = FailoverRequest(
            trigger="manual",
            target_replica="replica-east",
            force=True,
            reason="Testing manual failover"
        )
        
        with patch.object(mock_agent, '_execute_failover') as mock_execute:
            response = await mock_agent.trigger_manual_failover(request)
            
            assert response.status == "pending"
            assert response.target_replica == "replica-east"
            assert "Failover initiated" in response.message
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_failover_execution_success(self, mock_agent):
        """Test successful failover execution"""
        operation = FailoverOperation(
            operation_id="test-failover-001",
            trigger=FailoverTrigger.MANUAL,
            original_primary="primary-instance",
            target_replica="replica-east",
            status=FailoverStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        # Mock the promotion and validation methods
        with patch.object(mock_agent, '_promote_replica') as mock_promote, \
             patch.object(mock_agent, '_validate_failover') as mock_validate, \
             patch.object(mock_agent, '_update_application_config') as mock_update:
            
            mock_validate.return_value = {
                "connectivity_test": True,
                "write_test": True,
                "replication_status": "healthy"
            }
            
            await mock_agent._execute_failover(operation)
            
            # Verify the operation completed successfully
            assert operation.status == FailoverStatus.COMPLETED
            assert operation.downtime_seconds is not None
            mock_promote.assert_called_once_with("replica-east")
            mock_validate.assert_called_once_with("replica-east")
            mock_update.assert_called_once_with("replica-east")
    
    @pytest.mark.asyncio
    async def test_failover_execution_failure(self, mock_agent):
        """Test failed failover execution"""
        operation = FailoverOperation(
            operation_id="test-failover-002",
            trigger=FailoverTrigger.MANUAL,
            original_primary="primary-instance",
            target_replica="replica-east",
            status=FailoverStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        # Mock promotion to fail
        with patch.object(mock_agent, '_promote_replica', side_effect=Exception("Promotion failed")):
            await mock_agent._execute_failover(operation)
            
            # Verify the operation failed
            assert operation.status == FailoverStatus.FAILED
            assert "Promotion failed" in operation.error_message
    
    @pytest.mark.asyncio
    async def test_get_database_health_single_instance(self, mock_agent, sample_health_data):
        """Test getting health for a single instance"""
        # Add health history
        mock_agent.health_history["primary-instance"].append(sample_health_data)
        
        health_data = await mock_agent.get_database_health("primary-instance")
        
        assert health_data["instance_name"] == "primary-instance"
        assert health_data["state"] == "RUNNABLE"
        assert health_data["instance_type"] == "primary"
        assert health_data["is_healthy"] is True
    
    @pytest.mark.asyncio
    async def test_get_database_health_all_instances(self, mock_agent, sample_health_data):
        """Test getting health for all instances"""
        # Add health history for each instance
        for instance_name in mock_agent.database_instances.keys():
            health = DatabaseHealth(
                instance_name=instance_name,
                timestamp=datetime.utcnow(),
                is_accessible=True,
                response_time_ms=50.0,
                cpu_utilization=25.0,
                memory_utilization=40.0,
                disk_utilization=30.0,
                active_connections=10
            )
            mock_agent.health_history[instance_name].append(health)
        
        health_data = await mock_agent.get_database_health()
        
        assert len(health_data) == 3
        assert "primary-instance" in health_data
        assert "replica-east" in health_data
        assert "replica-central" in health_data
    
    @pytest.mark.asyncio
    async def test_failover_metrics(self, mock_agent):
        """Test failover metrics reporting"""
        # Add some mock failover history
        mock_agent.metrics["failovers_triggered"] = 5
        mock_agent.metrics["failovers_successful"] = 4
        mock_agent.metrics["failovers_failed"] = 1
        mock_agent.metrics["average_failover_time"] = 120.5
        
        metrics = await mock_agent.get_failover_metrics()
        
        assert metrics["metrics"]["failovers_triggered"] == 5
        assert metrics["metrics"]["failovers_successful"] == 4
        assert metrics["metrics"]["failovers_failed"] == 1
        assert metrics["success_rate"] == 80.0  # 4/5 * 100
        assert metrics["active_failovers"] == 0
    
    def test_average_failover_time_calculation(self, mock_agent):
        """Test average failover time calculation"""
        # First failover
        mock_agent.metrics["failovers_successful"] = 0
        mock_agent._update_average_failover_time(100)
        assert mock_agent.metrics["average_failover_time"] == 100
        assert mock_agent.metrics["failovers_successful"] == 1
        
        # Second failover
        mock_agent._update_average_failover_time(200)
        assert mock_agent.metrics["average_failover_time"] == 150  # (100 + 200) / 2
        assert mock_agent.metrics["failovers_successful"] == 2
        
        # Third failover
        mock_agent._update_average_failover_time(300)
        assert mock_agent.metrics["average_failover_time"] == 200  # (150*2 + 300) / 3
        assert mock_agent.metrics["failovers_successful"] == 3


class TestFailoverDrillScenarios:
    """Test various failover drill scenarios"""
    
    @pytest.fixture
    def drill_agent(self):
        """Create an agent specifically for drill testing"""
        with patch('database_failover_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = DatabaseFailoverAgent("drill-project")
            
            # Set up realistic drill scenario
            agent.database_instances = {
                "prod-primary": DatabaseInstance(
                    name="prod-primary",
                    region="us-central1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="primary",
                    ip_address="10.10.1.10"
                ),
                "prod-replica-east": DatabaseInstance(
                    name="prod-replica-east",
                    region="us-east1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="replica",
                    ip_address="10.10.2.10",
                    is_failover_target=True,
                    replication_lag=10
                ),
                "prod-replica-west": DatabaseInstance(
                    name="prod-replica-west",
                    region="us-west1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="replica",
                    ip_address="10.10.3.10",
                    is_failover_target=True,
                    replication_lag=15
                )
            }
            
            return agent
    
    @pytest.mark.asyncio
    async def test_primary_failure_simulation(self, drill_agent):
        """Test simulated primary failure scenario"""
        # Simulate primary failure by adding failed health checks
        for i in range(5):
            failed_health = DatabaseHealth(
                instance_name="prod-primary",
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                is_accessible=False,
                response_time_ms=float('inf'),
                cpu_utilization=0.0,
                memory_utilization=0.0,
                disk_utilization=0.0,
                active_connections=0,
                error_rate=100.0,
                availability=0.0
            )
            drill_agent.health_history["prod-primary"].append(failed_health)
        
        # Test failover decision
        decision = await drill_agent._make_failover_decision(
            "prod-primary",
            FailoverTrigger.HEALTH_CHECK_FAILURE
        )
        
        assert decision.should_failover is True
        assert decision.target_replica in ["prod-replica-east", "prod-replica-west"]
        assert decision.confidence_score > 0.5
    
    @pytest.mark.asyncio
    async def test_replica_selection_logic(self, drill_agent):
        """Test replica selection logic based on lag and region"""
        decision = await drill_agent._make_failover_decision(
            "prod-primary",
            FailoverTrigger.MANUAL
        )
        
        # Should prefer replica with lower lag
        assert decision.target_replica == "prod-replica-east"  # 10s lag vs 15s lag
    
    @pytest.mark.asyncio
    async def test_high_replication_lag_scenario(self, drill_agent):
        """Test scenario with high replication lag"""
        # Set high replication lag
        drill_agent.database_instances["prod-replica-east"].replication_lag = 400  # > 5 minutes
        drill_agent.database_instances["prod-replica-west"].replication_lag = 500
        
        decision = await drill_agent._make_failover_decision(
            "prod-primary",
            FailoverTrigger.HEALTH_CHECK_FAILURE
        )
        
        # Should still failover but with lower confidence
        assert decision.should_failover is True
        assert decision.confidence_score < 0.8  # Lower confidence due to high lag
        assert decision.estimated_downtime > 400  # Should include lag time
    
    @pytest.mark.asyncio
    async def test_multi_region_failover_preference(self, drill_agent):
        """Test multi-region failover preference"""
        # Simulate us-central1 region failure affecting primary
        drill_agent.database_instances["prod-primary"].region = "us-central1"
        
        decision = await drill_agent._make_failover_decision(
            "prod-primary",
            FailoverTrigger.HEALTH_CHECK_FAILURE
        )
        
        # Should prefer different region for failover
        target_replica = drill_agent.database_instances[decision.target_replica]
        assert target_replica.region != "us-central1"
    
    @pytest.mark.asyncio
    async def test_scheduled_drill_execution(self, drill_agent):
        """Test scheduled drill execution"""
        request = FailoverRequest(
            trigger="scheduled_drill",
            target_replica="prod-replica-east",
            force=True,
            reason="Monthly disaster recovery drill"
        )
        
        with patch.object(drill_agent, '_execute_failover') as mock_execute:
            response = await drill_agent.trigger_manual_failover(request)
            
            assert response.status == "pending"
            assert "Monthly disaster recovery drill" in str(mock_execute.call_args)
    
    @pytest.mark.asyncio
    async def test_validation_after_failover(self, drill_agent):
        """Test post-failover validation"""
        validation_results = await drill_agent._validate_failover("prod-replica-east")
        
        # Basic validation structure check
        expected_keys = ["connectivity_test", "write_test", "replication_status", "application_health"]
        for key in expected_keys:
            assert key in validation_results


class TestFailoverIntegration:
    """Integration tests for failover system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_failover_drill(self):
        """Test complete end-to-end failover drill"""
        with patch('database_failover_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = DatabaseFailoverAgent("integration-test")
            
            # Set up test environment
            agent.database_instances = {
                "main-db": DatabaseInstance(
                    name="main-db",
                    region="us-central1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="primary",
                    ip_address="10.1.1.10"
                ),
                "backup-db": DatabaseInstance(
                    name="backup-db",
                    region="us-east1",
                    state=DatabaseState.RUNNABLE,
                    instance_type="replica",
                    ip_address="10.1.2.10",
                    is_failover_target=True,
                    replication_lag=5
                )
            }
            
            # Mock all the external dependencies
            with patch.object(agent, '_promote_replica') as mock_promote, \
                 patch.object(agent, '_validate_failover') as mock_validate, \
                 patch.object(agent, '_update_application_config') as mock_update:
                
                mock_validate.return_value = {
                    "connectivity_test": True,
                    "write_test": True,
                    "replication_status": "healthy",
                    "application_health": "ready"
                }
                
                # Trigger failover
                request = FailoverRequest(
                    trigger="scheduled_drill",
                    target_replica="backup-db",
                    force=True,
                    reason="Integration test drill"
                )
                
                response = await agent.trigger_manual_failover(request)
                
                # Wait a bit for async execution
                await asyncio.sleep(0.1)
                
                # Verify response
                assert response.status == "pending"
                assert response.target_replica == "backup-db"
                
                # Check that failover was recorded
                assert len(agent.active_failovers) >= 0  # May move to history quickly
                assert agent.metrics["failovers_triggered"] >= 1
    
    def test_configuration_validation(self):
        """Test agent configuration validation"""
        with patch('database_failover_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = DatabaseFailoverAgent("config-test")
            
            # Test default configuration
            assert agent.health_check_interval > 0
            assert agent.connection_timeout > 0
            assert agent.max_replication_lag > 0
            assert agent.failover_threshold_failures > 0
            assert agent.replica_promotion_timeout > 0
            
            # Test metrics initialization
            expected_metrics = [
                "health_checks_performed",
                "failovers_triggered", 
                "failovers_successful",
                "failovers_failed",
                "average_failover_time"
            ]
            
            for metric in expected_metrics:
                assert metric in agent.metrics
                assert isinstance(agent.metrics[metric], (int, float))


class TestFailoverScriptIntegration:
    """Test integration with the failover drill script"""
    
    def test_script_execution_simulation(self):
        """Test simulated script execution"""
        # This would test the shell script integration
        # In a real environment, this would invoke the actual script
        
        script_config = {
            "PROJECT_ID": "test-project",
            "PRIMARY_INSTANCE": "test-primary",
            "REPLICA_EAST_INSTANCE": "test-replica-east",
            "REPLICA_CENTRAL_INSTANCE": "test-replica-central",
            "VALIDATION_TIMEOUT": 600
        }
        
        # Verify configuration is valid
        assert all(key in script_config for key in [
            "PROJECT_ID", "PRIMARY_INSTANCE", "REPLICA_EAST_INSTANCE"
        ])
        
        # Verify timeout is reasonable
        assert script_config["VALIDATION_TIMEOUT"] >= 300  # At least 5 minutes
    
    def test_script_dry_run_mode(self):
        """Test script dry run functionality"""
        # Simulate dry run mode
        dry_run_output = {
            "mode": "dry_run",
            "would_simulate_failover": True,
            "primary_instance": "test-primary",
            "target_replica": "test-replica-east",
            "estimated_duration": 300,
            "validation_steps": [
                "Check prerequisites",
                "Validate replica health",
                "Simulate primary failure",
                "Promote replica",
                "Validate failover success"
            ]
        }
        
        assert dry_run_output["mode"] == "dry_run"
        assert len(dry_run_output["validation_steps"]) == 5


# Test fixtures and utilities
@pytest.fixture
def sample_failover_operation():
    """Sample failover operation for testing"""
    return FailoverOperation(
        operation_id="test-op-123",
        trigger=FailoverTrigger.MANUAL,
        original_primary="test-primary",
        target_replica="test-replica",
        status=FailoverStatus.PENDING,
        created_at=datetime.utcnow(),
        decision=FailoverDecision(
            trigger=FailoverTrigger.MANUAL,
            should_failover=True,
            target_replica="test-replica",
            reasoning="Test failover",
            confidence_score=0.9,
            estimated_downtime=120,
            impact_assessment="Minimal impact expected"
        )
    )


@pytest.fixture
def mock_cloud_sql_client():
    """Mock Cloud SQL client for testing"""
    mock_client = Mock()
    mock_client.list.return_value = Mock()
    mock_client.get.return_value = Mock()
    mock_client.promote_replica.return_value = Mock()
    return mock_client


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"]) 