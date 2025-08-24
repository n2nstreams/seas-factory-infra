"""
Centralized logging configuration for SaaS Factory
Eliminates multiple logging.basicConfig() calls and provides proper file handle management
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

# Global logger instances to prevent recreation
_loggers: Dict[str, logging.Logger] = {}
_file_handlers: Dict[str, logging.handlers.RotatingFileHandler] = {}

class LoggingConfig:
    """Centralized logging configuration manager"""
    
    def __init__(self):
        self._configured = False
        self._log_dir = Path("logs")
        self._log_dir.mkdir(exist_ok=True)
        
    def configure_logging(
        self,
        level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        format_string: Optional[str] = None
    ) -> None:
        """Configure logging system centrally"""
        if self._configured:
            return
            
        # Prevent multiple configurations
        if logging.getLogger().handlers:
            return
            
        # Set default format
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
            
        # Create formatter
        formatter = logging.Formatter(format_string)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
        # File handler with rotation
        if log_to_file:
            log_file = self._log_dir / f"saas_factory_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            # Store reference to prevent garbage collection
            _file_handlers['main'] = file_handler
            
        self._configured = True
        
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with proper configuration"""
        if name in _loggers:
            return _loggers[name]
            
        # Ensure logging is configured
        if not self._configured:
            self.configure_logging()
            
        logger = logging.getLogger(name)
        _loggers[name] = logger
        return logger
        
    def cleanup(self) -> None:
        """Properly cleanup logging resources"""
        try:
            # Close all file handlers
            for handler_name, handler in _file_handlers.items():
                try:
                    handler.close()
                except Exception as e:
                    # Use print as fallback since logging might be broken
                    print(f"[WARNING] Failed to close log handler {handler_name}: {e}")
                    
            # Clear references
            _file_handlers.clear()
            _loggers.clear()
            
            # Reset root logger
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            
        except Exception as e:
            print(f"[ERROR] Failed to cleanup logging: {e}")
            
    def set_level(self, level: str) -> None:
        """Set logging level for all loggers"""
        try:
            log_level = getattr(logging, level.upper())
            logging.getLogger().setLevel(log_level)
            
            # Update all stored loggers
            for logger in _loggers.values():
                logger.setLevel(log_level)
                
        except Exception as e:
            print(f"[ERROR] Failed to set logging level: {e}")

# Global instance
logging_config = LoggingConfig()

def get_logger(name: str) -> logging.Logger:
    """Get a properly configured logger"""
    return logging_config.get_logger(name)

def configure_logging(**kwargs) -> None:
    """Configure logging system"""
    logging_config.configure_logging(**kwargs)

def cleanup_logging() -> None:
    """Cleanup logging resources"""
    logging_config.cleanup()

# Import-time configuration
configure_logging()
