# todoNEW.md

---

## 🔖 Categorised Task List

### Backend Foundation
- [ ] **Unify SSE event streaming**
  - **Issue:** Split event schemas and inconsistent streaming between legacy and unified publishers.
  - **Cause:** Migration in progress; legacy and unified code coexist.
  - **Concrete fix:** Refactor all nodes to use unified SSE publisher (`src/agent/sse_unified.py`), standardize event schema, ensure Redis heartbeat.
  - **Files:** `src/agent/sse_unified.py`, `src/agent/sse.py`, all node files using SSE
  - **Effort:** 3h

- [ ] **Remove silent fallbacks and stub imports**
  - **Issue:** Defensive coding in `unified_processor.py` and other modules hides missing dependencies.
  - **Cause:** Gradual migration, feature flags, try/except imports.
  - **Concrete fix:** Remove silent fallbacks, ensure all modules exist and are import-safe.
  - **Files:** `src/agent/routing/unified_processor.py`, `src/agent/sse.py`, `src/services/*`
  - **Effort:** 2h

- [ ] **Unify state contract and parameter normalization**
  - **Issue:** Nodes use different state contracts (Pydantic, dict, etc.), normalization not universal.
  - **Cause:** Incomplete integration of `normalization.py`.
  - **Concrete fix:** Refactor all nodes to use Pydantic models and normalization from `src/agent/routing/normalization.py`.
  - **Files:** `src/agent/nodes/*`, `src/agent/routing/normalization.py`
  - **Effort:** 3h

- [ ] **Fix all import errors and missing service modules**
  - **Issue:** Several nodes reference services that may not exist or are incomplete.
  - **Cause:** Service layer not fully implemented.
  - **Concrete fix:** Verify and fix all imports, create missing service modules with real logic.
  - **Files:** `src/agent/nodes/*`, `src/services/*`
  - **Effort:** 2h

- [ ] **Implement full file upload round-trip to R2 and pgvector**
  - **Issue:** File upload pipeline may be incomplete or stubbed.
  - **Cause:** Integration logic missing or not fully implemented.
  - **Concrete fix:** Implement backend pipeline for file upload, storage in R2, vectorization in pgvector, and quoting from uploaded PDFs.
  - **Files:** `src/agent/nodes/user_intent.py`, `src/services/file_content_service.py`, `src/services/document_processing_service.py`
  - **Effort:** 4h

- [ ] **Implement real highlight extraction for DOCX and text**
  - **Issue:** Highlight extraction is stubbed in `document_processing_service.py`.
  - **Cause:** Not yet implemented.
  - **Concrete fix:** Implement robust highlight extraction for DOCX and text files.
  - **Files:** `src/services/document_processing_service.py`
  - **Effort:** 2h

