"""Postgres-backed queue helpers for Autonomy V2.

Provides enqueue helpers for new and resume jobs.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import text


def _get_db_manager():
    from backend.src.db.database import get_db_manager  # type: ignore
    return get_db_manager()


def enqueue(run_id: str, user_id: str | None, journey: str, priority: int = 5, payload: Dict[str, Any] | None = None) -> int:
    dbm = _get_db_manager()
    with dbm.get_db_context() as session:
        q = session.execute(
            text(
                """
                INSERT INTO autonomy_job_queue (run_id, user_id, journey, priority, state, scheduled_at, attempts, payload)
                VALUES (:run_id, :user_id, :journey, :priority, 'queued', NOW(), 0, CAST(:payload AS JSON))
                RETURNING id
                """
            ),
            {"run_id": run_id, "user_id": user_id or "", "journey": journey, "priority": int(priority), "payload": (payload or {})},
        )
        row = q.fetchone()
        return int(row[0]) if row else -1


def enqueue_resume(run_id: str) -> int:
    # Include payload indicating desired route on resume
    return enqueue(run_id=run_id, user_id=None, journey="resume", priority=4, payload={"route": "act"})


def enqueue_start(run_id: str, user_id: str | None, journey: str, priority: int = 5) -> int:
    return enqueue(run_id=run_id, user_id=user_id, journey=journey, priority=priority, payload={"route": "act"})
