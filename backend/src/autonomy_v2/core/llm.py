"""LLM adapters for Autonomy V2.

Prefer the project's unified gateway + model selector. Fall back to a
deterministic local stub if unavailable. Includes simple backoff.
"""

import asyncio
import json
import logging
import random
from typing import Any, Dict, List, Optional

from ..tools.rate_limit import TokenBucket
from ..memory.episodic_repo import EpisodicRepo
from backend.src.config import get_settings  # type: ignore
import tiktoken

logger = logging.getLogger(__name__)


def _try_existing_gateway():
    try:
        from backend.src.services.gateway import get_llm_gateway  # type: ignore
        from backend.src.services.model_selector import get_model_selector, SelectionContext, SelectionStrategy  # type: ignore
        return get_llm_gateway(), get_model_selector(), SelectionContext, SelectionStrategy
    except Exception as e:  # pragma: no cover
        logger.debug(f"LLM gateway unavailable, using stub: {e}")
        return None, None, None, None


def _approx_tokens(text: str) -> int:
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Rough estimate: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)


async def _complete_async(
    messages: List[Dict[str, str]],
    *,
    node_name: str = "autonomy_v2_planner",
    temperature: float = 0.1,
    max_tokens: Optional[int] = 400,
    user_id: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    run_id: Optional[str] = None,
) -> str:
    gateway, selector, SelectionContext, SelectionStrategy = _try_existing_gateway()
    if gateway and selector:
        try:
            ctx = SelectionContext(
                node_name=node_name,
                capabilities=capabilities or ["json_mode"],
                user_id=user_id,
                strategy=SelectionStrategy.BALANCED,
            )
            sel = await selector.select_model(ctx)
            from backend.src.services.gateway import LLMRequest  # type: ignore
            req = LLMRequest(
                messages=messages,
                model_spec=sel.selected_model,
                node_name=node_name,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                user_id=user_id,
            )

            # Simple token bucket to avoid tight retry loops
            bucket = TokenBucket(rate_per_sec=1.0, capacity=3.0)
            last_error: Optional[Exception] = None
            for attempt in range(3):
                if not bucket.allow(1.0):
                    await asyncio.sleep(0.25)
                try:
                    resp = await gateway.execute(req)
                    try:
                        # Add metrics for budgets
                        _add_metrics(run_id, int(resp.tokens_used.get("total", 0)), float(resp.cost_usd or 0.0))
                    except Exception:
                        pass
                    return resp.content or ""
                except Exception as e:
                    last_error = e
                    # Backoff with jitter
                    if run_id:
                        try:
                            await EpisodicRepo(run_id=run_id).write_event(run_id, "note", {"event": "retry", "provider": str(sel.selected_model.provider.value), "attempt": attempt+1, "reason": str(e)})
                        except Exception:
                            pass
                    await asyncio.sleep(0.5 * (2 ** attempt) + random.random() * 0.2)
            if last_error:
                raise last_error
        except Exception as e:
            logger.debug(f"LLM complete fallback due to error: {e}")

    # Fallback deterministic response
    last_user = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
    return f"[stub-response] {last_user[:60]}"


def complete(messages: List[Dict[str, str]], **kwargs: Any) -> str:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.create_task(_complete_async(messages, **kwargs))  # type: ignore[return-value]
        return loop.run_until_complete(_complete_async(messages, **kwargs))
    except RuntimeError:
        return asyncio.run(_complete_async(messages, **kwargs))


async def json_call_async(system_prompt: str, user_prompt: str, **kwargs: Any) -> Any:
    content = await _complete_async(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        **kwargs,
    )
    try:
        return json.loads(content)
    except Exception:
        return None


def json_call(system_prompt: str, user_prompt: str, **kwargs: Any) -> Any:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.create_task(_complete_async(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                **kwargs,
            ))  # type: ignore[return-value]
        return loop.run_until_complete(_complete_async(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            **kwargs,
        ))
    except RuntimeError:
        return asyncio.run(_complete_async(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            **kwargs,
        ))


def _add_metrics(run_id: Optional[str], tokens: int, usd: float) -> None:
    if not run_id:
        return
    m = _last_metrics.setdefault(run_id, {"tokens": 0.0, "usd": 0.0})
    m["tokens"] = float(m.get("tokens", 0.0)) + float(tokens)
    m["usd"] = float(m.get("usd", 0.0)) + float(usd)


def get_and_reset_metrics(run_id: str) -> Dict[str, float]:
    m = _last_metrics.pop(run_id, {"tokens": 0.0, "usd": 0.0})
    return {"tokens": float(m.get("tokens", 0.0)), "usd": float(m.get("usd", 0.0))}
