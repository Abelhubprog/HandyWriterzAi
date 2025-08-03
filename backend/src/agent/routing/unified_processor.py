"""
Unified Processor for Unified AI Platform

Handles routing between simple and advanced systems and processes
requests using the optimal system based on complexity analysis.
"""

import asyncio
import time
import uuid
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict

from langchain_core.messages import HumanMessage
import redis.asyncio as redis
import os

# Feature-gated SSE publisher and params normalization (Do-Not-Harm)
try:
    from src.agent.sse import SSEPublisher  # type: ignore
except Exception:  # pragma: no cover
    SSEPublisher = None  # type: ignore

try:
    from src.agent.routing.normalization import normalize_user_params, validate_user_params  # type: ignore
except Exception:  # pragma: no cover
    def normalize_user_params(x):  # type: ignore
        return x
    def validate_user_params(x):  # type: no cover
        return None

_FEATURE_SSE = os.getenv("FEATURE_SSE_PUBLISHER_UNIFIED", "false").lower() == "true"
_FEATURE_PARAMS = os.getenv("FEATURE_PARAMS_NORMALIZATION", "false").lower() == "true"

from typing import Any as _Any
_sse_pub: Optional[_Any] = None
if _FEATURE_SSE and SSEPublisher is not None:
    try:
        _sse_pub = SSEPublisher(async_redis=redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379")))
    except Exception:
        _sse_pub = SSEPublisher(async_redis=None) if SSEPublisher else None

# Lazy import to avoid hard dependency at import time
try:
    from src.config import get_settings  # type: ignore
except Exception:
    get_settings = None  # type: ignore

# Budget control imports
try:
    from src.services.budget import guard_request, record_usage, CostLevel  # type: ignore
    from src.services.logging_context import with_correlation_context  # type: ignore
except Exception:  # pragma: no cover
    def guard_request(*args, **kwargs):  # type: ignore
        return None
    def record_usage(*args, **kwargs):  # type: ignore
        pass
    class CostLevel:  # type: ignore
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        PREMIUM = "premium"
    def with_correlation_context(*args, **kwargs):  # type: ignore
        class _DummyContext:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return _DummyContext()

# Typed event envelope (single definition)
class _EventData(TypedDict, total=False):
    type: str
    message: str
    timestamp: float
    system: str
    complexity: float
    reason: str

from .system_router import SystemRouter
from ..handywriterz_state import HandyWriterzState
from ..handywriterz_graph import handywriterz_graph
from ..base import UserParams

logger = logging.getLogger(__name__)

# Redis client for streaming
redis_client: "redis.Redis" = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)  # type: ignore[assignment]


