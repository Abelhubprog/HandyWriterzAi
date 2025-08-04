import os
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, List, TypedDict, cast

try:
    # Optional dependency; use best-effort type ignore for static analysis
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:  # pragma: no cover
    ChatOpenAI = object  # type: ignore[misc,assignment]

from ...agent.handywriterz_state import HandyWriterzState  # type: ignore


# Best-effort import for unified SSE publisher (non-fatal if unavailable)
try:
    from src.agent.sse import SSEPublisher  # type: ignore
    import redis.asyncio as _redis  # type: ignore
    _SSE: Optional["SSEPublisher"] = SSEPublisher(async_redis=_redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379")))  # type: ignore[call-arg]
except Exception:  # pragma: no cover
    _SSE = None


class SearchResultDict(TypedDict, total=False):
    id: str
    title: str
    url: str
    snippet: str
    score: float
    provider: str


class OpenAISearchAgent:
    """A search agent that uses OpenAI's GPT-4 for general intelligence."""

    def __init__(self) -> None:
        self._model: Optional["ChatOpenAI"] = None  # type: ignore[type-arg]

    @property
    def model(self) -> "ChatOpenAI":  # type: ignore[override]
        """Lazy initialization of OpenAI model."""
        if self._model is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for OpenAISearchAgent.")
            # type: ignore[call-arg]
            self._model = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=api_key)  # type: ignore[call-arg]
        return cast("ChatOpenAI", self._model)

    async def _publish(self, conversation_id: Optional[str], event_type: str, payload: Dict[str, Any]) -> None:
        """Publish SSE event if publisher available (best-effort, non-fatal)."""
        if not conversation_id or _SSE is None:
            return
        try:
            data: Dict[str, Any] = dict(payload)
            if "ts" not in data:
                data["ts"] = datetime.utcnow().isoformat()
            await _SSE.publish(conversation_id, event_type, data)  # type: ignore[attr-defined]
        except Exception:
            # Ignore SSE failures
            pass

    async def execute(self, state: "HandyWriterzState", config: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[override]
        """
        Executes the OpenAI search agent.
        Streams search lifecycle events and sources snapshot via SSE.
        """
        # Derive query from state; keep backward compatibility
        queries = cast(List[str], state.get("search_queries", []))  # type: ignore[attr-defined]
        query = (queries[-1] if queries else None) or state.get("query") or state.get("user_query")  # type: ignore[attr-defined]
        if not query:
            raise ValueError("Missing search query for OpenAISearchAgent.")

        conversation_id = cast(Optional[str], state.get("conversation_id"))  # type: ignore[attr-defined]
        await self._publish(conversation_id, "search_started", {"query": query})

        # Simulate progressive retrieval updates in 3 mini-batches
        prompt = (
            "Provide a concise, well-structured outline of key sources, keywords, and angles to research for the query:\n\n"
            f"{query}\n\nRespond in 3 short bullet sections."
        )

        await self._publish(conversation_id, "search_progress", {"retrieved": 0, "batch_index": 0, "batch_size": 0})

        # Mini-batch 1: keyword brainstorm
        await asyncio.sleep(0.05)
        await self._publish(conversation_id, "sources_update", {
            "sources": [
                {"id": "kw-1", "title": "Keyword brainstorm", "url": "", "score": 0.4, "provider": "planner"}
            ]
        })

        # Mini-batch 2: outline via LLM
        # type: ignore[attr-defined]
        response = await self.model.ainvoke(prompt)  # type: ignore[call-arg]
        await self._publish(conversation_id, "search_progress", {"retrieved": 1, "batch_index": 1, "batch_size": 1})
        await self._publish(conversation_id, "sources_update", {
            "sources": [
                {"id": "kw-1", "title": "Keyword brainstorm", "url": "", "score": 0.4, "provider": "planner"},
                {"id": "llm-outline", "title": "LLM outline", "url": "", "score": 0.6, "provider": "openai"}
            ]
        })

        # Mini-batch 3: finalize snapshot
        await asyncio.sleep(0.05)
        await self._publish(conversation_id, "search_progress", {"retrieved": 2, "batch_index": 2, "batch_size": 1})
        await self._publish(conversation_id, "sources_update", {
            "sources": [
                {"id": "kw-1", "title": "Keyword brainstorm", "url": "", "score": 0.4, "provider": "planner"},
                {"id": "llm-outline", "title": "LLM outline", "url": "", "score": 0.6, "provider": "openai"},
                {"id": "seed-1", "title": "Seed reference suggestions", "url": "", "score": 0.5, "provider": "heuristic"}
            ]
        })

        resp_content = getattr(response, "content", "")  # type: ignore[attr-defined]
        result_entry: SearchResultDict = {
            "id": "llm-outline",
            "title": "LLM outline",
            "url": "",
            "snippet": resp_content,
            "score": 0.6,
            "provider": "openai",
        }

        return {
            "raw_search_results": [{"source": "OpenAI", "content": resp_content}],
            "search_results": [result_entry],
            "filtered_sources": [result_entry],
        }
