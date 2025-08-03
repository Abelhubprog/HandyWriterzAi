# Simple agent re-exports to stabilize UnifiedProcessor simple path imports.
# Do-Not-Harm: this file provides a single import surface for the simple graph.
# Usage:
#   from src.agent.simple import gemini_graph, GeminiState
#
# These symbols are provided by the existing simple graph/state modules.
#
# This module tolerates environments where simple graph/state may be unavailable
# by exposing None and allowing callers to check for availability.

from typing import Any, Optional

gemini_graph: Optional[Any] = None
GeminiState: Optional[Any] = None

try:
    # Preferred import surface within src.agent namespace
    from src.agent.graph import graph as _graph  # type: ignore
    from src.agent.state import OverallState as _GeminiState  # type: ignore

    gemini_graph = _graph
    GeminiState = _GeminiState
except Exception:
    try:
        # Fallback to relative imports when package context differs
        from ..graph import graph as _graph  # type: ignore
        from ..state import OverallState as _GeminiState  # type: ignore

        gemini_graph = _graph
        GeminiState = _GeminiState
    except Exception:
        # Final fallback for legacy naming used by UnifiedProcessor
        try:
            from src.agent.graph import build_gemini_graph as _build_graph  # type: ignore
            from src.agent.state import OverallState as _GeminiState  # type: ignore

            gemini_graph = _build_graph  # type: ignore[assignment]
            GeminiState = _GeminiState
        except Exception:
            # Leave as None to avoid import-time crash; callers already guard this.
            gemini_graph = None
            GeminiState = None
