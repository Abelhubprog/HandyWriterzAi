# intel1 — Decisions, Assumptions, Risks for Phase 1

This document captures key decisions, underlying assumptions, and identified risks supporting the Phase 1 plan in [todoNEW.md](todoNEW.md:1).

## Decisions

1) Single SSE channel and envelope
- Decision
  - Use only Redis channel sse:{conversation_id} as the canonical stream for the main UI.
  - Define a minimal but typed envelope enforced at the publisher layer (SSEService).
- Rationale
  - The FastAPI stream endpoint already subscribes to sse:{cid}. Aligning all publishers avoids race conditions and remove ambiguity.
- Impacted files
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:1)
  - [backend/src/main.py](backend/src/main.py:1)
  - [backend/src/agent/routing/unified_processor.py](backend/src/agent/routing/unified_processor.py:1)
  - [backend/src/agent/nodes/writer.py](backend/src/agent/nodes/writer.py:1)
  - [backend/src/agent/nodes/planner.py](backend/src/agent/nodes/planner.py:1)
  - [backend/src/schemas/sse_events.py](backend/src/schemas/sse_events.py:1)

2) SSE unified publisher component remains auxiliary
- Decision
  - Keep [backend/src/agent/sse_unified.py](backend/src/agent/sse_unified.py:1) initialized but not required by the main pathway. It may mirror to the legacy channel or be disabled later.
- Rationale
  - Minimizes scope while preserving a migration path if the frontend later adopts a dedicated “unified” topic.

3) Normalization centralized at /api/chat
- Decision
  - Perform normalization and validation in the /api/chat endpoint; skip re-normalization in UnifiedProcessor when _normalization_meta is present.
- Rationale
  - Single source of truth for request shaping; avoids divergent parameter states.
- Impacted files
  - [backend/src/main.py](backend/src/main.py:1)
  - [backend/src/agent/routing/unified_processor.py](backend/src/agent/routing/unified_processor.py:1)
  - [backend/src/agent/routing/normalization.py](backend/src/agent/routing/normalization.py:1)
  - [backend/src/agent/handywriterz_state.py](backend/src/agent/handywriterz_state.py:1)

4) Thin wrappers vs direct publish in nodes
- Decision
  - Prefer adding thin wrapper methods to SSEService (publish_writer_started, publish_token, publish_content, publish_error) to minimize node code churn. Wrappers must emit the standardized envelope.
- Rationale
  - Reduces risk and patch size, improves readability for agent node authors.

5) BudgetGuard finalization event
- Decision
  - After the advanced processing completes, ensure record_usage is called with actual tokens and model where available. Emit CostEvent and MetricsEvent exactly once.
- Rationale
  - Guarantees consistent cost/metrics reporting and prevents double emission.

## Assumptions

- The main UI is currently wired to /api/stream/{conversation_id} on sse:{cid}. Moving to a different channel would require frontend changes; hence we avoid that in Phase 1.
- Redis is available and functioning in deployed environments as used by SSEService and the stream endpoint.
- Writer and Planner nodes are the primary sources of token/content events; other nodes either produce metadata or are silent on streaming.
- Normalization already contains the mapping tables for aliases to canonical enums; we will extend tests rather than rewrite the tables.
- Prompt orchestration is feature-gated and optional; its emitted events will be sent through the same envelope when enabled.

## Risks and Mitigations

1) Envelope drift between publishers and consumers
- Risk
  - Different modules could emit partial payloads (e.g., text vs content vs token).
- Mitigation
  - Centralize emission in SSEService; add unit tests enforcing envelope; final normalization remains at the endpoint for safety.

2) Double normalization or missed validation
- Risk
  - Both /api/chat and UnifiedProcessor attempt normalization leading to inconsistent states.
- Mitigation
  - Sentinel _normalization_meta; UnifiedProcessor checks presence and bypasses.

3) Token budget under/over-estimation
- Risk
  - Estimates differ significantly from actual usage, affecting budget guard behavior.
- Mitigation
  - record_usage post-run with actual tokens when available; use conservative margins in guard_request.

4) Legacy direct Redis publishes remaining in code
- Risk
  - Stray direct redis_client.publish confusing the stream.
- Mitigation
  - Search-and-remove pass; keep a single fallback path inside SSEService only.

5) E2E latency requirements
- Risk
  - “First token within 5s” fails due to model latency or initialization overhead.
- Mitigation
  - Emit early workflow_start and routing events as signals; pipeline warming at app startup; write tests that tolerate operational jitter but assert bounded behavior.

6) Planner/writer behavior divergence
- Risk
  - Wrapper methods might not cover special node metadata.
- Mitigation
  - Include meta passthrough in wrappers; extend tests with planner outline and writer phases.

## Envelope Contract (authoritative for Phase 1)

- Channel: sse:{conversation_id}
- JSON payload minimal fields
  - type: string
  - conversation_id: string
  - ts: number (ms epoch)
- Optional fields (depending on type)
  - content: string (for content messages)
  - token: string (for token-by-token)
  - is_partial: boolean (true for token/partial content)
  - source: string ("writer" | "planner" | "system" | "gateway" | "file" | ...)
  - workflow: object { phase?: string, step?: string, progress?: number }
  - routing: object
  - cost: object { model?: string, tokens?: number, input_tokens?: number, output_tokens?: number, cost_estimate?: number }
  - metrics: object
  - error: object { code?: string, message: string, details?: object }
  - meta: object

Event type suggestions
- "routing", "workflow_start", "workflow_progress", "workflow_complete"
- "token", "content"
- "file_processing_start", "file_processing_progress", "file_processing_complete"
- "cost", "metrics", "done", "error"

## Test Strategy (Phase 1 scope)

- Unit
  - SSEService envelope validation and channel selection.
  - Normalization strict mode; alias → canonical; derived fields.
  - Budget guard estimate/guard_request/record_usage.
- Integration
  - POST /api/chat with prompt, subscribe /api/stream/{cid}; assert early routing/workflow_start and at least one token or partial content within 5s; final done.
  - POST with file_ids; assert file_processing events appear.
- CI
  - GitHub Actions workflow to run unit + integration suites; cache dependencies.

## Implementation Order (Phase 1)

1) SSEService wrappers + endpoint envelope normalization confirmation.
2) Normalize at /api/chat; add sentinel bypass in UnifiedProcessor.
3) Writer/Planner refactor to SSEService wrappers.
4) Budget finalization event and tests.
5) File processing event standardization.
6) Docs: sse-envelope.md.
