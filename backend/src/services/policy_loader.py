"""
Policy Loader for ChatOrchestrator
Loads and manages externalized orchestration policies from configuration files.
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskType(str, Enum):
    """Task types for orchestration policies."""
    GENERAL = "GENERAL"
    ACADEMIC_WRITING = "ACADEMIC_WRITING"
    RESEARCH = "RESEARCH"
    CODE_ANALYSIS = "CODE_ANALYSIS"
    CREATIVE_WRITING = "CREATIVE_WRITING"

@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""
    max_retries: int
    timeout: int
    rate_limit_buffer: float
    preferred_models: List[str]

@dataclass
class SelectionCriteria:
    """Criteria weights for model selection."""
    cost_weight: float
    performance_weight: float
    availability_weight: float
    specialization_weight: float

@dataclass
class FailurePolicy:
    """Failure handling policies."""
    max_fallback_attempts: int
    circuit_breaker_failure_threshold: int
    circuit_breaker_recovery_timeout: int
    provider_cooldown_rate_limit: int
    provider_cooldown_service_error: int
    provider_cooldown_auth_error: int

@dataclass
class QualityThresholds:
    """Quality thresholds for model selection."""
    min_confidence_score: float
    max_latency_ms: int
    min_context_utilization: float

@dataclass
class CostPolicies:
    """Cost control policies."""
    max_cost_per_request: float
    preferred_cost_range: tuple
    cost_optimization_enabled: bool

class OrchestratorPolicies:
    """Container for all orchestration policies."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "src/config/orchestrator_policies.yaml"
        self.policies: Dict[str, Any] = {}
        self.provider_restrictions: Dict[str, Dict[str, List[str]]] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self.selection_criteria: SelectionCriteria = SelectionCriteria(0.3, 0.4, 0.2, 0.1)
        self.failure_policies: FailurePolicy = FailurePolicy(3, 5, 300, 300, 60, 1800)
        self.quality_thresholds: QualityThresholds = QualityThresholds(0.7, 30000, 0.5)
        self.cost_policies: CostPolicies = CostPolicies(5.0, (0.01, 1.0), True)
        self.task_model_preferences: Dict[str, Dict[str, List[str]]] = {}
        
        self._load_policies()
    
    def _load_policies(self):
        """Load policies from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.policies = yaml.safe_load(f) or {}
                
                self._parse_provider_restrictions()
                self._parse_provider_configs()
                self._parse_selection_criteria()
                self._parse_failure_policies()
                self._parse_quality_thresholds()
                self._parse_cost_policies()
                self._parse_task_model_preferences()
                
                logger.info(f"✅ Orchestrator policies loaded from {self.config_path}")
            else:
                logger.warning(f"⚠️  Policy file not found: {self.config_path}, using defaults")
                self._load_default_policies()
                
        except Exception as e:
            logger.error(f"❌ Failed to load orchestrator policies: {e}")
            self._load_default_policies()
    
    def _parse_provider_restrictions(self):
        """Parse provider restrictions from config."""
        restrictions = self.policies.get("provider_restrictions", {})
        
        for task_type, config in restrictions.items():
            self.provider_restrictions[task_type] = {
                "allowed_providers": config.get("allowed_providers", []),
                "preferred_providers": config.get("preferred_providers", []),
                "fallback_order": config.get("fallback_order", []),
                "excluded_providers": config.get("excluded_providers", [])
            }
    
    def _parse_provider_configs(self):
        """Parse provider-specific configurations."""
        configs = self.policies.get("provider_configs", {})
        
        for provider, config in configs.items():
            self.provider_configs[provider] = ProviderConfig(
                max_retries=config.get("max_retries", 3),
                timeout=config.get("timeout", 60),
                rate_limit_buffer=config.get("rate_limit_buffer", 0.8),
                preferred_models=config.get("preferred_models", [])
            )
    
    def _parse_selection_criteria(self):
        """Parse selection criteria weights."""
        criteria = self.policies.get("selection_criteria", {})
        
        self.selection_criteria = SelectionCriteria(
            cost_weight=criteria.get("cost_weight", 0.3),
            performance_weight=criteria.get("performance_weight", 0.4),
            availability_weight=criteria.get("availability_weight", 0.2),
            specialization_weight=criteria.get("specialization_weight", 0.1)
        )
    
    def _parse_failure_policies(self):
        """Parse failure handling policies."""
        failure_config = self.policies.get("failure_policies", {})
        circuit_breaker = failure_config.get("circuit_breaker", {})
        cooldown = failure_config.get("provider_cooldown", {})
        
        self.failure_policies = FailurePolicy(
            max_fallback_attempts=failure_config.get("max_fallback_attempts", 3),
            circuit_breaker_failure_threshold=circuit_breaker.get("failure_threshold", 5),
            circuit_breaker_recovery_timeout=circuit_breaker.get("recovery_timeout", 300),
            provider_cooldown_rate_limit=cooldown.get("on_rate_limit", 300),
            provider_cooldown_service_error=cooldown.get("on_service_error", 60),
            provider_cooldown_auth_error=cooldown.get("on_auth_error", 1800)
        )
    
    def _parse_quality_thresholds(self):
        """Parse quality thresholds."""
        quality = self.policies.get("quality_thresholds", {})
        
        self.quality_thresholds = QualityThresholds(
            min_confidence_score=quality.get("min_confidence_score", 0.7),
            max_latency_ms=quality.get("max_latency_ms", 30000),
            min_context_utilization=quality.get("min_context_utilization", 0.5)
        )
    
    def _parse_cost_policies(self):
        """Parse cost control policies."""
        cost = self.policies.get("cost_policies", {})
        cost_range = cost.get("preferred_cost_range", [0.01, 1.0])
        
        self.cost_policies = CostPolicies(
            max_cost_per_request=cost.get("max_cost_per_request", 5.0),
            preferred_cost_range=tuple(cost_range),
            cost_optimization_enabled=cost.get("cost_optimization_enabled", True)
        )
    
    def _parse_task_model_preferences(self):
        """Parse task-specific model preferences."""
        self.task_model_preferences = self.policies.get("task_model_preferences", {})
    
    def _load_default_policies(self):
        """Load hardcoded default policies as fallback."""
        logger.info("Loading default orchestrator policies")
        
        # Default provider restrictions (preserves original logic)
        self.provider_restrictions = {
            "GENERAL": {
                "allowed_providers": ["openai", "anthropic", "gemini", "perplexity", "openrouter"],
                "preferred_providers": ["gemini", "openai"],
                "fallback_order": ["gemini", "openai", "anthropic"],
                "excluded_providers": []
            },
            "ACADEMIC_WRITING": {
                "allowed_providers": ["openai", "anthropic", "perplexity"],
                "preferred_providers": ["openai", "anthropic"],
                "fallback_order": ["openai", "anthropic", "perplexity"],
                "excluded_providers": ["gemini"]  # Original Gemini exclusion
            }
        }
    
    def get_allowed_providers(self, task_type: str) -> List[str]:
        """Get allowed providers for a task type."""
        restrictions = self.provider_restrictions.get(task_type, {})
        return restrictions.get("allowed_providers", [])
    
    def get_excluded_providers(self, task_type: str) -> List[str]:
        """Get excluded providers for a task type."""
        restrictions = self.provider_restrictions.get(task_type, {})
        return restrictions.get("excluded_providers", [])
    
    def get_preferred_providers(self, task_type: str) -> List[str]:
        """Get preferred providers for a task type."""
        restrictions = self.provider_restrictions.get(task_type, {})
        return restrictions.get("preferred_providers", [])
    
    def get_fallback_order(self, task_type: str) -> List[str]:
        """Get fallback order for a task type."""
        restrictions = self.provider_restrictions.get(task_type, {})
        return restrictions.get("fallback_order", [])
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return self.provider_configs.get(provider)
    
    def is_provider_allowed(self, provider: str, task_type: str) -> bool:
        """Check if provider is allowed for task type."""
        allowed = self.get_allowed_providers(task_type)
        excluded = self.get_excluded_providers(task_type)
        
        # If no specific rules, allow all
        if not allowed and not excluded:
            return True
        
        # Check exclusion first
        if excluded and provider in excluded:
            return False
        
        # Check inclusion if rules exist
        if allowed:
            return provider in allowed
        
        return True
    
    def reload_policies(self):
        """Reload policies from configuration file."""
        logger.info("Reloading orchestrator policies")
        self._load_policies()

# Global policies instance
_policies: Optional[OrchestratorPolicies] = None

def get_orchestrator_policies() -> OrchestratorPolicies:
    """Get global orchestrator policies instance."""
    global _policies
    if _policies is None:
        _policies = OrchestratorPolicies()
    return _policies

def reload_orchestrator_policies():
    """Reload orchestrator policies from configuration."""
    global _policies
    if _policies is not None:
        _policies.reload_policies()
    else:
        _policies = OrchestratorPolicies()