# HandyWriterzAI — Production-Ready Stabilization Plan

Objective
Deliver a fully working agentic system with a functioning chat interface and real-time streaming, using only production-grade implementations (no mocks/stubs). This plan aligns backend SSE emission, stream transport, and frontend consumption into one coherent, tested pipeline, and fixes file-ingestion and orchestration handoff issues.

Strategic Decision (to get to green quickly)
- Canonical SSE channel: legacy Redis channel sse:{trace_id}
- Canonical SSE schema: legacy event shapes already handled by the frontend hook
  - token: { type: "token", delta: string }
  - content: { type: "content", text: string }
  - step markers: planning_started, search_started, search_progress, sources_update, verify_started, writer_started, evaluator_started, formatter_started, cost_update, workflow_finished, done, error
- Canonical transport: Frontend uses Next.js server-side proxy routes (no direct browser→backend CORS). The proxy hits BACKEND_URL from server runtime.
- Trace flow: POST /api/chat returns trace_id; UI MUST pass that trace_id to the streaming hook.

Why this decision
- Minimal diffs: backend already publishes legacy events in multiple places and the stream endpoint subscribes to sse:{trace_id}.
- Frontend hook already parses legacy events; we avoid re-plumbing the whole UI.
- Using the Next.js server-side SSE proxy removes CORS misconfigs and environment drift between browser and server.

Core Problems (diagnosed)
1) Split-brain SSE channels
- Unified SSE publisher emits to sse:unified:{id} and optionally sse:legacy:{id}; stream endpoint listens only to sse:{id}.
- Result: crucial events (e.g., file_processing) are invisible to client.

2) Event payload mismatch
- Unified publisher emits { event_type, data: { content } }, but hook expects legacy { type: "content", text } or { type: "token", delta }.
- Result: even if events arrive, the hook ignores them; perceived “stuck” UI.

3) Dual URL strategies (CORS drift)
- Hook uses NEXT_PUBLIC_API_BASE_URL (direct browser→backend); server route uses BACKEND_URL. If hosts/ports/protocol differ, connections fail or are blocked.
- Result: ECONNREFUSED/CORS; user sees “Processing…” forever.

4) Trace propagation fragility
- Chat POST returns trace_id; UI must connect to SSE with the same id. Any break in propagation yields an empty stream.

5) File processing events bypass legacy channel
- main.py emits FILE_PROCESSING via unified publisher. If not mirrored into sse:{id}, no visible “parsing files” step.

6) Potential missing/renamed chat component
- Referenced ChatPane.tsx not found at expected path; this can cause runtime/import issues and page-level failures.

Backlog: Long-term unification (post-stabilization)
- Migrate to Unified SSE schema end-to-end with an adapter at the stream endpoint to down-convert to legacy event shapes (or update hook to native unified schema).
- Consolidate env resolution into one source (server-only), passing resolved URLs to client via config endpoint.

Implementation Plan (production-ready)

A. Backend SSE and event schema alignment
A1) Ensure all published events are mirrored to sse:{trace_id} in legacy shape:
- In any place that uses get_sse_publisher().publish_event(...), add a parallel legacy publish:
  - channel = f"sse:{trace_id}"
  - payload = canonical legacy JSON ({ type, ... })
- UnifiedProcessor already has _publish_event that falls back to legacy sse:{id}. Confirm it’s used consistently for planning_started, routing, search_started, writer_started, token/content, workflow_finished, done, error.

A2) Initialize unified publisher only if required, with feature flag:
- If unified publisher remains enabled, set a double-publish flag that mirrors to sse:{trace_id} with legacy schema. Otherwise, keep unified publisher disabled until the migration.

A3) Guarantee error events always arrive on legacy channel:
- Any exception path publishes { type: "error", message } to sse:{trace_id}.

A4) File processing events path:
- For file ingestion in unified_chat_endpoint, after using file_content_service, publish a legacy “planning_started” or “parsing_files” event on sse:{trace_id}, including counts. If using unified publisher too, send both.

B. Frontend transport unification
B1) Make the hook connect via Next.js proxy:
- Update useStream to connect to relative /api/chat/stream/${traceId} (internal route). Remove direct usage of NEXT_PUBLIC_API_BASE_URL for SSE.
- The proxy [frontend/src/app/api/chat/stream/[traceId]/route.ts] will fetch BACKEND_URL/api/stream/${traceId} and pipe bytes to the browser.

