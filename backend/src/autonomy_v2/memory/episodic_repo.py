from typing import Any, Dict, List, Optional
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _get_db_manager():
    try:
        from backend.src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception as e:  # pragma: no cover
        logger.warning(f"EpisodicRepo DB unavailable: {e}")
        return None


class EpisodicRepo:
    """Episodic repository backed by autonomy_episodic_logs.

    Falls back to in-memory buffer if DB not available or table missing.
    """

    def __init__(self, run_id: Optional[str] = None):
        self._events: List[Dict[str, Any]] = []
        self._run_id = run_id

    async def append(self, event: Dict[str, Any]) -> None:
        # Always keep in-memory copy
        self._events.append(dict(event))

        dbm = _get_db_manager()
        if dbm is None:
            return
        try:
            with dbm.get_db_context() as session:
                payload = {
                    "run_id": event.get("run_id") or self._run_id or "",
                    "step_id": event.get("step_id"),
                    "role": event.get("role"),
                    "content": event.get("content", {}),
                }
                session.execute(text(
                    """
                    INSERT INTO autonomy_episodic_logs (run_id, step_id, role, content)
                    VALUES (:run_id, :step_id, :role, CAST(:content AS JSON))
                    """
                ), payload)
        except Exception as e:  # pragma: no cover
            logger.debug(f"episodic.append failed: {e}")

    async def list(self) -> List[Dict[str, Any]]:
        # Prefer DB if run_id present and table available; otherwise return memory copy
        if not self._run_id:
            return list(self._events)

        dbm = _get_db_manager()
        if dbm is None:
            return list(self._events)
        try:
            with dbm.get_db_context() as session:
                q = session.execute(text(
                    """
                    SELECT id, run_id, step_id, role, content, created_at
                    FROM autonomy_episodic_logs
                    WHERE run_id = :run_id
                    ORDER BY created_at ASC
                    """
                ), {"run_id": self._run_id})
                rows = q.fetchall()
                return [dict(row._mapping) for row in rows]
        except Exception as e:  # pragma: no cover
            logger.debug(f"episodic.list failed: {e}")
            return list(self._events)

    # Convenience wrappers to match prompt naming
    async def write_event(self, run_id: Optional[str], role: str, content: Dict[str, Any]) -> None:
        await self.append({
            "run_id": run_id or self._run_id or "",
            "role": role,
            "content": content,
        })

    async def list_events(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if run_id and run_id != self._run_id:
            # Temporarily switch
            orig = self._run_id
            self._run_id = run_id
            try:
                return await self.list()
            finally:
                self._run_id = orig
        return await self.list()
