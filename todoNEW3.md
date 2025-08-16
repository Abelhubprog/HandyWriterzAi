# Phase 1 — Backend/Frontend Multi‑Agent SSE + Normalization Plan

This document tracks actionable fixes with Issue → Cause → Fix, precise file:line pointers, estimates, and checkboxes. It targets a working unified SSE stream, normalized parameters, and agent node streaming alignment.

Notes:
- Line numbers are approximate anchors from the current analysis context. They will be adjusted during implementation diffs.

## Legend
- [ ] pending
- [-] in progress
- [x] done

---

## A. SSE Unification

1) [ ] Writer node uses undefined SSEService methods
- Issue
  - RevolutionaryWriterAgent calls _sse().publish_writer_started / publish_token / publish_content / publish_error which do not exist on SSEService.
- Cause
  - Historical publisher API drift; SSEService only exposes publish_event(...) and workflow/content helpers.
- Fix
  - Option A (preferred): Add thin wrappers into SSEService that conform to current event schema and forward to publish_event.
  - Option B: Refactor writer/planner nodes to call SSEService.publish_event/publish_content/workflow_* directly with standardized envelope.
- Files
  - [backend/src/agent/nodes/writer.py](backend/src/agent/nodes/writer.py:365)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:57)
- Deliverables
  - Implement wrappers OR refactor calls.
  - Add unit tests for token streaming and writer_started.
- Estimate
  - 6–8h (incl. tests)

2) [ ] Dual SSE paths (SSEService vs direct Redis; unified vs legacy channels)
- Issue
  - UnifiedProcessor publishes mainly via SSEService to sse:{cid}, but there are legacy publish paths and a separate sse_unified publisher and shim.
- Cause
  - Transitional design with both sse_unified and legacy event shapes.
- Fix
  - Route all runtime emissions via SSEService to channel sse:{conversation_id}. Keep sse_unified running but make it mirror or be no-op until frontend is updated. Remove direct redis_client.publish calls from business code (keep as last-chance fallback in SSEService).
- Files
  - [backend/src/agent/routing/unified_processor.py](backend/src/agent/routing/unified_processor.py:390)
  - [backend/src/agent/sse_unified.py](backend/src/agent/sse_unified.py:72)
  - [backend/src/agent/sse.py](backend/src/agent/sse.py:20)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:57)
- Deliverables
  - One canonical publish path + typed envelope.
  - Endpoint /api/stream remains subscribed to sse:{cid}.
- Estimate
  - 6h

3) [ ] Stream endpoint event normalization
- Issue
  - /api/stream/{conversation_id} emits flat dicts; upstream publishers mix content/text/token fields.
- Cause
  - Typed events in schemas vs legacy minimal payloads.
- Fix
  - Keep endpoint normalization, but standardize upstream events to minimal envelope: { type, conversation_id, ts, content, token?, source?, meta? }. Map token events to type: "content" with is_partial=true or type: "token".
- Files
  - [backend/src/main.py](backend/src/main.py:1682)
  - [backend/src/schemas/sse_events.py](backend/src/schemas/sse_events.py:20)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:125)
- Deliverables
  - Envelope contract documented and enforced in SSEService.
- Estimate
  - 4h (incl. tests)

---

## B. Parameter Normalization

4) [ ] Duplicate normalization and inconsistent gating
- Issue
  - Normalization runs both in /api/chat and inside UnifiedProcessor depending on feature flags.
- Cause
  - Mixed flag sources cause divergence.
- Fix
  - Centralize in /api/chat. If request contains _normalization_meta, UnifiedProcessor must not re-normalize. Otherwise UnifiedProcessor can normalize only when endpoint was bypassed (safety net).
- Files
  - [backend/src/main.py](backend/src/main.py:1568)
  - [backend/src/agent/routing/unified_processor.py](backend/src/agent/routing/unified_processor.py:176)
  - [backend/src/agent/routing/normalization.py](backend/src/agent/routing/normalization.py:254)
- Deliverables
  - Single source of truth; strict mode validation unit tests.
- Estimate
  - 5h

5) [ ] HandyWriterzState param alignment
- Issue
  - State fields must match normalized keys consumed by nodes (complexity, research_depth, target_sources, deadline, tone, audience).
- Cause
  - Drift between enums/aliases and node expectations.
