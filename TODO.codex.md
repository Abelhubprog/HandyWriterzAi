
# TODO.codex.md — Phase 2 (Next Steps)
Generated: 2025-08-09 12:33 UTC

## Critical fixes
- [ ] **CG-1 ChatInit completion** — `backend/src/routes/chat_gateway.py`
  - [ ] `trace_id = str(uuid.uuid4())`
  - [ ] Safe import `normalize_user_params` (fallback to identity)
  - [ ] Correct `UnifiedProcessor` import and call signature
  - [ ] `background_tasks.add_task(...)` with `(prompt, file_ids, normalized_params, user_id, trace_id)`
  - [ ] Return `{"status":"accepted","trace_id": trace_id}`
  - [ ] Structured logging; narrow `except`

- [ ] **SSE-5 Single publisher** — grep for `redis.publish`/old publishers; route through **SSEService** wrappers.

## Backend polish
- [ ] **RDY-1** `/health/ready` returns redis/db/version; <150ms p95.
- [ ] **NOR-1** Normalize params in ChatInit; skip in `UnifiedProcessor` when `_normalization_meta` present.
- [ ] **RAG-1** Wire `FileContentService` ⇄ `EmbeddingService` ⇄ vector store; stub retrieval call in writer.

## Frontend
- [ ] **FE-1 Chat proxy** — `frontend/src/app/api/chat/send/route.ts` consumes `trace_id`; `useStream(trace_id)` opens SSE.
- [ ] **FE-2 Error UX** — Retry action; downgrade state if heartbeat > 25s.
- [ ] **FE-3 Chips** — Verify mapping for `node_start|node_end|progress|files:*|done|error`.

## Tests & CI
- [ ] **T-1 pytest ini/caches** — Add `pytest.ini`, `.pytest_tmp`, `.cache`, `.reports`; doc env flags in README.
- [ ] **T-2 Unit** — `test_chat_init_returns_trace_id.py`, extend normalizer tests, SSE envelope tests.
- [ ] **T-3 E2E (Playwright)** — prompt → stream → export PDF (local only).

## Ops
- [ ] **CI-1** Lint → Unit → (optional) E2E GitHub Actions.
- [ ] **OPS-1** Log slow `/health/ready`; capture `GIT_SHA`/`RELEASE_SHA` in readiness.

---
**Run order**: CG-1 → SSE-5 → FE-1 → NOR-1 → RDY-1 → RAG-1 → FE-2/FE-3 → T-1/T-2 → (optional) T-3/CI-1.
