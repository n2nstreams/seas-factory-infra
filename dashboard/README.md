# SaaS Factory Event Dashboard

Real-time event monitoring dashboard with WebSocket streaming for the SaaS Factory platform.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  React Frontend │◄──►│  FastAPI Backend│◄──►│  WebSocket Mgr  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Glassmorphism  │    │  REST API       │    │  Event History  │
│  UI Components  │    │  WebSocket API  │    │  Client Manager │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                                ▼
                    ┌─────────────────┐
                    │                 │
                    │  Agent System   │
                    │  (Pub/Sub)      │
                    │                 │
                    └─────────────────┘
```

## Features

### 🔄 Real-time Event Streaming
- **WebSocket Connections**: Sub-second latency event streaming
- **Auto-reconnection**: Robust connection handling with automatic retry
- **Client Management**: Support for 100+ concurrent connections
- **Event History**: Maintains rolling history of 1000 events

### 🎨 Modern UI Design
- **Glassmorphism Theme**: Natural olive green color scheme
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live connection status and event counts
- **Interactive Components**: Collapsible panels and tabbed interface

### 🔍 Advanced Filtering
- **Multi-dimensional Filters**: Event type, source, priority, time range
- **Text Search**: Full-text search across event data
- **Real-time Application**: Filters apply instantly without page reload
- **Active Filter Display**: Visual indicators for applied filters

### 📊 Live Analytics
- **Event Metrics**: Events per minute charting
- **Priority Distribution**: Visual breakdown of event priorities
- **Agent Activity**: Real-time agent performance monitoring
- **Event Type Analysis**: Breakdown of event types and frequencies

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (for production scaling)

### Backend Setup
```bash
cd dashboard
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd ui
npm install
```

## Configuration

### Environment Variables
Create a `.env` file in the dashboard directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# WebSocket Configuration
MAX_CONNECTIONS=100
MAX_HISTORY_SIZE=1000
PING_INTERVAL=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend Configuration
Update `ui/src/pages/EventDashboard.tsx` WebSocket URL:

```typescript
const wsUrl = `ws://${window.location.host}/ws/${clientId}`;
```

## Usage

### Starting the Services

#### Development Mode
```bash
# Terminal 1 - Backend
cd dashboard
python app.py

# Terminal 2 - Frontend
cd ui
npm run dev
```

#### Production Mode
```bash
# Using Docker Compose
docker-compose up -d

# Or using deployment script
cd dashboard
./deploy.sh production
```

### Accessing the Dashboard
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws/{client_id}
- **Built-in Dashboard**: http://localhost:8000/dashboard

## API Reference

### REST Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "websocket_manager": "available",
  "active_connections": 5
}
```

#### Get Metrics
```http
GET /api/metrics
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "active_connections": 5,
  "total_connections": 127,
  "events_sent": 1543,
  "last_activity": "2024-01-15T10:29:45Z",
  "event_history_size": 234
}
```

#### Get Event History
```http
GET /api/events/history?limit=100
```

**Response:**
```json
[
  {
    "event_type": "agent_request",
    "data": {
      "agent": "requirements_agent",
      "payload": "..."
    },
    "timestamp": "2024-01-15T10:29:30Z",
    "source": "orchestrator",
    "priority": "normal"
  }
]
```

#### Apply Event Filter
```http
POST /api/events/filter
Content-Type: application/json

{
  "event_types": ["agent_request", "agent_response"],
  "sources": ["requirements_agent"],
  "priority": ["high", "normal"],
  "search": "error",
  "time_range": "1h"
}
```

#### Send Test Event
```http
POST /api/test/publish-event
Content-Type: application/json

{
  "event_type": "test",
  "source": "dashboard",
  "priority": "normal",
  "data": {
    "message": "Test event",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### WebSocket API

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client-123');
```

#### Event Message Format
```json
{
  "event_type": "agent_request",
  "data": {
    "agent": "requirements_agent",
    "payload": "Generate requirements for e-commerce platform"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "orchestrator",
  "priority": "normal"
}
```

#### Client Filter Update
```javascript
ws.send(JSON.stringify({
  "type": "filter",
  "filters": {
    "event_types": ["agent_request"],
    "priority": ["high"]
  }
}));
```

## Performance Metrics

