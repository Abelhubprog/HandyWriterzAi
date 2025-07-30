"""
Intelligent Routing System for Unified AI Platform

This module provides the core routing logic that intelligently directs
requests between the simple Gemini system and advanced HandyWriterz system
based on complexity analysis and request characteristics.
"""

from .system_router import SystemRouter
from .unified_processor import UnifiedProcessor
from .complexity_analyzer import ComplexityAnalyzer

__all__ = [
    'SystemRouter',
    'UnifiedProcessor', 
    'ComplexityAnalyzer'
]