- Fix
  - Ensure UserParams canonical keys mapped; add to_dict harmony and user_params_from_dict consistency.
- Files
  - [backend/src/agent/handywriterz_state.py](backend/src/agent/handywriterz_state.py:40)
  - [backend/src/agent/routing/normalization.py](backend/src/agent/routing/normalization.py:254)
- Deliverables
  - Unit tests covering alias → canonical mapping.
- Estimate
  - 4h

---

## C. Nodes and Graph

6) [ ] Writer node streaming migration
- Issue
  - Streams via non-existent methods.
- Cause
  - See A1.
- Fix
  - Replace calls with SSEService standard envelope; include phases: "planning" → "generation" → "qa" → "compliance", with workflow progress events.
- Files
  - [backend/src/agent/nodes/writer.py](backend/src/agent/nodes/writer.py:365)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:57)
- Deliverables
  - Integration test validates token arrival & final content within 5s.
- Estimate
  - Included in A1 (implementation), +2h for integration.

7) [ ] Planner node progress events
- Issue
  - Ensure planner emits consistent progress and content events compatible with /api/stream.
- Cause
  - Mixed schemas.
- Fix
  - Use SSEService workflow_start/progress/complete + content events with source="planner".
- Files
  - [backend/src/agent/nodes/planner.py](backend/src/agent/nodes/planner.py:40)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:57)
- Deliverables
  - Unit tests for planner outline content event.
- Estimate
  - 3h

---

## D. File Pipeline

8) [ ] File-processing events and content roundtrip
- Issue
  - /api/chat publishes file processing events; ensure frontend receives them and they conform to envelope.
- Cause
  - Legacy event names or shapes.
- Fix
  - Standardize file_processing start/progress/complete events via SSEService; include file_ids and sizes.
- Files
  - [backend/src/main.py](backend/src/main.py:1500)
  - [backend/src/services/sse_service.py](backend/src/services/sse_service.py:180)
- Deliverables
  - Integration test: POST with file_ids → receives file_processing events.
- Estimate
  - 3h

---

## E. Budget and Metrics

9) [ ] BudgetGuard usage record and metrics emission
- Issue
  - Ensure tokens_used/model_used recorded post-run; emit CostEvent/MetricsEvent once.
- Cause
  - Estimates used as fallback; missing finalization event in some paths.
- Fix
  - After advanced processing, call record_usage with actuals when available; publish cost/metrics via SSEService.
- Files
  - [backend/src/services/budget.py](backend/src/services/budget.py:570)
  - [backend/src/agent/routing/unified_processor.py](backend/src/agent/routing/unified_processor.py:309)
  - [backend/src/schemas/sse_events.py](backend/src/schemas/sse_events.py:90)
- Deliverables
  - Unit tests for guard_request overflow and record_usage behavior.
- Estimate
  - 4h

---

## F. Tests and CI

10) [ ] Unit tests — normalization, SSE, budget
- Scope
  - normalization aliases/strict
  - sse_service publish_event envelope validation
  - budget guard: estimate, guard_request, record_usage
- Files
  - [backend/tests/test_normalization.py](backend/tests/test_normalization.py:1)
  - [backend/tests/test_sse_service.py](backend/tests/test_sse_service.py:1)
  - [backend/tests/test_budget.py](backend/tests/test_budget.py:1)
- Estimate
  - 8h

11) [ ] Integration tests — /api/chat + /api/stream
- Scope
  - POST /api/chat with prompt → within 5s first token event; final content and done event; file_ids path
- Files
  - [backend/tests/test_chat_stream_integration.py](backend/tests/test_chat_stream_integration.py:1)
- Estimate
  - 8h

12) [ ] CI workflow
- Scope
  - GitHub Actions: lint + tests, cache, artifact on failure
- Files
  - [.github/workflows/ci.yml](.github/workflows/ci.yml:1)
- Estimate
  - 3h

---

## G. Documentation

13) [ ] SSE Event Envelope Contract
- Content
  - type, conversation_id, ts, content/token, source, is_partial, meta
  - Examples for token, content, routing, progress, cost, metrics, done, error
- Files
  - [docs/sse-envelope.md](docs/sse-envelope.md:1)
- Estimate
  - 2h

---

## Timeline (rough)
- Week 1: A1–A3, B4–B5, C6–C7
- Week 2: D8, E9, F10–F12, G13
