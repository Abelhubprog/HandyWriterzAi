#!/usr/bin/env python3
"""
Test configuration that bypasses complex validation for testing.
"""

import os


class TestConfig:
    """Simple test configuration."""
    
    def __init__(self):
        # Basic settings
        self.environment = "testing"
        self.debug = True
        self.test_mode = True
        
        # Required fields with defaults
        self.database_url = "sqlite:///./test.db"
        self.redis_url = "redis://localhost:6379"
        self.jwt_secret_key = "test-secret-key-for-testing-only-32-chars-long"
        
        # API keys from environment
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Optional settings
        self.api_host = "0.0.0.0"
        self.api_port = 8000
        self.log_level = "INFO"
        
        # Frontend
        self.frontend_url = "http://localhost:3000"
        self.allowed_origins = ["http://localhost:3000"]
        self.cors_origins = ["http://localhost:3000"]
        
        # File storage
        self.upload_dir = "/tmp/test_uploads"
        
        # Agent settings
        self.max_agent_retries = 3
        self.agent_timeout_seconds = 300
        
        # Quality settings
        self.min_quality_score = 0.75
        self.min_citation_density = 0.02
        self.min_academic_tone = 0.70
        
        # Limits
        self.max_word_count = 10000
        self.min_word_count = 100
        self.max_sources_per_request = 50
        
        # Rate limiting
        self.rate_limit_requests = 100
        self.rate_limit_window = 300
    
    def is_production(self) -> bool:
        return False
        
    def is_development(self) -> bool:
        return False
        
    def is_testing(self) -> bool:
        return True
    
    def get_ai_provider_config(self):
        return {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
            "perplexity": self.perplexity_api_key
        }
    
    def get_storage_config(self):
        return {
            "provider": "local",
            "upload_dir": self.upload_dir
        }


# Global test settings instance
test_settings = TestConfig()