B2) Keep direct POST /api/chat on the Next.js server proxy side (if present) to standardize env resolution and return a guaranteed trace_id.

B3) Enforce single env source:
- BACKEND_URL used only on server (route handlers). Client avoids touching backend origin to eliminate CORS risk.

C. Event parsing fixes in hook
C1) Honor both token and content:
- token: append delta to buffer
- content: append text to buffer
- Ensure flushing on workflow_finished/done/error
- Maintain sources_update and cost_update cases.

C2) Back-compat tolerant:
- If a message has data.content instead of text (in case of accidental unified event), map it to text. This is a small guard to avoid hard failures.

D. Trace_id propagation
D1) Ensure the chat send code captures trace_id or conversation_id from backend POST and passes it into useStream(traceId).
D2) Store traceId in UI state for page reload resilience.

E. Verification suite (no mocks)
E1) CLI checks:
- curl -F "files=@README.md" http://localhost:8000/api/files → returns file_ids
- curl -H "Content-Type: application/json" -d '{"prompt":"Write an abstract...","mode":"general","file_ids":["..."],"user_params":{}}' http://localhost:8000/api/chat → {"trace_id": "..."}
- curl http://localhost:8000/api/stream/{trace_id} → see planning_started → search_started → token/content → workflow_finished/done

E2) Frontend checks:
- Start dev servers; open chat; submit prompt; verify:
  - “Processing…” shows briefly
  - Streaming text appears and grows
  - Terminal event clears the spinner
  - Sources/cost update entries render when emitted

F. Hardening (production)
F1) Backpressure and dropped events:
- Keep queue size reasonable (unified publisher). As we’re using legacy Redis pub/sub for now, ensure events are small and frequent rather than huge.

F2) Error boundary in UI:
- If SSE errors, show “Connection lost. Retrying…” and allow manual retry.

F3) Observability:
- Log correlation_id/trace_id consistently. Add structured logs around SSE open/close and publish failures.

File-by-file Changes (high-level)

Backend
- backend/src/main.py
  - In unified_chat_endpoint: after loading files, publish a legacy event to sse:{trace_id}:
    { type: "planning_started", ts: Date.now(), message:"Processing X files..." }
  - Ensure try/except around file loading publishes { type:"error", message } legacy event on the same channel.
  - SSE endpoint remains subscribed to sse:{conversation_id} (legacy).

- backend/src/agent/routing/unified_processor.py
  - Confirm _publish_event always hits sse:{id} with legacy payloads (it does). Ensure writer_started, token, content, workflow_finished, done paths route through _publish_event.
  - If any internal nodes publish via unified publisher only, either route them through _publish_event or mirror them.

- backend/src/agent/sse_unified.py
  - Optionally set feature flag to disable unified publisher for now, or enable double-publish with legacy mirror formatter. Avoid changing stream endpoint to unified channel until post-stabilization.

Frontend
- frontend/src/hooks/useStream.ts
  - Use relative SSE URL: /api/chat/stream/${traceId}
  - Add small guard: if (data.type === "content" && !data.text && data.content) treat data.content as text (defensive).
  - Ensure finalization: on workflow_finished/done/error flush buffer and close.

- frontend/src/app/api/chat/stream/[traceId]/route.ts
  - Keep as-is; ensure BACKEND_URL is correctly set in env for server runtime.

- Chat sending code (e.g., frontend/src/services/advancedApiClient.ts or route proxies)
  - Verify it POSTs to /api/chat (proxy), extracts trace_id (or conversation_id fallback), and passes it to UI.

Risk Assessment
- Low risk: We align with existing legacy path. Migrations to unified schema can be handled later with an adapter layer.
- High test value: curl + browser checks confirm the complete pipeline.

Cutover Steps (operators)
1) Set env:
   BACKEND_URL=http://localhost:8000
   (No need for NEXT_PUBLIC_API_BASE_URL for streaming.)
2) Start Redis and backend; then Next.js.
3) Upload a file; POST /api/chat; stream /api/stream/{trace_id}.
4) Use the app; confirm UI streaming.

Post-Green Enhancements (optional)
- Add an adapter in stream endpoint to subscribe to sse:unified:{id} and down-convert to legacy for the browser.
- Eventually update the hook to parse unified SSEEvent natively and remove legacy support.

Deliverables created in this plan
- todoZ.md with a sequenced, production-ready task list, including exact edits and validation commands.
