
You are the **Lead Engineer** inside Codex CLI for HandyWriterzAI. Use **gpt-5**.

### Objective (next patch set)
1) **Fix ChatInit (`routes/chat_gateway.py`)**
   - Generate `trace_id = str(uuid.uuid4())`.
   - Safely import `normalize_user_params` (fallback to identity if absent).
   - Build background task via `UnifiedProcessor` with `(prompt, file_ids, normalized_params, user_id, trace_id)`.
   - Return `{"status":"accepted","trace_id": trace_id}`.
   - Add structured logging; narrow `except` blocks.

2) **Harden SSE**
   - Ensure all nodes publish via **SSEService** wrappers only.
   - Keep envelope minimal and inject `conversation_id` for `connected`, `heartbeat`, data events.
   - Confirm ring buffer + heartbeat cadence; unit-test the pure normalizer.

3) **Files → RAG (scaffold in this patch)**
   - Ensure `FileContentService` extracts text (pdf/docx) and passes to `EmbeddingService` → vector store.
   - Add TODO hook in writer for retrieval + citation of uploaded content.

4) **Frontend wiring**
   - `app/api/chat/send/route.ts` POSTs to backend `/api/chat`, reads `trace_id`, then opens `/api/stream/{trace_id}` via `useStream`.
   - Keep ProgressChips, heartbeat indicator, error overlay; add a “Retry” action.

5) **Testing / Dev experience**
   - Add `pytest.ini`; create `.pytest_tmp`, `.cache`, `.reports` and route tmp/cache/coverage into repo.
   - Create `test_chat_init_returns_trace_id.py`, extend normalizer tests, add SSE envelope tests.
   - Use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `--basetemp ./.pytest_tmp` to avoid `/tmp`.

### Constraints
- Only edit `backend/src/**` and `frontend/src/**` (plus test/config files).
- After each step, show `/diff`, then wait for approval.
- Do not reintroduce direct `redis.publish`.

### Acceptance
- `POST /api/chat` returns a fresh `trace_id` and background task starts (log).
- EventSource to `/api/stream/{trace_id}` shows connected + heartbeats + token events.
- Unit tests for ChatInit and normalizer pass locally with in-repo tmp/caches.
- No stray `redis.publish` calls.
