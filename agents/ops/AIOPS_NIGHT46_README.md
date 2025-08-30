# AIOps Agent - Night 46 Implementation

## Overview

The AIOps Agent implements **Night 46** from the AI SaaS Factory masterplan: "AIOpsAgent – stream logs, detect anomalies using Gemini on log batches." This agent provides AI-driven operations and monitoring capabilities with real-time log streaming from Google Cloud Logging and intelligent anomaly detection using Google's Gemini AI.

## Features

### ✅ Night 46 Requirements Complete

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **Stream logs from Google Cloud Logging** | ✅ Real-time log streaming with configurable filters | Complete |
| **Detect anomalies using Gemini on log batches** | ✅ Gemini 1.5 Pro integration for intelligent analysis | Complete |
| **Batch processing** | ✅ Configurable batch size and timeout processing | Complete |
| **Alerting system** | ✅ Multi-channel alerting with severity-based escalation | Complete |

### 🚀 Core Capabilities

- **Real-time Log Streaming**: Stream logs from Google Cloud Logging with configurable filters
- **AI-Powered Anomaly Detection**: Use Gemini 1.5 Pro for intelligent pattern recognition
- **Batch Processing**: Process logs in configurable batches for efficient analysis
- **Multi-Channel Alerting**: Email, Slack, and custom notification channels
- **Tenant Isolation**: Built-in multi-tenant support with row-level security
- **Performance Monitoring**: Real-time metrics and performance tracking
- **Rule-Based Detection**: Fast pattern detection for common anomaly types
- **Alert Management**: Acknowledge, resolve, and track alert lifecycle

### 🔍 Anomaly Types Detected

- **Error Spikes**: Sudden increases in error rates
- **Latency Increases**: Performance degradation detection
- **Unusual Patterns**: Repeated error messages and unexpected behaviors
- **Resource Exhaustion**: Memory, CPU, and storage issues
- **Security Incidents**: Unauthorized access attempts and suspicious activity
- **Performance Degradation**: Service reliability issues

## Architecture

```
AIOps Agent Architecture
├── Log Streaming Engine
│   ├── Google Cloud Logging Integration
│   ├── Real-time Stream Processing
│   └── Configurable Filtering
├── Batch Processing System
│   ├── Configurable Batch Size/Timeout
│   ├── Statistical Analysis
│   └── Background Processing
├── Anomaly Detection Engine
│   ├── Rule-Based Quick Detection
│   ├── Gemini AI Analysis
│   └── Confidence Scoring
├── Alert Management
│   ├── Severity-Based Escalation
│   ├── Multi-Channel Notifications
│   └── Alert Lifecycle Tracking
└── API Layer
    ├── FastAPI REST Endpoints
    ├── Tenant Isolation
    └── Real-time Metrics
```

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export DB_HOST="your-db-host"
export DB_NAME="factorydb"
export DB_USER="factoryadmin"
export DB_PASSWORD="your-password"
```

### 2. Run the Service

```bash
# Start the AIOps Agent
python agents/ops/main.py

# Or run with custom port
PORT=8086 python agents/ops/main.py
```

### 3. Start Log Streaming

```python
import httpx

config = {
    "project_id": "your-project-id",
    "services": ["api-backend", "user-service"],
    "severity_filter": ["ERROR", "WARNING", "CRITICAL"],
    "batch_size": 100,
    "batch_timeout_seconds": 300,
    "enable_gemini_analysis": True
}

response = httpx.post("http://localhost:8086/start-log-streaming", json=config)
print(f"Stream ID: {response.json()['stream_id']}")
```

## API Documentation

### Authentication

All endpoints require tenant context headers:

```
X-Tenant-ID: your-tenant-id
X-User-ID: your-user-id (optional)
```

### Core Endpoints

#### Start Log Streaming

```http
POST /start-log-streaming
Content-Type: application/json

