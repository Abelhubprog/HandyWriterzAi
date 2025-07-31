"""Compatibility re-exports for chat orchestrator components.

This module intentionally re-exports the concrete implementations from
chat_orchestrator_core to avoid import errors where code imports from
src.models.chat_orchestrator.

Keep this as a thin façade with no heavy logic.
"""

from .chat_orchestrator_core import ChatOrchestrator

__all__ = ["ChatOrchestrator"]
