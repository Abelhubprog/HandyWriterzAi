"""Resume utilities for Autonomy V2 runs.

For now this is a direct invoke helper; later prompts may add job queueing.
"""

from ..core.state import GraphState
from ..core.graph import build_graph
from .checkpointer_sql import sql_checkpointer


def resume_run(run_id: str, route: str = "act") -> GraphState:
    cp = sql_checkpointer()
    payload = cp.get(run_id)
    if not payload:
        raise RuntimeError("No checkpoint found for run")
    state = GraphState.model_validate(payload)
    state.route = route
    graph = build_graph()
    out = graph.invoke(state)
    return out


def enqueue_resume(run_id: str, route: str = "act") -> GraphState:
    # Future: place in a job queue. For now, call resume directly.
    return resume_run(run_id, route=route)

