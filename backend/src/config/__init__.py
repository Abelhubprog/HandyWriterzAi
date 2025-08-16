"""Configuration module for HandyWriterz backend."""

import os
import json

# Move the content here directly to avoid circular imports
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class HandyWriterzSettings(BaseSettings):
    """Production-ready settings with validation and type safety."""

    # ==========================================
    # ENVIRONMENT CONFIGURATION
    # ==========================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # ==========================================
    # API CONFIGURATION
    # ==========================================
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")

    # ==========================================
    # AI PROVIDER CONFIGURATION
    # ==========================================
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    perplexity_api_key: Optional[str] = Field(None, env="PERPLEXITY_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    app_url: str = Field(default="http://localhost:3000", env="APP_URL")

    # ==========================================
    # DATABASE CONFIGURATION
    # ==========================================
    database_url: str = Field("postgresql://localhost:5432/handywriterz", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")

    # Test database
    test_database_url: Optional[str] = Field(None, env="TEST_DATABASE_URL")

    # ==========================================
    # FRONTEND CONFIGURATION
    # ==========================================
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )

    # ==========================================
    # AUTHENTICATION & SECURITY
    # ==========================================
    # Dynamic.xyz
    dynamic_env_id: Optional[str] = Field(None, env="DYNAMIC_ENV_ID")
    dynamic_public_key: Optional[str] = Field(None, env="DYNAMIC_PUBLIC_KEY")
    dynamic_webhook_url: Optional[str] = Field(None, env="DYNAMIC_WEBHOOK_URL")

    # JWT
    jwt_secret_key: str = Field("default_development_secret_key_change_in_production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")

    # Security
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=300, env="RATE_LIMIT_WINDOW")

    # ==========================================
    # FEATURE FLAGS
    # ==========================================
    feature_sse_publisher_unified: bool = Field(default=False, env="FEATURE_SSE_PUBLISHER_UNIFIED")
    feature_params_normalization: bool = Field(default=False, env="FEATURE_PARAMS_NORMALIZATION")
    feature_double_publish_sse: bool = Field(default=False, env="FEATURE_DOUBLE_PUBLISH_SSE")
    feature_registry_enforced: bool = Field(default=False, env="FEATURE_REGISTRY_ENFORCED")
    feature_search_adapter: bool = Field(default=False, env="FEATURE_SEARCH_ADAPTER")

    # ==========================================
    # VALIDATORS
    # ==========================================

    @field_validator("allowed_origins", "cors_origins", mode="before")
    @classmethod
    def parse_list_from_string(cls, v):
        """Parse comma-separated string to list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()

    # ==========================================
    # CONFIGURATION METHODS
    # ==========================================

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"

    def get_ai_provider_config(self) -> Dict[str, Optional[str]]:
        """Get AI provider configuration."""
        return {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
            "perplexity": self.perplexity_api_key
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
def _coerce_list_env(var_name: str) -> None:
    """Ensure comma-separated list envs are valid JSON arrays for pydantic-settings.

    Pydantic's EnvSettingsSource tries to JSON-decode list fields; when users
    provide comma-separated values (e.g., "a,b"), it fails before validators run.
    This coerces such envs into JSON arrays at runtime.
    """
    try:
        val = os.getenv(var_name)
        if not val:
            return
        s = val.strip()
        # if it's already JSON array-ish, leave as-is
        if s.startswith('[') and s.endswith(']'):
            return
        # otherwise, split on commas
        parts = [p.strip() for p in s.split(',') if p.strip()]
        os.environ[var_name] = json.dumps(parts)
    except Exception:
        # best effort; fall back to default
        pass


def get_settings() -> HandyWriterzSettings:
    """Get the global settings instance."""
    # Normalize list envs to JSON arrays so pydantic can parse them reliably
    _coerce_list_env('ALLOWED_ORIGINS')
    _coerce_list_env('CORS_ORIGINS')
    return HandyWriterzSettings()


def setup_logging(settings: HandyWriterzSettings):
    """Setup structured logging configuration."""
    import logging

    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


__all__ = [
    'get_settings',
    'setup_logging',
    'HandyWriterzSettings'
]
