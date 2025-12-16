"""
Configuration settings for Firefly application
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Firefly Mental Health"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@firefly.com"
    ADMIN_PASSWORD: str

    # APIs
    ALPHA_VANTAGE_API_KEY: str = ""

    # ML Service
    ML_SERVICE_URL: str = "http://localhost:5001"

    # Feature Flags
    ENABLE_CRISIS_DETECTION: bool = True
    ENABLE_ML_RECOMMENDATIONS: bool = False  # Phase 2
    ENABLE_WEARABLE_INTEGRATION: bool = False  # Phase 4

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
