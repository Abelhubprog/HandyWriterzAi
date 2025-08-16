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
  - **Concrete fix:** Update frontend to match backend SSE event schema.
  - **Files:** `frontend/src/hooks/useStream.ts`, `src/agent/sse_unified.py`
  - **Effort:** 1.5h

### File Pipeline
- [ ] **Prove file-upload round-trip by quoting from uploaded PDF**
  - **Issue:** End-to-end test for file upload and quoting not implemented.
  - **Cause:** Missing integration test.
  - **Concrete fix:** Implement test that uploads PDF and verifies quoting (`lorem-context-42`).
  - **Files:** `src/agent/nodes/user_intent.py`, `src/services/file_content_service.py`, E2E test files
  - **Effort:** 2h

### Frontend UI
- [ ] **Unify chat UI logic and integrate chips, EventSource streaming**
  - **Issue:** Multiple chat UIs, chips and streaming may be missing or duplicated.
  - **Cause:** Demo-specific features, incomplete integration.
  - **Concrete fix:** Refactor to single chat bar, chips for uploads, EventSource streaming via `useSSEStream`.
  - **Files:** `frontend/src/components/chat/PromptEditor.tsx`, `frontend/src/components/chat/DemoReadyChatInterface.tsx`, `frontend/src/hooks/useStream.ts`
  - **Effort:** 2h

### Tests
- [ ] **>90% coverage, Playwright E2E from prompt to PDF download**
  - **Issue:** Test suite coverage and E2E not verified.
  - **Cause:** Missing or incomplete tests.
  - **Concrete fix:** Implement full test suite, Playwright E2E from prompt to PDF download.
  - **Files:** `test_critical_fixes.py`, Playwright test files
  - **Effort:** 3h

### CI
- [ ] **GitHub Actions: lint → unit → e2e → deploy to Railway**
  - **Issue:** CI pipeline may be incomplete or missing steps.
  - **Cause:** Not fully implemented.
  - **Concrete fix:** Implement full CI pipeline with lint, unit, E2E, deploy.
  - **Files:** `.github/workflows/*`, Railway deploy scripts
  - **Effort:** 2h

### Docs
- [ ] **Update docs for new pipeline and multiagent system**
  - **Issue:** Documentation may be outdated or incomplete.
  - **Cause:** Refactors and new features not documented.
  - **Concrete fix:** Update all docs for new pipeline, SSE, file pipeline, multiagent system.
  - **Files:** `README.md`, `INTEGRATION_GUIDE.md`, `IMPLEMENTATION_SUMMARY.md`, `CLAUDE.md`, `prompt.md`
  - **Effort:** 2h

---

## ⏱️ Effort Estimate
- **Total:** ~28.5 hours

---

## ✔️ End-to-End Working-Indicators Checklist (to append after implementation)
- [ ] `python -m pytest -q` → all green
- [ ] `/health/ready` → returns `{ "redis": "ok", "db": "ok", "version": "<git-sha>" }` in <150ms
- [ ] `curl -F "message=Hi" http://localhost:8000/api/chat` returns SSE `token` within 5s
- [ ] Manual smoke: prompt to PDF download round-trip
- [ ] All sections above read **PASS**

---

## 📎 File References
- All file+line references are available in the above task list for direct navigation.

---

## Intelligence Files
- See `intel1.md` for context-aware analysis and fix rationale (to be generated per fix).

---
