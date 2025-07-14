#!/usr/bin/env python3
"""
SaaS Factory - Centralized Configuration Management
Provides type-safe, environment-specific configuration for all services
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings
from enum import Enum


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"
    TEST = "test"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="factorydb", env="DB_NAME")
    user: str = Field(default="factoryadmin", env="DB_USER")
    password: SecretStr = Field(default="", env="DB_PASSWORD")
    max_connections: int = Field(default=20, env="DB_MAX_CONNECTIONS")
    min_connections: int = Field(default=5, env="DB_MIN_CONNECTIONS")
    connection_timeout: int = Field(default=60, env="DB_CONNECTION_TIMEOUT")
    ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")
    
    @property
    def url(self) -> str:
        """Database URL for SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """Async database URL for asyncpg"""
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class GoogleCloudConfig(BaseSettings):
    """Google Cloud Platform configuration"""
    project_id: str = Field(default="summer-nexus-463503-e1", env="PROJECT_ID")
    region: str = Field(default="us-central1", env="GOOGLE_CLOUD_REGION")
    service_account_key_path: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Storage
    storage_bucket: str = Field(default="", env="GOOGLE_STORAGE_BUCKET")
    
    # Monitoring
    monitoring_enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    
    # Secret Manager
    secret_manager_enabled: bool = Field(default=True, env="SECRET_MANAGER_ENABLED")


class AIConfig(BaseSettings):
    """AI/ML service configuration"""
    openai_api_key: SecretStr = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Google AI
    google_ai_enabled: bool = Field(default=True, env="GOOGLE_AI_ENABLED")
    google_ai_model: str = Field(default="gemini-1.5-pro", env="GOOGLE_AI_MODEL")
    
    # Model provider selection
    model_provider: str = Field(default="openai", env="MODEL_PROVIDER")
    
    @field_validator('model_provider')
    def validate_model_provider(cls, v):
        if v not in ['openai', 'google', 'gpt4o', 'gemini']:
            raise ValueError('model_provider must be one of: openai, google, gpt4o, gemini')
        return v


