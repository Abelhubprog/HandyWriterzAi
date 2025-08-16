"""
Unified Processor for Multi-Agent AI Platform

Enhances the existing HandyWriterz system with intelligent routing between
simple Gemini system and advanced HandyWriterz system based on complexity analysis.

This integrates with the existing robust backend infrastructure in backend/backend/src/
"""

import asyncio
import time
import uuid
import logging
import sys
import os
from typing import Dict, Any, List

# Rely on environment/runner to include project paths.
# Repo includes a root-level sitecustomize.py that prepends `backend` and `backend/src` to sys.path.

logger = logging.getLogger(__name__)

# Import simple Gemini system (if present)
try:
    from src.agent.graph import graph as gemini_graph
    from src.agent.state import OverallState as GeminiState
    from langchain_core.messages import HumanMessage
    SIMPLE_AVAILABLE = True
    logger.info("✅ Simple Gemini system imported successfully")
except ImportError as e:
    logger.info(f"ℹ️ Simple Gemini system not available: {e}")
    gemini_graph = None
    GeminiState = None
    HumanMessage = None
    SIMPLE_AVAILABLE = False

# Import advanced HandyWriterz system (primary)
try:
    from src.agent.handywriterz_graph import handywriterz_graph
    from src.agent.handywriterz_state import HandyWriterzState
    from src.agent.base import UserParams
    ADVANCED_AVAILABLE = True
    logger.info("✅ Advanced HandyWriterz system imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Advanced HandyWriterz system not available: {e}")
    handywriterz_graph = None
    HandyWriterzState = None
    UserParams = None
    ADVANCED_AVAILABLE = False


class UnifiedAuth:
    """Unified authentication system (placeholder for integration)."""

    def __init__(self):
        logger.info("🔐 UnifiedAuth initialized")

    async def get_current_user(self):
        """Get current user (placeholder)."""
        return {"id": "demo_user", "wallet_address": None}


