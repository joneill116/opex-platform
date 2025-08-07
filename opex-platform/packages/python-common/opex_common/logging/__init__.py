"""
ENTERPRISE LOGGING FACTORY
Centralized logging configuration following SRE best practices.
Single source of truth for all logging across the platform.
"""

import structlog
from typing import Dict, Any
import os

_logger_configured = False

def configure_enterprise_logging(service_name: str, log_level: str = "INFO") -> structlog.stdlib.BoundLogger:
    """
    Configure enterprise-grade structured logging once per service.
    Prevents duplicate configuration conflicts.
    
    Args:
        service_name: Name of the service for log context
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured structured logger
    """
    global _logger_configured
    
    if not _logger_configured:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        _logger_configured = True
    
    logger = structlog.get_logger()
    return logger.bind(service=service_name)

def get_logger(service_name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for a service.
    Automatically configures if not already done.
    """
    if not _logger_configured:
        return configure_enterprise_logging(service_name)
    
    return structlog.get_logger().bind(service=service_name)
