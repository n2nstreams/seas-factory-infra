#!/usr/bin/env python3
"""
Minimal Logging Configuration for API Gateway
Provides basic logging functionality for the API gateway service
"""

import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO",
    log_to_file: bool = False,
    log_to_console: bool = True,
    format_string: Optional[str] = None
) -> None:
    """Configure basic logging system"""
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
        
    # File handler (if requested)
    if log_to_file:
        try:
            file_handler = logging.FileHandler("api_gateway.log")
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to console only if file logging fails
            logging.warning(f"File logging failed: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with proper configuration"""
    # Ensure logging is configured
    if not logging.getLogger().handlers:
        configure_logging()
        
    return logging.getLogger(name)


# Initialize logging
configure_logging()
