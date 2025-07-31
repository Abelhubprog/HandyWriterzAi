"""
Model Registry for HandyWriterzAI

Provides unified model ID mapping and validation across providers.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, NamedTuple
import yaml

logger = logging.getLogger(__name__)


class ModelInfo(NamedTuple):
    """Model information from registry."""
    provider: str
    provider_model_id: str
    pricing: Dict[str, Any]
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    supports_streaming: bool = True
    supports_function_calling: bool = False


class ModelRegistry:
    """
    Unified model registry that maps logical model IDs to provider-specific IDs
    and maintains pricing information for budget enforcement.
    """
    
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._loaded = False
        self._strict_mode = False
    
    def load(self, model_config_path: str, price_table_path: str, strict: bool = False) -> None:
        """
        Load model configuration and pricing from files.
        
        Args:
            model_config_path: Path to model_config.yaml
            price_table_path: Path to price_table.json
            strict: Whether to fail on validation errors (default: warn)
        """
        self._strict_mode = strict
        
        try:
            # Load model configuration
            model_config = self._load_model_config(model_config_path)
            
            # Load pricing table
            price_table = self._load_price_table(price_table_path)
            
            # Build registry
            self._build_registry(model_config, price_table)
            
            self._loaded = True
            logger.info(f"✅ Model registry loaded with {len(self._models)} models")
            
        except Exception as e:
            error_msg = f"Failed to load model registry: {e}"
            if self._strict_mode:
                raise RuntimeError(error_msg)
            else:
                logger.warning(f"⚠️  {error_msg}")
    
    def resolve(self, logical_id: str) -> Optional[ModelInfo]:
        """
        Resolve logical model ID to provider information.
        
        Args:
            logical_id: Logical model identifier (e.g., "o3-reasoner", "sonar-deep")
            
        Returns:
            ModelInfo if found, None otherwise
        """
        if not self._loaded:
            logger.warning("Model registry not loaded")
            return None
        
        return self._models.get(logical_id)
    
    def validate(self) -> bool:
        """
        Validate registry consistency.
        
        Returns:
            True if valid, False if issues found
        """
        if not self._loaded:
            logger.error("Cannot validate unloaded registry")
            return False
        
        issues = []
        
        # Check for missing pricing
        for logical_id, model_info in self._models.items():
            if not model_info.pricing:
                issues.append(f"Missing pricing for {logical_id}")
            
            required_pricing_fields = ["input_cost_per_1k", "output_cost_per_1k"]
            for field in required_pricing_fields:
                if field not in model_info.pricing:
                    issues.append(f"Missing {field} in pricing for {logical_id}")
        
        if issues:
            for issue in issues:
                if self._strict_mode:
                    logger.error(f"❌ Registry validation: {issue}")
                else:
                    logger.warning(f"⚠️  Registry validation: {issue}")
            return not self._strict_mode
        
        logger.info("✅ Model registry validation passed")
        return True
    
    def get_all_models(self) -> Dict[str, ModelInfo]:
        """Get all registered models."""
        return self._models.copy()
    
    def get_models_by_provider(self, provider: str) -> Dict[str, ModelInfo]:
        """Get all models for a specific provider."""
        return {
            logical_id: model_info
            for logical_id, model_info in self._models.items()
            if model_info.provider == provider
        }
    
    def _load_model_config(self, config_path: str) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded model config from {config_path}")
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load model config from {config_path}: {e}")
    
    def _load_price_table(self, price_path: str) -> Dict[str, Any]:
        """Load pricing table from JSON file."""
        try:
            with open(price_path, 'r') as f:
                pricing = json.load(f)
            logger.debug(f"Loaded price table from {price_path}")
            return pricing
        except Exception as e:
            raise RuntimeError(f"Failed to load price table from {price_path}: {e}")
    
    def _build_registry(self, model_config: Dict[str, Any], price_table: Dict[str, Any]) -> None:
        """Build registry from configuration and pricing data."""
        
        # Get model mappings from config
        model_defaults = model_config.get("model_defaults", {})
        provider_models = model_config.get("providers", {})
        
        # Build logical -> provider mappings
        logical_mappings = {}
        
        # Add default models
        for provider, default_model in model_defaults.items():
            if isinstance(default_model, str):
                logical_mappings[f"{provider}-default"] = {
                    "provider": provider,
                    "model_id": default_model
                }
        
        # Add explicit provider models
        for provider, models in provider_models.items():
            if isinstance(models, dict):
                for logical_name, provider_model_id in models.items():
                    logical_mappings[logical_name] = {
                        "provider": provider,
                        "model_id": provider_model_id
                    }
        
        # Add hardcoded mappings for known aliases
        hardcoded_mappings = {
            "o3-reasoner": {"provider": "openai", "model_id": "o1-preview"},
            "o3-mini": {"provider": "openai", "model_id": "o1-mini"},
            "sonar-deep": {"provider": "perplexity", "model_id": "llama-3.1-sonar-large-128k-online"},
            "sonar-fast": {"provider": "perplexity", "model_id": "llama-3.1-sonar-small-128k-online"},
            "gemini-pro": {"provider": "gemini", "model_id": "gemini-pro"},
            "gemini-flash": {"provider": "gemini", "model_id": "gemini-1.5-flash"},
            "claude-sonnet": {"provider": "anthropic", "model_id": "claude-3-sonnet-20240229"},
            "claude-haiku": {"provider": "anthropic", "model_id": "claude-3-haiku-20240307"},
        }
        
        # Merge hardcoded mappings (prioritize config over hardcoded)
        for logical_id, mapping in hardcoded_mappings.items():
            if logical_id not in logical_mappings:
                logical_mappings[logical_id] = mapping
        
        # Build final registry with pricing
        for logical_id, mapping in logical_mappings.items():
            provider = mapping["provider"]
            provider_model_id = mapping["model_id"]
            
            # Find pricing information
            pricing = self._find_pricing(provider, provider_model_id, price_table)
            
            # Get model capabilities (defaults)
            context_window = self._get_context_window(provider, provider_model_id)
            max_output_tokens = self._get_max_output_tokens(provider, provider_model_id)
            supports_streaming = self._supports_streaming(provider, provider_model_id)
            supports_function_calling = self._supports_function_calling(provider, provider_model_id)
            
            self._models[logical_id] = ModelInfo(
                provider=provider,
                provider_model_id=provider_model_id,
                pricing=pricing,
                context_window=context_window,
                max_output_tokens=max_output_tokens,
                supports_streaming=supports_streaming,
                supports_function_calling=supports_function_calling
            )
    
    def _find_pricing(self, provider: str, model_id: str, price_table: Dict[str, Any]) -> Dict[str, Any]:
        """Find pricing information for a model."""
        
        # Try exact match first
        for price_entry in price_table.get("models", []):
            if (price_entry.get("provider") == provider and 
                price_entry.get("model") == model_id):
                return {
                    "input_cost_per_1k": price_entry.get("input_cost_per_1k", 0.0),
                    "output_cost_per_1k": price_entry.get("output_cost_per_1k", 0.0),
                    "currency": price_entry.get("currency", "USD")
                }
        
        # Try provider defaults
        provider_defaults = price_table.get("provider_defaults", {}).get(provider, {})
        if provider_defaults:
            return {
                "input_cost_per_1k": provider_defaults.get("input_cost_per_1k", 0.0),
                "output_cost_per_1k": provider_defaults.get("output_cost_per_1k", 0.0),
                "currency": provider_defaults.get("currency", "USD")
            }
        
        # Default fallback pricing
        default_pricing = {
            "input_cost_per_1k": 0.01,  # $0.01 per 1K tokens
            "output_cost_per_1k": 0.02,  # $0.02 per 1K tokens
            "currency": "USD"
        }
        
        if self._strict_mode:
            logger.warning(f"No pricing found for {provider}:{model_id}, using defaults")
        
        return default_pricing
    
    def _get_context_window(self, provider: str, model_id: str) -> Optional[int]:
        """Get context window size for model."""
        
        # Known context windows
        context_windows = {
            ("openai", "gpt-4"): 8192,
            ("openai", "gpt-4-turbo"): 128000,
            ("openai", "gpt-3.5-turbo"): 16385,
            ("openai", "o1-preview"): 128000,
            ("openai", "o1-mini"): 128000,
            ("anthropic", "claude-3-sonnet-20240229"): 200000,
            ("anthropic", "claude-3-haiku-20240307"): 200000,
            ("gemini", "gemini-pro"): 32768,
            ("gemini", "gemini-1.5-flash"): 1048576,
            ("perplexity", "llama-3.1-sonar-large-128k-online"): 127072,
            ("perplexity", "llama-3.1-sonar-small-128k-online"): 127072,
        }
        
        return context_windows.get((provider, model_id), 8192)  # Default 8K
    
    def _get_max_output_tokens(self, provider: str, model_id: str) -> Optional[int]:
        """Get maximum output tokens for model."""
        
        # Most models default to 4K max output, some exceptions
        max_outputs = {
            ("openai", "o1-preview"): 32768,
            ("openai", "o1-mini"): 32768,
            ("anthropic", "claude-3-sonnet-20240229"): 4096,
            ("anthropic", "claude-3-haiku-20240307"): 4096,
            ("gemini", "gemini-1.5-flash"): 8192,
        }
        
        return max_outputs.get((provider, model_id), 4096)  # Default 4K
    
    def _supports_streaming(self, provider: str, model_id: str) -> bool:
        """Check if model supports streaming."""
        
        # Most models support streaming, few exceptions
        non_streaming_models = [
            ("openai", "o1-preview"),
            ("openai", "o1-mini"),
        ]
        
        return (provider, model_id) not in non_streaming_models
    
    def _supports_function_calling(self, provider: str, model_id: str) -> bool:
        """Check if model supports function calling."""
        
        # Function calling support by provider/model
        function_calling_models = [
            ("openai", "gpt-4"),
            ("openai", "gpt-4-turbo"),
            ("openai", "gpt-3.5-turbo"),
            ("anthropic", "claude-3-sonnet-20240229"),
            ("gemini", "gemini-pro"),
            ("gemini", "gemini-1.5-flash"),
        ]
        
        return (provider, model_id) in function_calling_models


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get global model registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def initialize_registry(model_config_path: str, price_table_path: str, strict: bool = False) -> ModelRegistry:
    """Initialize global model registry."""
    registry = get_registry()
    registry.load(model_config_path, price_table_path, strict)
    return registry


def resolve_model(logical_id: str) -> Optional[ModelInfo]:
    """Convenience function to resolve model via global registry."""
    return get_registry().resolve(logical_id)