{
    "project_id": "your-project-id",
    "services": ["service1", "service2"],
    "severity_filter": ["ERROR", "WARNING"],
    "batch_size": 100,
    "batch_timeout_seconds": 300,
    "enable_gemini_analysis": true
}
```

**Response:**
```json
{
    "status": "success",
    "stream_id": "stream-uuid",
    "message": "Log streaming started for project your-project-id",
    "config": { ... }
}
```

#### Get Anomalies

```http
GET /anomalies?service=api-backend&severity=high&limit=50
```

**Response:**
```json
{
    "status": "success",
    "total_anomalies": 5,
    "anomalies": [
        {
            "anomaly_id": "anomaly-uuid",
            "anomaly_type": "error_spike",
            "severity": "high",
            "service": "api-backend",
            "description": "High error rate detected: 25.0% (50/200 logs)",
            "gemini_analysis": "Detailed AI analysis...",
            "evidence_count": 10,
            "metrics": { "error_rate": 0.25 },
            "detected_at": "2024-01-15T12:00:00Z",
            "confidence_score": 0.85,
            "recommended_actions": [
                "Investigate recent deployments",
                "Check database connectivity"
            ]
        }
    ]
}
```

#### Get Active Alerts

```http
GET /alerts
```

**Response:**
```json
{
    "status": "success",
    "active_alerts": 2,
    "alerts": [
        {
            "alert_id": "alert-uuid",
            "anomaly": { ... },
            "notification_channels": ["email", "slack"],
            "created_at": "2024-01-15T12:00:00Z",
            "acknowledged_at": null,
            "resolved_at": null,
            "duration_seconds": 1800,
            "is_active": true,
            "escalated": false
        }
    ]
}
```

#### Acknowledge Alert

```http
POST /alerts/{alert_id}/acknowledge
```

#### Resolve Alert

```http
POST /alerts/{alert_id}/resolve?resolution_note=Fixed database connection issue
```

#### Get Metrics

```http
GET /metrics
```

**Response:**
```json
{
    "status": "success",
    "metrics": {
        "logs_processed": 1000,
        "batches_created": 10,
        "anomalies_detected": 5,
        "alerts_generated": 2,
        "gemini_api_calls": 8,
        "active_streams": 1,
        "active_anomalies": 3,
        "active_alerts": 2,
        "pending_batches": 0,
        "processing_batches": 1
    },
    "timestamp": "2024-01-15T12:00:00Z"
}
```

### Management Endpoints

#### Get Active Streams

```http
GET /streams
```

#### Stop Log Stream

```http
DELETE /streams/{stream_id}
```

#### Cleanup Old Data

```http
POST /cleanup?retention_days=7
```

#### Health Check

```http
GET /health
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | `saas-factory-prod` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | Required |
| `PORT` | Service port | `8086` |
| `HOST` | Service host | `0.0.0.0` |
| `DB_HOST` | Database host | `localhost` |
| `DB_NAME` | Database name | `factorydb` |
| `DB_USER` | Database user | `factoryadmin` |
| `DB_PASSWORD` | Database password | Required |

### Log Stream Configuration

```python
class LogStreamConfig:
    project_id: str                    # GCP project ID
    services: List[str] = []          # Filter by services (empty = all)
    severity_filter: List[str] = ["ERROR", "WARNING", "INFO"]
    batch_size: int = 100             # Logs per batch (10-1000)
    batch_timeout_seconds: int = 300  # Max wait time (60-3600)
    enable_gemini_analysis: bool = True
```

### Anomaly Detection Thresholds

```python
# Rule-based detection thresholds
ERROR_RATE_THRESHOLD = 0.1          # 10% error rate
REPEATED_ERROR_THRESHOLD = 5        # 5+ identical errors
CONFIDENCE_THRESHOLD = 0.7          # Minimum confidence score
```

## Gemini AI Integration

### Analysis Prompt

The agent sends structured prompts to Gemini 1.5 Pro:

```
Analyze the following log batch for anomalies and unusual patterns:

BATCH STATISTICS:
- Total logs: 100
- Error rate: 15.0%
- Services: ["api-backend", "user-service"]
- Time span: 120.5 seconds

LOG SAMPLE:
[2024-01-15T12:00:00] ERROR api-backend: Database connection failed
[2024-01-15T12:00:01] ERROR api-backend: Database connection failed
...

Please analyze this log data and identify any anomalies. Look for:
1. Unusual error patterns or spikes
2. Performance degradation indicators
3. Security-related issues
4. Resource exhaustion signs
5. Service reliability problems
```

### Expected Response Format

```json
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
            "analysis": "The logs show repeated database connection failures..."
        }
    ]
}
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY agents/ops/ ./ops/
COPY agents/shared/ ./shared/

EXPOSE 8086

CMD ["python", "ops/main.py"]
```

