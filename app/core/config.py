"""
Cấu hình ứng dụng
"""

import os
from typing import Optional


class Settings:
    """Cấu hình ứng dụng"""
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "grade_analyzer_auth")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Grade Analyzer API"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"


# Singleton instance
settings = Settings()
