import structlog
import logging

def configure_logging(service_name: str, log_level: str = "INFO"):
    """Configure structured logging for the service"""
    logging.basicConfig(level=getattr(logging, log_level))
    
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()
