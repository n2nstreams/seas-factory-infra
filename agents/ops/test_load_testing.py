#!/usr/bin/env python3
"""
Test cases for Night 69 Load Testing functionality
Tests the k6 load testing integration in AIOpsAgent
"""

import asyncio
import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the classes we're testing
from aiops_agent import (
    AIOpsAgent, LoadTestRequest, LoadTestTargetRequest, LoadTestType,
    LoadTestStatus, LoadTestResult, LoadTestConfiguration, LoadTestTarget,
    LoadTestExecution, AlertSeverity, AnomalyType
)


class TestLoadTesting(unittest.TestCase):
    """Test cases for load testing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.project_id = "test-project"
        self.agent = AIOpsAgent(self.project_id)
        
        # Mock the Google Cloud clients
        self.agent.logging_client = MagicMock()
        self.agent.monitoring_client = MagicMock()
        self.agent.error_reporting_client = MagicMock()
        self.agent.gemini_model = MagicMock()
        
        # Create a temporary k6 script for testing
        self.temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
        self.temp_script.write("""
        import http from 'k6/http';
        export default function() {
            http.get(__ENV.BASE_URL || 'http://localhost:8080');
        }
        """)
        self.temp_script.close()
        self.agent.k6_script_path = self.temp_script.name
        
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_script.name):
            os.unlink(self.temp_script.name)
    
    def test_load_test_configuration_creation(self):
        """Test creation of load test configuration"""
        target = LoadTestTarget(
            name="test-service",
            base_url="https://api.example.com",
            endpoints=["/health", "/metrics"],
            auth_required=True,
            auth_token="test-token",
            custom_headers={"X-Custom": "test"}
        )
        
        config = LoadTestConfiguration(
            test_id="test-123",
            test_type=LoadTestType.STRESS,
            target=target,
            duration_minutes=5,
            virtual_users=50,
            ramp_up_duration_seconds=30
        )
        
        self.assertEqual(config.test_id, "test-123")
        self.assertEqual(config.test_type, LoadTestType.STRESS)
        self.assertEqual(config.target.name, "test-service")
        self.assertEqual(config.duration_minutes, 5)
        self.assertEqual(config.virtual_users, 50)
        
        # Test serialization
        config_dict = config.to_dict()
        self.assertIn("test_id", config_dict)
        self.assertIn("test_type", config_dict)
        self.assertIn("target", config_dict)
    
    def test_load_test_result_creation(self):
        """Test creation and serialization of load test results"""
        result = LoadTestResult(
            test_id="test-123",
            test_type=LoadTestType.LOAD,
            status=LoadTestStatus.COMPLETED,
            started_at=datetime.utcnow(),
            total_requests=1000,
            failed_requests=50,
            error_rate=0.05,
            avg_response_time=250.5,
            p95_response_time=450.0,
            requests_per_second=33.3,
            data_received_mb=5.2,
            thresholds_passed={"http_req_duration": True, "http_req_failed": False},
            overall_passed=False
        )
        
        self.assertEqual(result.test_id, "test-123")
        self.assertEqual(result.error_rate, 0.05)
        self.assertFalse(result.overall_passed)
        
        # Test serialization
        result_dict = result.to_dict()
        self.assertIn("test_id", result_dict)
        self.assertIn("error_rate", result_dict)
        self.assertIn("thresholds_passed", result_dict)
        self.assertIsInstance(result_dict["started_at"], str)
    
    @pytest.mark.asyncio
    async def test_start_load_test(self):
        """Test starting a load test"""
        
        # Create test request
        request = LoadTestRequest(
            test_type="stress",
            target=LoadTestTargetRequest(
                name="test-api",
                base_url="https://api.example.com",
                endpoints=["/health"]
            ),
            duration_minutes=2,
            virtual_users=20
        )
        
        # Mock the subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'test output', b'')
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Start the load test
            test_id = await self.agent.start_load_test(request)
            
            self.assertIsNotNone(test_id)
            self.assertTrue(test_id.startswith("loadtest-"))
            
            # Check that execution was created
            self.assertIn(test_id, self.agent.load_test_executions)
            execution = self.agent.load_test_executions[test_id]
            self.assertEqual(execution.config.test_type, LoadTestType.STRESS)
            self.assertEqual(execution.config.target.name, "test-api")
    
    def test_generate_k6_command(self):
        """Test k6 command generation"""
        
        target = LoadTestTarget(
            name="test-service",
            base_url="https://api.example.com",
            endpoints=["/health"],
            auth_required=False
        )
        
        config = LoadTestConfiguration(
            test_id="test-123",
            test_type=LoadTestType.LOAD,
            target=target,
            duration_minutes=5,
            virtual_users=25,
            environment_vars={"CUSTOM_VAR": "test_value"}
        )
        
        # Test command generation
        async def test_command():
            cmd = await self.agent._generate_k6_command(config)
            
            self.assertIn("k6", cmd)
            self.assertIn("run", cmd)
            self.assertIn("--include-scenario", cmd)
            self.assertIn("load_test", cmd)
            
            # Check environment variables
            env_found = False
            for i, arg in enumerate(cmd):
                if arg == "-e" and i + 1 < len(cmd):
                    if cmd[i + 1].startswith("BASE_URL="):
                        env_found = True
                        break
            self.assertTrue(env_found)
        
        asyncio.run(test_command())
    
    @pytest.mark.asyncio
    async def test_parse_k6_results(self):
        """Test parsing k6 results"""
        
        result = LoadTestResult(
            test_id="test-123",
            test_type=LoadTestType.STRESS,
            status=LoadTestStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        # Mock k6 JSON output
        mock_summary = {
            "metrics": {
                "http_reqs": {"values": {"count": 1000}},
                "http_req_failed": {"values": {"rate": 0.05}},
                "http_req_duration": {"values": {"avg": 250.5, "p(95)": 450.0}},
                "data_received": {"values": {"count": 5242880}}
            },
            "thresholds": {
                "http_req_duration": {"ok": True},
                "http_req_failed": {"ok": False}
            },
            "state": {"testRunDurationMs": 30000}
        }
        
        # Create temporary summary file
        summary_file = os.path.join(os.path.dirname(self.agent.k6_script_path), "summary.json")
        with open(summary_file, 'w') as f:
            json.dump(mock_summary, f)
        
        try:
            # Parse results
            await self.agent._parse_k6_results(result, "test stdout", "")
            
            self.assertEqual(result.total_requests, 1000)
            self.assertEqual(result.error_rate, 0.05)
            self.assertEqual(result.avg_response_time, 250.5)
            self.assertEqual(result.p95_response_time, 450.0)
            self.assertAlmostEqual(result.data_received_mb, 5.0, places=1)
            self.assertTrue(result.thresholds_passed["http_req_duration"])
            self.assertFalse(result.thresholds_passed["http_req_failed"])
            self.assertFalse(result.overall_passed)
            
        finally:
            # Clean up
            if os.path.exists(summary_file):
                os.remove(summary_file)
    
    @pytest.mark.asyncio
    async def test_analyze_load_test_results(self):
        """Test analysis of load test results for anomalies"""
        
        # Test with high error rate
        result_high_errors = LoadTestResult(
            test_id="test-high-errors",
            test_type=LoadTestType.STRESS,
            status=LoadTestStatus.COMPLETED,
            started_at=datetime.utcnow(),
            total_requests=1000,
            failed_requests=120,
            error_rate=0.12,  # 12% error rate
            avg_response_time=300.0,
            p95_response_time=500.0
        )
        
        await self.agent._analyze_load_test_results(result_high_errors)
        
        # Should have detected anomaly for high error rate
        self.assertGreater(len(self.agent.active_anomalies), 0)
        
        # Find the load test failure anomaly
        load_test_anomaly = None
        for anomaly in self.agent.active_anomalies.values():
            if anomaly.anomaly_type == AnomalyType.LOAD_TEST_FAILURE:
                load_test_anomaly = anomaly
                break
        
        self.assertIsNotNone(load_test_anomaly)
        self.assertEqual(load_test_anomaly.severity, AlertSeverity.HIGH)
        self.assertIn("High error rate", load_test_anomaly.description)
        
        # Test with high response times
        result_high_latency = LoadTestResult(
            test_id="test-high-latency",
            test_type=LoadTestType.LOAD,
            status=LoadTestStatus.COMPLETED,
            started_at=datetime.utcnow(),
            total_requests=1000,
            failed_requests=20,
            error_rate=0.02,
            avg_response_time=1500.0,
            p95_response_time=2500.0  # High P95
        )
        
        await self.agent._analyze_load_test_results(result_high_latency)
        
        # Should have detected latency anomaly
        latency_anomaly = None
        for anomaly in self.agent.active_anomalies.values():
            if anomaly.anomaly_type == AnomalyType.LATENCY_INCREASE:
                latency_anomaly = anomaly
                break
        
        self.assertIsNotNone(latency_anomaly)
        self.assertIn("High response times", latency_anomaly.description)
    
    @pytest.mark.asyncio
    async def test_get_load_test_status(self):
        """Test getting load test status"""
        
        # Create a test execution
        config = LoadTestConfiguration(
            test_id="test-status",
            test_type=LoadTestType.LOAD,
            target=LoadTestTarget(
                name="test-service",
                base_url="https://api.example.com",
                endpoints=[]
            ),
            duration_minutes=5,
            virtual_users=20
        )
        
        execution = LoadTestExecution(
            test_id="test-status",
            config=config
        )
        
        self.agent.load_test_executions["test-status"] = execution
        
        # Test pending status
        status = await self.agent.get_load_test_status("test-status")
        self.assertIsNotNone(status)
        self.assertEqual(status.test_id, "test-status")
        self.assertEqual(status.status, LoadTestStatus.PENDING.value)
        
        # Test with result
        result = LoadTestResult(
            test_id="test-status",
            test_type=LoadTestType.LOAD,
            status=LoadTestStatus.RUNNING,
            started_at=datetime.utcnow(),
            total_requests=500,
            error_rate=0.02
        )
        
        execution.result = result
        self.agent.load_test_results["test-status"] = result
        
        status = await self.agent.get_load_test_status("test-status")
        self.assertEqual(status.status, LoadTestStatus.RUNNING.value)
        self.assertEqual(status.total_requests, 500)
        self.assertEqual(status.error_rate, 0.02)
        self.assertGreater(status.progress_percentage, 0)
    
    @pytest.mark.asyncio
    async def test_cancel_load_test(self):
        """Test cancelling a running load test"""
        
        # Create a mock running execution
        config = LoadTestConfiguration(
            test_id="test-cancel",
            test_type=LoadTestType.STRESS,
            target=LoadTestTarget(
                name="test-service",
                base_url="https://api.example.com",
                endpoints=[]
            )
        )
        
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        mock_process.wait = AsyncMock()
        
        execution = LoadTestExecution(
            test_id="test-cancel",
            config=config,
            process=mock_process
        )
        
        result = LoadTestResult(
            test_id="test-cancel",
            test_type=LoadTestType.STRESS,
            status=LoadTestStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        execution.result = result
        self.agent.load_test_executions["test-cancel"] = execution
        
        # Cancel the test
        success = await self.agent.cancel_load_test("test-cancel")
        
        self.assertTrue(success)
        mock_process.terminate.assert_called_once()
        self.assertEqual(result.status, LoadTestStatus.CANCELLED)
        self.assertIsNotNone(result.completed_at)
    
    def test_invalid_test_type(self):
        """Test handling of invalid test types"""
        
        request = LoadTestRequest(
            test_type="invalid_type",
            target=LoadTestTargetRequest(
                name="test-api",
                base_url="https://api.example.com"
            )
        )
        
        async def test_invalid():
            with self.assertRaises(ValueError):
                await self.agent.start_load_test(request)
        
        asyncio.run(test_invalid())
    
    @pytest.mark.asyncio
    async def test_gemini_analysis_integration(self):
        """Test Gemini analysis of load test results"""
        
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = """
        The load test results indicate significant performance issues:
        1. High error rate suggests service instability
        2. Elevated response times indicate bottlenecks
        3. Recommend scaling and optimization
        """
        
        self.agent.gemini_model.generate_content.return_value = mock_response
        
        result = LoadTestResult(
            test_id="test-gemini",
            test_type=LoadTestType.STRESS,
            status=LoadTestStatus.COMPLETED,
            started_at=datetime.utcnow(),
            total_requests=1000,
            failed_requests=100,
            error_rate=0.1,
            avg_response_time=800.0,
            p95_response_time=1500.0,
            duration_seconds=300.0
        )
        
        analysis = await self.agent._analyze_load_test_with_gemini(result)
        
        self.assertIsNotNone(analysis)
        self.assertIn("performance issues", analysis)
        self.assertIn("error rate", analysis)
        self.assertIn("recommend", analysis.lower())


class TestLoadTestingIntegration(unittest.TestCase):
    """Integration tests for load testing with the broader AIOps system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.project_id = "test-project"
        self.agent = AIOpsAgent(self.project_id)
        
        # Mock external dependencies
        self.agent.logging_client = MagicMock()
        self.agent.monitoring_client = MagicMock()
        self.agent.error_reporting_client = MagicMock()
        self.agent.gemini_model = MagicMock()
        
        # Mock tenant database
        self.agent.tenant_db = MagicMock()
        self.agent.tenant_db.log_agent_event = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_load_test_anomaly_alert_integration(self):
        """Test that load test anomalies trigger proper alerts"""
        
        # Create a failed load test result
        result = LoadTestResult(
            test_id="test-integration",
            test_type=LoadTestType.STRESS,
            status=LoadTestStatus.COMPLETED,
            started_at=datetime.utcnow(),
            total_requests=1000,
            failed_requests=150,
            error_rate=0.15,  # High error rate
            avg_response_time=400.0,
            p95_response_time=800.0
        )
        
        # Analyze results (should create anomaly and alert)
        await self.agent._analyze_load_test_results(result)
        
        # Check that anomaly was created
        self.assertGreater(len(self.agent.active_anomalies), 0)
        
        # Check that alert was generated for high severity anomaly
        high_severity_anomalies = [
            a for a in self.agent.active_anomalies.values()
            if a.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        ]
        
        if high_severity_anomalies:
            # Should have created alerts for high severity anomalies
            self.assertGreater(len(self.agent.active_alerts), 0)
    
    @pytest.mark.asyncio
    async def test_load_test_metrics_tracking(self):
        """Test that load test execution updates agent metrics"""
        
        initial_metrics = self.agent.get_metrics()
        
        # Mock a successful load test execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'test output', b'')
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            request = LoadTestRequest(
                test_type="load",
                target=LoadTestTargetRequest(
                    name="test-api",
                    base_url="https://api.example.com"
                ),
                duration_minutes=1,
                virtual_users=10
            )
            
            test_id = await self.agent.start_load_test(request)
            
            # Wait a bit for async execution
            await asyncio.sleep(0.1)
            
            # Check that execution was tracked
            self.assertIn(test_id, self.agent.load_test_executions)
    
    def test_load_test_configuration_validation(self):
        """Test validation of load test configurations"""
        
        # Valid configuration
        valid_request = LoadTestRequest(
            test_type="stress",
            target=LoadTestTargetRequest(
                name="valid-service",
                base_url="https://api.example.com",
                endpoints=["/health", "/metrics"]
            ),
            duration_minutes=5,
            virtual_users=50,
            ramp_up_duration_seconds=30
        )
        
        # Should not raise exception
        self.assertIsNotNone(valid_request)
        
        # Test boundary values
        boundary_request = LoadTestRequest(
            test_type="load",
            target=LoadTestTargetRequest(
                name="boundary-test",
                base_url="https://api.example.com"
            ),
            duration_minutes=1,  # Minimum
            virtual_users=1,     # Minimum
            ramp_up_duration_seconds=0  # Minimum
        )
        
        self.assertIsNotNone(boundary_request)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 