class SecurityConfig(BaseSettings):
    """Security configuration"""
    # JWT
    jwt_secret_key: SecretStr = Field(default="test-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # API Keys
    github_token: Optional[SecretStr] = Field(None, env="GITHUB_TOKEN")
    stripe_api_key: Optional[SecretStr] = Field(None, env="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[SecretStr] = Field(None, env="STRIPE_WEBHOOK_SECRET")
    
    # Security scanning
    snyk_token: Optional[SecretStr] = Field(None, env="SNYK_TOKEN")
    snyk_org: Optional[str] = Field(None, env="SNYK_ORG")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")


class ServiceConfig(BaseSettings):
    """Service URLs and endpoints"""
    # Core services
    orchestrator_url: str = Field(default="http://localhost:8080", env="ORCHESTRATOR_URL")
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    
    # Agent services
    techstack_agent_url: str = Field(default="http://localhost:8081", env="TECHSTACK_AGENT_URL")
    design_agent_url: str = Field(default="http://localhost:8082", env="DESIGN_AGENT_URL")
    dev_agent_url: str = Field(default="http://localhost:8083", env="DEV_AGENT_URL")
    review_agent_url: str = Field(default="http://localhost:8084", env="REVIEW_AGENT_URL")
    ui_dev_agent_url: str = Field(default="http://localhost:8085", env="UI_DEV_AGENT_URL")
    qa_agent_url: str = Field(default="http://localhost:8086", env="QA_AGENT_URL")
    
    # External services
    figma_api_url: str = Field(default="https://api.figma.com", env="FIGMA_API_URL")
    github_api_url: str = Field(default="https://api.github.com", env="GITHUB_API_URL")
    stripe_api_url: str = Field(default="https://api.stripe.com", env="STRIPE_API_URL")
    
    # WebSocket
    websocket_max_connections: int = Field(default=100, env="WEBSOCKET_MAX_CONNECTIONS")
    websocket_ping_interval: int = Field(default=30, env="WEBSOCKET_PING_INTERVAL")


class NotificationConfig(BaseSettings):
    """Notification configuration"""
    # Email
    sendgrid_api_key: Optional[SecretStr] = Field(None, env="SENDGRID_API_KEY")
    alert_email: str = Field(default="alerts@saasfactory.com", env="ALERT_EMAIL")
    
    # Slack
    slack_webhook_url: Optional[SecretStr] = Field(None, env="SLACK_WEBHOOK_URL")
    slack_channel: str = Field(default="#alerts", env="SLACK_CHANNEL")
    
    # PagerDuty
    pagerduty_api_key: Optional[SecretStr] = Field(None, env="PAGERDUTY_API_KEY")
    pagerduty_service_key: Optional[SecretStr] = Field(None, env="PAGERDUTY_SERVICE_KEY")


class CacheConfig(BaseSettings):
    """Cache configuration"""
    redis_enabled: bool = Field(default=False, env="REDIS_ENABLED")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[SecretStr] = Field(None, env="REDIS_PASSWORD")
    redis_ttl: int = Field(default=3600, env="REDIS_TTL")
    
    # Memory cache
    memory_cache_enabled: bool = Field(default=True, env="MEMORY_CACHE_ENABLED")
    memory_cache_size: int = Field(default=1000, env="MEMORY_CACHE_SIZE")


class Settings(BaseSettings):
    """Main application settings"""
    # Application
    app_name: str = Field(default="SaaS Factory", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Feature flags
    auto_commit_enabled: bool = Field(default=False, env="ENABLE_AUTO_COMMIT")
    auto_pr_enabled: bool = Field(default=False, env="ENABLE_AUTO_PR")
    tenant_isolation_enabled: bool = Field(default=True, env="TENANT_ISOLATION_ENABLED")
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    google_cloud: GoogleCloudConfig = GoogleCloudConfig()
    ai: AIConfig = AIConfig()
    security: SecurityConfig = SecurityConfig()
    services: ServiceConfig = ServiceConfig()
    notifications: NotificationConfig = NotificationConfig()
    cache: CacheConfig = CacheConfig()
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False
        
    @field_validator('environment', mode='before')
    def parse_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @field_validator('log_level', mode='before')
    def parse_log_level(cls, v):
        if isinstance(v, str):
            return LogLevel(v.upper())
        return v
    
    @property
    def is_development(self) -> bool:
        return self.environment in [Environment.DEVELOPMENT, Environment.LOCAL]
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    def get_service_url(self, service_name: str) -> str:
        """Get service URL by name"""
        service_map = {
            'orchestrator': self.services.orchestrator_url,
            'api_gateway': self.services.api_gateway_url,
            'techstack_agent': self.services.techstack_agent_url,
            'design_agent': self.services.design_agent_url,
            'dev_agent': self.services.dev_agent_url,
            'review_agent': self.services.review_agent_url,
            'ui_dev_agent': self.services.ui_dev_agent_url,
            'qa_agent': self.services.qa_agent_url,
        }
        return service_map.get(service_name, f"http://localhost:8080")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def configure_logging():
    """Configure logging based on settings"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.value),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_required_settings():
    """Validate that all required settings are present"""
    errors = []
    
    # Check database password
    if not settings.database.password.get_secret_value():
        errors.append("DB_PASSWORD is required")
    
    # Check AI API key
    if not settings.ai.openai_api_key.get_secret_value():
        errors.append("OPENAI_API_KEY is required")
    
    # Check JWT secret in production
    if settings.is_production and not settings.security.jwt_secret_key.get_secret_value():
        errors.append("JWT_SECRET_KEY is required in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    if settings.environment == Environment.PRODUCTION:
        return {
            'debug': False,
            'log_level': LogLevel.INFO,
            'cors_origins': ['https://saasfactory.com'],
            'rate_limit_enabled': True,
            'redis_enabled': True,
        }
    elif settings.environment == Environment.STAGING:
        return {
            'debug': False,
            'log_level': LogLevel.INFO,
            'cors_origins': ['https://staging.saasfactory.com'],
            'rate_limit_enabled': True,
            'redis_enabled': True,
        }
    else:  # Development/Local
        return {
            'debug': True,
            'log_level': LogLevel.DEBUG,
            'cors_origins': ['*'],
            'rate_limit_enabled': False,
            'redis_enabled': False,
        }


# Initialize logging
configure_logging()

# Validate settings on import
try:
    validate_required_settings()
except ValueError as e:
    if settings.environment == Environment.PRODUCTION:
        raise e
    else:
        logging.warning(f"Configuration validation failed: {e}")


if __name__ == "__main__":
    print("SaaS Factory Configuration")
    print("=" * 50)
    print(f"Environment: {settings.environment.value}")
    print(f"Debug: {settings.debug}")
    print(f"Log Level: {settings.log_level.value}")
    print(f"Database: {settings.database.host}:{settings.database.port}")
    print(f"Project ID: {settings.google_cloud.project_id}")
    print(f"Model Provider: {settings.ai.model_provider}")
    print("=" * 50) 