from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "metadata-service"
    DATABASE_URL: str = ""
    REDIS_URL: str = ""
    KAFKA_BOOTSTRAP_SERVERS: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
