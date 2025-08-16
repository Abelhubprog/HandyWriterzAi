"""Autonomy V2 harness and task runner."""

from ..core.graph import build_graph
from ..core.state import GraphState
from ..memory.episodic_repo import EpisodicRepo
from ..runtime.resume import resume_run
import os
import yaml
from pathlib import Path
from typing import Any, Dict


def run_once() -> GraphState:
    graph = build_graph()
    state = GraphState(run_id="v2-smoke", task={"goal": "hello"})
    result = graph.invoke(state)
    assert isinstance(result, GraphState)

    # Verify that episodic events were written
    import asyncio

    async def _check():
        repo = EpisodicRepo(run_id="v2-smoke")
        events = await repo.list()
        assert len(events) >= 2
        return events[:4]

    events_preview = asyncio.get_event_loop().run_until_complete(_check())
    # Print a brief preview to stdout for manual runs
    for e in events_preview:
        print({k: e.get(k) for k in ("id", "run_id", "role", "created_at")})

    return result


def demo_turnitin_pause_resume() -> GraphState:
    """Demonstrate hitl pause→webhook→resume flow without HTTP.

    1) Start a run with target_similarity to trigger the handoff.
    2) Run until pause.
    3) Update the cycle and resume.
    """
    run_id = "v2-hitl-demo"
    graph = build_graph()
    state = GraphState(run_id=run_id, task={"goal": "topic", "target_similarity": 0.15})
    paused = graph.invoke(state)
    print("Paused route:", paused.route)

    # Find last cycle id from episodic logs content
    import asyncio
    async def _get_cycle():
        repo = EpisodicRepo(run_id=run_id)
        events = await repo.list()
        cycle = None
        for e in reversed(events):
            c = (e.get("content") or {}).get("cycle_id")
            if c is not None:
                cycle = c
                break
        return cycle
    cycle_id = asyncio.get_event_loop().run_until_complete(_get_cycle())
    print("Cycle id:", cycle_id)

    # Simulate webhook DB update
    try:
        from sqlalchemy import text
        from src.db.database import get_db_manager  # type: ignore
        dbm = get_db_manager()
        with dbm.get_db_context() as session:
            session.execute(text(
                "UPDATE autonomy_turnitin_cycles SET status='report_ready', observed_similarity=:s, report_path=:u WHERE id=:cid AND run_id=:run"
            ), {"s": 0.08, "u": "https://example.com/report.pdf", "cid": cycle_id, "run": run_id})
    except Exception as e:  # pragma: no cover
        print("DB update failed:", e)

    # Resume
    resumed = resume_run(run_id, route="act")
    print("Resumed route:", resumed.route)
    return resumed


def _load_tasks_dir() -> list[tuple[str, Dict[str, Any]]]:
    base = Path(__file__).parent / "tasks"
    out = []
    for p in sorted(base.glob("*.yaml")):
        with open(p, "r", encoding="utf-8") as f:
            out.append((p.name, yaml.safe_load(f)))
    return out


def _monkey_rate_limit_planner(n_failures: int):
    from ..core import llm as llm_mod
    attempts = {"count": 0}

    async def flaky_complete(messages, **kwargs):  # type: ignore
        attempts["count"] += 1
        if attempts["count"] <= n_failures:
            raise Exception("429: rate limited")
        # Return a minimal JSON compatible with planner
        return "[{\"id\":\"step-1\",\"kind\":\"research\",\"description\":\"Find sources\"}]"

    # Patch json_call_async internals by overriding _complete_async
    llm_mod._complete_async = flaky_complete  # type: ignore[attr-defined]


def run_rate_limit_resilience(task: Dict[str, Any]) -> None:
    _monkey_rate_limit_planner(int(task.get("planner_failures", 2)))
    run_id = "v2-rlr"
    graph = build_graph()
    state = GraphState(run_id=run_id, task={"goal": task.get("goal", "")})
    out = graph.invoke(state)
    assert isinstance(out, GraphState)
    # planner should have produced a plan despite transient 429s
    assert len(out.plan) >= 1


def run_out_of_scope_research(task: Dict[str, Any]) -> None:
    # Temporarily disable turnitin policy to allow END
    try:
        import types
        from src import config as cfg  # type: ignore
        orig = cfg.get_settings
        def fake():
            s = orig()
            s.turnitin_target_default = None  # type: ignore[attr-defined]
            return s
        cfg.get_settings = fake  # type: ignore[assignment]
    except Exception:
        pass

    run_id = "v2-oor"
    graph = build_graph()
    state = GraphState(run_id=run_id, task={"goal": task.get("goal", "")})
    out = graph.invoke(state)
    assert isinstance(out, GraphState)
    obs = out.last_observation or {}
    sources = obs.get("sources") or []
    assert len(sources) >= int(task.get("min_sources", 1))
    assert out.route in ("END", "end")


def run_turnitin_cycle(task: Dict[str, Any]) -> None:
    run_id = "v2-turnitin"
    graph = build_graph()
    state = GraphState(run_id=run_id, task={"goal": task.get("goal", ""), "target_similarity": float(task.get("target_similarity", 0.15))})
    paused = graph.invoke(state)
    assert paused.route == "turnitin_pause"

    # Simulate webhook
    from ..runtime.resume import resume_run as _resume
    try:
        from backend.src.api.autonomy_v2 import turnitin_report_webhook, TurnitinWebhook  # type: ignore
        import asyncio
        payload = TurnitinWebhook(cycle_id=1, report_url="https://example.com/report.pdf", observed_similarity=float(task.get("observed_similarity", 0.1)))
        asyncio.get_event_loop().run_until_complete(turnitin_report_webhook(run_id, payload))
    except Exception:
        # Fallback: directly update DB and resume
        from sqlalchemy import text
        from src.db.database import get_db_manager  # type: ignore
        dbm = get_db_manager()
        with dbm.get_db_context() as session:
            session.execute(text(
                "UPDATE autonomy_turnitin_cycles SET status='report_ready', observed_similarity=:s WHERE run_id=:r"
            ), {"s": float(task.get("observed_similarity", 0.1)), "r": run_id})

    out = _resume(run_id, route="act")
    assert out.route in ("END", "end")


def run_all_tasks() -> None:
    tasks = _load_tasks_dir()
    for name, spec in tasks:
        ttype = spec.get("type")
        print(f"Running task: {name} ({ttype})")
        if ttype == "rate_limit_resilience":
            run_rate_limit_resilience(spec)
        elif ttype == "out_of_scope_research":
            run_out_of_scope_research(spec)
        elif ttype == "turnitin_cycle":
            run_turnitin_cycle(spec)
        else:
            raise AssertionError(f"Unknown task type: {ttype}")
    print("All tasks passed")


if __name__ == "__main__":
    run_all_tasks()
