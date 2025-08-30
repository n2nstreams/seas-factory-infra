#!/usr/bin/env python3
"""
Test Suite for AIOps Agent - Night 46 Implementation

This test suite validates:
- Log streaming functionality
- Anomaly detection using Gemini
- Alert management
- API endpoints
- Error handling
"""

import os
import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Test dependencies
from fastapi.testclient import TestClient

# Import components to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from aiops_agent import (
    AIOpsAgent, LogEntry, LogBatch, Anomaly, AlertSeverity, AnomalyType, LogProcessingStatus,
    LogStreamConfig
)
from main import app


class TestAIOpsAgent:
    """Test cases for the AIOps Agent core functionality"""
    
    @pytest.fixture
    def mock_google_cloud_clients(self):
        """Mock Google Cloud clients"""
        with patch('aiops_agent.GOOGLE_CLOUD_AVAILABLE', True), \
             patch('aiops_agent.cloud_logging.Client') as mock_logging, \
             patch('aiops_agent.monitoring_v3.MetricServiceClient') as mock_monitoring, \
             patch('aiops_agent.error_reporting.Client') as mock_error_reporting, \
             patch('aiops_agent.vertexai') as mock_vertexai, \
             patch('aiops_agent.GenerativeModel') as mock_gemini:
            
            # Setup mock responses
            mock_logging_instance = Mock()
            mock_logging.return_value = mock_logging_instance
            
            mock_monitoring_instance = Mock()
            mock_monitoring.return_value = mock_monitoring_instance
            
            mock_error_reporting_instance = Mock()
            mock_error_reporting.return_value = mock_error_reporting_instance
            
            mock_gemini_instance = Mock()
            mock_gemini.return_value = mock_gemini_instance
            
            yield {
                'logging': mock_logging_instance,
                'monitoring': mock_monitoring_instance,
                'error_reporting': mock_error_reporting_instance,
                'gemini': mock_gemini_instance
            }
    
    @pytest.fixture
    def aiops_agent(self, mock_google_cloud_clients):
        """Create AIOps agent instance for testing"""
        agent = AIOpsAgent("test-project")
        return agent
    
    @pytest.fixture
    def sample_log_entries(self):
        """Sample log entries for testing"""
        base_time = datetime.utcnow()
        
        return [
            LogEntry(
                timestamp=base_time,
                severity="INFO",
                service="api-backend",
                message="Request processed successfully",
                labels={"version": "1.0.0", "env": "prod"}
            ),
            LogEntry(
                timestamp=base_time + timedelta(seconds=1),
                severity="ERROR",
                service="api-backend",
                message="Database connection failed",
                labels={"version": "1.0.0", "env": "prod"}
            ),
            LogEntry(
                timestamp=base_time + timedelta(seconds=2),
                severity="ERROR",
                service="api-backend",
                message="Database connection failed",
                labels={"version": "1.0.0", "env": "prod"}
            ),
            LogEntry(
                timestamp=base_time + timedelta(seconds=3),
                severity="WARNING",
                service="user-service",
                message="High memory usage detected",
                labels={"version": "1.2.0", "env": "prod"}
            ),
            LogEntry(
                timestamp=base_time + timedelta(seconds=4),
                severity="CRITICAL",
                service="payment-service",
                message="Payment processing failed",
                labels={"version": "2.0.0", "env": "prod"}
            )
        ]
    
    @pytest.fixture
    def sample_log_batch(self, sample_log_entries):
        """Sample log batch for testing"""
        return LogBatch(
            batch_id=f"batch-{uuid.uuid4()}",
            logs=sample_log_entries,
            created_at=datetime.utcnow()
        )
    
    def test_agent_initialization(self, mock_google_cloud_clients):
        """Test agent initialization"""
        agent = AIOpsAgent("test-project")
        
        assert agent.project_id == "test-project"
        assert agent.default_batch_size == 100
        assert agent.default_batch_timeout == 300
        assert agent.anomaly_detection_enabled is True
        assert agent.gemini_analysis_enabled is True
        assert len(agent.log_batches) == 0
        assert len(agent.active_anomalies) == 0
        assert len(agent.active_alerts) == 0
    
    def test_log_batch_statistics(self, aiops_agent, sample_log_batch):
        """Test log batch statistics calculation"""
        stats = aiops_agent._calculate_batch_statistics(sample_log_batch)
        
        assert stats["total_logs"] == 5
        assert stats["error_count"] == 3  # 2 ERROR + 1 CRITICAL
        assert stats["warning_count"] == 1
        assert stats["error_rate"] == 0.6  # 3/5
        assert "api-backend" in stats["services"]
        assert stats["services"]["api-backend"] == 3
        assert stats["severities"]["ERROR"] == 2
        assert stats["severities"]["CRITICAL"] == 1
    
    def test_quick_anomaly_detection(self, aiops_agent, sample_log_batch):
        """Test rule-based anomaly detection"""
        stats = aiops_agent._calculate_batch_statistics(sample_log_batch)
        anomalies = aiops_agent._detect_quick_anomalies(sample_log_batch, stats)
        
        # Should detect high error rate (60% > 10% threshold)
        assert len(anomalies) >= 1
        
        error_spike_anomaly = next(
            (a for a in anomalies if a.anomaly_type == AnomalyType.ERROR_SPIKE), 
            None
        )
        assert error_spike_anomaly is not None
        assert error_spike_anomaly.severity in [AlertSeverity.HIGH, AlertSeverity.MEDIUM]
        assert error_spike_anomaly.confidence_score == 0.8
        assert "High error rate detected" in error_spike_anomaly.description
    
    def test_repeated_error_pattern_detection(self, aiops_agent):
        """Test detection of repeated error patterns"""
        # Create batch with repeated error messages
        repeated_logs = []
        base_time = datetime.utcnow()
        
        # Add 6 instances of the same error
        for i in range(6):
            repeated_logs.append(LogEntry(
                timestamp=base_time + timedelta(seconds=i),
                severity="ERROR",
                service="api-backend",
                message="Database connection timeout",
                labels={"error_code": "DB_TIMEOUT"}
            ))
        
        # Add some other logs
        repeated_logs.append(LogEntry(
            timestamp=base_time + timedelta(seconds=7),
            severity="INFO",
            service="api-backend",
            message="Request completed",
            labels={}
        ))
        
        batch = LogBatch(
            batch_id=f"batch-{uuid.uuid4()}",
            logs=repeated_logs,
            created_at=datetime.utcnow()
        )
        
        stats = aiops_agent._calculate_batch_statistics(batch)
        anomalies = aiops_agent._detect_quick_anomalies(batch, stats)
        
        # Should detect repeated pattern
        pattern_anomaly = next(
            (a for a in anomalies if a.anomaly_type == AnomalyType.UNUSUAL_PATTERN), 
            None
        )
        assert pattern_anomaly is not None
        assert "Repeated error pattern detected" in pattern_anomaly.description
        assert "occurred 6 times" in pattern_anomaly.description
    
    @pytest.mark.asyncio
    async def test_gemini_analysis_prompt_creation(self, aiops_agent, sample_log_entries):
        """Test Gemini analysis prompt creation"""
        stats = {"total_logs": 5, "error_rate": 0.4, "services": ["api-backend"], "time_span": 10.0}
        
        prompt = aiops_agent._create_gemini_analysis_prompt(sample_log_entries, stats)
        
        assert "BATCH STATISTICS:" in prompt
        assert "Total logs: 5" in prompt
        assert "Error rate: 40.0%" in prompt
        assert "LOG SAMPLE:" in prompt
        assert "api-backend" in prompt
        assert "Format your response as JSON" in prompt
        assert '"anomalies"' in prompt
    
    @pytest.mark.asyncio
    async def test_gemini_response_parsing(self, aiops_agent, sample_log_batch):
        """Test parsing of Gemini API responses"""
        # Mock Gemini response
        gemini_response = """
        {
            "anomalies": [
                {
                    "type": "error_spike",
                    "severity": "high",
                    "service": "api-backend",
                    "description": "High error rate detected in database connections",
                    "confidence": 0.85,
                    "recommended_actions": [
                        "Check database connection pool",
                        "Review recent database changes"
                    ],
                    "analysis": "The logs show repeated database connection failures indicating a potential infrastructure issue."
                }
            ]
        }
        """
        
        anomalies = aiops_agent._parse_gemini_response(gemini_response, sample_log_batch)
        
        assert len(anomalies) == 1
        anomaly = anomalies[0]
        assert anomaly.anomaly_type == AnomalyType.ERROR_SPIKE
        assert anomaly.severity == AlertSeverity.HIGH
        assert anomaly.service == "api-backend"
        assert anomaly.confidence_score == 0.85
        assert len(anomaly.recommended_actions) == 2
        assert "database connection failures" in anomaly.gemini_analysis
    
    @pytest.mark.asyncio
    async def test_gemini_response_parsing_with_markdown(self, aiops_agent, sample_log_batch):
        """Test parsing of Gemini responses with markdown formatting"""
        gemini_response = """```json
        {
            "anomalies": [
                {
                    "type": "performance_degradation",
                    "severity": "medium",
                    "service": "user-service",
                    "description": "Response time increasing",
                    "confidence": 0.7,
                    "recommended_actions": ["Scale up resources"],
                    "analysis": "Performance metrics show degradation."
                }
            ]
        }
        ```"""
        
        anomalies = aiops_agent._parse_gemini_response(gemini_response, sample_log_batch)
        
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == AnomalyType.PERFORMANCE_DEGRADATION
        assert anomalies[0].severity == AlertSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_gemini_response_parsing_invalid_json(self, aiops_agent, sample_log_batch):
        """Test handling of invalid JSON in Gemini response"""
        gemini_response = "This is not valid JSON"
        
        anomalies = aiops_agent._parse_gemini_response(gemini_response, sample_log_batch)
        
        assert len(anomalies) == 0  # Should return empty list for invalid JSON
    
    @pytest.mark.asyncio
    async def test_gemini_response_parsing_no_anomalies(self, aiops_agent, sample_log_batch):
        """Test parsing when no anomalies are found"""
        gemini_response = '{"anomalies": []}'
        
        anomalies = aiops_agent._parse_gemini_response(gemini_response, sample_log_batch)
        
        assert len(anomalies) == 0
    
    @pytest.mark.asyncio
    async def test_anomaly_handling_and_alerting(self, aiops_agent):
        """Test anomaly handling and alert creation"""
        # Create a high-severity anomaly
        anomaly = Anomaly(
            anomaly_id=f"anomaly-{uuid.uuid4()}",
            anomaly_type=AnomalyType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            service="auth-service",
            description="Unauthorized access attempt detected",
            gemini_analysis="Multiple failed login attempts from suspicious IP addresses",
            evidence=[],
            metrics={"failed_attempts": 50},
            detected_at=datetime.utcnow(),
            confidence_score=0.95,
            recommended_actions=["Block suspicious IPs", "Review access logs"]
        )
        
        # Handle the anomaly
        await aiops_agent._handle_detected_anomaly(anomaly)
        
        # Check that anomaly was stored
        assert anomaly.anomaly_id in aiops_agent.active_anomalies
        
        # Check that alert was created for critical severity
        active_alerts = await aiops_agent.get_active_alerts()
        assert len(active_alerts) == 1
        
        alert = active_alerts[0]
        assert alert.anomaly.anomaly_id == anomaly.anomaly_id
        assert alert.is_active
        assert "email" in alert.notification_channels
        assert "slack" in alert.notification_channels
    
    @pytest.mark.asyncio
    async def test_alert_acknowledgment(self, aiops_agent):
        """Test alert acknowledgment functionality"""
        # Create and add an alert
        anomaly = Anomaly(
            anomaly_id=f"anomaly-{uuid.uuid4()}",
            anomaly_type=AnomalyType.ERROR_SPIKE,
            severity=AlertSeverity.HIGH,
            service="test-service",
            description="Test anomaly",
            gemini_analysis="Test analysis",
            evidence=[],
            metrics={},
            detected_at=datetime.utcnow(),
            confidence_score=0.8,
            recommended_actions=[]
        )
        
        await aiops_agent._handle_detected_anomaly(anomaly)
        
        alerts = await aiops_agent.get_active_alerts()
        alert_id = alerts[0].alert_id
        
        # Acknowledge the alert
        success = await aiops_agent.acknowledge_alert(alert_id, "test-user")
        assert success is True
        
        # Check that alert is acknowledged
        updated_alert = aiops_agent.active_alerts[alert_id]
        assert updated_alert.acknowledged_at is not None
        assert updated_alert.is_active  # Still active until resolved
    
    @pytest.mark.asyncio
    async def test_alert_resolution(self, aiops_agent):
        """Test alert resolution functionality"""
        # Create and add an alert
        anomaly = Anomaly(
            anomaly_id=f"anomaly-{uuid.uuid4()}",
            anomaly_type=AnomalyType.LATENCY_INCREASE,
            severity=AlertSeverity.MEDIUM,
            service="test-service",
            description="Test anomaly",
            gemini_analysis="Test analysis",
            evidence=[],
            metrics={},
            detected_at=datetime.utcnow(),
            confidence_score=0.7,
            recommended_actions=[]
        )
        
        await aiops_agent._handle_detected_anomaly(anomaly)
        
        alerts = await aiops_agent.get_active_alerts()
        alert_id = alerts[0].alert_id
        
        # Resolve the alert
        success = await aiops_agent.resolve_alert(alert_id, "test-user", "Fixed the issue")
        assert success is True
        
        # Check that alert is resolved
        updated_alert = aiops_agent.active_alerts[alert_id]
        assert updated_alert.resolved_at is not None
        assert not updated_alert.is_active
    
    @pytest.mark.asyncio
    async def test_get_anomalies_filtering(self, aiops_agent):
        """Test anomaly filtering functionality"""
        # Create anomalies with different services and severities
        anomalies = [
            Anomaly(
                anomaly_id="anomaly-1",
                anomaly_type=AnomalyType.ERROR_SPIKE,
                severity=AlertSeverity.HIGH,
                service="service-a",
                description="High severity in service A",
                gemini_analysis="Analysis A",
                evidence=[],
                metrics={},
                detected_at=datetime.utcnow(),
                confidence_score=0.8,
                recommended_actions=[]
            ),
            Anomaly(
                anomaly_id="anomaly-2",
                anomaly_type=AnomalyType.LATENCY_INCREASE,
                severity=AlertSeverity.MEDIUM,
                service="service-b",
                description="Medium severity in service B",
                gemini_analysis="Analysis B",
                evidence=[],
                metrics={},
                detected_at=datetime.utcnow(),
                confidence_score=0.6,
                recommended_actions=[]
            ),
            Anomaly(
                anomaly_id="anomaly-3",
                anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                severity=AlertSeverity.HIGH,
                service="service-a",
                description="Another high severity in service A",
                gemini_analysis="Analysis C",
                evidence=[],
                metrics={},
                detected_at=datetime.utcnow(),
                confidence_score=0.9,
                recommended_actions=[]
            )
        ]
        
        # Add anomalies to agent
        for anomaly in anomalies:
            aiops_agent.active_anomalies[anomaly.anomaly_id] = anomaly
        
        # Test service filtering
        service_a_anomalies = await aiops_agent.get_anomalies(service="service-a")
        assert len(service_a_anomalies) == 2
        
        # Test severity filtering
        high_severity_anomalies = await aiops_agent.get_anomalies(severity=AlertSeverity.HIGH)
        assert len(high_severity_anomalies) == 2
        
        # Test combined filtering
        service_a_high = await aiops_agent.get_anomalies(service="service-a", severity=AlertSeverity.HIGH)
        assert len(service_a_high) == 2
        
        # Test limit
        limited_anomalies = await aiops_agent.get_anomalies(limit=1)
        assert len(limited_anomalies) == 1
    
    def test_metrics_collection(self, aiops_agent):
        """Test metrics collection"""
        # Add some test data
        aiops_agent.metrics["logs_processed"] = 100
        aiops_agent.metrics["anomalies_detected"] = 5
        aiops_agent.metrics["alerts_generated"] = 2
        
        # Add some test objects
        test_batch = LogBatch(
            batch_id="test-batch",
            logs=[],
            created_at=datetime.utcnow(),
            status=LogProcessingStatus.PROCESSING
        )
        aiops_agent.log_batches["test-batch"] = test_batch
        
        metrics = aiops_agent.get_metrics()
        
        assert metrics["logs_processed"] == 100
        assert metrics["anomalies_detected"] == 5
        assert metrics["alerts_generated"] == 2
        assert metrics["active_streams"] == 0
        assert metrics["processing_batches"] == 1
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, aiops_agent):
        """Test cleanup of old data"""
        old_time = datetime.utcnow() - timedelta(days=10)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        
        # Add old and recent data
        old_batch = LogBatch(
            batch_id="old-batch",
            logs=[],
            created_at=old_time
        )
        recent_batch = LogBatch(
            batch_id="recent-batch",
            logs=[],
            created_at=recent_time
        )
        
        aiops_agent.log_batches["old-batch"] = old_batch
        aiops_agent.log_batches["recent-batch"] = recent_batch
        
        # Run cleanup with 7-day retention
        await aiops_agent.cleanup_old_data(retention_days=7)
        
        # Check that old data was removed and recent data kept
        assert "old-batch" not in aiops_agent.log_batches
        assert "recent-batch" in aiops_agent.log_batches


