import logging
import yaml
import json
from functools import lru_cache
from typing import Dict, Any, Optional

# Placeholder for a proper Redis client
class MockRedis:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

redis_client = MockRedis()

logger = logging.getLogger(__name__)

class BudgetExceeded(Exception):
    """Custom exception for when a budget is exceeded."""
    pass

class LLMClient:
    """Represents a client for a large language model."""
    def __init__(self, model_id: str, price_per_1k_input: float, price_per_1k_output: float):
        self.model_id = model_id
        self.price_per_1k_input = price_per_1k_input
        self.price_per_1k_output = price_per_1k_output

    def __repr__(self) -> str:
        return f"LLMClient(model_id='{self.model_id}')"

class PriceGuard:
    """Handles budget checks for model usage."""
    def __init__(self, user_budget: float = 5.0):
        self.user_budget = user_budget
        self.current_spend = 0.0

    def charge(self, node: str, model_id: str, tokens: Dict[str, int], price_table: Dict[str, Any]) -> None:
        """
        Calculates the cost of a model call and raises an exception if the budget is exceeded.
        """
        model_prices = price_table.get(model_id)
        if not model_prices:
            raise ValueError(f"Price not found for model: {model_id}")

        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        cost = (input_tokens / 1000 * model_prices["input"]) + (output_tokens / 1000 * model_prices["output"])

        if self.current_spend + cost > self.user_budget:
            raise BudgetExceeded(f"Operation on node '{node}' with model '{model_id}' exceeds budget.")

        self.current_spend += cost
        logger.info(f"Charged ${cost:.4f} for {input_tokens} input and {output_tokens} output tokens. Total spend: ${self.current_spend:.4f}")

class ModelService:
    """Manages the mapping between pipeline stages, models, and tenants."""

    def __init__(self, config_path: str = "src/config/model_config.yaml", price_table_path: str = "src/config/price_table.json"):
        self.config_path = config_path
        self.price_table_path = price_table_path
        self.model_config = self._load_config(self.config_path)
        self.price_table = self._load_config(self.price_table_path, is_json=True)
        self.price_guard = PriceGuard()

        # Feature flags
        self._strict_registry = str(os.getenv("FEATURE_MODEL_REGISTRY_STRICT", "false")).lower() == "true"

        # Map logical IDs from YAML to provider IDs in price table
        # Extendable alias map; keep additive and conservative to avoid harm
        self._id_map: Dict[str, str] = {
            # YAML defaults -> price_table keys
            "gemini-2.5-pro": "google/gemini-2.5-pro",
            # additional common aliases
            "gemini-2.5-flash": "google/gemini-2.5-pro",  # if flash not present, map to closest priced entry
            "o3-reasoner": "openai/o3",
            "o3-reasoner-mini": "openai/o3",  # fallback alias to o3 pricing if mini not listed
            "sonar-deep": "perplexity/sonar-deep-research",
            "kimi-k2": "moonshotai/kimi-k2",
            "claude-opus": "anthropic/claude-opus-4",
            "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",
            "gpt-4o-mini": "openai/gpt-4o-mini",
        }

        # Validate mapped defaults at startup (warn by default, strict via flag)
        try:
            missing = self.validate_startup_defaults()
            if missing:
                msg = f"ModelService defaults validation: missing pricing for {list(missing.keys())}"
                if self._strict_registry:
                    raise ValueError(msg)
                logger.warning(msg)
        except Exception as e:
            logger.error(f"ModelService defaults validation error: {e}")

    def _load_config(self, path: str, is_json: bool = False) -> Dict[str, Any]:
        """Loads a configuration file (YAML or JSON)."""
        try:
            with open(path, "r") as f:
                if is_json:
                    return json.load(f)
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found at {path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading configuration from {path}: {e}")
            return {}

    def _normalize_model_id(self, model_id: str) -> str:
        """
        Normalize a logical model id from YAML into a concrete provider id
        used by the price table. Falls back to the original when no mapping.
        """
        if not isinstance(model_id, str):
            return model_id
        key = model_id.strip()
        mapped = self._id_map.get(key)
        if mapped:
            return mapped
        # If provided key already looks like a provider id and exists in price table, return as-is
        if key in self.price_table:
            return key
        # Last-resort: try suffix match of known provider ids to logical tail
        logical_tail = key.split("/")[-1]
        for provider_id in self.price_table.keys():
            if provider_id.endswith(logical_tail):
                return provider_id
        return key

    @lru_cache(maxsize=128)
    def get(self, node_name: str, tenant: str = "default") -> Optional[LLMClient]:
        """
        Gets the appropriate LLMClient for a given node and tenant, checking for overrides.
        """
        # 1. Check for Redis override
        override_key = f"model_override:{tenant}:{node_name}"
        override_model = redis_client.get(override_key)
        if isinstance(override_model, bytes):
            override_model = override_model.decode('utf-8')

        model_id: Optional[str] = None
        if override_model:
            normalized = self._normalize_model_id(override_model)
            if normalized in self.price_table:
                logger.info(f"Using override model '{normalized}' for node '{node_name}' and tenant '{tenant}'")
                model_id = normalized
            else:
                logger.warning(f"Override model '{override_model}' not found in price table (normalized '{normalized}')")
        if not model_id:
            # 2. Fallback to YAML defaults
            configured = (self.model_config.get("defaults", {}) or {}).get(node_name)
            model_id = self._normalize_model_id(configured) if configured else None

        if not model_id:
            logger.warning(f"No model configured for node: {node_name}")
            return None

        # 3. Create LLMClient with pricing
        model_prices = self.price_table.get(model_id)
        if not model_prices:
            logger.error(f"Price not found for model: {model_id}")
            return None

        return LLMClient(
            model_id=model_id,
            price_per_1k_input=model_prices["input"],
            price_per_1k_output=model_prices["output"]
        )

    def get_with_pricing(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        Resolve model_key (logical or provider id) to a provider id and include pricing.
        Returns {"model_id": "...", "pricing": {...}} or None if unknown.
        """
        if not isinstance(model_key, str) or not model_key:
            return None
        resolved = self._normalize_model_id(model_key)
        pricing = self.price_table.get(resolved)
        if not pricing:
            return None
        return {"model_id": resolved, "pricing": pricing}

    def validate_startup_defaults(self) -> Dict[str, str]:
        """
        Validate that all defaults in model_config.yaml resolve to priced provider IDs.
        Returns {logical_id: reason} for any that do not resolve.
        """
        missing: Dict[str, str] = {}
        defaults = (self.model_config.get("defaults", {}) or {})
        for node, logical in defaults.items():
            if not logical:
                missing[f"{node}:<empty>"] = "no logical id configured"
                continue
            resolved = self._normalize_model_id(str(logical))
            if resolved not in self.price_table:
                missing[str(logical)] = f"normalized to '{resolved}' but not found in price_table"
        return missing

# Singleton instance
model_service = ModelService()

def get_model_service() -> ModelService:
    """Get the singleton model service instance."""
    return model_service
