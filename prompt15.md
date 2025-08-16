Here’s what Codex has already done, what’s still missing, and the exact next prompts to ship. I read CodexCLI3.MD end-to-end (plus the earlier Codex logs) and pulled the real diffs/notes straight from there. 

Snapshot — what’s in place
Turnitin HITL handoff: Coordinator inserts a cycle, logs events, pauses the run (turnitin_pause), and exposes a webhook to resume. Cycle ID retrieval was fixed and added to episodic logs; harness demo simulates setting report_ready. The webhook now enqueues a resume job (not direct resume). 
 
 

Job queue + worker: Postgres queue with FOR UPDATE SKIP LOCKED, per-user concurrency check, exponential backoff, and transitions to waiting_human or done. Makefile target run-autonomy-worker added. 
 

Vector memory: VectorRepo uses embedding+pgvector when available, otherwise a safe SQL fallback to autonomy_semantic_notes; connected into Researcher/Executor; focused test added. 

Planner/Executor/Critic: Real plan→act→reflect cycle, tools registry (web_search + echo), planner via LLM JSON, critic: END if sources else re-plan; critic also checks Turnitin status/threshold before ending. 

Gaps & risks to fix next
Operator endpoints missing — No /v2/runs to seed runs, inspect state, or stream events. Right now you can’t start/monitor runs via API; only a Turnitin webhook exists. 

Queue seeding — We added enqueue/enqueue_resume, but no API to create a run, write the initial checkpoint, and enqueue the first job. Manual DB/graph calls are used in harness. 

Idempotency & state machine for Turnitin — /turnitin/{run_id}/report is not clearly idempotent (repeat webhooks could double-resume). Cycle statuses need a tighter state machine and constraints. 

Auth/permissions — The new v2 API route doesn’t show auth/tenant checks. Needs to reuse your existing middleware/policies. 

Budget enforcement — You’re tracking counters but not enforcing token/time/$ limits across nodes/tools; no provider fallback cascade beyond planner. 

Observability — No SSE stream for episodic events; no metrics/structured logs for worker transitions, rate-limit retries, or tool failures. 

Consistency of imports & portability — Mixed src. vs backend.src. imports and use of os.uname() in the worker can break on non-Unix systems. 

Vector memory lifecycle — Fallback path appends to autonomy_semantic_notes but there’s no dedupe/TTL beyond a simple idempotent insert; no delete/evict; no “cite-from-memory” formatting. 

Tests — We have a vector test and basic harness demos, but no end-to-end tests for job transitions, webhook idempotency, or SSE. 
 

Below are the next prompts to paste into Codex, in priority order. Each prompt is self-contained and assumes the current repo state.


SYSTEM
You are ChatGPT-5 in codex CLI. Add operator-facing endpoints to start, inspect, and stream Autonomy V2 runs; keep changes additive and guarded by ENABLE_AUTONOMY_V2.

USER
Context:
- V2 graph, SQL checkpointing, episodic logs, queue, and worker exist.
- Turnitin webhook is implemented but there is no way to create/monitor runs via API.
- SSE infra exists elsewhere in the repo (sse.py / sse_unified.py); reuse if viable.

TODOs:
1) API (backend/src/api/autonomy_v2.py):
   - POST /api/v2/runs {user_id?, journey, task_spec} → create run_id, write initial checkpoint (GraphState with route="plan"), enqueue the job, return {run_id, job_id}.
   - GET  /api/v2/runs/{run_id} → return last checkpoint (task, plan, route, last_observation, budgets if tracked).
   - GET  /api/v2/runs/{run_id}/events (SSE) → stream autonomy_episodic_logs for that run in near real-time.
   - All endpoints: reuse existing auth/middleware patterns (same as other /api routes). If no auth, use the lightest existing decorator.

2) Runtime helpers:
   - backend/src/autonomy_v2/runtime/queue.py: add `enqueue_start(run_id, user_id, journey, priority=5)`.
   - backend/src/autonomy_v2/runtime/checkpointer_sql.py: expose a tiny `seed(run_id, GraphState)` that performs an upsert.

3) SSE:
   - Reuse backend/src/autonomy_v2/memory/episodic_repo.py to fetch initial backlog (last N events) then tail newly inserted rows (poll or trigger).
   - If the shared SSE service exists, wrap it; else, implement a minimal `text/event-stream` endpoint emitting JSON lines.

