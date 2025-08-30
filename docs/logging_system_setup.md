# SaaS Factory Logging System Setup

## Overview

The SaaS Factory logging system has been redesigned to eliminate I/O operations on closed files, provide proper file handle management, and ensure reliable tenant database logging. This document describes the new centralized logging architecture and usage patterns.

## Architecture

### Centralized Configuration
- **File:** `config/logging_config.py`
- **Purpose:** Single point of logging configuration to prevent conflicts
- **Features:** File rotation, proper file handle management, centralized logger instances

### Tenant-Aware Logging
- **File:** `agents/shared/logging_utils.py`
- **Purpose:** Robust logging with tenant context and fallback handling
- **Features:** Safe logging operations, tenant context tracking, operation logging decorators

### Integration Points
- **Main Config:** `config/settings.py` - Centralized logging configuration
- **API Gateway:** `api_gateway/app.py` - Main application logging
- **Tenant Database:** `agents/shared/tenant_db.py` - Database operation logging

## Key Features

### 1. File Handle Management
- **Automatic Rotation:** Log files rotate at 10MB with 5 backup files
- **Proper Cleanup:** File handles are properly managed and cleaned up
- **No I/O Errors:** Eliminates operations on closed file handles

### 2. Tenant Context Logging
- **Automatic Context:** Tenant ID automatically added to log messages
- **Operation Tracking:** Database operations are logged with timing
- **Audit Trail:** Complete audit trail for tenant operations

### 3. Fallback Handling
- **Graceful Degradation:** If logging fails, falls back to print statements
- **Error Reporting:** Logging failures are reported to stderr
- **Metrics Tracking:** Logging system health is monitored

## Usage Patterns

### Basic Logging
```python
from config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.error("An error occurred")
```

### Tenant-Aware Logging
```python
from agents.shared.logging_utils import get_tenant_logger

logger = get_tenant_logger(__name__, tenant_id="tenant123")
logger.info("Tenant operation started")
```

### Operation Logging Decorators
```python
from agents.shared.logging_utils import log_tenant_operation

@log_tenant_operation("create_project")
async def create_project(self, tenant_context, name, description):
    # Operation automatically logged with timing and tenant context
    pass
```

### Database Operation Logging
```python
from agents.shared.logging_utils import log_database_operation

@log_database_operation("user_query")
async def query_users(self, tenant_context):
    # Database operation automatically logged
    pass
```

## Configuration

### Environment Variables
```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log to file (true/false)
LOG_TO_FILE=true

# Log to console (true/false)
LOG_TO_CONSOLE=true

# Max log file size in bytes (default: 10MB)
LOG_MAX_FILE_SIZE=10485760

# Number of backup files (default: 5)
LOG_BACKUP_COUNT=5
```

### Log File Structure
```
logs/
├── saas_factory_20241201.log      # Current log file
├── saas_factory_20241201.log.1    # Backup 1
├── saas_factory_20241201.log.2    # Backup 2
└── ...
```

## Migration Guide

### From Old Logging System
1. **Remove `logging.basicConfig()` calls** from individual files
2. **Replace `logging.getLogger()`** with `get_logger()` from centralized config
3. **Use tenant-aware logging** for database operations
4. **Add operation decorators** for automatic logging

### Example Migration
```python
# OLD WAY (problematic)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NEW WAY (robust)
from config.logging_config import get_logger
logger = get_logger(__name__)
```

## Monitoring and Health

### Logging Metrics
```python
from agents.shared.logging_utils import get_logging_metrics

metrics = get_logging_metrics()
stats = metrics.get_stats()
print(f"Logging success rate: {stats['success_rate_percent']}%")
```

### Health Check Endpoint
```python
@app.get("/health/logging")
async def logging_health_check():
    metrics = get_logging_metrics()
    stats = metrics.get_stats()
    
    return {
        "status": "healthy" if stats['success_rate_percent'] > 95 else "degraded",
        "success_rate": stats['success_rate_percent'],
        "total_operations": stats['total_operations'],
        "fallback_usage": stats['fallback_usage']
    }
```

## Troubleshooting

### Common Issues

#### 1. Logging Configuration Conflicts
**Problem:** Multiple `logging.basicConfig()` calls
**Solution:** Use centralized configuration only

#### 2. File Handle Errors
**Problem:** I/O operations on closed files
**Solution:** Centralized logging handles file lifecycle automatically

#### 3. Tenant Context Missing
**Problem:** Logs don't show tenant information
**Solution:** Use `get_tenant_logger()` or operation decorators

### Debug Mode
```python
from config.logging_config import configure_logging

# Enable debug logging
configure_logging(level="DEBUG", log_to_file=True, log_to_console=True)
```

## Best Practices

### 1. Use Centralized Configuration
- Never call `logging.basicConfig()` in individual files
- Import logging configuration from `config.logging_config`

### 2. Leverage Operation Decorators
- Use `@log_tenant_operation()` for tenant-specific operations
- Use `@log_database_operation()` for database operations
- Automatic timing and context tracking

### 3. Handle Logging Failures Gracefully
- The system automatically falls back to print statements
- Monitor fallback usage for system health
- Use metrics to track logging system performance

### 4. Maintain Tenant Context
- Always pass tenant context to logging operations
- Use tenant-aware loggers for multi-tenant operations
- Ensure audit trail completeness

## Performance Considerations

### Log File Rotation
- Automatic rotation prevents disk space issues
- Configurable file size and backup count
- Efficient file handle management

### Memory Usage
- Logger instances are cached to prevent recreation
- File handlers are properly managed to prevent leaks
- Minimal memory overhead for logging operations

### Async Operations
- All logging operations are async-safe
- No blocking operations in logging code
- Proper context management for async operations

## Security Considerations

### Log File Permissions
- Log files are created with appropriate permissions
- No sensitive data in log messages by default
- Tenant isolation maintained in logging

### Audit Trail
- Complete operation logging for compliance
- Tenant context preserved in all logs
- Timestamp and duration tracking

## Future Enhancements

### Planned Features
1. **Structured Logging:** JSON format for better parsing
2. **Log Aggregation:** Centralized log collection and analysis
3. **Performance Metrics:** Enhanced logging performance monitoring
4. **Custom Formatters:** Configurable log message formats

### Integration Points
1. **ELK Stack:** Elasticsearch, Logstash, Kibana integration
2. **Cloud Logging:** Google Cloud Logging integration
3. **Alerting:** Automated alerting for logging failures
4. **Analytics:** Log analysis and reporting tools

## Conclusion

The new logging system provides:
- **Reliability:** No more I/O errors or file handle issues
- **Observability:** Complete system monitoring and debugging
- **Maintainability:** Centralized configuration and management
- **Performance:** Efficient file handling and rotation
- **Security:** Proper tenant isolation and audit trails

This system ensures that all logging operations work consistently and reliably across the entire SaaS Factory platform.
