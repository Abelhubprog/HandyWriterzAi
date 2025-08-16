
# AGENTS.md — HandyWriterzAI (Codex CLI)

Last updated: 2025-08-09 12:33 UTC

## Mission
Ship a working end-to-end multi-agent experience in dev:
1) `POST /api/chat` → returns `trace_id`
2) UI opens EventSource to `/api/stream/{trace_id}`
3) Agents stream tokens + progress via one publisher
4) Files pipeline (upload → embed → retrieve quote)
5) UI renders smoothly with progress + error handling

Default model: **gpt-5**.

## Current status (from recent Codex work)
- Canonical SSE lives in `routes/stream.py`; legacy stream in `main.py` removed; `/health/ready` added.
- Nodes refactored to use **SSEService**; direct `redis.publish` removed across writer, writer_migrated, turnitin_advanced, tutor_feedback_loop, user_intent, base.
- `stream.py` injects `conversation_id`, normalizes payloads, heartbeat enabled; pure normalizer covered by tests.
- Frontend `useStream.ts` targets `/api/stream/{cid}`, minimal envelope, ProgressChips + heartbeat dot + error overlay.

## Known gaps to fix next
- **ChatInit incomplete** in `routes/chat_gateway.py`: need `trace_id` generation, safe imports, correct background task call, and `{ "status": "accepted", "trace_id": "..." }` response.
- **Tests**: sandbox read-only blocked pytest; add local `pytest.ini` and route tmp/cache into repo to run in WSL.
- **Files→RAG**: wire `FileContentService` + `EmbeddingService` to vector store; expose retrieval in writer.
- **Frontend**: ensure Next.js proxy posts to `/api/chat`, consumes `trace_id`, then opens `/api/stream/{trace_id}`.

## Roles
- **Backend Surgeon** — finish ChatInit, readiness, SSE envelopes.
- **Frontend Integrator** — align hooks/components with envelope; add retry UX.
- **File Pipeline Engineer** — wire R2/pgvector round-trip + retrieval in writer.
- **QA Engineer** — unit + Playwright prompt → stream → export.
- **Ops** — health checks + CI.

## Guardrails
- Small patches; show plan before edits.
- Single event envelope: `{type, ts, conversation_id, content?, token?, source?, meta?}`.
- No direct `redis.publish` in business code — only **SSEService** wrappers.
- Heartbeat ~20s; small replay buffer; graceful disconnects; no silent excepts.

## Acceptance checks
- `POST /api/chat` returns `trace_id` and starts background processing.
- `/api/stream/{trace_id}` streams minimal envelope with heartbeats; UI renders tokens.
- Upload → embed → retrieve quoted snippet in final text.
- `/health/ready` returns `{"redis":"ok","db":"ok","version":"<sha>"} in <150ms.
