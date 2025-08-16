"""Autonomy V2 Queue Worker.

Claims jobs from autonomy_job_queue and advances runs.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy import text
import socket

from backend.src.autonomy_v2.runtime.resume import resume_run
from backend.src.autonomy_v2.memory.episodic_repo import EpisodicRepo

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def _get_db_manager():
    from backend.src.db.database import get_db_manager  # type: ignore
    return get_db_manager()


def _get_settings():
    try:
        from backend.src.config import get_settings  # type: ignore
        return get_settings()
    except Exception:
        class _S:
            v2_job_concurrency_per_user = 2
        return _S()


def _running_for_user(session, user_id: str) -> int:
    q = session.execute(text(
        "SELECT COUNT(1) FROM autonomy_job_queue WHERE user_id = :uid AND state = 'running'"
    ), {"uid": user_id})
    return int(q.scalar() or 0)


def _claim_next(session) -> Optional[Dict[str, Any]]:
    job = session.execute(text(
        """
        SELECT id, run_id, user_id, journey, priority, attempts, payload
        FROM autonomy_job_queue
        WHERE state = 'queued' AND (scheduled_at IS NULL OR scheduled_at <= NOW())
        ORDER BY priority ASC, scheduled_at ASC NULLS FIRST, id ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
        """
    )).mappings().first()
    if not job:
        return None

    # per-user concurrency check
    settings = _get_settings()
    if job["user_id"]:
        if _running_for_user(session, job["user_id"]) >= int(getattr(settings, "v2_job_concurrency_per_user", 2)):
            return None  # leave queued; another worker can try later

    session.execute(text(
        "UPDATE autonomy_job_queue SET state='running', locked_by=:host, locked_at=NOW() WHERE id=:id"
    ), {"host": socket.gethostname(), "id": job["id"]})
    return dict(job)


def _requeue(session, job_id: int, attempts: int, backoff_seconds: float) -> None:
    session.execute(text(
        "UPDATE autonomy_job_queue SET state='queued', attempts=:a, scheduled_at=NOW() + (:d || ' seconds')::interval WHERE id=:id"
    ), {"a": attempts, "d": backoff_seconds, "id": job_id})


def _finalize(session, job_id: int, new_state: str) -> None:
    session.execute(text(
        "UPDATE autonomy_job_queue SET state=:s WHERE id=:id"
    ), {"s": new_state, "id": job_id})


def _episodic_log(run_id: str, content: Dict[str, Any]) -> None:
    try:
        import asyncio
        asyncio.get_event_loop().run_until_complete(EpisodicRepo(run_id=run_id).append({
            "run_id": run_id,
            "role": "note",
            "content": content,
        }))
    except Exception:
        pass


def process_once() -> bool:
    """Claim and process a single job. Returns True if a job was processed."""
    dbm = _get_db_manager()
    with dbm.get_db_context() as session:
        job = _claim_next(session)
        if not job:
            return False
        run_id = job["run_id"]
        payload = job.get("payload") or {}
        desired_route = payload.get("route") or "act"
        _episodic_log(run_id, {"event": "job_claimed", "job_id": job["id"], "journey": job["journey"]})
        try:
            out_state = resume_run(run_id, route=desired_route)
            route = (out_state.route or "").lower()
            if route == "turnitin_pause":
                _finalize(session, job["id"], "waiting_human")
                _episodic_log(run_id, {"event": "job_waiting_human", "job_id": job["id"]})
            elif route in ("end", "END"):
                _finalize(session, job["id"], "done")
                _episodic_log(run_id, {"event": "job_done", "job_id": job["id"]})
            else:
                _requeue(session, job["id"], attempts=job["attempts"], backoff_seconds=0.2)
                _episodic_log(run_id, {"event": "job_requeued", "job_id": job["id"], "route": route})
        except Exception as e:
            attempts = int(job["attempts"] or 0) + 1
            delay = min(30.0, (2 ** min(attempts, 5)) * 0.5)
            _requeue(session, job["id"], attempts=attempts, backoff_seconds=delay)
            _episodic_log(run_id, {"event": "job_failed_retry", "job_id": job["id"], "attempts": attempts, "error": str(e)})
        return True


def main() -> None:
    poll_interval = float(os.getenv("AUTONOMY_WORKER_POLL", "0.5"))
    while True:
        try:
            processed = process_once()
            if not processed:
                time.sleep(poll_interval)
        except Exception as outer:
            logger.warning(f"Worker loop error: {outer}")
            time.sleep(1.0)


if __name__ == "__main__":
    main()
