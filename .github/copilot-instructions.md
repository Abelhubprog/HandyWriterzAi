## HandyWriterz AI — Copilot Instructions (for coding agents)

This codebase is a FastAPI + Next.js multi‑agent writer with real‑time SSE streaming. Follow these repo‑specific rules to ship safe, minimal patches fast.

Architecture and routing
- Multi‑agent graph: backend/src/agent/handywriterz_graph.py (LangGraph). Nodes must publish via SSEService only.
- Intelligent router: backend/src/agent/routing/{unified_processor.py, complexity_analyzer.py}. ComplexityAnalyzer scores; UnifiedProcessor orchestrates and streams.
- Model access: backend/src/models/factory.py is the single factory for LLM calls—don’t import providers directly.

Chat + streaming flow
- POST /api/chat → returns { status: "accepted", trace_id } and schedules UnifiedProcessor.process_message(..., conversation_id=trace_id). See backend/src/routes/chat_gateway.py.
- GET /api/stream/{trace_id} → canonical SSE in backend/src/routes/stream.py (sse_starlette.EventSourceResponse).
- Publisher: backend/src/services/sse_service.py is the only emitter. Do not call redis.publish from agents/services; use agent/base.py helpers where present.
- Envelope (standard):
	- Fields: { type, ts, conversation_id, seq?, token?, content?, source?, meta?, error? }
	- Types: "start" | "token" | "content" | "progress" | "done" | "error" | "heartbeat"
	- Example: { "type":"token", "ts":"2025-08-10T12:00:00Z", "conversation_id":"<cid>", "seq":42, "token":"text", "source":"writer", "meta":{}}

Frontend integration
- EventSource(`/api/stream/${traceId}`) via frontend/src/hooks/useStream.ts. Components (e.g., ChatPane.tsx) assume heartbeats and small payloads.
- The UI expects a quick /api/chat response with trace_id, then continuous token/content events until a final "done".

Local development
- VS Code tasks: Run Both (Frontend + Backend) starts pnpm dev (frontend) and python start_server.py (backend).
- Manual: frontend: pnpm dev; backend (from backend/): python start_server.py or uvicorn src.main:app --reload.
- Env: backend/.env and frontend/.env.local must be present (DB, Redis, OpenAI/Anthropic/Gemini/Perplexity keys).

Testing and debugging
- Backend tests: backend/src/tests; run `python -m pytest backend/src/tests -q`.
- SSE: open /api/stream/{trace_id}; check SSEService heartbeats; backend/src/main.py wires health/startup/shutdown.
- Routing: log ComplexityAnalyzer scores; ensure UnifiedProcessor emits start/progress/token/content/done.

Conventions and guardrails
- Single‑source SSE: emit only via SSEService; remove/avoid any direct Redis pub/sub.
- Keep the event envelope stable; update frontend hook parsing if fields change.
- Prefer backend/src/agent/... routing/types; avoid ad‑hoc provider imports—use models/factory.py.
- File uploads/RAG exist; respect size limits and service contracts before extending.

Do/Don’t (SSE publishing)
- Do: from backend/src/services/sse_service.py use SSEService.emit(cid, payload) or agent/base.py helpers.
- Don’t: import or call Redis publish directly from agents/services.

Key files
- Backend: routes/stream.py, routes/chat_gateway.py, services/sse_service.py, agent/handywriterz_graph.py, agent/routing/{unified_processor.py, complexity_analyzer.py}, main.py.
- Frontend: hooks/useStream.ts, components/ChatPane.tsx, store/useChatStore.ts.

Acceptance (happy path)
- POST /api/chat returns a trace_id quickly; UI connects to /api/stream/{trace_id}; heartbeats + token/content stream; final "done" event received.

If anything here diverges from code, prefer the code. Note mismatches in AGENTS.md and align both sides promptly.
