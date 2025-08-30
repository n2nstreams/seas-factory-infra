#!/usr/bin/env python3
"""
Minimal Settings Configuration for API Gateway
Provides essential configuration for the API gateway service
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class CacheConfig(BaseSettings):
    """Cache configuration"""
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[SecretStr] = None


class SecurityConfig(BaseSettings):
    """Security configuration"""
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600


class Settings(BaseSettings):
    """Application settings"""
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Cache
    cache: CacheConfig = CacheConfig()
    
    # Security
    security: SecurityConfig = SecurityConfig()
    
    # Database
    database_url: str = "postgresql://postgres:postgres@postgres:5432/saas_factory"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Security
    jwt_secret_key: Optional[SecretStr] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[SecretStr] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[SecretStr] = None
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
