from typing import Any, Dict, List, Optional
import logging
import asyncio
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _get_db_manager():
    try:
        from backend.src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception:
        return None


def _get_settings():
    try:
        from backend.src.config import get_settings  # type: ignore
        return get_settings()
    except Exception:
        class _S: skip_ai_calls = True
        return _S()


class VectorRepo:
    """Vector storage adapter with graceful fallbacks.

    Primary path uses embedding_service + vector_storage evidence store.
    Fallback path stores notes in autonomy_semantic_notes and does naive search.
    """

    def __init__(self, run_id: str):
        self.run_id = run_id

    def _supports_vectors(self) -> bool:
        s = _get_settings()
        if getattr(s, "skip_ai_calls", False):
            return False
        try:
            # Quick import check
            from src.services.embedding_service import RevolutionaryEmbeddingService  # type: ignore
            from src.services.vector_storage import get_vector_storage  # type: ignore
            return True
        except Exception:
            return False

    async def upsert_chunks(self, chunks: List[Dict[str, str]]) -> None:
        texts = [c.get("text", "") for c in chunks]
        urls = [c.get("url", "") for c in chunks]
        if self._supports_vectors():
            try:
                from backend.src.services.embedding_service import RevolutionaryEmbeddingService  # type: ignore
                from backend.src.services.vector_storage import get_vector_storage  # type: ignore
                es = RevolutionaryEmbeddingService()
                embeddings = await es.embed_batch(texts)
                evidence_data = [{"text": t, "source_id": u} for t, u in zip(texts, urls)]
                vs = get_vector_storage()
                await vs.store_evidence_vectors(self.run_id, evidence_data, embeddings)
                return
            except Exception as e:  # pragma: no cover
                logger.debug(f"vector upsert fallback: {e}")

        # Fallback: store as semantic notes (idempotent)
        dbm = _get_db_manager()
        if dbm is None:
            return
        try:
            with dbm.get_db_context() as session:
                for t, u in zip(texts, urls):
                    note = f"{u}|||{t}"
                    q = session.execute(text(
                        "SELECT id FROM autonomy_semantic_notes WHERE run_id=:r AND note=:n LIMIT 1"
                    ), {"r": self.run_id, "n": note})
                    if q.fetchone():
                        continue
                    session.execute(text(
                        "INSERT INTO autonomy_semantic_notes (run_id, note) VALUES (:r, :n)"
                    ), {"r": self.run_id, "n": note})
        except Exception as e:  # pragma: no cover
            logger.debug(f"semantic fallback upsert failed: {e}")

    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self._supports_vectors():
            try:
                from backend.src.services.embedding_service import RevolutionaryEmbeddingService  # type: ignore
                from backend.src.services.vector_storage import get_vector_storage  # type: ignore
                es = RevolutionaryEmbeddingService()
                qemb = await es.embed_text(query)
                vs = get_vector_storage()
                results = await vs.find_similar_evidence(qemb, conversation_id=self.run_id, limit=k)
                out: List[Dict[str, Any]] = []
                for r in results:
                    out.append({
                        "text": r.get("evidence_text", ""),
                        "url": r.get("source_id"),
                        "score": float(r.get("semantic_similarity", 0.0))
                    })
                return out
            except Exception as e:  # pragma: no cover
                logger.debug(f"vector search fallback: {e}")

        # Fallback: naive search over semantic_notes rows
        dbm = _get_db_manager()
        if dbm is None:
            return []
        try:
            with dbm.get_db_context() as session:
                q = session.execute(text(
                    "SELECT note FROM autonomy_semantic_notes WHERE run_id=:r ORDER BY created_at DESC LIMIT 200"
                ), {"r": self.run_id})
                rows = [row[0] for row in q.fetchall()]
                results: List[Dict[str, Any]] = []
                for note in rows:
                    if "|||" in note:
                        url, txt = note.split("|||", 1)
                    else:
                        url, txt = "", note
                    score = 1.0 if query.lower() in txt.lower() else 0.2
                    results.append({"text": txt, "url": url, "score": score})
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:k]
        except Exception as e:  # pragma: no cover
            logger.debug(f"naive search failed: {e}")
            return []
