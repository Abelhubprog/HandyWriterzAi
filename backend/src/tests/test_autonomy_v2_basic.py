import asyncio

from backend.src.autonomy_v2.core.graph import build_graph
from backend.src.autonomy_v2.core.state import GraphState


def test_plan_act_reflect_end(monkeypatch):
    graph = build_graph()
    state = GraphState(run_id="v2-pytest", task={"goal": "test research topic"})
    result = graph.invoke(state)
    assert isinstance(result, GraphState)
    # After one cycle, critic should pass if sources found
    obs = result.last_observation or {}
    sources = obs.get("sources") or []
    assert isinstance(sources, list)
    # google_web_search returns mock results; fallback stub returns at least 0.. ensure code didn't error
    assert result.route in ("END", "plan")
    # prefer END when sources exist
    if sources:
        assert result.route == "END"

