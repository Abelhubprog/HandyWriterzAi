# Changelog

## 2025-08-13 — Autonomy V2 skeleton and streaming-ready gateway

- Added Autonomy V2 package skeleton under `backend/src/autonomy_v2/*` with import-safe stubs:
  - Core: `types.py`, `state.py`, `prompts.py`, `llm.py`, `graph.py` (LangGraph wiring with noop SQL checkpointer).
  - Agents: `planner.py`, `executor.py`, `critic.py`, `researcher.py`, `self_debugger.py`, `tool_ingestor.py`.
  - Tools: `registry.py`, `rate_limit.py`, `python_sandbox.py`, `web_search.py` (no network side effects).
  - Memory: `episodic_repo.py`, `semantic_repo.py`, `vector_repo.py` (signatures and in-memory stubs).
  - Runtime: `checkpointer_sql.py`, `budgets.py`, `eval.py` stubs.
  - Evaluation: `harness.py` and `evaluation/tasks/` placeholder.
- Added an unmounted FastAPI router at `backend/src/api/autonomy_v2.py` under `/v2` with health and no-op run.
- Verified imports via `python -m compileall backend/src`.
- Confirmed SSE stream route `/api/stream/{conversation_id}` and `POST /api/chat` background processing remain intact.

