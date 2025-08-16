"""
Unified Processor for Unified AI Platform

Handles routing between simple and advanced systems and processes
requests using the optimal system based on complexity analysis.
"""

import time
import uuid
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict, Union, cast, Any

from langchain_core.messages import HumanMessage
import redis.asyncio as redis
import os

# Import typed SSE events for production-grade event streaming
from src.schemas.sse_events import (
    SSEEventFactory, SSEEventType, ContentEvent, RoutingEvent,
    DoneEvent, ErrorEvent, CostEvent, MetricsEvent
)

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
    def validate_user_params(x):  # type: ignore
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

# Prompt Orchestrator imports
try:
    from src.services.prompt_orchestrator import (
        get_prompt_orchestrator, UserParams as PromptUserParams,
        EvidenceSnippet, CostLevel as PromptCostLevel, UseCase
    )  # type: ignore
    _FEATURE_PROMPT_ORCHESTRATOR = os.getenv("FEATURE_PROMPT_ORCHESTRATOR", "true").lower() == "true"
except Exception:  # pragma: no cover
    def get_prompt_orchestrator():  # type: ignore
        return None
    class PromptUserParams:  # type: ignore
        pass
    class EvidenceSnippet:  # type: ignore
        pass
    class PromptCostLevel:  # type: ignore
        BUDGET = "budget"
        STANDARD = "standard"
        PREMIUM = "premium"
    class UseCase:  # type: ignore
        GENERAL = "general"
    _FEATURE_PROMPT_ORCHESTRATOR = False  # type: ignore[assignment]

# Legacy event data - being replaced by typed SSE events
class _EventData(TypedDict, total=False):
    type: str
    message: str
    timestamp: float
    system: str
    complexity: float
    reason: str
    # Back-compat fields used by publisher callsites
    text: str

from .system_router import SystemRouter
from src.agent.handywriterz_state import HandyWriterzState
from ..handywriterz_graph import handywriterz_graph
from ..base import UserParams

logger = logging.getLogger(__name__)

# Redis client kept only for extreme fallback paths (should be unused after SSEService unification)
redis_client: "redis.Redis" = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)  # type: ignore[assignment]

# Unified lightweight SSE service (Redis-backed), used as primary publisher
try:
    from src.services.sse_service import get_sse_service
    _sse_service = get_sse_service()
