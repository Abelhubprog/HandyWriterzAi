from typing import Any, Dict, Optional, List
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _get_db_manager():
    try:
        from backend.src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception as e:  # pragma: no cover
        logger.warning(f"SemanticRepo DB unavailable: {e}")
        return None


class SemanticRepo:
    """Semantic notes storage backed by autonomy_semantic_notes.

    Embedding optional for first pass: we store note text; embeddings can be added later.
    """

    async def distill(self, run_id: str, notes: str = "") -> Optional[int]:
        run_id = str(run_id or "")
        if not notes:
            return None
        dbm = _get_db_manager()
        if dbm is None:
            return None
        try:
            with dbm.get_db_context() as session:
                # Idempotent insert: skip if identical exists
                q = session.execute(text(
                    "SELECT id FROM autonomy_semantic_notes WHERE run_id=:r AND note=:n ORDER BY created_at DESC LIMIT 1"
                ), {"r": run_id, "n": notes})
                row = q.fetchone()
                if row:
                    return int(row[0])
                q2 = session.execute(text(
                    "INSERT INTO autonomy_semantic_notes (run_id, note) VALUES (:r, :n) RETURNING id"
                ), {"r": run_id, "n": notes})
                row2 = q2.fetchone()
                return int(row2[0]) if row2 else None
        except Exception as e:  # pragma: no cover
            logger.debug(f"semantic.distill failed: {e}")
            return None

    async def list(self, run_id: str) -> List[Dict[str, Any]]:
        dbm = _get_db_manager()
        if dbm is None:
            return []
        try:
            with dbm.get_db_context() as session:
                q = session.execute(text(
                    "SELECT id, note, created_at FROM autonomy_semantic_notes WHERE run_id=:r ORDER BY created_at DESC"
                ), {"r": run_id})
                return [dict(row._mapping) for row in q.fetchall()]
        except Exception as e:  # pragma: no cover
            logger.debug(f"semantic.list failed: {e}")
            return []
