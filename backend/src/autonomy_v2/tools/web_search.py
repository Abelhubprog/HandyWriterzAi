"""Web search wrapper.

If backend/src/tools/google_web_search.py is available, wrap it; otherwise use
the local deterministic stub (no network).
"""

from typing import List, Dict
import logging
import time
import random

logger = logging.getLogger(__name__)


def _stub_search(query: str, k: int = 3) -> List[Dict[str, str]]:
    return [
        {"title": f"Stub result {i+1}", "url": f"https://example.com/{i+1}", "snippet": query[:80]}
        for i in range(max(0, k))
    ]


def search(query: str, k: int = 3) -> List[Dict[str, str]]:
    """Web search with simple retry/backoff then stub fallback."""
    try:
        from backend.src.tools.google_web_search import google_web_search  # type: ignore
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                results = google_web_search(query, num_results=k)
                # Handle coroutine return
                try:
                    import asyncio
                    if asyncio.iscoroutine(results):
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            logger.debug("google_web_search returned coroutine in running loop; using stub")
                            return _stub_search(query, k)
                        return loop.run_until_complete(results)
                except Exception:
                    pass
                return results  # type: ignore[return-value]
            except Exception as e:
                # Backoff on transient errors
                time.sleep(0.5 * (2 ** (attempts - 1)) + random.random() * 0.1)
        # All retries failed; fall back
        return _stub_search(query, k)
    except Exception as e:
        logger.debug(f"Falling back to stub web search: {e}")
        return _stub_search(query, k)
