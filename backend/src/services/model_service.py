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

        if override_model and override_model in self.price_table:
            logger.info(f"Using override model '{override_model}' for node '{node_name}' and tenant '{tenant}'")
            model_id = override_model
        else:
            # 2. Fallback to YAML defaults
            model_id = self.model_config.get("defaults", {}).get(node_name)

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

# Singleton instance
model_service = ModelService()

def get_model_service() -> ModelService:
    """Get the singleton model service instance."""
    return model_service
