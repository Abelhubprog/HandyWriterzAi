from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)


_TOOLS: Dict[str, Dict[str, Any]] = {}
_KIND_MAP: Dict[str, str] = {}
_DEFAULTS_DONE = False


def register_tool(name: str, func: Callable[..., Any], *, schema: Optional[Dict[str, Any]] = None, kinds: Optional[list[str]] = None) -> None:
    _TOOLS[name] = {"func": func, "schema": schema or {}}
    for k in (kinds or []):
        _KIND_MAP[k] = name


def get(name: str) -> Callable[..., Any]:
    return _TOOLS[name]["func"]


def list_tools() -> Dict[str, Callable[..., Any]]:
    return {k: v["func"] for k, v in _TOOLS.items()}


def _echo_tool(**kwargs: Any) -> Dict[str, Any]:
    text = kwargs.get("text") or kwargs.get("query") or ""
    return {"output": text, "results": [], "sources": []}


def _ensure_defaults() -> None:
    global _DEFAULTS_DONE
    if _DEFAULTS_DONE:
        return
    # Register echo by default
    register_tool("echo", _echo_tool, kinds=["write", "summarize"]) 
    # Register web_search if available
    try:
        from ..tools.web_search import search as web_search
        register_tool("web_search", lambda query, k=3: {"output": f"found {k} results", "results": web_search(query, k), "sources": [r.get("url") for r in web_search(query, k)]}, kinds=["research"])
    except Exception as e:  # pragma: no cover
        logger.debug(f"web_search not available: {e}")
    _DEFAULTS_DONE = True


def choose_tool(step_kind: str) -> Callable[..., Any]:
    _ensure_defaults()
    name = _KIND_MAP.get(step_kind, "echo")
    return get(name)