except Exception:
    _sse_service = None  # Fallback to direct Redis if unavailable


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
        with with_correlation_context(  # type: ignore[misc]
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
                budget_result = guard_request(  # type: ignore[call-arg, assignment]
                    estimated_tokens=estimated_tokens,
                    role="user",  # Could be enhanced with actual user role
                    tenant=user_id,
                    cost_level=CostLevel.MEDIUM  # Will be adjusted based on routing
                )
                if budget_result is None:
                    class _BR:  # minimal shim
                        estimated_cost = 0.0
                    budget_result = _BR()  # type: ignore[assignment]

                logger.info(f"Budget check passed: ${getattr(budget_result, 'estimated_cost', 0.0):.4f} estimated")

                # Emit unified milestone for budget creation/projection
                try:
                    if _sse_service is not None:
                        await _sse_service.publish_workflow_progress(conversation_id, {
                            "type": "progress:budget_created",
                            "estimated_cost": float(getattr(budget_result, "estimated_cost", 0.0)),
                            "estimated_tokens": int(estimated_tokens) if isinstance(estimated_tokens, (int, float)) else 0,
                        })
                except Exception as _sse_budget_err:
                    logger.warning(f"Failed to publish budget milestone: {_sse_budget_err}")

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

            # Start streaming (route through SSEService)
            await self._publish_event(conversation_id, _EventData(
                type="start",
                message="Processing your request...",
                timestamp=time.time()
            ), use_sse=True, double_publish=False)

            # Back-compat routing/planning markers for UI timelines
            await self._publish_event(conversation_id, _EventData(
                type="planning_started",
                message="Planning the approach...",
                timestamp=time.time()
            ), use_sse=True, double_publish=False)

            # (deduplicated - planning_started emitted above for consistent ordering)

            # (deduplicated - planning_started emitted above for consistent ordering)

            # Optional params normalization prior to routing
            effective_params = user_params or {}
            # If upstream already normalized (has _normalization_meta), skip re-normalization
            if use_params and isinstance(effective_params, dict) and effective_params.get("_normalization_meta"):
                use_params = False
            if use_params:
                try:
                    effective_params = normalize_user_params(effective_params or {})
                    validate_user_params(effective_params)  # type: ignore[call-arg]
                except Exception:
                    effective_params = user_params or {}

            # Analyze and route
            routing = await self.router.analyze_request(message, files, effective_params)  # type: ignore[call-arg]
            logger.info(f"🎯 Routing decision: {routing}")

            await self._publish_event(conversation_id, _EventData(
                type="routing",
                system=str(routing.get("system", "")),
                complexity=float(routing.get("complexity", 0.0)),
                reason=str(routing.get("reason", ""))
            ), use_sse=True, double_publish=False)

            # Always use advanced system - simple and hybrid systems removed
            # Emit verify/writer/evaluator/formatter lifecycle around the advanced execution window.
            await self._publish_event(conversation_id, _EventData(
                type="search_started",
                message="Starting multi-agent search...",
                timestamp=time.time()
            ), use_sse=True, double_publish=False)

            # Advanced execution (search/verify/write/evaluate/format handled inside graph; writer will stream tokens)
            result = await self._process_advanced(
                message=message,
                files=cast(List[Dict[str, Any]], files or []),
                user_params=cast(Dict[str, Any], effective_params if use_params else (user_params or {})),  # type: ignore[valid-type]
                user_id=str(user_id or ""),
                conversation_id=str(conversation_id),
            )

            # Finalize with finished event emitted below (done)

            # Add routing metadata
            result.update({
                "system_used": "advanced",  # Always advanced now
                "complexity_score": routing["complexity"],
                "routing_reason": "Simple system removed - using advanced",
                "routing_confidence": routing["confidence"],
                "processing_time": time.time() - start_time
            })

            # Record actual usage for budget tracking
            try:
                _ = time.time() - start_time  # keep variable used
                actual_tokens = cast(Union[int, float], result.get("tokens_used", estimated_tokens))  # type: ignore[arg-type]
                actual_cost = float(getattr(locals().get("budget_result", None), "estimated_cost", 0.0))

                record_usage(  # type: ignore[call-arg]
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
                type="workflow_finished",
                message="Processing completed",
                timestamp=time.time()
            ), use_sse=True, double_publish=False)

            # Back-compat 'done'
            await self._publish_event(conversation_id, _EventData(
                type="done",
                message="Processing completed",
                timestamp=time.time()
            ), use_sse=True, double_publish=False)

            return result

        except Exception as e:
            logger.error(f"Unified processing error: {e}")

            await self._publish_event(
                conversation_id,
                _EventData(
                    type="error",
                    message=f"Error: {str(e)}",
                    timestamp=time.time()
                ),
                use_sse=True,
                double_publish=False
            )

            # Fallback to advanced system if available
            if locals().get("routing") and routing.get("system") != "advanced" and self.router.advanced_available:
                logger.info("🔄 Falling back to advanced system")
                try:
                    result = await self._process_advanced(
                        message=message,
                        files=cast(List[Dict[str, Any]], files or []),
                        user_params=cast(Dict[str, Any], user_params or {}),
                        user_id=str(user_id or ""),
                        conversation_id=str(conversation_id),
                    )
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
        """Publish event via SSEService unified channel; fallback to legacy channel."""
        evt_type = event_data.get("type", "content")
        payload = {k: v for k, v in event_data.items() if k != "type"}

        try:
            if _sse_service is not None:
                await _sse_service.publish_event(conversation_id, evt_type, payload)
                return
            else:
                logger.warning("SSEService unavailable; dropping event to avoid legacy drift")
        except Exception as e:
            logger.warning(f"SSEService publish failed: {e}")

    async def _publish_typed_event(self, event: Any, use_sse: bool = False, double_publish: bool = False):
        """Publish typed SSE event via SSEService, fallback to legacy if needed."""
        conversation_id = getattr(event, "conversation_id", None)
        event_data = event.dict() if hasattr(event, "dict") else {}
        evt_type = event_data.get("type", "content")
        payload = {k: v for k, v in event_data.items() if k not in ["type", "conversation_id"]}

        try:
            if _sse_service is not None:
                await _sse_service.publish_event(conversation_id, evt_type, payload)
                return
            else:
                logger.warning("SSEService unavailable; dropping typed event to avoid legacy drift")
        except Exception as e:
            logger.warning(f"SSEService typed publish failed: {e}")

    async def _emit_agent_event(self, conversation_id: str, kind: str, *, agent: str, **fields: Any) -> None:
        """Helper to emit agent:* events in a consistent shape.

        kind: 'agent:start' | 'agent:tool' | 'agent:result'
        fields may include: action, query, tool, result, tokens, cost, summary, count, details
        """
        try:
            await self._publish_event(conversation_id, _EventData(
                type=kind,
                message=json.dumps({"agent": agent, **fields}),
                timestamp=time.time()
            ), use_sse=True, double_publish=False)
        except Exception as e:
            logger.warning(f"Failed to emit {kind} for {agent}: {e}")

    async def _publish_legacy_event(self, conversation_id: str, event_data: _EventData, use_sse: bool = False, double_publish: bool = False):
        """Legacy event publishing fallback (kept for safety)."""
        # Legacy path removed; route through SSEService only to maintain a single canonical publisher
        await self._publish_event(conversation_id, event_data, use_sse=True, double_publish=False)

    # _process_simple method removed - simple system eliminated

    async def _process_advanced(
        self,
        message: str,
        files: List[Dict[str, Any]],
        user_params: Dict[str, Any],
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Process using advanced HandyWriterz system with prompt orchestration."""

        await self._publish_event(conversation_id, _EventData(
            type="content",
            text="Routing to advanced HandyWriterz agents...",
            timestamp=time.time()
        ), use_sse=True, double_publish=False)

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

            # Initialize prompt orchestration if enabled
            prompt_assembly_result = None
            if _FEATURE_PROMPT_ORCHESTRATOR:
                try:
                    orchestrator = get_prompt_orchestrator()
                    if orchestrator:
                        # Agent: planner start
                        await self._emit_agent_event(conversation_id, 'agent:start', agent='planner', action='assemble_prompt')
                        # Map user params to prompt orchestrator format
                        use_case = self._map_mode_to_use_case(user_params.get("mode", "general") if user_params else "general")

                        prompt_user_params = PromptUserParams(
                            citation_style=getattr(validated_params, 'citation_style', 'apa'),
                            word_count_target=getattr(validated_params, 'word_count', None),
                            academic_level=getattr(validated_params, 'academic_level', 'graduate'),
                            file_ids=[f.get('file_id', '') for f in files if f.get('file_id')]
                        )

                        # TODO: Integrate with memory service when available
                        memory_summary = None
                        evidence_snippets = []

                        # Map cost level
                        budget_level = self._map_cost_level(user_params.get("budget_level", "standard") if user_params else "standard")

                        await self._publish_event(conversation_id, _EventData(
                            type="content",
                            text=f"🎯 Assembling {use_case} prompt with {len(files)} files...",
                            timestamp=time.time()
                        ))

                        # Assemble production-grade prompt
                        prompt_assembly_result = orchestrator.assemble_prompt(
                            use_case=use_case,
                            user_params=prompt_user_params,
                            memory_summary=memory_summary,
                            evidence_snippets=evidence_snippets,
                            budget_level=budget_level,
                            custom_context={
                                "user_prompt": message,
                                "files_count": len(files),
                                "file_types": list(set(f.get('type', 'unknown') for f in files))
                            }
                        )

                        logger.info(f"🎯 Prompt assembled: {prompt_assembly_result.prompt_id} for {use_case}")

                        await self._publish_event(conversation_id, _EventData(
                            type="content",
                            text=f"✅ Prompt orchestration complete (ID: {prompt_assembly_result.prompt_id[:8]}...)",
                            timestamp=time.time()
                        ))

                        # Agent: planner result
                        try:
                            await self._emit_agent_event(
                                conversation_id,
                                'agent:result',
                                agent='planner',
                                summary='prompt_orchestrated',
                                details={
                                    "prompt_id": getattr(prompt_assembly_result, 'prompt_id', None),
                                    "policy_version": getattr(prompt_assembly_result, 'policy_version', None),
                                    "token_estimate": getattr(prompt_assembly_result, 'token_estimate', None),
                                }
                            )
                        except Exception:
                            pass

                except Exception as e:
                    logger.warning(f"⚠️ Prompt orchestration failed, using default: {e}")
                    await self._publish_event(conversation_id, _EventData(
                        type="content",
                        text="⚠️ Using fallback prompt system...",
                        timestamp=time.time()
                    ))

            # Create advanced state with prompt orchestration
            # Construct via kwargs dictionary to avoid Pylance false negatives on dataclass analysis
            _state_kwargs: Dict[str, Any] = {
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
                # Add prompt orchestration metadata
                "prompt_metadata": {
                    "prompt_id": prompt_assembly_result.prompt_id if prompt_assembly_result else None,
                    "policy_version": prompt_assembly_result.policy_version if prompt_assembly_result else None,
                    "use_case": prompt_assembly_result.metadata.get("use_case") if prompt_assembly_result else "general",
                    "model_hints": prompt_assembly_result.model_hints.dict() if prompt_assembly_result else {},
                    "output_contract": prompt_assembly_result.output_contract.dict() if prompt_assembly_result else {},
                    "token_estimate": prompt_assembly_result.token_estimate if prompt_assembly_result else 0
                } if _FEATURE_PROMPT_ORCHESTRATOR else {}
            }
            state = HandyWriterzState(**_state_kwargs)  # type: ignore[arg-type]

            # Execute the workflow with enhanced configuration
            config = {
                "configurable": {"thread_id": conversation_id},
                # Pass prompt assembly to graph execution
                "prompt_assembly": prompt_assembly_result if prompt_assembly_result else None
            }
            # Agent: research + writer start markers (high-level)
            await self._emit_agent_event(conversation_id, 'agent:start', agent='research_swarm', action='search_and_filter_sources')
            await self._emit_agent_event(conversation_id, 'agent:start', agent='writer', action='draft_and_format')

            result = await handywriterz_graph.ainvoke(state, config)  # type: ignore[call-arg]

            # Extract comprehensive results
            # Emit agent results based on output
            try:
                sources = getattr(result, 'verified_sources', []) or []
                await self._emit_agent_event(
                    conversation_id,
                    'agent:result',
                    agent='research_swarm',
                    summary='verified_sources',
                    count=len(sources)
                )
                # Emit top sources as tool outcomes (title + url when available)
                for s in (sources[:5] if isinstance(sources, list) else []):
                    title = (s.get('title') if isinstance(s, dict) else None) or str(s)
                    url = s.get('url') if isinstance(s, dict) else None
                    conf = s.get('confidence') if isinstance(s, dict) else None
                    await self._emit_agent_event(
                        conversation_id,
                        'agent:tool',
                        agent='retriever',
                        result=title,
                        url=url,
                        confidence=conf
                    )
            except Exception:
                pass

            try:
                content = self._extract_content(result)
                words = len(content.split()) if isinstance(content, str) else 0
                await self._emit_agent_event(
                    conversation_id,
                    'agent:result',
                    agent='writer',
                    summary='draft_generated',
                    words=words
                )
            except Exception:
                pass

            # Emit evaluator metrics if available
            try:
                eval_score = getattr(result, 'evaluation_score', None)
                eval_results = getattr(result, 'evaluation_results', None)
                samples = []
                if isinstance(eval_results, list):
                    for it in eval_results[:3]:
                        if isinstance(it, dict):
                            txt = it.get('feedback') or it.get('message') or it.get('text')
                            if txt:
                                samples.append(str(txt)[:300])
                        elif isinstance(it, str):
                            samples.append(it[:300])
                if eval_score is not None:
                    await self._emit_agent_event(
                        conversation_id,
                        'agent:result',
                        agent='evaluator',
                        summary='evaluation_complete',
                        score=float(eval_score),
                        feedback_samples=samples,
                        details={"items": len(eval_results) if isinstance(eval_results, list) else 0}
                    )
            except Exception:
                pass

            # Emit tool outcomes if present in processing_metrics
            try:
                metrics = getattr(result, 'processing_metrics', {}) or {}
                tools = metrics.get('tools') or metrics.get('tools_used') or metrics.get('tool_calls') or []
                if isinstance(tools, list):
                    for t in tools[:20]:  # cap to avoid flooding
                        tool_name = (t.get('tool') or t.get('name') or 'tool') if isinstance(t, dict) else 'tool'
                        summary = (t.get('summary') or t.get('result') or t.get('status') or '') if isinstance(t, dict) else str(t)
                        query = t.get('query') if isinstance(t, dict) else None
                        url = t.get('url') if isinstance(t, dict) else None
                        title = t.get('title') if isinstance(t, dict) else None
                        await self._emit_agent_event(
                            conversation_id,
                            'agent:tool',
                            agent=str(tool_name),
                            result=title or summary,
                            query=query,
                            url=url
                        )
                # Emit search queries if present on result
                search_queries = getattr(result, 'search_queries', []) or []
                if isinstance(search_queries, list):
                    for q in search_queries[:10]:
                        await self._emit_agent_event(
                            conversation_id,
                            'agent:tool',
                            agent='search',
                            query=str(q)
                        )
            except Exception:
                pass

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

    # _process_hybrid method removed - hybrid system eliminated

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

        # No content found - return structured error for debugging
        error_details = {
            "error": "No content generated",
            "checked_sources": content_sources,
            "available_attributes": [attr for attr in dir(result) if not attr.startswith('_')],
            "messages_count": len(getattr(result, 'messages', [])),
            "workflow_status": getattr(result, 'workflow_status', 'unknown')
        }
        logger.error(f"Content extraction failed: {error_details}")
        return f"Content generation incomplete. Agent workflow may have failed. Check logs for details."

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

    def _map_mode_to_use_case(self, mode: str) -> str:
        """Map frontend mode to prompt orchestrator use case."""
        if not _FEATURE_PROMPT_ORCHESTRATOR:
            return "general"

        mode_mapping = {
            "general": UseCase.GENERAL,
            "dissertation": UseCase.DISSERTATION,
            "thesis": UseCase.THESIS,
            "research_paper": UseCase.RESEARCH_PAPER,
            "review_article": UseCase.REVIEW_ARTICLE,
            "case_study": UseCase.CASE_STUDY,
            "methodology_writer": UseCase.METHODOLOGY_WRITER,
            "literature_review": UseCase.LITERATURE_REVIEW,
            "slide_generator": UseCase.SLIDE_GENERATOR,
            "coding_helper": UseCase.CODING_HELPER,
            # Legacy mode mappings
            "qa_general": UseCase.GENERAL,
            "academic_writing": UseCase.DISSERTATION,
            "research": UseCase.RESEARCH_PAPER
        }
        return mode_mapping.get(mode.lower(), UseCase.GENERAL)

    def _map_cost_level(self, cost_level: str) -> "PromptCostLevel":
        """Map cost level to prompt orchestrator format."""
        if not _FEATURE_PROMPT_ORCHESTRATOR:
            return PromptCostLevel.STANDARD

        level_mapping = {
            "low": PromptCostLevel.BUDGET,
            "budget": PromptCostLevel.BUDGET,
            "medium": PromptCostLevel.STANDARD,
            "standard": PromptCostLevel.STANDARD,
            "high": PromptCostLevel.PREMIUM,
            "premium": PromptCostLevel.PREMIUM
        }
        mapped_level = level_mapping.get(cost_level.lower(), PromptCostLevel.STANDARD)
        return mapped_level
