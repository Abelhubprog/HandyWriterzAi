"""Compatibility re-exports for policy components.

This module intentionally re-exports the concrete implementations from
policy_core to avoid import errors where code imports from src.models.policy.

Do not add heavy logic here. Keep this as a thin façade.
"""

from .policy_core import (
    Task,
    SafetyRule,
    CandidateModel,
    PolicyDefinition,
    PolicyRegistry,
)

__all__ = [
    "Task",
    "SafetyRule",
    "CandidateModel",
    "PolicyDefinition",
    "PolicyRegistry",
]
