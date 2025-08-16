"""LangGraph wiring for Autonomy V2 with persistence + episodic logs.

Each node logs an event and persists a checkpoint via the SQL checkpointer.
"""

from typing import Any, Callable, Awaitable, Dict
import logging

from langgraph.graph import StateGraph, END

from .state import GraphState
from ..agents import planner, executor, critic, researcher, self_debugger
from ..agents import turnitin_coordinator
from ..runtime.checkpointer_sql import sql_checkpointer
from ..runtime.budgets import BudgetGuard
from ..core import llm as v2llm
import time
from ..memory.episodic_repo import EpisodicRepo

logger = logging.getLogger(__name__)


def _get_defaults() -> Dict[str, int]:
    try:
        from src.config import get_settings  # type: ignore
        s = get_settings()
        return {
            "tokens": int(getattr(s, "v2_budget_tokens", 0)),
            "seconds": int(getattr(s, "v2_budget_seconds", 0)),
        }
    except Exception:
        return {"tokens": 0, "seconds": 0}


async def _checkpoint(state: GraphState) -> None:
    try:
        cp = sql_checkpointer()
        payload = state.model_dump()
        cp.put(state.run_id, payload)
    except Exception as e:  # pragma: no cover
        logger.debug(f"checkpoint failed: {e}")


async def _episodic(state: GraphState, role: str, content: Dict[str, Any]) -> None:
    try:
        repo = EpisodicRepo(run_id=state.run_id)
        await repo.append({
            "run_id": state.run_id,
            "step_id": content.get("step_id"),
            "role": role,
            "content": content,
        })
    except Exception as e:  # pragma: no cover
        logger.debug(f"episodic log failed: {e}")


def _wrap(node_name: str, fn: Callable[[GraphState], Awaitable[GraphState]]):
    role_map = {"plan": "plan", "act": "action", "reflect": "verdict", "expand": "note", "repair": "note"}
    role = role_map.get(node_name, "note")

    async def _run(state: GraphState) -> GraphState:
        # Ensure defaults exist
        if state.budget_tokens == 0 and state.budget_seconds == 0:
            d = _get_defaults()
            state.budget_tokens = d["tokens"]
            state.budget_seconds = d["seconds"]
        guard = BudgetGuard(run_id=state.run_id)
        await _episodic(state, role, {"node": node_name, "route": state.route})
        await _checkpoint(state)
        # Drain LLM metrics before and after to compute this node's usage
        _ = v2llm.get_and_reset_metrics(state.run_id)
        t0 = time.time()
        new_state = await fn(state)
        metrics = v2llm.get_and_reset_metrics(state.run_id)
        # Update budgets: prefer actual tokens/usd from gateway; add naive tokens from output as a floor
        tokens = int(metrics.get("tokens", 0))
        usd = float(metrics.get("usd", 0.0))
        try:
            content = (new_state.last_observation or {}).get("output", "")
            tokens = max(tokens, len(str(content).split()))
        except Exception:
            pass
        ok = await guard.tick(new_state, tokens_used=tokens, usd_used=usd)
        if not ok:
            new_state.route = "END"
        await _checkpoint(new_state)
        # TODO: emit SSE via SSEService for UI timeline if needed
        return new_state

    return _run


def build_graph() -> Any:
    g = StateGraph(GraphState)

    g.add_node("plan", _wrap("plan", planner.run))
    g.add_node("act", _wrap("act", executor.run))
    g.add_node("reflect", _wrap("reflect", critic.run))
    g.add_node("expand", _wrap("expand", researcher.run))
    g.add_node("repair", _wrap("repair", self_debugger.run))
    g.add_node("turnitin", _wrap("turnitin", turnitin_coordinator.handoff))

    g.add_edge("plan", "act")
    g.add_edge("act", "reflect")

    def _route(state: GraphState) -> str:
        r = (state.route or "").lower()
        if r in {"plan", "expand", "repair", "turnitin"}:
            return r
        # Graph pauses by mapping to END while preserving state.route
        return "END"

    g.add_conditional_edges("reflect", _route, {"plan": "plan", "expand": "expand", "repair": "repair", "turnitin": "turnitin", "END": END})

    # Any node may set route to 'turnitin_pause' to indicate external wait; map to END
    g.add_conditional_edges("turnitin", _route, {"turnitin": "turnitin", "plan": "plan", "expand": "expand", "repair": "repair", "END": END})

    # Compile with SQL checkpointer (used by our wrappers manually as well)
    return g.compile(checkpointer=sql_checkpointer())