### SSE & Streaming
- [ ] **Align frontend event contract with backend SSE schema**
  - **Issue:** Event schema in `useStream.ts` may not match backend unified SSE schema.
  - **Cause:** Backend migration in progress.
  # HandyWriterz AI — Comprehensive Execution Plan (Phase 1)

  Generated: 2025-08-08

  ## 🔖 Categories
  - Backend Foundation
  - SSE / Streaming
  - Multi-Agent Graph & State
  - Parameter Normalization & Routing
  - File Pipeline & RAG
  - Frontend Chat/UI Revamp
  - Tests & Coverage
  - CI/CD & Quality Gates
  - Docs & Operational Readiness

  ---
  ## ⚠️ Issue → Cause → Concrete fix (Task list)
  Each task has: [ ] checkbox, file + line anchors (approx), effort (h), and fix description.

  ### 1. Backend Foundation
  1. [ ] BF-1 Missing `/api/stream/{conversation_id}` unified SSE endpoint → `backend/src/routes/stream.py` empty → Implement FastAPI route that subscribes Redis to `sse:unified:{cid}` and legacy `sse:{cid}` channels with heartbeat. (2h)
  2. [ ] BF-2 Redis SSE service inconsistency (async init misuse) → `backend/src/services/sse_service.py` lines ~1-80 uses non-existent await on sync fn + race → Refactor to clean lazy singleton, remove loop hacks, add ping. (1.5h)
  3. [ ] BF-3 Health endpoint lacks Redis/DB/version contract → Add `/health/ready` returning `{redis:"ok|fail", db:"ok|fail", version:"<git-sha>"}` in <150ms using `database_service` + Redis ping. (1h)
  4. [ ] BF-4 Budget guard optional import shims hide errors → `backend/src/agent/routing/unified_processor.py` ~54-90 → Log explicit warning once and emit SSE `error` if budget module missing. (0.5h)
  5. [ ] BF-5 Duplicate legacy SSE publisher logic → consolidate to `SSEService.publish_event` and drop `_publish_legacy_event`. (1h)

  ### 2. SSE / Streaming
  6. [ ] SSE-1 Mixed schemas (processor flat vs unified vs sse_unified) → Standardize event envelope `{type, ts, ...}`; map unified fields, preserve `token` and `content`. Refactor `_publish_event`. (2h)
  7. [ ] SSE-2 No heartbeat to clients → Add periodic heartbeat in `/api/stream/{cid}` when idle >20s. (0.75h)
  8. [ ] SSE-3 Ensure writer streams `token` events → Pipe writer or processor emissions through unified publisher; adapt if necessary. (1.5h)
  9. [ ] SSE-4 Provide `seq` ordering → passthrough from unified or synthesize in stream route. (0.75h)
  10. [ ] SSE-5 Normalize `progress:*` and `cost_update` → helper in SSE layer and processor usage. (1h)
  11. [ ] SSE-6 Add replay buffer (ring size ~50) in stream route and flush on connect to avoid cold-start loss. (1.5h)

  ### 3. Multi-Agent Graph & State
  12. [ ] AG-1 Add `prompt_metadata` to `backend/src/agent/handywriterz_state.py` and include in `to_dict`. (1h)
  13. [ ] AG-2 Parameter contract divergence → create normalization mapping to dataclass `UserParams` (word_count, document_type, etc.) and use consistently. (1h)
  14. [ ] AG-3 Content extraction fallback expand to match any `*_document`/`*_draft`. (0.5h)
  15. [ ] AG-4 Add SSE progress hooks in key nodes to emit `progress:<phase>`. (2h)
  16. [ ] AG-5 Surface detailed errors from `_process_advanced` via SSE with error_type + partial state id. (0.5h)

  ### 4. Parameter Normalization & Routing
  17. [ ] PN-1 Emit SSE `error` on params validation failures; keep raw params. (0.5h)
  18. [ ] PN-2 Remove comments referencing simple/hybrid; docs alignment. (0.5h)
  19. [ ] PN-3 Ensure POST response includes complexity and confidence back to UI. (0.5h)

  ### 5. File Pipeline & RAG
  20. [ ] FP-1 Add integration test proving RAG round-trip with `lorem-context-42` from uploaded PDF. (2h)
  21. [ ] FP-2 Emit `file_processing` SSE stages in `document_processing_service`. (1.5h)
  22. [ ] FP-3 Health check validates pgvector readiness. (0.5h)
  23. [ ] FP-4 Insert cooperative yields in long loops to avoid event starvation. (0.5h)

  ### 6. Frontend Chat/UI Revamp
  24. [ ] FE-1 Build `ChatComposer` merging prompt, params, file chips; refactor `DemoReadyChatInterface`. (3h)
  25. [ ] FE-2 Track `seq` and heartbeat in `useStream`; show connection state. (0.75h)
  26. [ ] FE-3 Show routing/complexity pills in header. (0.5h)
  27. [ ] FE-4 Centralize file chip interactions. (0.75h)
  28. [ ] FE-5 Loading spinner until first token or heartbeat >5s. (0.5h)

  ### 7. Tests & Coverage
  29. [ ] TST-1 Unit tests for UnifiedProcessor (routing, params, errors). (2h)
  30. [ ] TST-2 SSE route relay + heartbeat using fake Redis. (1.25h)
  31. [ ] TST-3 File pipeline round-trip (see FP-1). (0h extra)
  32. [ ] TST-4 Graph node event emission via monkeypatch. (1h)
  33. [ ] TST-5 Playwright E2E prompt→stream→complete. (3h)
  34. [ ] TST-6 Coverage threshold 90%. (0.5h)

  ### 8. CI/CD & Quality Gates
  35. [ ] CI-1 GH Actions: lint → unit → e2e → deploy to Railway on green. (2h)
  36. [ ] CI-2 Pre-push hook for lint + unit. (0.75h)
  37. [ ] CI-3 Coverage badges and artifacts. (0.5h)

  ### 9. Docs & Operational Readiness
  38. [ ] DOC-1 Update README (Streaming, Health, Budget, Routing). (1h)
  39. [ ] DOC-2 Add `WRITE_ENDPOINT_NORMALIZATION.md`. (0.75h)
  40. [ ] DOC-3 Append E2E Indicators YAML with PASS. (0.5h)
  41. [ ] DOC-4 SSE taxonomy & replay buffer guide. (1h)

  ---
  ## ⏱️ Effort Summary
  Total estimated hours: 36.25h
  Buffer (20%): 7.25h
  Grand Total: 43.5h

  ---
  ## Dependency / Ordering Notes
  - Implement BF + SSE tasks before FE & Tests.
  - Replay buffer (SSE-6) prerequisite for FE loading improvements.
  - Param normalization (PN) before Processor tests.
  - File pipeline test requires FP-2 instrumentation.

  ---
  ## Risk Register (Top 5)
  1. Redis event loss before subscriber connect → mitigated by replay buffer.
  2. Silent import fallbacks hide production misconfigurations → explicit logging & SSE surfaced errors.
  3. Frontend race (UI renders before complexity metadata) → optimistic placeholder then patch.
  4. Long-running embedding blocks event loop → cooperative yields.
  5. Coverage flakiness in streaming tests → deterministic fake publisher.

  ---
  ## Next Implementation Phase
  Proceed to implement tasks in logical commits ≤400 LOC referencing IDs (e.g., `feat(SSE-1): ...`).

  (Implementation Phase 2 will update this file with status checkmarks and append PASS YAML.)