class UnifiedProcessor:
    """
    Unified processor that handles routing between simple and advanced systems.
    Integrates with the existing HandyWriterz architecture.
    """

    def __init__(self, simple_available: bool = True, advanced_available: bool = True):
        self.router = SystemRouter(simple_available, advanced_available)
        logger.info("🔄 UnifiedProcessor initialized")

    async def process_message(
        self,
        message: str,
        files: Optional[List[Dict[str, Any]]] = None,
        user_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process message using optimal system routing with streaming support."""

        start_time = time.time()
        files = files or []
        conversation_id = conversation_id or str(uuid.uuid4())

        # Setup correlation context for logging
        with with_correlation_context(
            conversation_id=conversation_id,
            user_id=user_id,
            node_name="UnifiedProcessor",
            phase="routing"
        ):
            return await self._process_with_context(
                message, files, user_params, user_id, conversation_id, start_time
            )

    async def _process_with_context(
        self,
        message: str,
        files: List[Dict[str, Any]],
        user_params: Optional[Dict[str, Any]],
        user_id: Optional[str],
        conversation_id: str,
        start_time: float
    ) -> Dict[str, Any]:
        """Internal processing with correlation context."""

        # Bind routing early to avoid UnboundLocalError in except paths
        routing: Dict[str, Any] = {"system": "unknown", "complexity": 0.0, "reason": "", "confidence": 0.0}

        try:
            # Resolve feature toggles (env OR settings)
            use_params = _FEATURE_PARAMS
            use_sse = _FEATURE_SSE
            double_publish = False
            if get_settings:
                try:
                    s = get_settings()
                    use_params = use_params or getattr(s, "feature_params_normalization", False)
                    use_sse = use_sse or getattr(s, "feature_sse_publisher_unified", False)
                    double_publish = getattr(s, "feature_double_publish_sse", False)
                except Exception:
                    pass

            # Budget check - estimate tokens and validate before processing
            try:
                from src.services.budget import get_budget_guard
                budget_guard = get_budget_guard()
                estimated_tokens = budget_guard.estimate_tokens(message, files, complexity_multiplier=1.0)

                # Check budget (will raise BudgetExceededError if over limits)
                budget_result = guard_request(
                    estimated_tokens=estimated_tokens,
                    role="user",  # Could be enhanced with actual user role
                    tenant=user_id,
                    cost_level=CostLevel.MEDIUM  # Will be adjusted based on routing
                )

                logger.info(f"Budget check passed: ${budget_result.estimated_cost:.4f} estimated")

            except Exception as budget_error:
                logger.error(f"Budget check failed: {budget_error}")
                # Return budget error as SSE event
                await self._publish_event(conversation_id, _EventData(
                    type="error",
                    message=str(budget_error),
                    timestamp=time.time()
                ), use_sse=use_sse, double_publish=double_publish)

                return {
                    "success": False,
                    "response": f"Request blocked: {str(budget_error)}",
                    "sources": [],
                    "workflow_status": "budget_exceeded",
                    "system_used": "budget_guard",
                    "error_details": {
                        "error_type": "BudgetExceededError",
                        "error_message": str(budget_error)
                    }
                }

            # Start streaming
            await self._publish_event(conversation_id, _EventData(
                type="start",
                message="Processing your request...",
                timestamp=time.time()
            ), use_sse=use_sse, double_publish=double_publish)

            # Optional params normalization prior to routing
            effective_params = user_params or {}
            if use_params:
                try:
                    effective_params = normalize_user_params(effective_params or {})
                    validate_user_params(effective_params)
                except Exception:
                    effective_params = user_params or {}

            # Analyze and route
            routing = await self.router.analyze_request(message, files, effective_params)
            logger.info(f"🎯 Routing decision: {routing}")

            await self._publish_event(conversation_id, _EventData(
                type="routing",
                system=str(routing.get("system", "")),
                complexity=float(routing.get("complexity", 0.0)),
                reason=str(routing.get("reason", ""))
            ), use_sse=use_sse, double_publish=double_publish)

            if routing.get("system") == "simple":
                result = await self._process_simple(message, files or [], conversation_id)
            elif routing.get("system") == "advanced":
                result = await self._process_advanced(message, files or [], effective_params if use_params else (user_params or {}), user_id or "", conversation_id)
            else:  # hybrid
                result = await self._process_hybrid(message, files or [], effective_params if use_params else (user_params or {}), user_id or "", conversation_id)

            # Add routing metadata
            result.update({
                "system_used": routing["system"],
                "complexity_score": routing["complexity"],
                "routing_reason": routing["reason"],
                "routing_confidence": routing["confidence"],
                "processing_time": time.time() - start_time
            })

            # Record actual usage for budget tracking
            try:
                processing_time = time.time() - start_time
                actual_tokens = result.get("tokens_used", estimated_tokens)  # Use actual or fallback to estimate
                actual_cost = budget_result.estimated_cost  # Could be refined with actual model costs

                record_usage(
                    actual_cost=actual_cost,
                    tokens_used=actual_tokens,
                    tenant=user_id,
                    model=result.get("model_used", routing.get("system", "unknown"))
                )

                logger.info(f"Usage recorded: ${actual_cost:.4f}, {actual_tokens} tokens")

            except Exception as usage_error:
                logger.warning(f"Failed to record usage: {usage_error}")

            # Final completion event
            await self._publish_event(conversation_id, _EventData(
                type="done",
                message="Processing completed",
                timestamp=time.time()
            ), use_sse=use_sse, double_publish=double_publish)

            return result

        except Exception as e:
            logger.error(f"Unified processing error: {e}")

            await self._publish_event(
                conversation_id,
                {
                    "type": "error",
                    "message": f"Error: {str(e)}",
                    "timestamp": time.time()
                },
                use_sse=_FEATURE_SSE if 'use_sse' not in locals() else use_sse,
                double_publish=False if 'double_publish' not in locals() else double_publish
            )

            # Fallback to advanced system if available
            if locals().get("routing") and routing.get("system") != "advanced" and self.router.advanced_available:
                logger.info("🔄 Falling back to advanced system")
                try:
                    result = await self._process_advanced(message, files, user_params, user_id, conversation_id)
                    result.update({
                        "system_used": "advanced_fallback",
                        "complexity_score": routing.get("complexity", 5.0),
                        "fallback_reason": str(e),
                        "processing_time": time.time() - start_time
                    })
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback processing failed: {fallback_error}")

            # If all else fails, return error
            return {
                "success": False,
                "response": f"I encountered an error processing your request: {str(e)}",
                "sources": [],
                "workflow_status": "failed",
                "system_used": "error",
                "complexity_score": 0.0,
                "error_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            }

    async def _publish_event(self, conversation_id: str, event_data: _EventData, use_sse: bool = False, double_publish: bool = False):
        """Publish streaming event to Redis channel and optionally via unified SSEPublisher."""
        try:
            channel = f"sse:{conversation_id}"
            # Legacy path publish (stringified JSON)
            await redis_client.publish(channel, json.dumps(event_data))

            # Unified publisher path (JSON envelope)
            if use_sse and _sse_pub is not None and SSEPublisher is not None:
                try:
                    # Ensure awaited call to unified publisher for reliability and ordering
                    await _sse_pub.publish(
                        conversation_id,
                        event_data.get("type", "content"),
                        {k: v for k, v in event_data.items() if k != "type"}
                    )
                except Exception as pub_err:
                    logger.warning(f"SSE unified publish failed (shadow mode may continue): {pub_err}")

            # Optional: when double_publish is True, legacy + unified already covered above
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    async def _process_simple(self, message: str, files: List[Dict[str, Any]], conversation_id: str) -> Dict[str, Any]:
        """Process using simple Gemini system."""
        if not self.router.simple_available:
            raise Exception("Simple system not available")

        await self._publish_event(conversation_id, _EventData(
            type="content",
            message="Thinking with Gemini...",
            timestamp=time.time()
        ))

        try:
            # Import here to avoid circular imports
            from ..simple import gemini_graph, GeminiState  # type: ignore

            if gemini_graph is None or GeminiState is None:
                raise Exception("Simple system components not available")

            # Create simple state
            state = GeminiState(
                messages=[HumanMessage(content=message)],
                search_query=[message],
                max_research_loops=2
            )

            config = {"configurable": {"thread_id": f"simple_session_{uuid.uuid4()}"}}
            result = await gemini_graph.ainvoke(state, config)

            # Extract response
            final_message = result["messages"][-1] if result.get("messages") else None
            response_content = final_message.content if final_message else "No response generated"

            # Generate trace_id for simple system
            trace_id = str(uuid.uuid4())

            return {
                "success": True,
                "trace_id": trace_id,
                "conversation_id": trace_id,  # Use same ID for consistency
                "response": response_content,
                "sources": result.get("sources_gathered", []),
                "workflow_status": "completed",
                "research_loops": result.get("research_loop_count", 0),
                "system_type": "simple_gemini"
            }

        except Exception as e:
            logger.error(f"Simple processing error: {e}")
            raise Exception(f"Simple system processing failed: {e}")

    async def _process_advanced(
        self,
        message: str,
        files: List,
        user_params: dict = None,
        user_id: str = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Process using advanced HandyWriterz system."""

        await self._publish_event(conversation_id, {
            "type": "content",
            "text": "Routing to advanced HandyWriterz agents..."
        })

        try:
            # Use provided conversation_id or create new one
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Use provided user_params or create defaults
            if user_params:
                validated_params = UserParams(**user_params)
            else:
                # Smart defaults based on message analysis
                validated_params = self._infer_user_params(message)

            # Create advanced state
            # Construct via kwargs dictionary to avoid Pylance false negatives on dataclass analysis
            _state_kwargs = {
                "conversation_id": conversation_id,
                "user_id": user_id or "",
                "wallet_address": None,
                "messages": [HumanMessage(content=message)],
                "user_params": validated_params.dict(),
                "uploaded_docs": files,
                "outline": None,
                "research_agenda": [],
                "search_queries": [],
                "raw_search_results": [],
                "filtered_sources": [],
                "verified_sources": [],
                "draft_content": None,
                "current_draft": None,
                "revision_count": 0,
                "evaluation_results": [],
                "evaluation_score": None,
                "turnitin_reports": [],
                "turnitin_passed": False,
                "formatted_document": None,
                "learning_outcomes_report": None,
                "download_urls": {},
                "current_node": None,
                "workflow_status": "initiated",
                "error_message": None,
                "retry_count": 0,
                "max_iterations": 5,
                "enable_tutor_review": False,
                "start_time": time.time(),
                "end_time": None,
                "processing_metrics": {},
                "auth_token": None,
                "payment_transaction_id": None,
                "uploaded_files": [{"content": f.get("content", ""), "filename": f.get("filename", "")} for f in files],
            }
            state = HandyWriterzState(**_state_kwargs)  # type: ignore[arg-type]

            # Execute the workflow
            config = {"configurable": {"thread_id": conversation_id}}
            result = await handywriterz_graph.ainvoke(state, config)

            # Extract comprehensive results
            return {
                "success": True,
                "trace_id": conversation_id,
                "conversation_id": conversation_id,
                "response": self._extract_content(result),
                "sources": getattr(result, 'verified_sources', []),
                "workflow_status": getattr(result, 'workflow_status', 'completed'),
                "quality_score": getattr(result, 'evaluation_score', 0),
                "agent_metrics": getattr(result, 'processing_metrics', {}),
                "citation_count": len(getattr(result, 'verified_sources', [])),
                "system_type": "advanced_handywriterz",
                "user_params": validated_params.dict()
            }

        except Exception as e:
            logger.error(f"Advanced processing error: {e}")
            raise Exception(f"Advanced system processing failed: {e}")

    async def _process_hybrid(
        self,
        message: str,
        files: List,
        user_params: dict = None,
        user_id: str = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """Process using hybrid approach (both systems in parallel)."""

        await self._publish_event(conversation_id, {
            "type": "content",
            "text": "Running hybrid analysis with multiple AI systems..."
        })

        try:
            tasks = []

            # Start simple system for quick insights
            if self.router.simple_available:
                tasks.append(self._process_simple(message, files, conversation_id))

            # Start advanced system for comprehensive analysis
            if self.router.advanced_available:
                tasks.append(self._process_advanced(message, files, user_params, user_id, conversation_id))

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
                    simple_result["system_type"] = "simple_fallback"
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
                url = source.get("url", "")
                if url and url not in seen_urls:
                    unique_sources.append(source)
                    seen_urls.add(url)
                elif not url:  # No URL, include anyway
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
                    "advanced_available": not isinstance(advanced_result, Exception)
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

        # Fallback to last AI message
        messages = getattr(result, 'messages', [])
        if messages:
            for msg in reversed(messages):
                if hasattr(msg, 'content') and not isinstance(msg, HumanMessage):
                    return msg.content

        return "Advanced content generated successfully"

    def _infer_user_params(self, message: str) -> UserParams:
        """Infer user parameters from message content."""

        message_lower = message.lower()

        # Infer writeup type
        writeup_type = "essay"  # default
        if "research" in message_lower:
            writeup_type = "research"
        elif "thesis" in message_lower:
            writeup_type = "thesis"
        elif "report" in message_lower:
            writeup_type = "report"

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

        # Infer field
        field = "general"
        field_keywords = {
            "psychology": ["psychology", "psychological", "mental health"],
            "business": ["business", "management", "marketing", "economics"],
            "technology": ["technology", "computer", "software", "ai", "machine learning"],
            "healthcare": ["health", "medical", "medicine", "nursing"],
            "education": ["education", "teaching", "pedagogy", "learning"],
            "science": ["science", "research", "experiment", "biology", "chemistry"]
        }

        for field_name, keywords in field_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                field = field_name
                break

        return UserParams(
            writeupType=writeup_type,
            field=field,
            tone="academic",
            language="en",
            pages=min(max(pages, 1), 50),  # Clamp between 1-50
            referenceStyle="APA",
            educationLevel="undergraduate"
        )
