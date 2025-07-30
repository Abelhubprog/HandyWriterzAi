"""
Complexity Analyzer for Unified AI Platform

Analyzes request complexity to determine optimal routing between
simple and advanced AI systems.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """
    Analyzes request complexity for intelligent routing decisions.
    Uses multiple factors to determine complexity score (1-10 scale).
    """
    
    def __init__(self):
        # Academic writing keywords
        self.academic_keywords = [
            "essay", "research", "academic", "citation", "thesis", "dissertation",
            "literature review", "methodology", "analysis", "scholarly", "peer review",
            "bibliography", "reference", "apa", "mla", "harvard", "chicago",
            "write a paper", "academic paper", "research paper"
        ]
        
        # Complex task indicators
        self.complex_keywords = [
            "comprehensive", "systematic", "detailed analysis", "in-depth",
            "multi-dimensional", "synthesize", "evaluate", "critique",
            "compare and contrast", "meta-analysis", "critical analysis",
            "theoretical framework", "conceptual model"
        ]
        
        # Quality requirement indicators
        self.quality_indicators = [
            "high quality", "professional", "publication ready",
            "peer review ready", "journal quality", "conference paper"
        ]
        
        # Strong academic writing indicators
        self.strong_academic_indicators = [
            "write an essay", "write a research paper", "academic essay",
            "research report", "literature review", "thesis", "dissertation",
            "scholarly article", "academic paper", "write a paper"
        ]
        
        logger.info("🔍 ComplexityAnalyzer initialized")
    
    async def calculate_complexity(self, message: str, files: List, user_params: dict) -> float:
        """
        Calculate request complexity score (1-10 scale).
        
        Args:
            message: User message/query
            files: List of uploaded files
            user_params: User parameters for academic writing
            
        Returns:
            float: Complexity score between 1.0 and 10.0
        """
        score = 2.0  # Base score
        
        # Message length analysis
        word_count = len(message.split())
        if word_count > 50: score += 1.0
        if word_count > 100: score += 1.5
        if word_count > 200: score += 2.0
        if word_count > 500: score += 1.5
        
        # File complexity
        file_count = len(files)
        if file_count > 0: score += 2.0
        if file_count > 2: score += 1.5
        if file_count > 5: score += 1.0
        
        # Academic keywords analysis
        academic_matches = sum(1 for keyword in self.academic_keywords 
                             if keyword.lower() in message.lower())
        score += academic_matches * 1.5
        
        # Complex task indicators
        complex_matches = sum(1 for keyword in self.complex_keywords
                            if keyword.lower() in message.lower())
        score += complex_matches * 1.0
        
        # User parameters complexity
        if user_params:
            score += self._analyze_user_params_complexity(user_params)
        
        # Quality requirements
        quality_matches = sum(1 for keyword in self.quality_indicators
                            if keyword.lower() in message.lower())
        score += quality_matches * 1.5
        
        # Cap the score at 10.0
        final_score = min(score, 10.0)
        
        logger.debug(f"Complexity analysis: {word_count} words, {file_count} files, "
                    f"{academic_matches} academic, {complex_matches} complex → {final_score:.1f}")
        
        return final_score
    
    def _analyze_user_params_complexity(self, user_params: dict) -> float:
        """Analyze user parameters for complexity indicators."""
        score = 0.0
        
        # Academic writing type specified
        writeup_type = user_params.get("writeupType", "").lower()
        if writeup_type in ["essay", "research", "thesis", "dissertation"]:
            score += 2.0
        elif writeup_type in ["report", "analysis"]:
            score += 1.0
        
        # Page count
        pages = user_params.get("pages", 0)
        if pages > 5: score += 1.0
        if pages > 10: score += 1.5
        if pages > 20: score += 1.0
        
        # Education level
        education = user_params.get("educationLevel", "").lower()
        if education in ["graduate", "postgraduate", "phd"]:
            score += 1.5
        elif education in ["masters", "doctoral"]:
            score += 1.0
        
        # Reference style (indicates academic rigor)
        ref_style = user_params.get("referenceStyle", "").lower()
        if ref_style in ["apa", "mla", "harvard", "chicago"]:
            score += 0.5
        
        # Quality tier
        quality_tier = user_params.get("qualityTier", "").lower()
        if quality_tier in ["excellent", "premium"]:
            score += 1.0
        elif quality_tier in ["good", "high"]:
            score += 0.5
        
        return score
    
    def is_academic_writing_request(self, message: str, user_params: dict) -> bool:
        """
        Detect explicit academic writing requests.
        
        Args:
            message: User message/query
            user_params: User parameters
            
        Returns:
            bool: True if this is clearly an academic writing request
        """
        # Check user parameters
        if user_params:
            writeup_type = user_params.get("writeupType", "").lower()
            if writeup_type in ["essay", "research", "thesis", "dissertation", "paper"]:
                return True
        
        # Strong academic indicators in message
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in self.strong_academic_indicators)
    
    def analyze_request_characteristics(self, message: str, files: List, user_params: dict) -> Dict[str, Any]:
        """
        Provide detailed analysis of request characteristics.
        
        Returns:
            Dict with detailed analysis breakdown
        """
        word_count = len(message.split())
        file_count = len(files)
        
        # Count keyword matches
        academic_matches = [keyword for keyword in self.academic_keywords 
                          if keyword.lower() in message.lower()]
        complex_matches = [keyword for keyword in self.complex_keywords
                         if keyword.lower() in message.lower()]
        quality_matches = [keyword for keyword in self.quality_indicators
                         if keyword.lower() in message.lower()]
        
        return {
            "word_count": word_count,
            "file_count": file_count,
            "has_user_params": bool(user_params),
            "academic_keywords": academic_matches,
            "complex_keywords": complex_matches,
            "quality_keywords": quality_matches,
            "is_academic_writing": self.is_academic_writing_request(message, user_params),
            "estimated_processing_time": self._estimate_processing_time(word_count, file_count, user_params),
            "recommended_system": self._recommend_system_based_on_analysis(
                word_count, file_count, len(academic_matches), len(complex_matches)
            )
        }
    
    def _estimate_processing_time(self, word_count: int, file_count: int, user_params: dict) -> Dict[str, str]:
        """Estimate processing time for different systems."""
        # Base estimates
        simple_time = "1-3 seconds"
        advanced_time = "30-300 seconds"
        
        # Adjust based on complexity
        if word_count > 200 or file_count > 2:
            simple_time = "3-10 seconds"
            advanced_time = "60-600 seconds"
        
        if user_params and user_params.get("pages", 0) > 10:
            advanced_time = "120-900 seconds"
        
        return {
            "simple": simple_time,
            "advanced": advanced_time,
            "hybrid": advanced_time + " (parallel processing)"
        }
    
    def _recommend_system_based_on_analysis(
        self, 
        word_count: int, 
        file_count: int, 
        academic_count: int, 
        complex_count: int
    ) -> str:
        """Recommend system based on analysis."""
        if academic_count > 0 or complex_count > 2:
            return "advanced"
        elif word_count < 20 and file_count == 0:
            return "simple"
        elif file_count > 0 or word_count > 100:
            return "hybrid"
        else:
            return "simple"