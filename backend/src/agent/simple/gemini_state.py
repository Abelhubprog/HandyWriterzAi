"""
Gemini State Integration for Unified AI Platform

Imports and adapts the simple Gemini state management for use within
the unified platform's intelligent routing system.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from ..state import OverallState as GeminiState
    GEMINI_STATE_AVAILABLE = True
    logger.info("✅ Simple Gemini state imported successfully")
except ImportError as e:
    GeminiState = None
    GEMINI_STATE_AVAILABLE = False
    logger.warning(f"⚠️  Simple Gemini state not available: {e}")

# Export for unified system
__all__ = ['GeminiState', 'GEMINI_STATE_AVAILABLE']