### WebSocket Performance
- **Latency**: < 50ms for event delivery
- **Throughput**: 1000+ events/second
- **Connections**: 100+ concurrent clients
- **Memory**: < 100MB for 1000 events in history

### Frontend Performance
- **Initial Load**: < 2 seconds
- **Event Rendering**: < 10ms per event
- **Memory Usage**: < 50MB for 1000 events
- **Bundle Size**: < 1MB gzipped

## Event Types

### Agent Events
- `agent_request`: Agent receives a request
- `agent_response`: Agent sends a response
- `agent_error`: Agent encounters an error

### System Events
- `system_health`: System health check
- `metrics`: Performance metrics
- `alerts`: System alerts

### Dashboard Events
- `connection`: WebSocket connection events
- `test`: Test events from dashboard

## Integration

### Adding New Event Sources
1. Import WebSocket manager:
```python
from agents.shared.websocket_manager import get_websocket_manager, EventMessage
```

2. Create and broadcast event:
```python
event = EventMessage(
    event_type="custom_event",
    data={"key": "value"},
    timestamp=datetime.now(timezone.utc),
    source="my_agent",
    priority="normal"
)

websocket_manager = get_websocket_manager()
await websocket_manager.broadcast_event(event)
```

### Custom Event Filters
Add new filter types in `EventFilterPanel.tsx`:
```typescript
const customFilters = {
  custom_field: ['value1', 'value2']
};
```

## Testing

### Backend Tests
```bash
cd dashboard
pytest test_dashboard.py -v
```

### Frontend Tests
```bash
cd ui
npm test
```

### Integration Tests
```bash
# Start all services
docker-compose up -d

# Run integration tests
cd dashboard
python -m pytest tests/integration/ -v
```

## Deployment

### Local Development
```bash
cd dashboard
./deploy.sh local
```

### Staging Environment
```bash
./deploy.sh staging
```

### Production Environment
```bash
./deploy.sh production
```

### Docker Deployment
```bash
# Build image
docker build -t saas-factory-dashboard .

# Run container
docker run -d \
  -p 8000:8000 \
  -e PORT=8000 \
  -e DEBUG=false \
  --name dashboard \
  saas-factory-dashboard
```

### Cloud Run Deployment
```bash
# Deploy to Google Cloud Run
gcloud run deploy dashboard \
  --image gcr.io/PROJECT_ID/dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Monitoring

### Health Checks
The dashboard includes built-in health monitoring:
- WebSocket connection health
- Event processing metrics
- Memory usage tracking
- Error rate monitoring

### Logging
All events are logged with structured JSON format:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "dashboard",
  "message": "WebSocket client connected",
  "client_id": "dashboard-abc123",
  "event_type": "connection"
}
```

### Metrics Collection
Key metrics tracked:
- Event throughput (events/second)
- WebSocket connection count
- Response latency
- Error rates
- Memory usage

## Troubleshooting

### Common Issues

#### WebSocket Connection Fails
**Symptoms**: Frontend shows "Disconnected" status
**Solutions**:
1. Check backend is running on port 8000
2. Verify CORS settings allow frontend origin
3. Check firewall/proxy settings for WebSocket support

#### Events Not Appearing
**Symptoms**: Dashboard shows no events
**Solutions**:
1. Verify agent system is publishing events
2. Check WebSocket manager integration
3. Review event filters - may be too restrictive

#### High Memory Usage
**Symptoms**: Backend consuming excessive memory
**Solutions**:
1. Reduce `MAX_HISTORY_SIZE` configuration
2. Implement event archiving
3. Add memory monitoring and alerts

#### Slow Event Processing
**Symptoms**: Delayed event delivery
**Solutions**:
1. Check WebSocket connection count
2. Optimize event filtering logic
3. Consider Redis for scaling

### Debug Mode
Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python app.py
```

### Performance Profiling
```bash
# Install profiling tools
pip install py-spy

# Profile running application
py-spy top --pid $(pgrep -f "python app.py")
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests before submitting

### Code Style
- Python: Follow PEP 8
- TypeScript: Use ESLint configuration
- Git: Conventional commit messages

### Testing Requirements
- Unit tests for all new features
- Integration tests for API endpoints
- Frontend component tests
- Performance benchmarks

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

- **Documentation**: This README and inline code comments
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: team@saasfactory.dev

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Authors**: SaaS Factory Team 