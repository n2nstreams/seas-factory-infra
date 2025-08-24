"""
Improved logging utilities for tenant database operations
Eliminates silent logging failure handling and provides robust logging patterns
"""

import logging
import sys
from typing import Optional, Any, Dict
from contextlib import contextmanager
from functools import wraps
import traceback

# Import centralized logging configuration
try:
    from config.logging_config import get_logger
except ImportError:
    # Fallback if centralized config is not available
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

class TenantAwareLogger:
    """Tenant-aware logger with robust error handling"""
    
    def __init__(self, name: str, tenant_id: Optional[str] = None):
        self.logger = get_logger(name)
        self.tenant_id = tenant_id
        self._fallback_enabled = True
        
    def _safe_log(self, level: str, message: str, *args, **kwargs) -> bool:
        """Safely log a message with fallback handling"""
        try:
            # Add tenant context if available
            if self.tenant_id:
                message = f"[Tenant: {self.tenant_id}] {message}"
                
            # Get the logging method
            log_method = getattr(self.logger, level.lower(), None)
            if log_method:
                log_method(message, *args, **kwargs)
                return True
            else:
                raise AttributeError(f"Unknown log level: {level}")
                
        except Exception as e:
            # Fallback to print if logging fails
            if self._fallback_enabled:
                fallback_message = f"[{level.upper()}] {message}"
                if args:
                    fallback_message = fallback_message.format(*args)
                print(f"{fallback_message} (logging failed: {e})")
                
                # Log the original error to stderr for debugging
                print(f"[ERROR] Logging system failure: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                
            return False
            
    def info(self, message: str, *args, **kwargs) -> bool:
        """Log info message safely"""
        return self._safe_log("INFO", message, *args, **kwargs)
        
    def warning(self, message: str, *args, **kwargs) -> bool:
        """Log warning message safely"""
        return self._safe_log("WARNING", message, *args, **kwargs)
        
    def error(self, message: str, *args, **kwargs) -> bool:
        """Log error message safely"""
        return self._safe_log("ERROR", message, *args, **kwargs)
        
    def debug(self, message: str, *args, **kwargs) -> bool:
        """Log debug message safely"""
        return self._safe_log("DEBUG", message, *args, **kwargs)
        
    def critical(self, message: str, *args, **kwargs) -> bool:
        """Log critical message safely"""
        return self._safe_log("CRITICAL", message, *args, **kwargs)
        
    def set_tenant(self, tenant_id: str) -> None:
        """Set tenant context for this logger"""
        self.tenant_id = tenant_id
        
    def disable_fallback(self) -> None:
        """Disable fallback to print statements"""
        self._fallback_enabled = False
        
    def enable_fallback(self) -> None:
        """Enable fallback to print statements"""
        self._fallback_enabled = True

def get_tenant_logger(name: str, tenant_id: Optional[str] = None) -> TenantAwareLogger:
    """Get a tenant-aware logger instance"""
    return TenantAwareLogger(name, tenant_id)

@contextmanager
def safe_logging_context(logger: TenantAwareLogger, operation: str, **context):
    """Context manager for safe logging operations"""
    start_time = None
    try:
        # Log operation start
        logger.info(f"Starting operation: {operation}", extra=context)
        start_time = __import__('time').time()
        yield logger
        
    except Exception as e:
        # Log operation failure
        logger.error(f"Operation failed: {operation} - {e}", extra=context)
        raise
        
    finally:
        # Log operation completion
        if start_time:
            duration = __import__('time').time() - start_time
            logger.info(f"Operation completed: {operation} (duration: {duration:.3f}s)", extra=context)

def log_operation(operation_name: str, tenant_id: Optional[str] = None):
    """Decorator for logging operations with tenant context"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_tenant_logger(func.__module__, tenant_id)
            with safe_logging_context(logger, operation_name):
                return await func(*args, **kwargs)
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_tenant_logger(func.__module__, tenant_id)
            with safe_logging_context(logger, operation_name):
                return func(*args, **kwargs)
                
        # Return appropriate wrapper based on function type
        if __import__('inspect').iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

def log_database_operation(operation: str):
    """Decorator specifically for database operations"""
    return log_operation(f"DB_{operation}")

def log_tenant_operation(operation: str):
    """Decorator for tenant-specific operations"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, tenant_context, *args, **kwargs):
            tenant_id = getattr(tenant_context, 'tenant_id', 'unknown')
            logger = get_tenant_logger(func.__module__, tenant_id)
            with safe_logging_context(logger, operation):
                return await func(self, tenant_context, *args, **kwargs)
                
        @wraps(func)
        def sync_wrapper(self, tenant_context, *args, **kwargs):
            tenant_id = getattr(tenant_context, 'tenant_id', 'unknown')
            logger = get_tenant_logger(func.__module__, tenant_id)
            with safe_logging_context(logger, operation):
                return func(self, tenant_context, *args, **kwargs)
                
        # Return appropriate wrapper based on function type
        if __import__('inspect').iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

class LoggingMetrics:
    """Track logging system health and performance"""
    
    def __init__(self):
        self.logging_successes = 0
        self.logging_failures = 0
        self.fallback_usage = 0
        self.tenant_context_usage = 0
        
    def record_success(self) -> None:
        """Record successful logging operation"""
        self.logging_successes += 1
        
    def record_failure(self) -> None:
        """Record failed logging operation"""
        self.logging_failures += 1
        
    def record_fallback(self) -> None:
        """Record fallback to print usage"""
        self.fallback_usage += 1
        
    def record_tenant_context(self) -> None:
        """Record tenant context usage"""
        self.tenant_context_usage += 1
        
    def get_stats(self) -> Dict[str, Any]:
        """Get logging system statistics"""
        total = self.logging_successes + self.logging_failures
        success_rate = (self.logging_successes / total * 100) if total > 0 else 0
        
        return {
            'total_operations': total,
            'successes': self.logging_successes,
            'failures': self.logging_failures,
            'success_rate_percent': round(success_rate, 2),
            'fallback_usage': self.fallback_usage,
            'tenant_context_usage': self.tenant_context_usage
        }

# Global metrics instance
logging_metrics = LoggingMetrics()

def get_logging_metrics() -> LoggingMetrics:
    """Get global logging metrics"""
    return logging_metrics