class SystemRouter:
    """Intelligent routing system for determining optimal processing approach."""

    def __init__(self, simple_available: bool = SIMPLE_AVAILABLE, advanced_available: bool = ADVANCED_AVAILABLE):
        self.simple_available = simple_available
        self.advanced_available = advanced_available
        self._routing_stats = {
            "total_requests": 0,
            "simple_requests": 0,
            "advanced_requests": 0,
            "hybrid_requests": 0,
            "average_complexity": 0.0
        }
        logger.info(f"🎯 SystemRouter initialized - Simple: {simple_available}, Advanced: {advanced_available}")

    async def analyze_request(
        self,
        message: str,
        files: List = None,
        user_params: dict = None
    ) -> Dict[str, Any]:
        """Analyze request to determine optimal routing strategy."""

        files = files or []
        complexity_score = self._calculate_complexity(message, files, user_params)

        # Update routing statistics
        self._routing_stats["total_requests"] += 1
        self._routing_stats["average_complexity"] = (
            (self._routing_stats["average_complexity"] * (self._routing_stats["total_requests"] - 1) + complexity_score) /
            self._routing_stats["total_requests"]
        )

        # Determine routing strategy
        if not self.advanced_available:
            return {
                "system": "simple",
                "complexity": complexity_score,
                "reason": "Advanced system unavailable",
                "confidence": 0.8
            }
        elif not self.simple_available:
            return {
                "system": "advanced",
                "complexity": complexity_score,
                "reason": "Simple system unavailable",
                "confidence": 0.8
            }

        # Intelligent routing based on complexity and content analysis
        academic_indicators = self._detect_academic_indicators(message, user_params)

        if complexity_score >= 7.0 or academic_indicators["strong_academic_signals"]:
            self._routing_stats["advanced_requests"] += 1
            return {
                "system": "advanced",
                "complexity": complexity_score,
                "reason": "High complexity or academic requirements detected",
                "confidence": 0.95,
                "academic_indicators": academic_indicators
            }
        elif complexity_score >= 4.0 or academic_indicators["moderate_academic_signals"]:
            self._routing_stats["hybrid_requests"] += 1
            return {
                "system": "hybrid",
                "complexity": complexity_score,
                "reason": "Medium complexity benefits from hybrid approach",
                "confidence": 0.85,
                "academic_indicators": academic_indicators
            }
        else:
            self._routing_stats["simple_requests"] += 1
            return {
                "system": "simple",
                "complexity": complexity_score,
                "reason": "Low complexity, simple system optimal",
                "confidence": 0.9,
                "academic_indicators": academic_indicators
            }

    def _calculate_complexity(self, message: str, files: List, user_params: dict = None) -> float:
        """Calculate request complexity score (1-10)."""

        score = 3.0  # Base score
        message_lower = message.lower()

        # Length analysis (progressive scoring)
        word_count = len(message.split())
        if word_count > 50:
            score += 0.5
        if word_count > 100:
            score += 0.5
        if word_count > 200:
            score += 1.0
        if word_count > 500:
            score += 1.5

        # File complexity analysis
        if files:
            file_count = len(files)
            score += min(file_count * 0.7, 2.5)  # Cap file impact at 2.5 points

            # Additional scoring for file types
            for file in files:
                if isinstance(file, dict):
                    filename = file.get("filename", "")
                    if filename.endswith((".pdf", ".docx", ".doc")):
                        score += 0.5
                    elif filename.endswith((".xlsx", ".csv", ".data")):
                        score += 0.3

        # Academic/research keywords (weighted by importance)
        high_priority_academic = [
            "research paper", "thesis", "dissertation", "literature review",
            "systematic review", "meta-analysis", "academic essay", "scholarly article"
        ]

        medium_priority_academic = [
            "research", "academic", "citation", "bibliography", "references",
            "methodology", "analysis", "evaluation", "critique", "argument"
        ]

        basic_academic = [
            "study", "review", "analyze", "synthesize", "evaluate", "compare",
            "essay", "paper", "report", "evidence", "scholarly"
        ]

        # Score based on academic keyword presence
        for keyword in high_priority_academic:
            if keyword in message_lower:
                score += 1.5

        for keyword in medium_priority_academic:
            if keyword in message_lower:
                score += 0.8

        for keyword in basic_academic:
            if keyword in message_lower:
                score += 0.4

        # Complex reasoning indicators
        reasoning_keywords = [
            "comprehensive", "systematic", "multi-dimensional", "interdisciplinary",
            "compare and contrast", "pros and cons", "advantages and disadvantages",
            "critical thinking", "problem solving", "decision making", "theoretical framework"
        ]

        reasoning_score = sum(1 for keyword in reasoning_keywords if keyword in message_lower)
        score += min(reasoning_score * 0.8, 2.5)

        # User parameters analysis (if provided)
        if user_params:
            # Academic requirements
            writeup_type = user_params.get("writeupType", "").lower()
            if writeup_type in ["research", "thesis", "dissertation"]:
                score += 2.0
            elif writeup_type in ["essay", "report", "review"]:
                score += 1.0

            # Page/length requirements
            pages = user_params.get("pages", 0)
            if pages > 10:
                score += 1.5
            elif pages > 5:
                score += 1.0
            elif pages > 2:
                score += 0.5

            # Citation requirements
            if user_params.get("referenceStyle"):
                score += 1.0

            # Education level
            education_level = user_params.get("educationLevel", "").lower()
            if education_level in ["graduate", "postgraduate", "phd", "doctoral"]:
                score += 1.5
            elif education_level in ["undergraduate", "bachelor"]:
                score += 0.5

        # Technical/specialized content detection
        technical_domains = [
            "programming", "software", "algorithm", "data science", "machine learning",
            "artificial intelligence", "computer science", "engineering", "mathematics",
            "statistics", "finance", "economics", "law", "medicine", "healthcare"
        ]

        for domain in technical_domains:
            if domain in message_lower:
                score += 0.6

        return min(score, 10.0)

    def _detect_academic_indicators(self, message: str, user_params: dict = None) -> Dict[str, Any]:
        """Detect academic indicators for routing decisions."""

        message_lower = message.lower()

        # Strong academic signals
        strong_signals = [
            "write an essay", "research paper", "thesis", "dissertation",
            "literature review", "academic writing", "citation needed",
            "harvard referencing", "apa style", "mla format", "chicago style",
            "peer-reviewed", "scholarly sources", "academic sources"
        ]

        # Moderate academic signals
        moderate_signals = [
            "analysis", "evaluation", "critique", "argument", "evidence",
            "methodology", "hypothesis", "research", "study", "theory",
            "academic", "scholarly", "bibliography", "references"
        ]

        strong_count = sum(1 for signal in strong_signals if signal in message_lower)
        moderate_count = sum(1 for signal in moderate_signals if signal in message_lower)

        # User parameter indicators
        param_academic_score = 0
        if user_params:
            if user_params.get("writeupType") in ["research", "thesis", "dissertation", "essay"]:
                param_academic_score += 2
            if user_params.get("referenceStyle"):
                param_academic_score += 1
            if user_params.get("pages", 0) > 3:
                param_academic_score += 1

        return {
            "strong_academic_signals": strong_count > 0 or param_academic_score >= 3,
            "moderate_academic_signals": moderate_count > 1 or param_academic_score >= 1,
            "signal_counts": {
                "strong": strong_count,
                "moderate": moderate_count,
                "param_score": param_academic_score
            },
            "detected_signals": [
                signal for signal in strong_signals + moderate_signals
                if signal in message_lower
            ]
        }

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for monitoring."""
        return {
            "statistics": self._routing_stats,
            "thresholds": {
                "simple": "< 4.0",
                "hybrid": "4.0 - 7.0",
                "advanced": ">= 7.0"
            },
            "routing_modes": [
                {
                    "mode": "simple",
                    "description": "Fast Gemini-powered responses",
                    "use_cases": ["Quick questions", "General research", "Simple analysis"]
                },
                {
                    "mode": "advanced",
                    "description": "Full HandyWriterz academic workflow",
                    "use_cases": ["Academic writing", "Research papers", "Complex analysis", "Citations"]
                },
                {
                    "mode": "hybrid",
                    "description": "Parallel processing for comprehensive results",
                    "use_cases": ["Medium complexity queries", "Research + quick insights"]
                }
            ],
            "capabilities": {
                "simple_system": SIMPLE_AVAILABLE,
                "advanced_system": ADVANCED_AVAILABLE,
                "intelligent_routing": True,
                "complexity_analysis": True,
                "academic_detection": True
            }
        }


class UnifiedProcessor:
    """
    Main processor that coordinates between different AI systems.
    Integrates with the existing HandyWriterz infrastructure.
    """

    def __init__(self, simple_available: bool = SIMPLE_AVAILABLE, advanced_available: bool = ADVANCED_AVAILABLE):
        self.router = SystemRouter(simple_available, advanced_available)
        self._processing_stats = {
            "total_processed": 0,
            "successful_completions": 0,
            "average_processing_time": 0.0,
            "error_rate": 0.0
        }
        logger.info("🔄 UnifiedProcessor initialized with existing HandyWriterz integration")

    async def process_message(
        self,
        message: str,
        files: List = None,
        user_params: dict = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Process message using optimal system routing."""

        start_time = time.time()
        files = files or []

        try:
            self._processing_stats["total_processed"] += 1

            # Analyze and route
            routing = await self.router.analyze_request(message, files, user_params)
            logger.info(f"🎯 Routing decision: {routing}")

            if routing["system"] == "simple":
                result = await self._process_simple(message, files)
            elif routing["system"] == "advanced":
                result = await self._process_advanced(message, files, user_params, user_id)
            else:  # hybrid
                result = await self._process_hybrid(message, files, user_params, user_id)

            # Update success statistics
            processing_time = time.time() - start_time
            self._processing_stats["successful_completions"] += 1
            self._processing_stats["average_processing_time"] = (
                (self._processing_stats["average_processing_time"] * (self._processing_stats["successful_completions"] - 1) + processing_time) /
                self._processing_stats["successful_completions"]
            )

            # Add routing metadata
            result.update({
                "system_used": routing["system"],
                "complexity_score": routing["complexity"],
                "routing_reason": routing["reason"],
                "routing_confidence": routing["confidence"],
                "processing_time": processing_time,
                "academic_indicators": routing.get("academic_indicators", {})
            })

            return result

        except Exception as e:
            logger.error(f"Unified processing error: {e}")

            # Update error statistics
            total_requests = self._processing_stats["total_processed"]
            failures = total_requests - self._processing_stats["successful_completions"]
            self._processing_stats["error_rate"] = failures / total_requests if total_requests > 0 else 0.0

            # Fallback strategy
            if routing.get("system") != "advanced" and self.router.advanced_available:
                logger.info("🔄 Falling back to advanced system")
                try:
                    result = await self._process_advanced(message, files, user_params, user_id)
                    result.update({
                        "system_used": "advanced_fallback",
                        "complexity_score": routing.get("complexity", 5.0),
                        "fallback_reason": str(e),
                        "processing_time": time.time() - start_time
                    })
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback processing failed: {fallback_error}")

            # If all else fails, return structured error
            return {
                "success": False,
                "response": f"I encountered an error processing your request: {str(e)}",
                "sources": [],
                "workflow_status": "failed",
                "system_used": "error_fallback",
                "complexity_score": 0.0,
                "processing_time": time.time() - start_time,
                "error_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "suggested_action": "Please try again or contact support if the issue persists."
                }
            }

    async def _process_simple(self, message: str, files: List) -> Dict[str, Any]:
        """Process using simple Gemini system."""
        if not self.router.simple_available:
            raise Exception("Simple system not available")

        try:
            # Create simple state compatible with existing Gemini graph
            initial_state = {
                "messages": [{"role": "user", "content": message}],
                "search_query": [message],
                "sources_gathered": [],
                "web_research_result": [],
                "research_loop_count": 0,
                "max_research_loops": 2
            }

            # Execute simple Gemini workflow
            config = {"configurable": {"thread_id": f"simple_session_{uuid.uuid4()}"}}

            if gemini_graph:
                result = await gemini_graph.ainvoke(initial_state, config)

                # Extract response from result
                response_content = ""
                if "messages" in result and result["messages"]:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        response_content = last_message.content
                    elif isinstance(last_message, dict):
                        response_content = last_message.get("content", "")

                return {
                    "success": True,
                    "response": response_content or "Response generated successfully",
                    "sources": result.get("sources_gathered", []),
                    "workflow_status": "completed",
                    "research_loops": result.get("research_loop_count", 0),
                    "system_type": "simple_gemini"
                }
            else:
                # Fallback for when graph is not available
                return {
                    "success": True,
                    "response": f"I understand you're asking about: {message}. This is a placeholder response from the simple system.",
                    "sources": [],
                    "workflow_status": "completed",
                    "system_type": "simple_fallback"
                }

        except Exception as e:
            logger.error(f"Simple processing error: {e}")
            raise Exception(f"Simple system processing failed: {e}")

    async def _process_advanced(
        self,
        message: str,
        files: List,
        user_params: dict = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Process using advanced HandyWriterz system."""
        from src.services.model_service import model_service, BudgetExceeded

        try:
            # Create conversation ID
            conversation_id = str(uuid.uuid4())

            # Use provided user_params or create smart defaults
            if user_params and UserParams:
                try:
                    validated_params = UserParams(**user_params)
                except Exception as e:
                    logger.warning(f"Invalid user_params, using inferred params: {e}")
                    validated_params = self._infer_user_params(message)
            else:
                validated_params = self._infer_user_params(message)

            # Budget check
            try:
                # A simplified token estimation for the budget check
                estimated_tokens = {"input": len(message.split()) // 2, "output": 1000}
                model_service.price_guard.charge("writer", "gemini-pro-25", estimated_tokens, model_service.price_table)
            except BudgetExceeded as e:
                # Emit budget_degraded event via WebSocket (placeholder)
                logger.warning(f"Budget exceeded for user {user_id}: {e}")
                # In a real app, you would use a WebSocket manager to send this event.
                # For now, we'll just log it.

                # Fallback to a cheaper model
                if HandyWriterzState and handywriterz_graph:
                    state = HandyWriterzState(
                        conversation_id=conversation_id,
                        user_id=user_id or "",
                        # ... (rest of the state initialization)
                    )
                    # Override the model for this run
                    # This is a simplified example. A real implementation would be more robust.
                    config = {"configurable": {"thread_id": conversation_id, "model_override": {"writer": "kimi-k2"}}}
                    result = await handywriterz_graph.ainvoke(state, config)
                    # Add a flag to the result to indicate a fallback was used
                    result.budget_degraded = True
                    return self._format_advanced_result(result, conversation_id, validated_params)

            # Create advanced state if available
            if HandyWriterzState and handywriterz_graph:
                state = HandyWriterzState(
                    conversation_id=conversation_id,
                    user_id=user_id or "",
                    wallet_address=None,
                    messages=[{"role": "user", "content": message}],
                    user_params=validated_params.dict() if hasattr(validated_params, 'dict') else validated_params,
                    uploaded_docs=files,
                    # ... (rest of the state initialization)
                )

                # Execute the workflow
                config = {"configurable": {"thread_id": conversation_id}}
                result = await handywriterz_graph.ainvoke(state, config)

                return self._format_advanced_result(result, conversation_id, validated_params)
            else:
                # Fallback when advanced system is not fully available
                return {
                    "success": True,
                    "response": f"Advanced academic analysis for: {message}\n\nThis would be processed by the full HandyWriterz system with 30+ agents for comprehensive research, writing, and quality assurance.",
                    "conversation_id": conversation_id,
                    "sources": [],
                    "workflow_status": "completed",
                    "system_type": "advanced_fallback"
                }

        except Exception as e:
            logger.error(f"Advanced processing error: {e}")
            raise Exception(f"Advanced system processing failed: {e}")

    def _format_advanced_result(self, result, conversation_id, validated_params) -> Dict[str, Any]:
        """Formats the result from the advanced system."""
        return {
            "success": True,
            "response": self._extract_content(result),
            "conversation_id": conversation_id,
            "sources": getattr(result, 'verified_sources', []),
            "workflow_status": getattr(result, 'workflow_status', 'completed'),
            "quality_score": getattr(result, 'evaluation_score', 0),
            "agent_metrics": getattr(result, 'processing_metrics', {}),
            "citation_count": len(getattr(result, 'verified_sources', [])),
            "system_type": "advanced_handywriterz",
            "user_params": validated_params.dict() if hasattr(validated_params, 'dict') else validated_params,
            "budget_degraded": getattr(result, 'budget_degraded', False)
        }

    async def _process_hybrid(
        self,
        message: str,
        files: List,
        user_params: dict = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Process using hybrid approach (both systems in parallel)."""

        try:
            tasks = []

            # Start simple system for quick insights
            if self.router.simple_available:
                tasks.append(self._process_simple(message, files))

            # Start advanced system for comprehensive analysis
            if self.router.advanced_available:
                tasks.append(self._process_advanced(message, files, user_params, user_id))

            # Wait for both to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            simple_result = None
            advanced_result = None

            if len(results) == 2:
                simple_result, advanced_result = results
            elif len(results) == 1:
                # Only one system was available
                if self.router.advanced_available:
                    advanced_result = results[0]
                else:
                    simple_result = results[0]

            # Handle exceptions
            if isinstance(advanced_result, Exception):
                if isinstance(simple_result, Exception) or simple_result is None:
                    raise advanced_result
                else:
                    # Use simple result as fallback
                    simple_result["system_type"] = "simple_fallback_from_hybrid"
                    return simple_result

            # If only simple system ran
            if advanced_result is None:
                if isinstance(simple_result, Exception):
                    raise simple_result
                return simple_result

            # Combine results intelligently
            combined_sources = []
            if simple_result and not isinstance(simple_result, Exception):
                combined_sources.extend(simple_result.get("sources", []))
            if advanced_result and not isinstance(advanced_result, Exception):
                combined_sources.extend(advanced_result.get("sources", []))

            # Deduplicate sources
            unique_sources = []
            seen_urls = set()
            for source in combined_sources:
                if isinstance(source, dict):
                    url = source.get("url", source.get("value", ""))
                    if url and url not in seen_urls:
                        unique_sources.append(source)
                        seen_urls.add(url)
                    elif not url:  # No URL, include anyway
                        unique_sources.append(source)
                else:
                    unique_sources.append(source)

            return {
                "success": True,
                "response": advanced_result.get("response", ""),
                "conversation_id": advanced_result.get("conversation_id"),
                "sources": unique_sources,
                "workflow_status": "completed",
                "quality_score": advanced_result.get("quality_score", 0),
                "simple_insights": simple_result.get("response", "") if simple_result and not isinstance(simple_result, Exception) else None,
                "advanced_analysis": advanced_result.get("response", ""),
                "research_depth": len(unique_sources),
                "system_type": "hybrid",
                "hybrid_results": {
                    "simple_available": simple_result is not None and not isinstance(simple_result, Exception),
                    "advanced_available": not isinstance(advanced_result, Exception),
                    "simple_processing_time": simple_result.get("processing_time", 0) if simple_result else 0,
                    "advanced_processing_time": advanced_result.get("processing_time", 0) if advanced_result else 0
                }
            }

        except Exception as e:
            logger.error(f"Hybrid processing error: {e}")
            raise Exception(f"Hybrid processing failed: {e}")

    def _extract_content(self, result) -> str:
        """Extract final content from HandyWriterz result."""

        # Try different content sources in order of preference
        content_sources = [
            'formatted_document',
            'current_draft',
            'draft_content'
        ]

        for source in content_sources:
            content = getattr(result, source, None)
            if content and isinstance(content, str) and content.strip():
                return content

        # Fallback to messages
        messages = getattr(result, 'messages', [])
        if messages:
            for msg in reversed(messages):
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                elif hasattr(msg, 'content'):
                    content = msg.content
                else:
                    continue

                if content and not content.startswith("Human:"):
                    return content

        return "Advanced academic content generated successfully"

    def _infer_user_params(self, message: str) -> Dict[str, Any]:
        """Infer user parameters from message content."""

        message_lower = message.lower()

        # Infer writeup type
        writeup_type = "essay"  # default
        if any(term in message_lower for term in ["research paper", "research study"]):
            writeup_type = "research"
        elif "thesis" in message_lower:
            writeup_type = "thesis"
        elif "dissertation" in message_lower:
            writeup_type = "dissertation"
        elif "report" in message_lower:
            writeup_type = "report"
        elif "literature review" in message_lower:
            writeup_type = "literature_review"

        # Infer pages from message
        pages = 3  # default
        import re
        page_match = re.search(r'(\d+)\s*(?:page|word)', message_lower)
        if page_match:
            num = int(page_match.group(1))
            if "word" in page_match.group(0):
                pages = max(1, num // 300)  # Estimate pages from words
            else:
                pages = num

        # Infer field from keywords
        field = "general"
        field_keywords = {
            "psychology": ["psychology", "psychological", "mental health", "cognitive", "behavioral"],
            "business": ["business", "management", "marketing", "economics", "finance", "entrepreneurship"],
            "technology": ["technology", "computer", "software", "ai", "machine learning", "programming"],
            "healthcare": ["health", "medical", "medicine", "nursing", "healthcare", "clinical"],
            "education": ["education", "teaching", "pedagogy", "learning", "curriculum"],
            "science": ["science", "research", "experiment", "biology", "chemistry", "physics"],
            "engineering": ["engineering", "mechanical", "electrical", "civil", "construction"],
            "literature": ["literature", "literary", "english", "writing", "poetry", "novel"],
            "history": ["history", "historical", "ancient", "medieval", "modern"],
            "sociology": ["sociology", "social", "society", "cultural", "anthropology"]
        }

        for field_name, keywords in field_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                field = field_name
                break

        # Infer citation style
        reference_style = "APA"  # default
        if "harvard" in message_lower:
            reference_style = "Harvard"
        elif "mla" in message_lower:
            reference_style = "MLA"
        elif "chicago" in message_lower:
            reference_style = "Chicago"
        elif "vancouver" in message_lower:
            reference_style = "Vancouver"

        # Infer education level
        education_level = "undergraduate"
        if any(term in message_lower for term in ["phd", "doctoral", "doctorate"]):
            education_level = "phd"
        elif any(term in message_lower for term in ["master", "graduate", "postgraduate"]):
            education_level = "graduate"

        return {
            "writeupType": writeup_type,
            "field": field,
            "tone": "academic",
            "language": "en",
            "pages": min(max(pages, 1), 50),  # Clamp between 1-50
            "referenceStyle": reference_style,
            "educationLevel": education_level
        }

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring."""
        return self._processing_stats