### Cloud Run Deployment

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: aiops-agent
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "5"
    spec:
      containers:
      - image: gcr.io/your-project/aiops-agent:latest
        ports:
        - containerPort: 8086
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        - name: DB_HOST
          value: "your-db-host"
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiops-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aiops-agent
  template:
    metadata:
      labels:
        app: aiops-agent
    spec:
      containers:
      - name: aiops-agent
        image: gcr.io/your-project/aiops-agent:latest
        ports:
        - containerPort: 8086
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: aiops-agent-service
spec:
  selector:
    app: aiops-agent
  ports:
  - port: 80
    targetPort: 8086
  type: LoadBalancer
```

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest agents/ops/test_aiops_agent.py -v

# Run specific test class
pytest agents/ops/test_aiops_agent.py::TestAIOpsAgent -v

# Run with coverage
pytest agents/ops/test_aiops_agent.py --cov=agents.ops --cov-report=html
```

### Test Categories

1. **Core Functionality Tests**
   - Agent initialization
   - Log batch processing
   - Anomaly detection algorithms
   - Alert management

2. **Gemini Integration Tests**
   - Prompt generation
   - Response parsing
   - Error handling

3. **API Endpoint Tests**
   - All REST endpoints
   - Authentication/authorization
   - Error responses

4. **Edge Case Tests**
   - Missing dependencies
   - Invalid configurations
   - Network failures

### Example Test Run

```bash
$ pytest agents/ops/test_aiops_agent.py -v

agents/ops/test_aiops_agent.py::TestAIOpsAgent::test_agent_initialization PASSED
agents/ops/test_aiops_agent.py::TestAIOpsAgent::test_log_batch_statistics PASSED
agents/ops/test_aiops_agent.py::TestAIOpsAgent::test_quick_anomaly_detection PASSED
agents/ops/test_aiops_agent.py::TestAIOpsAgent::test_gemini_response_parsing PASSED
agents/ops/test_aiops_agent.py::TestAIOpsAPI::test_health_endpoint PASSED
agents/ops/test_aiops_agent.py::TestAIOpsAPI::test_start_log_streaming_endpoint PASSED

========================= 25 passed in 2.45s =========================
```

## Integration with SaaS Factory

### Agent Orchestration

The AIOps Agent integrates with the Project Orchestrator:

```python
# In orchestrator/project_orchestrator.py
async def monitor_deployment(self, project_id: str):
    """Monitor deployed project using AIOps Agent"""
    
    # Start log streaming for the project
    config = {
        "project_id": project_id,
        "services": self.get_project_services(project_id),
        "enable_gemini_analysis": True
    }
    
    aiops_response = await self.call_agent(
        "aiops",
        "start-log-streaming",
        config
    )
    
    return aiops_response["stream_id"]
```

### Dashboard Integration

Real-time metrics display in the UI dashboard:

```typescript
// In ui/src/components/AIOpsMetrics.tsx
const AIOpsMetrics = () => {
    const [metrics, setMetrics] = useState(null);
    const [alerts, setAlerts] = useState([]);
    
    useEffect(() => {
        const fetchMetrics = async () => {
            const response = await fetch('/api/aiops/metrics');
            const data = await response.json();
            setMetrics(data.metrics);
        };
        
        const fetchAlerts = async () => {
            const response = await fetch('/api/aiops/alerts');
            const data = await response.json();
            setAlerts(data.alerts);
        };
        
        fetchMetrics();
        fetchAlerts();
        
        // Refresh every 30 seconds
        const interval = setInterval(() => {
            fetchMetrics();
            fetchAlerts();
        }, 30000);
        
        return () => clearInterval(interval);
    }, []);
    
    return (
        <div className="aiops-metrics">
            <MetricsPanel metrics={metrics} />
            <AlertsPanel alerts={alerts} />
        </div>
    );
};
```

### Event Integration

Pub/Sub event publishing for anomalies:

```python
# Publish anomaly events
async def _handle_detected_anomaly(self, anomaly: Anomaly):
    """Handle detected anomaly with event publishing"""
    
    # Store locally
    self.active_anomalies[anomaly.anomaly_id] = anomaly
    
    # Publish to Pub/Sub for other agents
    event_data = {
        "event_type": "anomaly_detected",
        "anomaly": anomaly.to_dict(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await self.publish_event("aiops-events", event_data)
    
    # Create alert if high severity
    if anomaly.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
        await self._create_alert(anomaly)
```

