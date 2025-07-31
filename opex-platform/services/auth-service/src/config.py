from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "auth-service"
    SERVICE_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # External Services
    KAFKA_BOOTSTRAP_SERVERS: str
    REDIS_URL: str

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Monitoring
    JAEGER_AGENT_HOST: str = "localhost"
    JAEGER_AGENT_PORT: int = 6831
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
