"""
Memory Safety and Cost Control Service for HandyWriterzAI.
Implements PII detection, rate limiting, cost tracking, and safety guards.
"""

import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CostMetrics:
    """Track memory system costs."""
    embeddings_generated: int = 0
    vector_operations: int = 0
    llm_reflection_calls: int = 0
    storage_bytes: int = 0
    total_cost_usd: float = 0.0


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    max_memories_per_hour: int = 100
    max_retrievals_per_minute: int = 50
    max_reflection_calls_per_hour: int = 10
    max_storage_mb_per_user: int = 50


class MemorySafetyService:
    """Production-ready safety service for memory operations."""
    
    def __init__(self):
        # Cost tracking
        self.cost_metrics = CostMetrics()
        self.user_costs: Dict[str, CostMetrics] = {}
        
        # Rate limiting
        self.rate_limit_config = RateLimitConfig()
        self.user_operations: Dict[str, Dict[str, List[datetime]]] = {}
        
        # PII patterns (production-ready patterns)
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'(\+\d{1,3}\s?)?\(?\d{3}\)?\s?-?\d{3}\s?-?\d{4}'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}\s?-?\d{4}\s?-?\d{4}\s?-?\d{4}\b'),
            'api_key': re.compile(r'(api[_-]?key|token)["\s:=]+[a-z0-9-_]{20,}', re.IGNORECASE),
            'url_with_params': re.compile(r'https?://[^\s]+[?&][^\s]*'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        }
        
        # Cost estimates (USD)
        self.cost_estimates = {
            'embedding_per_1k_tokens': 0.0001,  # OpenAI text-embedding-3-small
            'gpt4_mini_per_1k_tokens': 0.0015,  # GPT-4o-mini
            'vector_operation': 0.00001,  # Approximate vector DB cost
            'storage_per_mb_month': 0.10   # Storage cost
        }
        
        # Safety thresholds
        self.safety_thresholds = {
            'max_content_length': 10000,  # Max chars per memory
            'max_daily_cost_per_user': 5.0,  # USD
            'max_total_memories_per_user': 10000,
            'min_importance_threshold': 0.01,
            'max_importance_threshold': 1.0
        }
        
        logger.info("MemorySafetyService initialized with production safety controls")
    
    def rate_limit_check(self, operation_type: str):
        """Decorator for rate limiting operations."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user_id from arguments
                user_id = None
                if args and hasattr(args[0], '__dict__'):  # Method call
                    user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
                else:  # Function call
                    user_id = kwargs.get('user_id') or (args[0] if args else None)
                
                if user_id and not await self._check_rate_limit(user_id, operation_type):
                    raise MemorySafetyError(f"Rate limit exceeded for {operation_type}")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def validate_memory_content(
        self, 
        content: str, 
        user_id: str,
        allow_pii: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate memory content for safety and PII.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Length check
        if len(content) > self.safety_thresholds['max_content_length']:
            issues.append(f"Content too long ({len(content)} chars, max {self.safety_thresholds['max_content_length']})")
        
        # Empty content check
        if not content.strip():
            issues.append("Content is empty")
        
        # PII detection
        if not allow_pii:
            pii_found = self._detect_pii(content)
            if pii_found:
                issues.append(f"PII detected: {', '.join(pii_found)}")
        
        # Spam/repetitive content check
        if self._is_spam_content(content):
            issues.append("Content appears to be spam or overly repetitive")
        
        # Cost validation
        daily_cost = await self._get_user_daily_cost(user_id)
        if daily_cost > self.safety_thresholds['max_daily_cost_per_user']:
            issues.append(f"Daily cost limit exceeded: ${daily_cost:.2f}")
        
        return len(issues) == 0, issues
    
    async def validate_retrieval_request(
        self, 
        user_id: str,
        query: str,
        k: int
    ) -> Tuple[bool, List[str]]:
        """Validate memory retrieval request."""
        issues = []
        
        # Query validation
        if not query.strip():
            issues.append("Query is empty")
        
        if len(query) > 1000:
            issues.append("Query too long (max 1000 chars)")
        
        # Results count validation
        if k > 20:
            issues.append("Too many results requested (max 20)")
        
        if k < 1:
            issues.append("Invalid results count")
        
        # Rate limiting check
        if not await self._check_rate_limit(user_id, 'retrieval'):
            issues.append("Rate limit exceeded for memory retrieval")
        
        return len(issues) == 0, issues
    
    async def track_operation_cost(
        self,
        user_id: str,
        operation_type: str,
        **kwargs
    ):
        """Track costs for memory operations."""
        try:
            cost = 0.0
            
            if operation_type == 'embedding':
                token_count = kwargs.get('token_count', 0)
                cost = (token_count / 1000) * self.cost_estimates['embedding_per_1k_tokens']
                self.cost_metrics.embeddings_generated += 1
                
            elif operation_type == 'reflection':
                input_tokens = kwargs.get('input_tokens', 0)
                output_tokens = kwargs.get('output_tokens', 0)
                cost = ((input_tokens + output_tokens) / 1000) * self.cost_estimates['gpt4_mini_per_1k_tokens']
                self.cost_metrics.llm_reflection_calls += 1
                
            elif operation_type == 'vector_operation':
                cost = self.cost_estimates['vector_operation']
                self.cost_metrics.vector_operations += 1
                
            elif operation_type == 'storage':
                storage_bytes = kwargs.get('storage_bytes', 0)
                storage_mb = storage_bytes / (1024 * 1024)
                cost = storage_mb * self.cost_estimates['storage_per_mb_month'] / 30  # Daily cost
                self.cost_metrics.storage_bytes += storage_bytes
            
            # Update global and user costs
            self.cost_metrics.total_cost_usd += cost
            
            if user_id not in self.user_costs:
                self.user_costs[user_id] = CostMetrics()
            
            user_cost = self.user_costs[user_id]
            user_cost.total_cost_usd += cost
            
            if operation_type == 'embedding':
                user_cost.embeddings_generated += 1
            elif operation_type == 'reflection':
                user_cost.llm_reflection_calls += 1
            elif operation_type == 'vector_operation':
                user_cost.vector_operations += 1
            elif operation_type == 'storage':
                user_cost.storage_bytes += kwargs.get('storage_bytes', 0)
            
            logger.debug(f"Tracked {operation_type} cost: ${cost:.6f} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Cost tracking failed: {e}")
    
    async def get_cost_report(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost report for user or system."""
        if user_id:
            user_cost = self.user_costs.get(user_id, CostMetrics())
            return {
                "user_id": user_id,
                "total_cost_usd": user_cost.total_cost_usd,
                "embeddings_generated": user_cost.embeddings_generated,
                "vector_operations": user_cost.vector_operations,
                "llm_reflection_calls": user_cost.llm_reflection_calls,
                "storage_mb": user_cost.storage_bytes / (1024 * 1024),
                "daily_cost": await self._get_user_daily_cost(user_id)
            }
        else:
            return {
                "system_total_cost_usd": self.cost_metrics.total_cost_usd,
                "total_embeddings": self.cost_metrics.embeddings_generated,
                "total_vector_operations": self.cost_metrics.vector_operations,
                "total_reflection_calls": self.cost_metrics.llm_reflection_calls,
                "total_storage_mb": self.cost_metrics.storage_bytes / (1024 * 1024),
                "active_users": len(self.user_costs)
            }
    
    def sanitize_content(self, content: str, user_opted_in_pii: bool = False) -> str:
        """Sanitize content by removing or masking PII."""
        if user_opted_in_pii:
            return content
        
        sanitized = content
        
        # Mask email addresses
        sanitized = self.pii_patterns['email'].sub('[EMAIL]', sanitized)
        
        # Mask phone numbers
        sanitized = self.pii_patterns['phone'].sub('[PHONE]', sanitized)
        
        # Mask SSNs
        sanitized = self.pii_patterns['ssn'].sub('[SSN]', sanitized)
        
        # Mask credit cards
        sanitized = self.pii_patterns['credit_card'].sub('[CREDIT_CARD]', sanitized)
        
        # Mask API keys
        sanitized = self.pii_patterns['api_key'].sub('[API_KEY]', sanitized)
        
        # Mask URLs with parameters
        sanitized = self.pii_patterns['url_with_params'].sub('[URL]', sanitized)
        
        # Mask IP addresses
        sanitized = self.pii_patterns['ip_address'].sub('[IP_ADDRESS]', sanitized)
        
        return sanitized
    
    async def check_user_limits(self, user_id: str) -> Dict[str, Any]:
        """Check if user is within safety limits."""
        user_cost = self.user_costs.get(user_id, CostMetrics())
        daily_cost = await self._get_user_daily_cost(user_id)
        
        return {
            "within_daily_cost_limit": daily_cost <= self.safety_thresholds['max_daily_cost_per_user'],
            "daily_cost": daily_cost,
            "daily_cost_limit": self.safety_thresholds['max_daily_cost_per_user'],
            "total_cost": user_cost.total_cost_usd,
            "operations_today": {
                "embeddings": user_cost.embeddings_generated,
                "retrievals": len(self.user_operations.get(user_id, {}).get('retrieval', [])),
                "reflections": user_cost.llm_reflection_calls
            }
        }
    
    # Private helper methods
    
    def _detect_pii(self, content: str) -> List[str]:
        """Detect PII in content."""
        pii_found = []
        
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(content):
                pii_found.append(pii_type)
        
        return pii_found
    
    def _is_spam_content(self, content: str) -> bool:
        """Detect spam or overly repetitive content."""
        # Check for excessive repetition
        words = content.lower().split()
        if len(words) > 10:
            word_frequency = {}
            for word in words:
                word_frequency[word] = word_frequency.get(word, 0) + 1
            
            # If any single word appears more than 30% of the time, it's likely spam
            max_frequency = max(word_frequency.values())
            if max_frequency / len(words) > 0.3:
                return True
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace()) / max(len(content), 1)
        if special_char_ratio > 0.5:
            return True
        
        return False
    
    async def _check_rate_limit(self, user_id: str, operation_type: str) -> bool:
        """Check if user is within rate limits."""
        now = datetime.utcnow()
        
        if user_id not in self.user_operations:
            self.user_operations[user_id] = {}
        
        if operation_type not in self.user_operations[user_id]:
            self.user_operations[user_id][operation_type] = []
        
        operations = self.user_operations[user_id][operation_type]
        
        # Clean old operations
        if operation_type == 'memory_write':
            cutoff = now - timedelta(hours=1)
            limit = self.rate_limit_config.max_memories_per_hour
        elif operation_type == 'retrieval':
            cutoff = now - timedelta(minutes=1)
            limit = self.rate_limit_config.max_retrievals_per_minute
        elif operation_type == 'reflection':
            cutoff = now - timedelta(hours=1)
            limit = self.rate_limit_config.max_reflection_calls_per_hour
        else:
            return True  # Unknown operation type, allow
        
        # Remove old operations
        operations[:] = [op_time for op_time in operations if op_time > cutoff]
        
        # Check limit
        if len(operations) >= limit:
            logger.warning(f"Rate limit exceeded for user {user_id}, operation {operation_type}")
            return False
        
        # Record this operation
        operations.append(now)
        return True
    
    async def _get_user_daily_cost(self, user_id: str) -> float:
        """Get user's cost for the current day."""
        # In a real implementation, this would query the database for today's costs
        # For now, return the total cost (simplified)
        user_cost = self.user_costs.get(user_id, CostMetrics())
        return user_cost.total_cost_usd


class MemorySafetyError(Exception):
    """Exception raised for memory safety violations."""
    pass


# Global safety service instance
_memory_safety_service = None

def get_memory_safety_service() -> MemorySafetyService:
    """Get or create memory safety service instance."""
    global _memory_safety_service
    if _memory_safety_service is None:
        _memory_safety_service = MemorySafetyService()
    return _memory_safety_service