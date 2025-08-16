"""Production-ready configuration management for HandyWriterz backend."""

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
    
    # ==========================================
    # DATABASE CONFIGURATION
    # ==========================================
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Test database
    test_database_url: Optional[str] = Field(None, env="TEST_DATABASE_URL")
    
    # ==========================================
    # FILE STORAGE CONFIGURATION
    # ==========================================
    # Cloudflare R2
    r2_endpoint_url: Optional[str] = Field(None, env="R2_ENDPOINT_URL")
    r2_bucket_name: Optional[str] = Field(None, env="R2_BUCKET_NAME")
    r2_access_key_id: Optional[str] = Field(None, env="R2_ACCESS_KEY_ID")
    r2_secret_access_key: Optional[str] = Field(None, env="R2_SECRET_ACCESS_KEY")
    
    # AWS S3 Fallback
    aws_bucket_name: Optional[str] = Field(None, env="AWS_BUCKET_NAME")
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Local storage
    upload_dir: str = Field(default="/tmp/handywriterz/uploads", env="UPLOAD_DIR")
    
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
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
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
    # BLOCKCHAIN & PAYMENTS
    # ==========================================
    # Base Network
    base_rpc_url: str = Field(default="https://mainnet.base.org", env="BASE_RPC_URL")
    base_chain_id: int = Field(default=8453, env="BASE_CHAIN_ID")
    
    # Solana Network
    solana_rpc_url: str = Field(default="https://api.mainnet-beta.solana.com", env="SOLANA_RPC_URL")
    solana_cluster: str = Field(default="mainnet-beta", env="SOLANA_CLUSTER")
    
    # Token Configuration
    handy_token_mint: Optional[str] = Field(None, env="HANDY_TOKEN_MINT")
    handy_token_decimals: int = Field(default=9, env="HANDY_TOKEN_DECIMALS")
    
    # USDC Addresses
    usdc_base_address: str = Field(
        default="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        env="USDC_BASE_ADDRESS"
    )
    usdc_solana_address: str = Field(
        default="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        env="USDC_SOLANA_ADDRESS"
    )
    
    # Payment Providers
    paystack_secret_key: Optional[str] = Field(None, env="PAYSTACK_SECRET_KEY")
    paystack_public_key: Optional[str] = Field(None, env="PAYSTACK_PUBLIC_KEY")
    coinbase_api_key: Optional[str] = Field(None, env="COINBASE_API_KEY")
    coinbase_webhook_secret: Optional[str] = Field(None, env="COINBASE_WEBHOOK_SECRET")
    
    # ==========================================
    # EXTERNAL SERVICES
    # ==========================================
    # Telegram/Turnitin
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_api_id: Optional[str] = Field(None, env="TELEGRAM_API_ID")
    telegram_api_hash: Optional[str] = Field(None, env="TELEGRAM_API_HASH")
    turnitin_bot_username: str = Field(default="@TurnitinPremiumBot", env="TURNITIN_BOT_USERNAME")
    
    # Email
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@handywriterz.com", env="SMTP_FROM_EMAIL")
    
    # Webhooks
    turnitin_webhook_url: Optional[str] = Field(None, env="TURNITIN_WEBHOOK_URL")
    turnitin_webhook_secret: Optional[str] = Field(None, env="TURNITIN_WEBHOOK_SECRET")
    
    # ==========================================
    # ACADEMIC SEARCH APIS
    # ==========================================
    crossref_api_key: Optional[str] = Field(None, env="CROSSREF_API_KEY")
    crossref_email: Optional[str] = Field(None, env="CROSSREF_EMAIL")
    semantic_scholar_api_key: Optional[str] = Field(None, env="SEMANTIC_SCHOLAR_API_KEY")
    arxiv_base_url: str = Field(default="http://export.arxiv.org/api/query", env="ARXIV_BASE_URL")
    ncbi_api_key: Optional[str] = Field(None, env="NCBI_API_KEY")
    pubmed_email: Optional[str] = Field(None, env="PUBMED_EMAIL")
    
    # ==========================================
    # MONITORING & LOGGING
    # ==========================================
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    applicationinsights_connection_string: Optional[str] = Field(None, env="APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: str = Field(default="handywriterz.log", env="LOG_FILE")
    log_max_bytes: int = Field(default=10485760, env="LOG_MAX_BYTES")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # ==========================================
    # PERFORMANCE & SCALING
    # ==========================================
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    worker_connections: int = Field(default=1000, env="WORKER_CONNECTIONS")
    worker_timeout: int = Field(default=120, env="WORKER_TIMEOUT")
    
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # ==========================================
    # AGENT CONFIGURATION
    # ==========================================
    max_agent_retries: int = Field(default=3, env="MAX_AGENT_RETRIES")
    agent_timeout_seconds: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    swarm_coordination_timeout: int = Field(default=600, env="SWARM_COORDINATION_TIMEOUT")
    
    # Content limits
    max_word_count: int = Field(default=10000, env="MAX_WORD_COUNT")
    min_word_count: int = Field(default=100, env="MIN_WORD_COUNT")
    max_sources_per_request: int = Field(default=50, env="MAX_SOURCES_PER_REQUEST")
    
    # Quality thresholds
    min_quality_score: float = Field(default=0.75, env="MIN_QUALITY_SCORE")
    min_citation_density: float = Field(default=0.02, env="MIN_CITATION_DENSITY")
    min_academic_tone: float = Field(default=0.70, env="MIN_ACADEMIC_TONE")
    
    # ==========================================
    # TESTING CONFIGURATION
    # ==========================================
    test_mode: bool = Field(default=False, env="TEST_MODE")
    mock_external_apis: bool = Field(default=False, env="MOCK_EXTERNAL_APIS")
    skip_ai_calls: bool = Field(default=False, env="SKIP_AI_CALLS")

    # ==========================================
    # AUTONOMY V2 FEATURE FLAGS & DEFAULTS
    # ==========================================
    enable_autonomy_v2: bool = Field(default=False, env="ENABLE_AUTONOMY_V2")
    v2_budget_tokens: int = Field(default=200_000, env="V2_BUDGET_TOKENS")
    v2_budget_seconds: int = Field(default=9, env="V2_BUDGET_SECONDS")
    v2_job_concurrency_per_user: int = Field(default=2, env="V2_JOB_CONCURRENCY_PER_USER")
    turnitin_target_default: float = Field(default=0.15, env="TURNITIN_TARGET_DEFAULT")
    
    # Development tools
    enable_debug_toolbar: bool = Field(default=False, env="ENABLE_DEBUG_TOOLBAR")
    enable_profiling: bool = Field(default=False, env="ENABLE_PROFILING")
    enable_swagger_ui: bool = Field(default=True, env="ENABLE_SWAGGER_UI")
    
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
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgres://", "sqlite://")):
            raise ValueError("Database URL must be a valid PostgreSQL or SQLite connection string")
        return v
    
    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must be a valid Redis connection string")
        return v
    
    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key strength."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v
    
    @field_validator("api_port")
    @classmethod
    def validate_api_port(cls, v):
        """Validate API port range."""
        if not 1000 <= v <= 65535:
            raise ValueError("API port must be between 1000 and 65535")
        return v
    
    @field_validator("max_word_count")
    @classmethod
    def validate_max_word_count(cls, v):
        """Validate maximum word count."""
        if v > 50000:
            raise ValueError("Maximum word count cannot exceed 50,000")
        return v
    
    @field_validator("min_quality_score", "min_citation_density", "min_academic_tone")
    @classmethod
    def validate_quality_scores(cls, v):
        """Validate quality score ranges."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Quality scores must be between 0.0 and 1.0")
        return v
    
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
        return self.environment == "testing" or self.test_mode
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration based on available credentials."""
        if self.r2_access_key_id and self.r2_secret_access_key:
            return {
                "provider": "r2",
                "endpoint_url": self.r2_endpoint_url,
                "bucket_name": self.r2_bucket_name,
                "access_key_id": self.r2_access_key_id,
                "secret_access_key": self.r2_secret_access_key
            }
        elif self.aws_access_key_id and self.aws_secret_access_key:
            return {
                "provider": "s3",
                "bucket_name": self.aws_bucket_name,
                "access_key_id": self.aws_access_key_id,
                "secret_access_key": self.aws_secret_access_key,
                "region": self.aws_region
            }
        else:
            return {
                "provider": "local",
                "upload_dir": self.upload_dir
            }
    
    def get_ai_provider_config(self) -> Dict[str, Optional[str]]:
        """Get AI provider configuration."""
        return {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
            "perplexity": self.perplexity_api_key
        }
    
    def validate_required_for_production(self) -> List[str]:
        """Validate required settings for production environment."""
        missing = []
        
        if self.is_production():
            required_fields = [
                ("anthropic_api_key", "ANTHROPIC_API_KEY"),
                ("openai_api_key", "OPENAI_API_KEY"),
                ("gemini_api_key", "GEMINI_API_KEY"),
                ("perplexity_api_key", "PERPLEXITY_API_KEY"),
                ("dynamic_env_id", "DYNAMIC_ENV_ID"),
                ("dynamic_public_key", "DYNAMIC_PUBLIC_KEY"),
            ]
            
            for field_name, env_var in required_fields:
                if not getattr(self, field_name):
                    missing.append(env_var)
            
            # Check storage configuration
            storage_config = self.get_storage_config()
            if storage_config["provider"] == "local":
                missing.append("R2_ACCESS_KEY_ID or AWS_ACCESS_KEY_ID")
        
        return missing
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@dataclass
class ConfigurationValidator:
    """Configuration validation and health checks."""
    
    def __init__(self, settings: HandyWriterzSettings):
        self.settings = settings
        self.validation_errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive configuration validation."""
        self.validation_errors.clear()
        self.warnings.clear()
        
        # Core validation
        self._validate_database_connectivity()
        self._validate_redis_connectivity()
        self._validate_ai_providers()
        self._validate_storage_configuration()
        self._validate_security_settings()
        
        # Production-specific validation
        if self.settings.is_production():
            self._validate_production_requirements()
        
        return {
            "valid": len(self.validation_errors) == 0,
            "errors": self.validation_errors,
            "warnings": self.warnings,
            "environment": self.settings.environment,
            "storage_provider": self.settings.get_storage_config()["provider"],
            "ai_providers": {
                k: "configured" if v else "missing"
                for k, v in self.settings.get_ai_provider_config().items()
            }
        }
    
    def _validate_database_connectivity(self):
        """Validate database configuration."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.settings.database_url)
            
            if not parsed.hostname:
                self.validation_errors.append("Database URL missing hostname")
            if not parsed.port and not parsed.hostname == "localhost":
                self.warnings.append("Database URL missing port (using default)")
            if not parsed.username:
                self.validation_errors.append("Database URL missing username")
            if not parsed.password and not self.settings.is_development():
                self.validation_errors.append("Database URL missing password")
                
        except Exception as e:
            self.validation_errors.append(f"Invalid database URL format: {e}")
    
    def _validate_redis_connectivity(self):
        """Validate Redis configuration."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.settings.redis_url)
            
            if parsed.scheme != "redis":
                self.validation_errors.append("Redis URL must use redis:// scheme")
            if not parsed.hostname:
                self.validation_errors.append("Redis URL missing hostname")
                
        except Exception as e:
            self.validation_errors.append(f"Invalid Redis URL format: {e}")
    
    def _validate_ai_providers(self):
        """Validate AI provider configurations."""
        ai_config = self.settings.get_ai_provider_config()
        configured_providers = [k for k, v in ai_config.items() if v]
        
        if len(configured_providers) == 0:
            self.validation_errors.append("At least one AI provider API key must be configured")
        elif len(configured_providers) == 1:
            self.warnings.append("Only one AI provider configured - consider adding fallback providers")
        
        # Check primary provider (Anthropic)
        if not ai_config["anthropic"]:
            self.warnings.append("Anthropic API key not configured - primary model unavailable")
    
    def _validate_storage_configuration(self):
        """Validate storage configuration."""
        storage_config = self.settings.get_storage_config()
        
        if storage_config["provider"] == "local" and self.settings.is_production():
            self.validation_errors.append("Local storage not recommended for production - configure R2 or S3")
        
        # Validate upload directory exists for local storage
        if storage_config["provider"] == "local":
            upload_path = Path(storage_config["upload_dir"])
            try:
                upload_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.validation_errors.append(f"Cannot create upload directory: {e}")
    
    def _validate_security_settings(self):
        """Validate security configurations."""
        # JWT secret strength
        if len(self.settings.jwt_secret_key) < 64 and self.settings.is_production():
            self.warnings.append("JWT secret key should be at least 64 characters in production")
        
        # CORS origins
        if "*" in self.settings.cors_origins and self.settings.is_production():
            self.validation_errors.append("Wildcard CORS origins not allowed in production")
        
        # Debug mode in production
        if self.settings.debug and self.settings.is_production():
            self.validation_errors.append("Debug mode must be disabled in production")
    
    def _validate_production_requirements(self):
        """Validate production-specific requirements."""
        missing = self.settings.validate_required_for_production()
        if missing:
            self.validation_errors.extend([
                f"Missing required production setting: {setting}"
                for setting in missing
            ])
        
        # Additional production checks
        if self.settings.log_level == "DEBUG":
            self.warnings.append("Debug logging enabled in production")
        
        if not self.settings.sentry_dsn:
            self.warnings.append("Sentry DSN not configured - error tracking disabled")


# Global settings instance
def get_settings() -> HandyWriterzSettings:
    """Get the global settings instance."""
    return HandyWriterzSettings()


def validate_configuration() -> Dict[str, Any]:
    """Validate the current configuration."""
    settings = get_settings()
    validator = ConfigurationValidator(settings)
    return validator.validate_all()


def setup_logging(settings: HandyWriterzSettings):
    """Setup structured logging configuration with JSON output."""
    import json
    import logging.config
    from datetime import datetime
    
    class JSONFormatter(logging.Formatter):
        """Custom JSON formatter for structured logging."""
        
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "module": record.name,
                "message": record.getMessage(),
                "function": record.funcName,
                "line": record.lineno,
                "environment": settings.environment
            }
            
            # Add extra fields if present
            if hasattr(record, 'request_id'):
                log_data["request_id"] = record.request_id
            if hasattr(record, 'user_id'):
                log_data["user_id"] = record.user_id
            if hasattr(record, 'conversation_id'):
                log_data["conversation_id"] = record.conversation_id
            if hasattr(record, 'agent_name'):
                log_data["agent_name"] = record.agent_name
            if hasattr(record, 'processing_time'):
                log_data["processing_time"] = record.processing_time
                
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = {
                    "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                    "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                    "traceback": self.formatException(record.exc_info) if record.exc_info else None
                }
            
            return json.dumps(log_data)
    
    # Register the custom formatter class
    logging.JSONFormatter = JSONFormatter
    
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "logging.JSONFormatter"
            },
            "standard": {
                "format": settings.log_format
            },
        },
        "handlers": {
            "console": {
                "level": settings.log_level,
                "class": "logging.StreamHandler",
                "formatter": "json" if settings.is_production() else "standard",
            },
            "file": {
                "level": settings.log_level,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": settings.log_file,
                "maxBytes": settings.log_max_bytes,
                "backupCount": settings.log_backup_count,
                "formatter": "json",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": settings.log_level,
                "propagate": False
            },
            "handywriterz": {
                "handlers": ["console", "file"],
                "level": settings.log_level,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
        }
    }
    
    logging.config.dictConfig(log_config)


# Initialize settings for import
settings = get_settings()
