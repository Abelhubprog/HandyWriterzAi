"""Autonomy V2 API: start runs, read snapshots, and stream events (SSE)."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sse_starlette import EventSourceResponse
import asyncio
import time
import uuid

from ..autonomy_v2.core.graph import build_graph
from ..autonomy_v2.core.state import GraphState
from ..autonomy_v2.memory.episodic_repo import EpisodicRepo
from ..autonomy_v2.runtime.resume import resume_run as _resume_run
from ..autonomy_v2.runtime.queue import enqueue, enqueue_resume
from ..autonomy_v2.runtime.checkpointer_sql import sql_checkpointer
from ..services.security_service import get_current_user


router = APIRouter(prefix="/v2", tags=["autonomy_v2"])


class RunRequest(BaseModel):
    journey: str = "write"
    task_spec: dict


class RunResponse(BaseModel):
    run_id: str
    state: dict


@router.get("/health")
async def health(user: dict | None = Depends(get_current_user)) -> dict:
    return {"status": "ok", "component": "autonomy_v2"}


@router.post("/runs", response_model=RunResponse)
async def start_run(req: RunRequest, user: dict | None = Depends(get_current_user)) -> RunResponse:
    # Create a new run_id and seed checkpoint
    run_id = str(uuid.uuid4())
    # Budgets from settings
    try:
        from backend.src.config import get_settings  # type: ignore
        s = get_settings()
        budget_tokens = int(getattr(s, "v2_budget_tokens", 0))
        budget_seconds = int(getattr(s, "v2_budget_seconds", 0))
        budget_usd = float(getattr(s, "v2_budget_usd", 0.0))
    except Exception:
        budget_tokens = 0
        budget_seconds = 0
        budget_usd = 0.0

    init_state = GraphState(
        run_id=run_id,
        task=req.task_spec,
        plan=[],
        notes=["run_created"],
        route="plan",
        last_observation=None,
        budget_tokens=budget_tokens,
        budget_seconds=budget_seconds,
        budget_usd=0.0,
    )
    cp = sql_checkpointer()
    cp.put(run_id, init_state.model_dump())

    # Log event
    await EpisodicRepo(run_id=run_id).write_event(run_id, "note", {"event": "run_created", "journey": req.journey})

    # Enqueue job
    user_id = None
    try:
        if isinstance(user, dict):
            user_id = str(user.get("id") or user.get("user_id") or "")
    except Exception:
        user_id = None
    enqueue(run_id=run_id, user_id=user_id, journey=req.journey, priority=5, payload={"route": "act"})

    return RunResponse(run_id=run_id, state=init_state.model_dump())


@router.get("/runs/{run_id}")
async def get_run(run_id: str, user: dict | None = Depends(get_current_user)):
    cp = sql_checkpointer()
    payload = cp.get(run_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Run not found")
    # Minimal snapshot
    snapshot = {
        "run_id": payload.get("run_id"),
        "task": payload.get("task"),
        "route": payload.get("route"),
        "plan": payload.get("plan", []),
        "budget_tokens": payload.get("budget_tokens", 0),
        "budget_seconds": payload.get("budget_seconds", 0),
        "last_observation": payload.get("last_observation"),
        "notes": payload.get("notes", []),
    }
    return snapshot


@router.get("/runs/{run_id}/events")
async def stream_run_events(run_id: str, user: dict | None = Depends(get_current_user)):
    dbm = _get_db_manager()
    if dbm is None:
        raise HTTPException(status_code=500, detail="DB unavailable")

    async def event_gen():
        last_id = 0
        # Send a connected event
        yield {"event": "message", "data": {"type": "connected", "run_id": run_id, "ts": time.time()}}
        try:
            while True:
                with dbm.get_db_context() as session:
                    rows = session.execute(text(
                        """
                        SELECT id, role, content, created_at
                        FROM autonomy_episodic_logs
                        WHERE run_id = :r AND id > :last
                        ORDER BY id ASC
                        LIMIT 100
                        """
                    ), {"r": run_id, "last": last_id}).fetchall()
                for row in rows:
                    last_id = int(row[0])
                    payload = {
                        "type": "event",
                        "id": last_id,
                        "role": row[1],
                        "content": row[2],
                        "ts": time.time(),
                    }
                    yield {"event": "message", "data": payload}
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            return

    def _format(event: dict) -> dict:
        # sse_starlette supports dict with data as JSON serializable
        d = event.get("data")
        if isinstance(d, (dict, list)):
            event["data"] = __import__("json").dumps(d)
        return event

    async def wrapper():
        async for e in event_gen():
            yield _format(e)

    return EventSourceResponse(wrapper())


class TurnitinWebhook(BaseModel):
    cycle_id: int
    report_url: str
    observed_similarity: float
    meta: dict | None = None


def _get_db_manager():
    try:
        from src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception:
        return None


def resume_run(run_id: str, route: str = "act") -> GraphState:
    try:
        return _resume_run(run_id, route=route)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turnitin/{run_id}/report")
async def turnitin_report_webhook(run_id: str, body: TurnitinWebhook, user: dict | None = Depends(get_current_user)):
    dbm = _get_db_manager()
    if dbm is None:
        raise HTTPException(status_code=500, detail="DB unavailable")

    # Idempotent transition and single enqueue
    try:
        with dbm.get_db_context() as session:
            row = session.execute(text(
                "SELECT status, report_path, observed_similarity, resume_job_id FROM autonomy_turnitin_cycles WHERE id=:cid AND run_id=:run"
            ), {"cid": body.cycle_id, "run": run_id}).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Cycle not found")
            status, url, obs, resume_jid = row
            if str(status) == 'report_ready' and str(url or '') == body.report_url and (obs is not None and float(obs) == float(body.observed_similarity)):
                # Already processed; return existing state
                return {"status": "ok", "job_id": int(resume_jid) if resume_jid else None}

            # Update to report_ready and set values
            session.execute(text(
                "UPDATE autonomy_turnitin_cycles SET status='report_ready', observed_similarity=:obs, report_path=:url WHERE id=:cid AND run_id=:run"
            ), {"obs": float(body.observed_similarity), "url": body.report_url, "cid": body.cycle_id, "run": run_id})

            # Log event
            await EpisodicRepo(run_id=run_id).append({
                "run_id": run_id,
                "role": "note",
                "content": {"event": "turnitin_report_ready", "cycle_id": body.cycle_id}
            })

            # Enqueue resume only once
            if resume_jid:
                return {"status": "ok", "job_id": int(resume_jid)}
            jid = enqueue_resume(run_id)
            session.execute(text(
                "UPDATE autonomy_turnitin_cycles SET resume_job_id=:jid WHERE id=:cid AND run_id=:run"
            ), {"jid": int(jid), "cid": body.cycle_id, "run": run_id})
            return {"status": "enqueued", "job_id": jid}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {e}")
