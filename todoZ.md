# HandyWriterzAI — Execution Todo (Production-Ready, No Mocks)

Status codes:
- [ ] pending
- [-] in progress
- [x] done

Goal
Deliver a working end-to-end agentic system with streaming chat by aligning SSE channels, schemas, URL strategy, file ingestion visibility, and trace propagation. No placeholders.

Backend: SSE alignment and file ingestion visibility
- [ ] main.py — emit visible legacy events during file ingestion
  - In unified_chat_endpoint (after generating trace_id and before routing):
    - Publish to Redis channel `sse:{trace_id}`:
      - Start: `{ "type":"planning_started", "ts": Date.now(), "message": "Processing {len(file_ids)} files..." }`
      - Success summary after load: `{ "type":"planning_started", "ts": Date.now(), "message": "Files processed: {successful}/{total}" }`
      - Error path: `{ "type":"error", "ts": Date.now(), "message": "Failed to process files: {err}" }`
  - Rationale: Frontend currently listens exclusively to legacy channel; progress must be visible.

- [ ] unified_processor.py — guarantee legacy publish for all step/content events
  - Ensure the following go through `_publish_event` (which falls back to legacy `sse:{id}`):
    - planning_started, routing, search_started
    - writer_started, token (delta), content (text)
    - workflow_finished, done, error
  - If any writer/token events are emitted from inner nodes using the unified publisher only, mirror those via `_publish_event` or add a small legacy bridge.

- [ ] sse_unified.py — disable or mirror
  - If `FEATURE_SSE_PUBLISHER_UNIFIED` is on, enable double-publish to `sse:{trace_id}` using a legacy JSON mapper (token/content/steps).
  - Otherwise, keep unified publisher disabled until after stabilization.

- [ ] stream endpoint remains legacy
  - Keep `/api/stream/{conversation_id}` subscribed to `sse:{conversation_id}`.
  - Do not switch to unified channel until the adapter is implemented.

Frontend: Transport unification and tolerant parsing
- [ ] useStream.ts — switch to server-side proxy (no CORS)
  - Change SSE URL to relative: `const sseUrl = \`/api/chat/stream/${traceId}\`;`
  - Remove `NEXT_PUBLIC_API_BASE_URL` usage for SSE.
  - Defensive parsing:
    - If event type is `'content'` and `data.text` is missing but `data.content` exists, treat `data.content` as `text`.
    - Always flush buffer on `'workflow_finished'`, `'done'`, `'error'` to clear spinner and close stream.

- [ ] Chat send flow — ensure trace_id propagation
  - When calling POST `/api/chat` (via Next.js proxy route if available), extract `result.trace_id || result.conversation_id`.
  - Pass the traceId into `useStream(traceId)` and store it in component/UI state.

- [ ] Verify actual chat component path/imports
  - Locate the rendered chat UI component (current file paths under `frontend/src/components/chat/` or equivalent).
  - Fix any broken imports (e.g., `ChatPane.tsx` references) to avoid runtime page failures.

Operations: End-to-end validation (no mocks)
- [ ] CLI validation (backend only)
  - Upload: `curl -F "files=@README.md" http://localhost:8000/api/files`
  - Chat: `curl -H "Content-Type: application/json" -d '{"prompt":"Write an abstract about ...","mode":"general","file_ids":["ID"],"user_params":{}}' http://localhost:8000/api/chat`
  - Stream: `curl http://localhost:8000/api/stream/{trace_id}`
  - Expect order: `planning_started → search_started → token/content → workflow_finished/done`

- [ ] Frontend validation (via Next.js proxy)
  - Set `BACKEND_URL=http://localhost:8000` for frontend server runtime.
  - Submit prompt with and without files.
  - Expect:
    - “Processing…” shows briefly.
    - Streaming text accumulates.
    - Terminal event clears spinner.
    - Sources/cost updates show when emitted.

Hardening & Observability
- [ ] Error must clear spinner
  - Ensure all failure paths publish a legacy `{ "type":"error", "message":"..." }` on the same `sse:{trace_id}` channel.

- [ ] Structured logging
  - Log correlation_id/trace_id on:
    - POST `/api/chat` acceptance
    - First SSE publish for the request
    - Stream subscribe/unsubscribe in the backend

- [ ] Budget guard UX
  - On budget errors, publish a legacy `error` event before returning JSON response to avoid a hanging UI.

Post-stabilization (optional, after green)
- [ ] Adapter at stream endpoint for unified channel
  - Subscribe to `sse:unified:{id}` and down-convert to legacy JSON for the browser.
  - Keep legacy publish for a transition period.

- [ ] Migrate the hook to unified schema
  - Parse unified SSEEvent directly: `event_type`, `data.content`, etc.
  - Retire legacy schema and channels once verified.

Acceptance Criteria
- End-to-end streaming works for file and non-file prompts.
- No CORS or ECONNREFUSED in browser console due to proxy path usage.
- Consistent `trace_id` from POST to streaming subscription.
- Visible parsing steps and progressive token/content accumulation.
- Deterministic terminal events that stop the stream and clear UI state.
