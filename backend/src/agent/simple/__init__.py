"""
Simple Gemini System Integration for Unified AI Platform

This module provides integration with the simple Gemini-based agent system,
allowing it to work seamlessly within the unified platform architecture.
"""

from .gemini_graph import gemini_graph, GEMINI_AVAILABLE
from .gemini_state import GeminiState, GEMINI_STATE_AVAILABLE

__all__ = [
    'gemini_graph',
    'GeminiState', 
    'GEMINI_AVAILABLE',
    'GEMINI_STATE_AVAILABLE'
]

# Simple system status
SIMPLE_SYSTEM_READY = GEMINI_AVAILABLE and GEMINI_STATE_AVAILABLE