Acceptance:
- Diffs for autonomy_v2.py, queue.py, checkpointer_sql.py, and any small SSE helper.
- A curl demo block:
  - Start run → curl -X POST /api/v2/runs …
  - Inspect run → curl /api/v2/runs/{run_id}
  - Stream events → curl -N /api/v2/runs/{run_id}/events
Notes:
- Keep imports consistent (prefer `backend.src...`).
- Use SQL indexes if needed (run_id on logs).


SYSTEM
Implement hard budget enforcement and robust provider fallback across nodes/tools.

USER
Objectives:
1) Budgets:
   - Add a BudgetGuard (decorator or helper) used by planner/executor/critic that updates counters and ENFORCES limits:
     - tokens, elapsed seconds, and optional USD if your gateway exposes cost.
   - On exceed: log episodic {role:"note", content:{budget_exceeded}}, set route="END".

2) Fallback cascade:
   - In core/llm.py and tools/web_search.py, implement a shared retry/backoff wrapper:
     - On 429/5xx, exponential backoff with jitter (cap 30s); try next provider via model_selector if available.
     - Emit episodic events for retries {event:"retry", provider, attempt, reason}.

3) Telemetry:
   - Add structured logs for worker transitions and node execution:
     - run_id, node, route_in/out, attempts, duration_ms, tokens_in/out (if available).

Acceptance:
- Diffs for core/llm.py, tools/web_search.py, agents/* wrappers to call BudgetGuard, plus logging additions.
- A test (can be in evaluation/harness) that simulates 2 transient 429s then success, asserting the run ends without manual retries.
- Minimal docs comment in code: how budgets are set from settings (V2_BUDGET_DEFAULTS).

SYSTEM
Harden the HITL loop: make the webhook idempotent, add constraints, and prevent duplicate resumes.

USER
Tasks:
1) DB migration:
   - Add partial unique index on autonomy_turnitin_cycles (run_id, id) and an optional `resume_job_id` column.
   - Ensure statuses are one of {'awaiting_report','report_ready','accepted','rejected'}; use CHECK constraint if supported.

2) API:
   - POST /api/v2/turnitin/{run_id}/report:
     - If the cycle is already 'report_ready' with the same report URL/similarity, treat as OK and return current state (do NOT enqueue again).
     - Otherwise, transition → 'report_ready', append episodic note, and enqueue resume ONCE; store `resume_job_id` to block duplicates.

3) Critic:
   - If latest cycle `status='report_ready'` and observed<=target → END.
   - If `status='report_ready'` but observed>target → route back to "plan" (iterate to improve draft).

Acceptance:
- Diffs: new Alembic migration, API idempotency, critic logic tweak, and a harness function showing double webhook posts only resume once.

SYSTEM
Harden the HITL loop: make the webhook idempotent, add constraints, and prevent duplicate resumes.

USER
Tasks:
1) DB migration:
   - Add partial unique index on autonomy_turnitin_cycles (run_id, id) and an optional `resume_job_id` column.
   - Ensure statuses are one of {'awaiting_report','report_ready','accepted','rejected'}; use CHECK constraint if supported.

2) API:
   - POST /api/v2/turnitin/{run_id}/report:
     - If the cycle is already 'report_ready' with the same report URL/similarity, treat as OK and return current state (do NOT enqueue again).
     - Otherwise, transition → 'report_ready', append episodic note, and enqueue resume ONCE; store `resume_job_id` to block duplicates.

3) Critic:
   - If latest cycle `status='report_ready'` and observed<=target → END.
   - If `status='report_ready'` but observed>target → route back to "plan" (iterate to improve draft).

Acceptance:
- Diffs: new Alembic migration, API idempotency, critic logic tweak, and a harness function showing double webhook posts only resume once.

SYSTEM
Unify imports, fix OS portability, and add targeted tests.

USER
Tasks:
1) Imports:
   - Standardize to `from backend.src...` for internal imports within worker, runtime, and agents. Avoid mixing with `from src...`.
2) Worker portability:
   - Replace `os.uname().nodename` with a portable host identity (e.g., `socket.gethostname()`).
3) Indexes:
   - Add DB indexes if missing: autonomy_episodic_logs(run_id, created_at DESC), autonomy_job_queue(state, scheduled_at), autonomy_checkpoints(run_id).
4) Tests:
   - E2E queue test: enqueue a start job, run worker loop for a few iterations (in-process), assert transitions including `waiting_human` on Turnitin tasks.
   - Webhook idempotency test (after Prompt 12).

Acceptance:
- Diffs for imports, worker host field, new migration for indexes.
- New tests under backend/src/tests or autonomy_v2/evaluation with deterministic assertions.