class TestAIOpsAPI:
    """Test cases for the AIOps Agent API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def tenant_headers(self):
        """Mock tenant headers"""
        return {
            "X-Tenant-ID": "test-tenant",
            "X-User-ID": "test-user"
        }
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "google_cloud_available" in data
        assert "agent_initialized" in data
    
    @patch('main.GOOGLE_CLOUD_AVAILABLE', True)
    @patch('main.aiops_agent')
    def test_start_log_streaming_endpoint(self, mock_agent, client, tenant_headers):
        """Test log streaming start endpoint"""
        mock_agent.start_log_streaming = AsyncMock(return_value="stream-123")
        mock_agent.tenant_db.log_agent_event = AsyncMock()
        
        config = {
            "project_id": "test-project",
            "services": ["api-backend"],
            "severity_filter": ["ERROR", "WARNING"],
            "batch_size": 50,
            "batch_timeout_seconds": 300,
            "enable_gemini_analysis": True
        }
        
        response = client.post("/start-log-streaming", json=config, headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["stream_id"] == "stream-123"
        assert "Log streaming started" in data["message"]
    
    @patch('main.aiops_agent')
    def test_get_anomalies_endpoint(self, mock_agent, client, tenant_headers):
        """Test get anomalies endpoint"""
        mock_anomaly = Mock()
        mock_anomaly.to_dict.return_value = {
            "anomaly_id": "test-anomaly",
            "description": "Test anomaly"
        }
        
        mock_agent.get_anomalies = AsyncMock(return_value=[mock_anomaly])
        
        response = client.get("/anomalies?service=test-service&severity=high&limit=10", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_anomalies"] == 1
        assert len(data["anomalies"]) == 1
    
    def test_get_anomalies_invalid_severity(self, client, tenant_headers):
        """Test get anomalies with invalid severity"""
        response = client.get("/anomalies?severity=invalid", headers=tenant_headers)
        
        assert response.status_code == 400
        assert "Invalid severity" in response.json()["detail"]
    
    @patch('main.aiops_agent')
    def test_acknowledge_alert_endpoint(self, mock_agent, client, tenant_headers):
        """Test acknowledge alert endpoint"""
        mock_agent.acknowledge_alert = AsyncMock(return_value=True)
        
        response = client.post("/alerts/test-alert-id/acknowledge", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "acknowledged" in data["message"]
    
    @patch('main.aiops_agent')
    def test_acknowledge_alert_not_found(self, mock_agent, client, tenant_headers):
        """Test acknowledge alert when alert not found"""
        mock_agent.acknowledge_alert = AsyncMock(return_value=False)
        
        response = client.post("/alerts/nonexistent-alert/acknowledge", headers=tenant_headers)
        
        assert response.status_code == 404
        assert "Alert not found" in response.json()["detail"]
    
    @patch('main.aiops_agent')
    def test_resolve_alert_endpoint(self, mock_agent, client, tenant_headers):
        """Test resolve alert endpoint"""
        mock_agent.resolve_alert = AsyncMock(return_value=True)
        
        response = client.post(
            "/alerts/test-alert-id/resolve?resolution_note=Fixed the issue", 
            headers=tenant_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "resolved" in data["message"]
    
    @patch('main.aiops_agent')
    def test_get_metrics_endpoint(self, mock_agent, client, tenant_headers):
        """Test get metrics endpoint"""
        mock_agent.get_metrics.return_value = {
            "logs_processed": 1000,
            "anomalies_detected": 10,
            "alerts_generated": 5
        }
        mock_agent.tenant_db._get_current_timestamp.return_value = datetime.utcnow()
        
        response = client.get("/metrics", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["metrics"]["logs_processed"] == 1000
        assert "timestamp" in data
    
    @patch('main.aiops_agent')
    def test_cleanup_endpoint(self, mock_agent, client, tenant_headers):
        """Test cleanup endpoint"""
        mock_agent.cleanup_old_data = AsyncMock()
        
        response = client.post("/cleanup?retention_days=14", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "14 days" in data["message"]
        assert data["retention_days"] == 14
    
    @patch('main.aiops_agent')
    def test_get_streams_endpoint(self, mock_agent, client, tenant_headers):
        """Test get active streams endpoint"""
        mock_agent.log_streams = {"stream-1": Mock(), "stream-2": Mock()}
        mock_batch = Mock()
        mock_batch.status.value = "processing"
        mock_agent.log_batches = {"batch-1": mock_batch}
        
        response = client.get("/streams", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["active_streams"] == 2
        assert len(data["stream_ids"]) == 2
        assert data["processing_batches"] == 1
    
    @patch('main.aiops_agent')
    def test_stop_stream_endpoint(self, mock_agent, client, tenant_headers):
        """Test stop log stream endpoint"""
        mock_agent.log_streams = {"stream-123": Mock()}
        
        response = client.delete("/streams/stream-123", headers=tenant_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stopped" in data["message"]
    
    @patch('main.aiops_agent')
    def test_stop_stream_not_found(self, mock_agent, client, tenant_headers):
        """Test stop log stream when stream not found"""
        mock_agent.log_streams = {}
        
        response = client.delete("/streams/nonexistent-stream", headers=tenant_headers)
        
        assert response.status_code == 404
        assert "Log stream not found" in response.json()["detail"]


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def aiops_agent_no_gcloud(self):
        """Create agent without Google Cloud libraries"""
        with patch('aiops_agent.GOOGLE_CLOUD_AVAILABLE', False):
            agent = AIOpsAgent("test-project")
            return agent
    
    def test_agent_without_google_cloud(self, aiops_agent_no_gcloud):
        """Test agent behavior without Google Cloud libraries"""
        agent = aiops_agent_no_gcloud
        
        assert agent.logging_client is None
        assert agent.monitoring_client is None
        assert agent.error_reporting_client is None
        assert agent.gemini_model is None
    
    @pytest.mark.asyncio
    async def test_start_streaming_without_gcloud(self, aiops_agent_no_gcloud):
        """Test starting log streaming without Google Cloud libraries"""
        config = LogStreamConfig(
            project_id="test-project",
            services=["test-service"]
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException equivalent
            await aiops_agent_no_gcloud.start_log_streaming(config)
    
    def test_log_entry_serialization(self):
        """Test LogEntry serialization"""
        log_entry = LogEntry(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            severity="ERROR",
            service="test-service",
            message="Test message",
            labels={"key": "value"},
            trace_id="trace-123",
            span_id="span-456"
        )
        
        serialized = log_entry.to_dict()
        
        assert serialized["timestamp"] == "2024-01-15T12:00:00"
        assert serialized["severity"] == "ERROR"
        assert serialized["service"] == "test-service"
        assert serialized["message"] == "Test message"
        assert serialized["labels"] == {"key": "value"}
        assert serialized["trace_id"] == "trace-123"
        assert serialized["span_id"] == "span-456"
    
    def test_anomaly_serialization(self):
        """Test Anomaly serialization"""
        anomaly = Anomaly(
            anomaly_id="test-anomaly",
            anomaly_type=AnomalyType.ERROR_SPIKE,
            severity=AlertSeverity.HIGH,
            service="test-service",
            description="Test description",
            gemini_analysis="Test analysis",
            evidence=[],
            metrics={"error_rate": 0.5},
            detected_at=datetime(2024, 1, 15, 12, 0, 0),
            confidence_score=0.8,
            recommended_actions=["action1", "action2"],
            affected_resources=["resource1"]
        )
        
        serialized = anomaly.to_dict()
        
        assert serialized["anomaly_id"] == "test-anomaly"
        assert serialized["anomaly_type"] == "error_spike"
        assert serialized["severity"] == "high"
        assert serialized["service"] == "test-service"
        assert serialized["confidence_score"] == 0.8
        assert serialized["recommended_actions"] == ["action1", "action2"]
        assert serialized["metrics"] == {"error_rate": 0.5}


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"]) 