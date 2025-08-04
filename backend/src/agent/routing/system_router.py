"""
System Router for Unified AI Platform

Intelligent router that analyzes request complexity and determines the optimal
system (simple Gemini, advanced HandyWriterz, or hybrid) for processing.
"""

import os
import logging
from typing import Dict, Any, List

from .complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)


class SystemRouter:
    """
    Intelligent router between simple Gemini and advanced HandyWriterz systems.
    Analyzes request complexity and routes to the most appropriate system.
    """
    
    def __init__(self, simple_available: bool = False, advanced_available: bool = True):
        # Simple system permanently disabled 
        self.simple_available = False
        self.advanced_available = advanced_available
        
        # Configuration thresholds (no longer used but kept for compatibility)
        self.simple_max_complexity = float(os.getenv("SIMPLE_MAX_COMPLEXITY", "4.0"))
        self.advanced_min_complexity = float(os.getenv("ADVANCED_MIN_COMPLEXITY", "7.0"))
        
        # Initialize complexity analyzer
        self.complexity_analyzer = ComplexityAnalyzer()
        
        logger.info("🎯 SystemRouter initialized:")
        logger.info(f"   Simple system: Permanently disabled")
        logger.info(f"   Advanced system: {'Available' if self.advanced_available else 'Unavailable'}")
        logger.info(f"   All requests route to advanced system")
        
    async def analyze_request(self, message: str, files: List = None, user_params: dict = None) -> Dict[str, Any]:
        """
        Analyze request complexity and determine optimal system routing.
        
        Args:
            message: User message/query
            files: List of uploaded files
            user_params: User parameters for academic writing
            
        Returns:
            {
                "system": "simple" | "advanced" | "hybrid",
                "complexity": float,
                "reason": str,
                "confidence": float
            }
        """
        files = files or []
        user_params = user_params or {}
        
        # Calculate complexity score (1-10 scale)
        complexity_score = await self.complexity_analyzer.calculate_complexity(message, files, user_params)
        
        # Always route to advanced system (simple and hybrid systems removed)
        return {
            "system": "advanced",
            "complexity": complexity_score,
            "reason": "simple_and_hybrid_systems_removed",
            "confidence": 1.0
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and configuration."""
        return {
            "systems_available": {
                "simple": self.simple_available,
                "advanced": self.advanced_available
            },
            "thresholds": {
                "simple_max": self.simple_max_complexity,
                "advanced_min": self.advanced_min_complexity
            },
            "routing_modes": ["simple", "advanced", "hybrid"],
            "capabilities": {
                "intelligent_routing": True,
                "complexity_analysis": True,
                "academic_detection": True,
                "file_processing": True
            }
        }
    
    def update_system_availability(self, simple_available: bool = None, advanced_available: bool = None):
        """Update system availability dynamically."""
        if simple_available is not None:
            self.simple_available = simple_available
            logger.info(f"Updated simple system availability: {simple_available}")
            
        if advanced_available is not None:
            self.advanced_available = advanced_available
            logger.info(f"Updated advanced system availability: {advanced_available}")
    
    def update_thresholds(self, simple_max: float = None, advanced_min: float = None):
        """Update complexity thresholds dynamically."""
        if simple_max is not None:
            self.simple_max_complexity = simple_max
            logger.info(f"Updated simple max complexity threshold: {simple_max}")
            
        if advanced_min is not None:
            self.advanced_min_complexity = advanced_min
            logger.info(f"Updated advanced min complexity threshold: {advanced_min}")