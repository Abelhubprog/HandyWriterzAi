"""
Budget Enforcement Service for HandyWriterzAI

Provides token estimation, cost tracking, and budget controls to prevent
excessive spending and abuse.
"""

import logging
import time
from typing import Dict, Any, Optional, NamedTuple
from enum import Enum

logger = logging.getLogger(__name__)


class BudgetResult(NamedTuple):
    """Result of budget check."""
    allowed: bool
    reason: str
    estimated_cost: float
    remaining_budget: float
    code: str


class BudgetExceededError(Exception):
    """Raised when budget limits are exceeded."""
    
    def __init__(self, message: str, code: str, estimated_cost: float, remaining_budget: float):
        super().__init__(message)
        self.code = code
        self.estimated_cost = estimated_cost
        self.remaining_budget = remaining_budget


class CostLevel(Enum):
    """Cost levels for different operation types."""
    LOW = "low"           # Simple queries, small responses
    MEDIUM = "medium"     # Standard research, moderate responses  
    HIGH = "high"         # Complex analysis, long documents
    PREMIUM = "premium"   # Advanced features, extensive processing


class BudgetGuard:
    """
    Budget enforcement system that tracks costs and prevents overspending.
    """
    
    def __init__(self):
        # Default budget limits (can be overridden per user/tenant)
        self.default_limits = {
            "daily_budget": 50.0,        # $50 per day
            "hourly_budget": 10.0,       # $10 per hour
            "request_budget": 5.0,       # $5 per request
            "monthly_budget": 500.0,     # $500 per month
        }
        
        # Cost estimation multipliers
        self.cost_multipliers = {
            CostLevel.LOW: 1.0,
            CostLevel.MEDIUM: 2.5,
            CostLevel.HIGH: 5.0,
            CostLevel.PREMIUM: 10.0,
        }
        
        # Token cost estimates (USD per 1K tokens)
        self.token_costs = {
            "input_base": 0.01,
            "output_base": 0.02,
            "processing_overhead": 0.005,
        }
        
        # Usage tracking (in-memory for now, should be Redis/DB in production)
        self._usage_tracker: Dict[str, Dict[str, Any]] = {}
    
    def guard(
        self,
        estimated_tokens: int,
        role: str = "user",
        model: Optional[str] = None,
        tenant: Optional[str] = None,
        cost_level: CostLevel = CostLevel.MEDIUM,
        user_limits: Optional[Dict[str, float]] = None
    ) -> BudgetResult:
        """
        Check if request is within budget limits.
        
        Args:
            estimated_tokens: Estimated total tokens (input + output)
            role: User role (affects limits)
            model: Model being used (affects cost)
            tenant: Tenant/user identifier
            cost_level: Cost level of the operation
            user_limits: Custom limits for this user
            
        Returns:
            BudgetResult with allow/deny decision and details
        """
        try:
            # Estimate cost
            estimated_cost = self._estimate_cost(
                estimated_tokens, 
                model, 
                cost_level
            )
            
            # Get applicable limits
            limits = self._get_limits(role, user_limits)
            
            # Check usage against limits
            usage = self._get_usage(tenant or "default")
            
            # Daily budget check
            daily_spent = usage.get("daily_spent", 0.0)
            if daily_spent + estimated_cost > limits["daily_budget"]:
                return BudgetResult(
                    allowed=False,
                    reason=f"Daily budget exceeded: ${daily_spent + estimated_cost:.2f} > ${limits['daily_budget']:.2f}",
                    estimated_cost=estimated_cost,
                    remaining_budget=max(0, limits["daily_budget"] - daily_spent),
                    code="DAILY_BUDGET_EXCEEDED"
                )
            
            # Hourly budget check
            hourly_spent = usage.get("hourly_spent", 0.0)
            if hourly_spent + estimated_cost > limits["hourly_budget"]:
                return BudgetResult(
                    allowed=False,
                    reason=f"Hourly budget exceeded: ${hourly_spent + estimated_cost:.2f} > ${limits['hourly_budget']:.2f}",
                    estimated_cost=estimated_cost,
                    remaining_budget=max(0, limits["hourly_budget"] - hourly_spent),
                    code="HOURLY_BUDGET_EXCEEDED"
                )
            
            # Request budget check
            if estimated_cost > limits["request_budget"]:
                return BudgetResult(
                    allowed=False,
                    reason=f"Request budget exceeded: ${estimated_cost:.2f} > ${limits['request_budget']:.2f}",
                    estimated_cost=estimated_cost,
                    remaining_budget=limits["request_budget"],
                    code="REQUEST_BUDGET_EXCEEDED"
                )
            
            # Monthly budget check
            monthly_spent = usage.get("monthly_spent", 0.0)
            if monthly_spent + estimated_cost > limits["monthly_budget"]:
                return BudgetResult(
                    allowed=False,
                    reason=f"Monthly budget exceeded: ${monthly_spent + estimated_cost:.2f} > ${limits['monthly_budget']:.2f}",
                    estimated_cost=estimated_cost,
                    remaining_budget=max(0, limits["monthly_budget"] - monthly_spent),
                    code="MONTHLY_BUDGET_EXCEEDED"
                )
            
            # All checks passed
            return BudgetResult(
                allowed=True,
                reason="Within budget limits",
                estimated_cost=estimated_cost,
                remaining_budget=min(
                    limits["daily_budget"] - daily_spent,
                    limits["hourly_budget"] - hourly_spent,
                    limits["monthly_budget"] - monthly_spent
                ),
                code="BUDGET_OK"
            )
            
        except Exception as e:
            logger.error(f"Budget guard error: {e}")
            # Fail open with warning
            return BudgetResult(
                allowed=True,
                reason=f"Budget check failed: {e}",
                estimated_cost=0.0,
                remaining_budget=0.0,
                code="BUDGET_CHECK_FAILED"
            )
    
    def record_usage(
        self,
        actual_cost: float,
        tokens_used: int,
        tenant: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """
        Record actual usage after request completion.
        
        Args:
            actual_cost: Actual cost incurred
            tokens_used: Actual tokens consumed
            tenant: Tenant/user identifier
            model: Model used
        """
        try:
            tenant_key = tenant or "default"
            current_time = time.time()
            
            if tenant_key not in self._usage_tracker:
                self._usage_tracker[tenant_key] = {
                    "daily_spent": 0.0,
                    "hourly_spent": 0.0,
                    "monthly_spent": 0.0,
                    "daily_reset": current_time,
                    "hourly_reset": current_time,
                    "monthly_reset": current_time,
                    "total_requests": 0,
                    "total_tokens": 0,
                }
            
            usage = self._usage_tracker[tenant_key]
            
            # Reset counters if time periods have elapsed
            self._reset_expired_counters(usage, current_time)
            
            # Update usage
            usage["daily_spent"] += actual_cost
            usage["hourly_spent"] += actual_cost
            usage["monthly_spent"] += actual_cost
            usage["total_requests"] += 1
            usage["total_tokens"] += tokens_used
            
            logger.debug(f"Recorded usage for {tenant_key}: ${actual_cost:.4f}, {tokens_used} tokens")
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
    
    def get_usage_summary(self, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage summary for a tenant.
        
        Args:
            tenant: Tenant/user identifier
            
        Returns:
            Usage summary dictionary
        """
        tenant_key = tenant or "default"
        
        if tenant_key not in self._usage_tracker:
            return {
                "daily_spent": 0.0,
                "hourly_spent": 0.0,
                "monthly_spent": 0.0,
                "total_requests": 0,
                "total_tokens": 0,
                "limits": self.default_limits.copy()
            }
        
        usage = self._usage_tracker[tenant_key].copy()
        usage["limits"] = self.default_limits.copy()
        
        # Reset expired counters for accurate reporting
        current_time = time.time()
        self._reset_expired_counters(usage, current_time)
        
        return usage
    
    def estimate_tokens(
        self,
        text: str,
        files: Optional[list] = None,
        complexity_multiplier: float = 1.0
    ) -> int:
        """
        Estimate tokens for input text and files.
        
        Args:
            text: Input text
            files: List of uploaded files
            complexity_multiplier: Multiplier based on task complexity
            
        Returns:
            Estimated total tokens (input + expected output)
        """
        # Rough token estimation (1 token ≈ 4 characters for English)
        input_tokens = len(text) // 4
        
        # Add file tokens
        if files:
            for file in files:
                file_content = file.get("content", "")
                if isinstance(file_content, str):
                    input_tokens += len(file_content) // 4
                else:
                    # Estimate for non-text files (images, audio, etc.)
                    file_size = file.get("size", 0)
                    input_tokens += file_size // 1000  # Very rough estimate
        
        # Estimate output tokens (usually 10-50% of input for academic writing)
        output_tokens = int(input_tokens * 0.3 * complexity_multiplier)
        
        total_tokens = input_tokens + output_tokens
        
        # Add processing overhead
        overhead_tokens = int(total_tokens * 0.1)
        
        return total_tokens + overhead_tokens
    
    def _estimate_cost(
        self,
        tokens: int,
        model: Optional[str] = None,
        cost_level: CostLevel = CostLevel.MEDIUM
    ) -> float:
        """Estimate cost for token usage."""
        
        # Base cost calculation
        base_cost = (tokens / 1000) * (
            self.token_costs["input_base"] + 
            self.token_costs["output_base"] + 
            self.token_costs["processing_overhead"]
        )
        
        # Apply cost level multiplier
        multiplier = self.cost_multipliers[cost_level]
        
        # Model-specific adjustments (premium models cost more)
        model_multiplier = 1.0
        if model:
            model_lower = model.lower()
            if "gpt-4" in model_lower or "claude-3" in model_lower:
                model_multiplier = 2.0
            elif "o1" in model_lower or "o3" in model_lower:
                model_multiplier = 5.0
            elif "premium" in model_lower or "advanced" in model_lower:
                model_multiplier = 3.0
        
        return base_cost * multiplier * model_multiplier
    
    def _get_limits(self, role: str, user_limits: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Get budget limits for role and user."""
        
        limits = self.default_limits.copy()
        
        # Role-based adjustments
        if role == "premium":
            limits = {k: v * 5 for k, v in limits.items()}
        elif role == "pro":
            limits = {k: v * 2 for k, v in limits.items()}
        elif role == "free":
            limits = {k: v * 0.1 for k, v in limits.items()}
        
        # User-specific overrides
        if user_limits:
            limits.update(user_limits)
        
        return limits
    
    def _get_usage(self, tenant: str) -> Dict[str, Any]:
        """Get current usage for tenant."""
        if tenant not in self._usage_tracker:
            return {
                "daily_spent": 0.0,
                "hourly_spent": 0.0,
                "monthly_spent": 0.0,
            }
        
        usage = self._usage_tracker[tenant]
        current_time = time.time()
        self._reset_expired_counters(usage, current_time)
        
        return usage
    
    def _reset_expired_counters(self, usage: Dict[str, Any], current_time: float) -> None:
        """Reset expired time-based counters."""
        
        # Reset daily counter (24 hours)
        if current_time - usage.get("daily_reset", 0) > 86400:
            usage["daily_spent"] = 0.0
            usage["daily_reset"] = current_time
        
        # Reset hourly counter (1 hour)
        if current_time - usage.get("hourly_reset", 0) > 3600:
            usage["hourly_spent"] = 0.0
            usage["hourly_reset"] = current_time
        
        # Reset monthly counter (30 days)
        if current_time - usage.get("monthly_reset", 0) > 2592000:
            usage["monthly_spent"] = 0.0
            usage["monthly_reset"] = current_time


# Global budget guard instance
_budget_guard: Optional[BudgetGuard] = None


def get_budget_guard() -> BudgetGuard:
    """Get global budget guard instance."""
    global _budget_guard
    if _budget_guard is None:
        _budget_guard = BudgetGuard()
    return _budget_guard


def guard_request(
    estimated_tokens: int,
    role: str = "user",
    model: Optional[str] = None,
    tenant: Optional[str] = None,
    cost_level: CostLevel = CostLevel.MEDIUM,
    user_limits: Optional[Dict[str, float]] = None
) -> BudgetResult:
    """
    Convenience function to check budget via global guard.
    
    Raises:
        BudgetExceededError: If budget limits are exceeded
    """
    result = get_budget_guard().guard(
        estimated_tokens, role, model, tenant, cost_level, user_limits
    )
    
    if not result.allowed:
        raise BudgetExceededError(
            result.reason,
            result.code,
            result.estimated_cost,
            result.remaining_budget
        )
    
    return result


def record_usage(
    actual_cost: float,
    tokens_used: int,
    tenant: Optional[str] = None,
    model: Optional[str] = None
) -> None:
    """Convenience function to record usage via global guard."""
    get_budget_guard().record_usage(actual_cost, tokens_used, tenant, model)