## Monitoring and Observability

### Metrics Collection

The agent exposes the following metrics:

- **Operational Metrics**: logs_processed, batches_created, anomalies_detected
- **Performance Metrics**: gemini_api_calls, processing_latency, error_rates
- **Resource Metrics**: active_streams, memory_usage, cpu_utilization
- **Business Metrics**: alert_resolution_time, false_positive_rate

### Logging

Structured logging with different levels:

```python
# INFO: Normal operations
logger.info(f"Started log streaming {stream_id} for project {project_id}")

# WARNING: Potential issues
logger.warning(f"High batch processing latency: {latency:.2f}s")

# ERROR: Error conditions
logger.error(f"Failed to process batch {batch_id}: {error}")

# DEBUG: Detailed debugging
logger.debug(f"Gemini response: {response_text[:100]}...")
```

### Health Checks

Multiple health check levels:

1. **Basic Health**: Service responsiveness
2. **Dependency Health**: Google Cloud connectivity
3. **Functional Health**: End-to-end log processing
4. **Performance Health**: Response time thresholds

## Troubleshooting

### Common Issues

#### 1. Google Cloud Authentication

```bash
# Verify credentials
gcloud auth application-default login

# Check service account permissions
gcloud projects get-iam-policy your-project-id

# Required roles:
# - Logging Viewer
# - AI Platform User
# - Error Reporting Writer
```

#### 2. Log Streaming Issues

```python
# Check log filters
response = await aiops_agent.get_active_streams()
print(f"Active streams: {response['active_streams']}")

# Verify log availability
gcloud logging read "timestamp >= '2024-01-15T12:00:00Z'" --limit=10
```

#### 3. Gemini API Issues

```python
# Check Vertex AI configuration
import vertexai
vertexai.init(project="your-project", location="us-central1")

# Test model availability
from vertexai.generative_models import GenerativeModel
model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content("Hello")
```

#### 4. Performance Issues

```bash
# Monitor resource usage
docker stats aiops-agent

# Check database connections
psql -h db-host -U factoryadmin -d factorydb -c "SELECT count(*) FROM pg_stat_activity;"

# Analyze slow queries
tail -f /var/log/postgresql/postgresql.log | grep "slow query"
```

## Security Considerations

### Authentication & Authorization

- **Service Account**: Use minimal permissions for Google Cloud access
- **Database**: Row-level security for tenant isolation
- **API**: Tenant context validation on all endpoints
- **Secrets**: Use Google Secret Manager for sensitive data

### Data Privacy

- **Log Data**: Anonymize PII before processing
- **Retention**: Configurable data retention periods
- **Encryption**: Encrypt data in transit and at rest
- **Audit**: Log all access and modifications

### Network Security

- **TLS**: Enforce HTTPS for all communications
- **Firewall**: Restrict access to necessary ports only
- **VPC**: Deploy in private networks when possible
- **IAM**: Principle of least privilege for all services

## Future Enhancements

### Planned Features

1. **Machine Learning Models**
   - Custom anomaly detection models
   - Time series forecasting
   - Behavioral baseline learning

2. **Multi-Cloud Support**
   - AWS CloudWatch integration
   - Azure Monitor integration
   - Hybrid cloud monitoring

3. **Advanced Analytics**
   - Root cause analysis automation
   - Impact prediction
   - Capacity planning

4. **Integration Improvements**
   - Slack/Teams notifications
   - PagerDuty integration
   - JIRA ticket creation

### Performance Optimizations

1. **Streaming Optimizations**
   - Connection pooling
   - Parallel processing
   - Memory-efficient batching

2. **AI Model Improvements**
   - Fine-tuned models for specific domains
   - Reduced latency inference
   - Cost optimization

## Support

### Documentation

- [Google Cloud Logging](https://cloud.google.com/logging/docs)
- [Vertex AI Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Troubleshooting

For issues and support:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Verify configuration and permissions
4. Test individual components in isolation

### Contributing

To contribute to the AIOps Agent:

1. Follow the existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Ensure security best practices

---

**Night 46 Implementation Complete** ✅

The AIOps Agent successfully implements all requirements for Night 46 of the AI SaaS Factory masterplan, providing a robust foundation for AI-driven operations and monitoring. 