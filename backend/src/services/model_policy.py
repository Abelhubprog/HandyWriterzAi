"""
Model Policy Registry for managing AI model configurations, capabilities, and routing.
Compatible with existing HandyWriterz admin system and cost controls.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import yaml
import redis.asyncio as redis
from pydantic import BaseModel, Field

from ..config import get_settings
from ..services.budget import CostLevel
# Prefer importing from the full gateway; fall back to light local definitions
try:
    from src.services.gateway import ModelSpec, ModelCapability, ProviderType  # type: ignore
except Exception:  # pragma: no cover
    from dataclasses import dataclass
    from enum import Enum as _Enum
    from typing import List as _List, Optional as _Optional

    class ProviderType(str, _Enum):  # type: ignore
        OPENROUTER = "openrouter"
        DIRECT_OPENAI = "direct_openai"
        DIRECT_ANTHROPIC = "direct_anthropic"
        DIRECT_GEMINI = "direct_gemini"
        DIRECT_PERPLEXITY = "direct_perplexity"

    @dataclass
    class ModelCapability:  # type: ignore
        streaming: bool = False
        function_calling: bool = False
        vision: bool = False
        reasoning: bool = False
        web_search: bool = False
        long_context: bool = False
        creative_writing: bool = False
        code_generation: bool = False
        json_mode: bool = False

    @dataclass
    class ModelSpec:  # type: ignore
        logical_id: str
        provider: ProviderType
        provider_model_id: str
        capabilities: ModelCapability
        cost_tier: "CostLevel"
        context_window: int
        input_cost_per_1k: float
        output_cost_per_1k: float
        fallback_models: _Optional[_List[str]] = None
        admin_overridable: bool = True


logger = logging.getLogger(__name__)


class PolicyUpdateMode(str, Enum):
    """Policy update modes"""
    OVERRIDE = "override"  # Admin override via Redis
    CONFIG = "config"      # File-based configuration
    DEFAULT = "default"    # System defaults


@dataclass
class NodeCapabilityRequirement:
    """Capability requirements for specific agent nodes"""
    node_name: str
    required_capabilities: List[str]
    preferred_capabilities: List[str] = None
    min_context_window: int = 4000
    max_cost_tier: CostLevel = CostLevel.HIGH
    reasoning_required: bool = False
    
    def __post_init__(self):
        if self.preferred_capabilities is None:
            self.preferred_capabilities = []


class PolicyValidationError(Exception):
    """Raised when model policy validation fails"""
    pass


class ModelPolicyRegistry:
    """Central registry for model policies with admin controls"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client = None
        self._initialize_redis()
        
        # Policy storage
        self.policies: Dict[str, ModelSpec] = {}
        self.node_requirements: Dict[str, NodeCapabilityRequirement] = {}
        self.provider_health: Dict[str, Dict[str, Any]] = {}
        
        # Configuration paths (derive safely from file location)
        base_dir = Path(__file__).resolve().parent.parent  # .../src/services
        self.config_dir = (base_dir.parent / "config")   # .../src/config
        self.policy_config_path = self.config_dir / "model_policies.yaml"
        self.node_requirements_path = self.config_dir / "node_requirements.yaml"
        
        # Load initial configuration
        self._load_configuration()
    
    def _initialize_redis(self):
        """Initialize Redis for admin overrides"""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available for policy overrides: {e}")
            self.redis_client = None
    
    def _load_configuration(self):
        """Load configuration from files"""
        try:
            self._load_policy_config()
            self._load_node_requirements()
            logger.info("Model policy configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load policy configuration: {e}")
            self._load_default_policies()
    
    def _load_policy_config(self):
        """Load model policies from YAML configuration"""
        if not self.policy_config_path.exists():
            self._create_default_policy_config()
        
        with open(self.policy_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Parse policies
        for policy_id, policy_data in config.get("policies", {}).items():
            try:
                # Parse capabilities
                capabilities_data = policy_data.get("capabilities", {})
                capabilities = ModelCapability(**capabilities_data)
                
                # Create model spec
                policy = ModelSpec(
                    logical_id=policy_id,
                    provider=ProviderType(policy_data["provider"]),
                    provider_model_id=policy_data["provider_model_id"],
                    capabilities=capabilities,
                    cost_tier=CostLevel(policy_data.get("cost_tier", "MEDIUM")),
                    context_window=policy_data.get("context_window", 8000),
                    input_cost_per_1k=policy_data.get("input_cost_per_1k", 0.001),
                    output_cost_per_1k=policy_data.get("output_cost_per_1k", 0.003),
                    fallback_models=policy_data.get("fallback_models", []),
                    admin_overridable=policy_data.get("admin_overridable", True)
                )
                
                self.policies[policy_id] = policy
                
            except Exception as e:
                logger.error(f"Failed to parse policy {policy_id}: {e}")
    
    def _load_node_requirements(self):
        """Load node capability requirements"""
        if not self.node_requirements_path.exists():
            self._create_default_node_requirements()
        
        with open(self.node_requirements_path, 'r') as f:
            config = yaml.safe_load(f)
        
        for node_name, requirements_data in config.get("nodes", {}).items():
            try:
                requirement = NodeCapabilityRequirement(
                    node_name=node_name,
                    required_capabilities=requirements_data.get("required_capabilities", []),
                    preferred_capabilities=requirements_data.get("preferred_capabilities", []),
                    min_context_window=requirements_data.get("min_context_window", 4000),
                    max_cost_tier=CostLevel(requirements_data.get("max_cost_tier", "HIGH")),
                    reasoning_required=requirements_data.get("reasoning_required", False)
                )
                
                self.node_requirements[node_name] = requirement
                
            except Exception as e:
                logger.error(f"Failed to parse node requirements {node_name}: {e}")
    
    def _create_default_policy_config(self):
        """Create default policy configuration file"""
        default_config = {
            "policies": {
                # Google SOTA Models
                "gemini-2.5-pro": {
                    "provider": "openrouter",
                    "provider_model_id": "google/gemini-2.5-pro",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "long_context": True,
                        "creative_writing": True,
                        "code_generation": True,
                        "reasoning": True
                    },
                    "cost_tier": "MEDIUM",
                    "context_window": 2000000,
                    "input_cost_per_1k": 0.00125,
                    "output_cost_per_1k": 0.005,
                    "fallback_models": ["claude-4-sonnet", "chatgpt-4.1"]
                },
                "gemini-2.5-flash": {
                    "provider": "openrouter",
                    "provider_model_id": "google/gemini-2.5-flash",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "long_context": True,
                        "creative_writing": True
                    },
                    "cost_tier": "LOW",
                    "context_window": 1000000,
                    "input_cost_per_1k": 0.000075,
                    "output_cost_per_1k": 0.0003,
                    "fallback_models": ["chatgpt-4o-mini-high"]
                },
                
                # OpenAI SOTA Models
                "chatgpt-o3": {
                    "provider": "openrouter",
                    "provider_model_id": "openai/chatgpt-o3",
                    "capabilities": {
                        "reasoning": True,
                        "function_calling": True,
                        "code_generation": True,
                        "streaming": True
                    },
                    "cost_tier": "PREMIUM",
                    "context_window": 200000,
                    "input_cost_per_1k": 0.015,
                    "output_cost_per_1k": 0.06,
                    "fallback_models": ["claude-4-opus", "chatgpt-4.1"]
                },
                "chatgpt-4.1": {
                    "provider": "openrouter",
                    "provider_model_id": "openai/chatgpt-4.1",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "creative_writing": True,
                        "code_generation": True
                    },
                    "cost_tier": "HIGH",
                    "context_window": 128000,
                    "input_cost_per_1k": 0.0075,
                    "output_cost_per_1k": 0.025,
                    "fallback_models": ["claude-4-sonnet", "gemini-2.5-pro"]
                },
                "o4-mini": {
                    "provider": "openrouter",
                    "provider_model_id": "openai/o4-mini-2025-04-16",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "creative_writing": True
                    },
                    "cost_tier": "LOW",
                    "context_window": 128000,
                    "input_cost_per_1k": 0.00015,
                    "output_cost_per_1k": 0.0006,
                    "fallback_models": ["gpt-4o-mini", "gemini-2.5-flash"]
                },
                "gpt-4o-mini": {
                    "provider": "openrouter",
                    "provider_model_id": "openai/gpt-4o-mini",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "creative_writing": True
                    },
                    "cost_tier": "LOW",
                    "context_window": 128000,
                    "input_cost_per_1k": 0.00015,
                    "output_cost_per_1k": 0.0006,
                    "fallback_models": ["gemini-2.5-flash"]
                },
                "chatgpt-4o": {
                    "provider": "openrouter",
                    "provider_model_id": "openai/chatgpt-4o",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "vision": True,
                        "creative_writing": True,
                        "code_generation": True
                    },
                    "cost_tier": "MEDIUM",
                    "context_window": 128000,
                    "input_cost_per_1k": 0.005,
                    "output_cost_per_1k": 0.015,
                    "fallback_models": ["chatgpt-4.1", "gemini-2.5-pro"]
                },
                
                # Anthropic SOTA Models
                "claude-4-sonnet": {
                    "provider": "openrouter",
                    "provider_model_id": "anthropic/claude-4-sonnet",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "creative_writing": True,
                        "code_generation": True,
                        "long_context": True
                    },
                    "cost_tier": "HIGH",
                    "context_window": 200000,
                    "input_cost_per_1k": 0.003,
                    "output_cost_per_1k": 0.015,
                    "fallback_models": ["chatgpt-4.1", "gemini-2.5-pro"]
                },
                "claude-4-opus": {
                    "provider": "openrouter",
                    "provider_model_id": "anthropic/claude-4-opus",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "creative_writing": True,
                        "code_generation": True,
                        "long_context": True
                    },
                    "cost_tier": "PREMIUM",
                    "context_window": 200000,
                    "input_cost_per_1k": 0.015,
                    "output_cost_per_1k": 0.075,
                    "fallback_models": ["claude-4-sonnet", "chatgpt-o3"]
                },
                
                # Specialized SOTA Models
                "deepseek-r1": {
                    "provider": "openrouter",
                    "provider_model_id": "deepseek/deepseek-r1",
                    "capabilities": {
                        "streaming": True,
                        "reasoning": True,
                        "code_generation": True,
                        "function_calling": True
                    },
                    "cost_tier": "MEDIUM",
                    "context_window": 64000,
                    "input_cost_per_1k": 0.00055,
                    "output_cost_per_1k": 0.0022,
                    "fallback_models": ["chatgpt-4.1", "claude-4-sonnet"]
                },
                "perplexity-deepresearch": {
                    "provider": "openrouter",
                    "provider_model_id": "perplexity/deepresearch",
                    "capabilities": {
                        "web_search": True,
                        "streaming": True,
                        "reasoning": True,
                        "long_context": True
                    },
                    "cost_tier": "HIGH",
                    "context_window": 127000,
                    "input_cost_per_1k": 0.005,
                    "output_cost_per_1k": 0.005,
                    "fallback_models": ["chatgpt-4.1", "gemini-2.5-pro"]
                },
                "qwen-3": {
                    "provider": "openrouter",
                    "provider_model_id": "qwen/qwen-3",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "code_generation": True
                    },
                    "cost_tier": "MEDIUM",
                    "context_window": 32000,
                    "input_cost_per_1k": 0.0008,
                    "output_cost_per_1k": 0.0008,
                    "fallback_models": ["deepseek-r1", "chatgpt-4.1"]
                },
                "glm-4.5": {
                    "provider": "openrouter",
                    "provider_model_id": "zhipuai/glm-4.5",
                    "capabilities": {
                        "streaming": True,
                        "function_calling": True,
                        "reasoning": True,
                        "creative_writing": True
                    },
                    "cost_tier": "MEDIUM",
                    "context_window": 128000,
                    "input_cost_per_1k": 0.001,
                    "output_cost_per_1k": 0.001,
                    "fallback_models": ["qwen-3", "gemini-2.5-pro"]
                },
                "kimi-k2": {
                    "provider": "openrouter",
                    "provider_model_id": "moonshot/kimi-k2",
                    "capabilities": {
                        "streaming": True,
                        "long_context": True,
                        "creative_writing": True,
                        "function_calling": True
                    },
                    "cost_tier": "LOW",
                    "context_window": 2000000,
                    "input_cost_per_1k": 0.00012,
                    "output_cost_per_1k": 0.00012,
                    "fallback_models": ["gemini-2.5-flash", "chatgpt-4o-mini-high"]
                }
            }
        }
        
        self.config_dir.mkdir(exist_ok=True)
        with open(self.policy_config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def _create_default_node_requirements(self):
        """Create default node requirements configuration"""
        default_requirements = {
            "nodes": {
                "writer": {
                    "required_capabilities": ["streaming", "creative_writing"],
                    "preferred_capabilities": ["long_context", "function_calling"],
                    "min_context_window": 8000,
                    "max_cost_tier": "HIGH",
                    "reasoning_required": False
                },
                "formatter_advanced": {
                    "required_capabilities": ["streaming"],
                    "preferred_capabilities": ["function_calling"],
                    "min_context_window": 4000,
                    "max_cost_tier": "MEDIUM",
                    "reasoning_required": False
                },
                "evaluator": {
                    "required_capabilities": ["reasoning"],
                    "preferred_capabilities": ["function_calling"],
                    "min_context_window": 8000,
                    "max_cost_tier": "PREMIUM",
                    "reasoning_required": True
                },
                "search_perplexity": {
                    "required_capabilities": ["web_search"],
                    "preferred_capabilities": ["streaming"],
                    "min_context_window": 16000,
                    "max_cost_tier": "HIGH",
                    "reasoning_required": False
                },
                "search_gemini": {
                    "required_capabilities": ["streaming"],
                    "preferred_capabilities": ["web_search", "long_context"],
                    "min_context_window": 8000,
                    "max_cost_tier": "MEDIUM",
                    "reasoning_required": False  
                },
                "qa_evaluator": {
                    "required_capabilities": ["reasoning"],
                    "preferred_capabilities": ["function_calling"],
                    "min_context_window": 8000,
                    "max_cost_tier": "HIGH",
                    "reasoning_required": True
                },
                "citation_master": {
                    "required_capabilities": ["function_calling"],
                    "preferred_capabilities": ["reasoning"],
                    "min_context_window": 16000,
                    "max_cost_tier": "MEDIUM",
                    "reasoning_required": False
                }
            }
        }
        
        self.config_dir.mkdir(exist_ok=True)
        with open(self.node_requirements_path, 'w') as f:
            yaml.dump(default_requirements, f, default_flow_style=False, indent=2)
    
    def _load_default_policies(self):
        """Load minimal default policies as fallback"""
        logger.warning("Loading minimal default policies")
        
        self.policies = {
            "gemini-2.5-pro": ModelSpec(
                logical_id="gemini-2.5-pro",
                provider=ProviderType.OPENROUTER,
                provider_model_id="google/gemini-2.0-flash-exp",
                capabilities=ModelCapability(streaming=True, creative_writing=True),
                cost_tier=CostLevel.MEDIUM,
                context_window=32000,
                input_cost_per_1k=0.00015,
                output_cost_per_1k=0.0006
            )
        }
    
    async def get_redis_override(self, key: str) -> Optional[str]:
        """Get admin override from Redis"""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.warning(f"Failed to get Redis override for {key}: {e}")
            return None
    
    async def set_redis_override(self, key: str, value: str, ttl: int = None):
        """Set admin override in Redis"""
        if not self.redis_client:
            raise PolicyValidationError("Redis not available for overrides")
        
        try:
            if ttl:
                await self.redis_client.setex(key, ttl, value)
            else:
                await self.redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set Redis override for {key}: {e}")
            raise PolicyValidationError(f"Failed to set override: {e}")
    
    async def get_policy_for_node(
        self, 
        node_name: str, 
        capabilities: List[str] = None,
        cost_override: CostLevel = None
    ) -> ModelSpec:
        """Get model policy for specific node with capability matching"""
        
        # 1. Check for admin Redis overrides first
        override_key = f"model_override:{node_name}"
        override_model = await self.get_redis_override(override_key)
        
        if override_model and override_model in self.policies:
            logger.info(f"Using admin override for {node_name}: {override_model}")
            policy = self.policies[override_model]
            
            # Apply cost override if specified
            if cost_override:
                policy.cost_tier = cost_override
            
            return policy
        
        # 2. Get node requirements
        node_req = self.node_requirements.get(node_name)
        if not node_req:
            logger.warning(f"No requirements defined for node {node_name}, using defaults")
            node_req = NodeCapabilityRequirement(
                node_name=node_name,
                required_capabilities=capabilities or [],
                max_cost_tier=cost_override or CostLevel.HIGH
            )
        
        # 3. Find best matching policy
        best_policy = self._select_best_policy(node_req, capabilities)
        
        if not best_policy:
            raise PolicyValidationError(f"No suitable model found for node {node_name}")
        
        return best_policy
    
    def _select_best_policy(
        self, 
        node_req: NodeCapabilityRequirement,
        additional_capabilities: List[str] = None
    ) -> Optional[ModelSpec]:
        """Select best policy based on requirements and capabilities"""
        
        # Combine required capabilities
        all_required = set(node_req.required_capabilities)
        if additional_capabilities:
            all_required.update(additional_capabilities)
        
        # Score policies
        scored_policies = []
        
        for policy_id, policy in self.policies.items():
            score = self._calculate_policy_score(policy, node_req, all_required)
            if score > 0:  # Only consider viable policies
                scored_policies.append((score, policy))
        
        if not scored_policies:
            logger.error(f"No viable policies for node {node_req.node_name}")
            return None
        
        # Sort by score (highest first) and return best
        scored_policies.sort(key=lambda x: x[0], reverse=True)
        best_policy = scored_policies[0][1]
        
        logger.info(f"Selected {best_policy.logical_id} for {node_req.node_name} (score: {scored_policies[0][0]})")
        return best_policy
    
    def _calculate_policy_score(
        self, 
        policy: ModelSpec, 
        node_req: NodeCapabilityRequirement,
        required_capabilities: set
    ) -> float:
        """Calculate policy match score"""
        score = 0.0
        
        # Check basic viability
        if policy.context_window < node_req.min_context_window:
            return 0.0  # Not viable
        
        if policy.cost_tier.value > node_req.max_cost_tier.value:
            return 0.0  # Too expensive
        
        if node_req.reasoning_required and not policy.capabilities.reasoning:
            return 0.0  # Reasoning required but not available
        
        # Score capability matches
        policy_capabilities = {
            cap for cap, enabled in asdict(policy.capabilities).items() 
            if enabled
        }
        
        # Required capabilities must all be met
        missing_required = required_capabilities - policy_capabilities
        if missing_required:
            return 0.0  # Missing required capabilities
        
        # Score based on capability matches
        score += len(required_capabilities & policy_capabilities) * 10
        
        # Bonus for preferred capabilities
        preferred_caps = set(node_req.preferred_capabilities)
        score += len(preferred_caps & policy_capabilities) * 5
        
        # Cost efficiency bonus (lower cost = higher score)
        cost_bonus = {
            CostLevel.LOW: 15,
            CostLevel.MEDIUM: 10,
            CostLevel.HIGH: 5,
            CostLevel.PREMIUM: 0
        }
        score += cost_bonus.get(policy.cost_tier, 0)
        
        # Context window bonus (more is better, diminishing returns)
        context_ratio = policy.context_window / max(node_req.min_context_window, 1000)
        score += min(context_ratio, 5) * 2
        
        return score
    
    async def update_node_policy(
        self, 
        node_name: str, 
        model_id: str,
        mode: PolicyUpdateMode = PolicyUpdateMode.OVERRIDE,
        ttl: int = None
    ):
        """Update policy for specific node"""
        
        # Validate model exists
        if model_id not in self.policies:
            raise PolicyValidationError(f"Model {model_id} not found in policies")
        
        policy = self.policies[model_id]
        if not policy.admin_overridable and mode == PolicyUpdateMode.OVERRIDE:
            raise PolicyValidationError(f"Model {model_id} is not admin overridable")
        
        # Update based on mode
        if mode == PolicyUpdateMode.OVERRIDE:
            override_key = f"model_override:{node_name}"
            await self.set_redis_override(override_key, model_id, ttl)
            logger.info(f"Set admin override for {node_name}: {model_id}")
        
        # TODO: Implement CONFIG mode (update YAML files)
        # TODO: Implement DEFAULT mode (reset to defaults)
    
    async def bulk_update_policies(self, updates: Dict[str, str]):
        """Bulk update multiple node policies"""
        results = {}
        
        for node_name, model_id in updates.items():
            try:
                await self.update_node_policy(node_name, model_id)
                results[node_name] = {"status": "success", "model": model_id}
            except Exception as e:
                results[node_name] = {"status": "error", "error": str(e)}
        
        return results
    
    def get_all_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get all policies for admin interface"""
        return {
            policy_id: {
                "logical_id": policy.logical_id,
                "provider": policy.provider.value,
                "provider_model_id": policy.provider_model_id,
                "capabilities": asdict(policy.capabilities),
                "cost_tier": policy.cost_tier.value,
                "context_window": policy.context_window,
                "input_cost_per_1k": policy.input_cost_per_1k,
                "output_cost_per_1k": policy.output_cost_per_1k,
                "fallback_models": policy.fallback_models,
                "admin_overridable": policy.admin_overridable
            }
            for policy_id, policy in self.policies.items()
        }
    
    def get_all_node_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Get all node requirements for admin interface"""
        return {
            node_name: {
                "required_capabilities": req.required_capabilities,
                "preferred_capabilities": req.preferred_capabilities,
                "min_context_window": req.min_context_window,
                "max_cost_tier": req.max_cost_tier.value,
                "reasoning_required": req.reasoning_required
            }
            for node_name, req in self.node_requirements.items()
        }
    
    async def get_current_assignments(self) -> Dict[str, str]:
        """Get current model assignments for all nodes"""
        assignments = {}
        
        for node_name in self.node_requirements.keys():
            try:
                policy = await self.get_policy_for_node(node_name)
                assignments[node_name] = policy.logical_id
            except Exception as e:
                assignments[node_name] = f"ERROR: {e}"
        
        return assignments
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        issues = []
        warnings = []
        
        # Check all nodes have valid assignments
        for node_name in self.node_requirements.keys():
            try:
                await self.get_policy_for_node(node_name)
            except Exception as e:
                issues.append(f"Node {node_name}: {e}")
        
        # Check for unused policies
        used_policies = set()
        for node_name in self.node_requirements.keys():
            try:
                policy = await self.get_policy_for_node(node_name)
                used_policies.add(policy.logical_id)
            except:
                pass
        
        unused_policies = set(self.policies.keys()) - used_policies
        if unused_policies:
            warnings.append(f"Unused policies: {', '.join(unused_policies)}")
        
        # Check fallback chains
        for policy_id, policy in self.policies.items():
            for fallback in policy.fallback_models:
                if fallback not in self.policies:
                    issues.append(f"Policy {policy_id} has invalid fallback: {fallback}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_policies": len(self.policies),
            "total_nodes": len(self.node_requirements)
        }
    
    async def reload_configuration(self):
        """Reload configuration from files"""
        try:
            self._load_configuration()
            logger.info("Model policy configuration reloaded")
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            raise


# Global registry instance
_registry_instance = None

def get_model_policy_registry() -> ModelPolicyRegistry:
    """Get global model policy registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModelPolicyRegistry()
    return _registry_instance
