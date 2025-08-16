from fastapi import APIRouter
import json
import uuid as _uuid
import io, csv
from datetime import datetime

try:
    from src.db.database import db_manager  # type: ignore
    from src.db.models import TimelineEventModel  # type: ignore
except Exception:
    db_manager = None  # type: ignore
    TimelineEventModel = None  # type: ignore

router = APIRouter(prefix="/api/stream", tags=["stream"])


@router.get("/{conversation_id}/history")
async def get_history(conversation_id: str, limit: int = 500, offset: int = 0):
    if not (db_manager and TimelineEventModel):
        return {"conversation_id": conversation_id, "events": []}
    try:
        conv_uuid = _uuid.UUID(conversation_id)
    except Exception:
        return {"conversation_id": conversation_id, "events": []}
    try:
        with db_manager.get_db_context() as db:
            q = db.query(TimelineEventModel).filter(TimelineEventModel.conversation_id == conv_uuid)
            q = q.order_by(TimelineEventModel.ts.asc(), TimelineEventModel.created_at.asc())
            if offset:
                q = q.offset(max(0, int(offset)))
            if limit:
                q = q.limit(max(1, min(int(limit), 2000)))
            rows = q.all()
            events = []
            for r in rows:
                try:
                    payload = r.payload or {}
                    if isinstance(payload, str):
                        obj = json.loads(payload)
                    else:
                        obj = dict(payload)
                    if 'conversation_id' not in obj:
                        obj['conversation_id'] = conversation_id
                    events.append(obj)
                except Exception:
                    events.append({
                        "type": r.type,
                        "agent": r.agent,
                        "node": r.node,
                        "ts": r.ts.timestamp() if r.ts else None,
                        "conversation_id": conversation_id,
                    })
        return {"conversation_id": conversation_id, "events": events}
    except Exception:
        return {"conversation_id": conversation_id, "events": []}


@router.get("/{conversation_id}/sources.csv")
async def export_sources_csv(conversation_id: str):
    from fastapi.responses import PlainTextResponse
    if not (db_manager and TimelineEventModel):
        return PlainTextResponse("title,url,confidence,agent\n", media_type="text/csv")
    try:
        conv_uuid = _uuid.UUID(conversation_id)
    except Exception:
        return PlainTextResponse("title,url,confidence,agent\n", media_type="text/csv")
    try:
        with db_manager.get_db_context() as db:
            q = db.query(TimelineEventModel).filter(TimelineEventModel.conversation_id == conv_uuid)
            q = q.order_by(TimelineEventModel.ts.asc())
            rows = q.all()
        items = []
        for r in rows:
            try:
                p = r.payload if isinstance(r.payload, dict) else json.loads(r.payload)
            except Exception:
                p = {}
            t = (p.get('type') or r.type or '').lower()
            if t == 'agent:tool':
                agent = p.get('agent') or r.agent
                url = p.get('url')
                title = p.get('result') or p.get('title')
                conf = p.get('confidence')
                if title or url:
                    items.append((title or '', url or '', conf, agent or ''))
            elif t == 'sources_update' and isinstance(p.get('sources'), list):
                for s in p['sources']:
                    title = s.get('title') or s.get('snippet') or s.get('url') or 'source'
                    url = s.get('url')
                    conf = s.get('confidence')
                    items.append((title or '', url or '', conf, 'retriever'))
        seen = set()
        dedup = []
        for title, url, conf, agent in items:
            key = (url, title)
            if key in seen:
                continue
            seen.add(key)
            dedup.append((title, url, conf, agent))
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(['title','url','confidence','agent'])
        for title, url, conf, agent in dedup:
            writer.writerow([title, url, '' if conf is None else f"{float(conf):.2f}", agent])
        data = buf.getvalue()
        return PlainTextResponse(data, media_type='text/csv')
    except Exception:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("title,url,confidence,agent\n", media_type='text/csv')
