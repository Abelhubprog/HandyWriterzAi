import os
import asyncio
from typing import Dict, Any, List, Optional

from .celery_app import app


async def _run_trace(
    trace_id: str,
    prompt: str,
    mode: str,
    file_ids: List[str],
    user_params: Optional[Dict[str, Any]],
    user_id: str,
):
    from src.services.sse_service import get_sse_service
    from src.services.file_content_service import get_file_content_service
    from src.services.embedding_service import get_embedding_service
    from src.agent.routing.unified_processor import UnifiedProcessor  # noqa

    sse = get_sse_service()
    fsvc = get_file_content_service()
    files: List[Dict[str, Any]] = []

    try:
        if file_ids:
            await sse.publish_workflow_progress(trace_id, {"type": "files:status", "status": "processing_files"})
            loaded = await fsvc.load_file_contents(file_ids)
            files = [
                {
                    "file_id": f.file_id,
                    "filename": f.filename,
                    "content": f.content,
                    "mime_type": f.mime_type,
                    "size": f.size,
                    "error": f.error,
                }
                for f in loaded
            ]

            # Add a compact header to the message to boost retrieval in early steps
            header = fsvc.format_files_for_prompt(loaded)
            prompt = f"{header}\n\n{prompt}"

            # Lightweight retrieval to prepend useful quotes
            try:
                esvc = get_embedding_service()
                query_emb = await esvc.embed_text(prompt)
                candidates: List[Dict[str, Any]] = []
                for f in loaded:
                    if f.error or not f.content:
                        continue
                    paras = [p.strip() for p in f.content.split("\n\n") if len(p.strip()) > 200][:30]
                    for p in paras[:200]:
                        candidates.append({"text": p[:1200], "file": f.filename})
                # Embed sequentially to keep it simple
                cand_embeddings: List[List[float]] = []
                for c in candidates:
                    emb = await esvc.embed_text(c["text"])
                    cand_embeddings.append(emb)
                sims = esvc.find_most_similar(query_emb, cand_embeddings, top_k=min(8, len(candidates)))
                top_quotes = []
                for idx, score in sims:
                    c = candidates[idx]
                    top_quotes.append(f"[source: {c['file']}, score: {score:.3f}]\n{c['text']}")
                if top_quotes:
                    quotes_block = "\n\n".join(top_quotes)
                    prompt = f"=== Retrieved Quotes (Top Matches) ===\n{quotes_block}\n\n{prompt}"
            except Exception:
                pass

            await sse.publish_workflow_progress(trace_id, {"type": "files:status", "status": "files_processed", "extra": {"count": len(loaded)}})
    except Exception as e:
        try:
            await sse.publish_workflow_progress(trace_id, {"type": "files:status", "status": "file_processing_error", "extra": {"error": str(e)}})
        except Exception:
            pass

    processor = UnifiedProcessor(simple_available=False, advanced_available=True)
    try:
        await processor.process_message(
            message=prompt,
            files=files,
            user_params=user_params or {},
            user_id=user_id,
            conversation_id=trace_id,
        )
    except Exception:
        # Errors are already emitted via SSE by processor
        pass


@app.task(name="src.workers.trace_worker.process_trace")
def process_trace_task(
    trace_id: str,
    request: Dict[str, Any],
    user: Optional[Dict[str, Any]] = None,
):
    """Celery task entrypoint to process a chat trace asynchronously."""
    prompt = request.get("prompt") or ""
    mode = request.get("mode") or "general"
    file_ids = request.get("file_ids") or []
    user_params = request.get("user_params") or {}
    user_id = str((user or {}).get("id") or (user or {}).get("user_id") or "anonymous")

    asyncio.run(_run_trace(trace_id, prompt, mode, file_ids, user_params, user_id))

