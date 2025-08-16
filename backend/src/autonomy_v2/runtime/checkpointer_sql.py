"""SQL checkpointer for Autonomy V2.

Persists GraphState payloads in autonomy_checkpoints using the existing
DatabaseManager (backend/src/db/database.py). Designed to be import-safe and
to no-op gracefully if tables are missing.
"""

from typing import Any, Optional
import json
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _get_db_manager():
    try:
        from backend.src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception as e:  # pragma: no cover
        logger.warning(f"Autonomy V2 checkpointer DB unavailable: {e}")
        return None


class _SQLCheckpointer:
    def get(self, run_id: str) -> Optional[dict]:
        dbm = _get_db_manager()
        if dbm is None:
            return None
        try:
            with dbm.get_db_context() as session:
                q = session.execute(text(
                    "SELECT payload FROM autonomy_checkpoints WHERE run_id = :run_id"
                ), {"run_id": run_id})
                row = q.fetchone()
                return dict(row._mapping)["payload"] if row else None
        except Exception as e:  # pragma: no cover - safe fallback
            logger.debug(f"checkpointer.get failed: {e}")
            return None

    def put(self, run_id: str, payload: dict) -> None:
        dbm = _get_db_manager()
        if dbm is None:
            return None
        try:
            with dbm.get_db_context() as session:
                # Upsert-like behavior (Postgres) with fallback to delete+insert
                dialect = session.bind.dialect.name if session.bind else ""
                if dialect == "postgresql":
                    session.execute(text(
                        """
                        INSERT INTO autonomy_checkpoints (run_id, payload, updated_at)
                        VALUES (:run_id, CAST(:payload AS JSONB), NOW())
                        ON CONFLICT (run_id) DO UPDATE SET payload = EXCLUDED.payload, updated_at = NOW()
                        """
                    ), {"run_id": run_id, "payload": json.dumps(payload)})
                else:
                    # Portable fallback
                    session.execute(text("DELETE FROM autonomy_checkpoints WHERE run_id = :run_id"), {"run_id": run_id})
                    session.execute(text(
                        "INSERT INTO autonomy_checkpoints (run_id, payload) VALUES (:run_id, :payload)"
                    ), {"run_id": run_id, "payload": json.dumps(payload)})
        except Exception as e:  # pragma: no cover - safe fallback
            logger.debug(f"checkpointer.put failed: {e}")
            return None


def sql_checkpointer() -> Any:
    return _SQLCheckpointer()


def seed(run_id: str, state_payload: dict) -> None:
    """Upsert initial checkpoint payload for a run."""
    cp = sql_checkpointer()
    cp.put(run_id, state_payload)
