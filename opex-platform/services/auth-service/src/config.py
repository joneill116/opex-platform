from pydantic_settings import BaseSettings
from pydantic import Field
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

    # CORS - Allow frontend access
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Local development
        "http://frontend:3000",   # Docker compose
    ]

    # Monitoring
    JAEGER_AGENT_HOST: str = Field(default="jaeger", env="JAEGER_AGENT_HOST")
    JAEGER_AGENT_PORT: int = Field(default=6831, env="JAEGER_AGENT_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
