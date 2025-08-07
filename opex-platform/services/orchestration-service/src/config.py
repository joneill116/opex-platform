"""
Configuration settings for the orchestration service.
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "orchestration-service"
    SERVICE_VERSION: str = "0.1.0"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://orchestration:orchestration@postgres-orchestration:5432/orchestration"
    
    # External Services
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    REDIS_URL: str = "redis://redis:6379"
    METADATA_SERVICE_URL: str = "http://metadata-service:8000"
    
    # Monitoring
    JAEGER_AGENT_HOST: str = "jaeger"
    JAEGER_AGENT_PORT: int = 6831
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()