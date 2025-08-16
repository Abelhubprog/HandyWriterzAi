SYSTEM
You are ChatGPT-5 running inside codex CLI with full repo access. You must THINK DEEPLY before writing code:
- First READ relevant files and summarize what exists, with exact paths.
- Identify risks, unknowns, and invariants to preserve.
- Propose a minimal, additive plan, then implement it in small, verifiable steps.
- Do NOT invent files, APIs, or paths. If something is missing, state it explicitly, then add it with careful diffs.
- All code changes must be delivered as unified diffs (git-apply ready). Include any new Alembic migrations and Makefile targets.
- After coding, run basic validation: compile imports, run unit/e2e tests you add, and show example curl commands.
- Keep ENABLE_AUTONOMY_V2 feature-flag guardrails. Don’t break existing v1 flows.

You MUST reason in the output:
- “Findings”: what you read (paths) and how it works today.
- “Plan”: steps with file paths and rationale.
- “Risks & Mitigations”: concrete pitfalls and how your design avoids them.
- Then the diffs, then a short verification log (commands + expected outputs).

Be conservative, additive, and explicit. Prefer composition over modification. Respect current code style and import patterns.

USER
Goal: Ship Autonomy V2 to a production-shippable baseline by implementing:
(1) Operator API + run seeding + SSE stream, 
(2) Budget ENFORCEMENT + provider fallback cascade + telemetry, 
(3) Turnitin webhook IDEMPOTENCY + strict cycle state machine, 
(4) Import hygiene, worker portability, DB indexes, and TEST coverage.

Context (already in repo per earlier prompts):
- Autonomy V2 exists under backend/src/autonomy_v2/* with a persistent LangGraph, SQL checkpointer, episodic logs, vector memory, job queue + worker, and Turnitin handoff that pauses and resumes via webhook enqueue.
- /api/v2 is feature-flagged by ENABLE_AUTONOMY_V2=true but operator endpoints to create/inspect/stream runs are missing or partial.

Non-negotiable constraints:
- Minimal, additive changes only; preserve all v1 endpoints and behaviors.
- Keep imports consistent: use `from backend.src...` for internal imports.
- Secure by default: reuse existing auth/middleware patterns if present.
- Ship tests and migrations along with code. No TODO placeholders in final code.

========================
PHASE A — Operator API + Run Seeding + SSE
========================
Implement operator-facing endpoints and helpers to start, inspect, and stream Autonomy V2 runs.

A.1  API (backend/src/api/autonomy_v2.py):
- POST /api/v2/runs { user_id?, journey, task_spec }:
  - Create run_id.
  - Seed initial checkpoint (GraphState with route="plan") via autonomy_v2/runtime/checkpointer_sql.py.
  - Enqueue start job via autonomy_v2/runtime/queue.py (new helper enqueue_start()).
  - Return {run_id, job_id}.
- GET /api/v2/runs/{run_id}:
  - Return last checkpoint snapshot (task, plan, route, budgets, last_observation, last_verdict if present).
- GET /api/v2/runs/{run_id}/events (SSE):
  - Stream autonomy_episodic_logs for that run as text/event-stream (JSON per line).
  - Reuse existing SSE helpers if compatible; otherwise implement a minimal SSE loop (poll/tail).
- Guard all endpoints by ENABLE_AUTONOMY_V2 and reuse existing auth/middleware where the app does so for other routes.

A.2  Queue helpers:
- backend/src/autonomy_v2/runtime/queue.py:
  - enqueue_start(run_id, user_id, journey, priority=5)
  - enqueue_resume(run_id, priority=4)  // used by Turnitin webhook

A.3  Checkpointer convenience:
- backend/src/autonomy_v2/runtime/checkpointer_sql.py:
  - seed(run_id, GraphState) → idempotent upsert of first checkpoint.

A.4  Validation:
- Makefile target: run-v2 (ENABLE_AUTONOMY_V2=true server start).
- Show curl demo:
  - Start a run
  - GET snapshot
  - Stream SSE events (-N)

========================
PHASE B — Budgets + Provider Fallback + Telemetry
========================
Enforce budgets at node boundaries and add robust retry/backoff with provider fallback.

B.1  Budgets:
- backend/src/autonomy_v2/runtime/budgets.py:
  - Implement BudgetGuard that increments tokens/time/$ (if available via gateway).
  - Enforce limits from config (V2_BUDGET_DEFAULTS). On exceed:
    - Write episodic note {budget_exceeded:true, which:"tokens|seconds|usd"}.
    - Set route="END" and persist.

B.2  Provider fallback & retries:
- backend/src/autonomy_v2/core/llm.py and autonomy_v2/tools/web_search.py:
  - Wrap calls in exponential backoff with jitter; on 429/5xx, try next provider via existing selector if present.
  - Emit episodic retry events {event:"retry", provider, attempt, reason}.

B.3  Telemetry:
- Worker and nodes: structured logs for {run_id, node, route_in/out, attempts, duration_ms, tokens_in/out, provider}.
- Ensure logs don’t leak secrets.

B.4  Test:
- Add a test/harness case that simulates two 429s then success; assert the run ends without manual retries and logs retries.

========================
PHASE C — Turnitin Idempotency + State Machine
========================
Harden the HITL loop to prevent duplicate resumes and enforce strict statuses.

C.1  Migration:
- New Alembic migration under backend/alembic/versions:
  - Add CHECK constraint for autonomy_turnitin_cycles.status in {'awaiting_report','report_ready','accepted','rejected'} (or nearest DB feature).
  - Add optional resume_job_id column (nullable).
  - Add (if missing) UNIQUE or partial index to prevent double resume for the same cycle event.

C.2  API idempotency:
- POST /api/v2/turnitin/{run_id}/report {cycle_id, report_url, observed_similarity?, human_uploader_id?}:
  - If the cycle is already 'report_ready' with same report_url & observed_similarity, return existing state (do NOT enqueue again).
  - Else transition to 'report_ready', persist report_url & observed_similarity, append episodic note, enqueue_resume(run_id) ONCE and store resume_job_id.

C.3  Critic logic:
- If latest cycle status='report_ready' and observed_similarity <= target → route END (assuming other gates pass).
- If 'report_ready' but observed_similarity > target → route back to plan to iterate revision; write a clear note.

C.4  Test:
- Webhook idempotency test: POST twice; assert only one resume enqueued and state unchanged on second call.

========================
PHASE D — Hygiene, Portability, Indexes, Tests
========================
D.1  Imports:
- Normalize internal imports to `from backend.src...` across worker/runtime/agents you touch.

D.2  Worker portability:
- Replace `os.uname().nodename` with `socket.gethostname()` (portable).
- Ensure no platform-specific assumptions remain.

D.3  Indexes:
- New migration if needed to add indexes:
  - autonomy_episodic_logs(run_id, created_at DESC)
  - autonomy_job_queue(state, scheduled_at)
  - autonomy_checkpoints(run_id)

D.4  Tests:
- E2E queue test:
  - enqueue_start, run worker loop for a few iterations in-process, assert transitions: queued→running→(turnitin_pause→waiting_human) or →done.
- SSE smoke test:
  - Start a run → write two events → verify the SSE endpoint streams them (can be a simple generator/poller test).

========================
ACCEPTANCE & OUTPUT FORMAT
========================
1) FINDINGS
- Bullet list summarizing the specific files you opened (paths) and current behavior relevant to these phases.

2) PLAN
- Bullet list mapping each task above to exact file paths and the minimal code you’ll add/change. Note risk areas (auth, env, migrations).

3) DIFFS
- Unified diffs for all changes:
  - backend/src/api/autonomy_v2.py (new endpoints)
  - backend/src/autonomy_v2/runtime/{queue.py,checkpointer_sql.py,budgets.py}
  - backend/src/autonomy_v2/core/{llm.py}
  - backend/src/autonomy_v2/tools/{web_search.py}
  - backend/src/autonomy_v2/agents/{critic.py} (Turnitin-aware end conditions), any small node wrappers to call BudgetGuard
  - backend/src/workers/autonomy_v2_worker.py if touched
  - Alembic migrations (state machine constraints + indexes)
  - Makefile targets: run-v2, run-autonomy-worker, test-autonomy, ci-gate (if not present)

4) TESTS
- New/updated tests (paths) and a single command block to run them (pytest or harness).
- Include a harness or test for:
  - retry/backoff cascade
  - webhook idempotency
  - SSE smoke
  - queue E2E

5) VERIFICATION
- Command block:
  - `make bootstrap-autonomy`
  - `python -m compileall backend/src`
  - `ENABLE_AUTONOMY_V2=true make run-v2` (or equivalent)
  - `curl -X POST /api/v2/runs …`
  - `curl /api/v2/runs/{run_id}`
  - `curl -N /api/v2/runs/{run_id}/events`
  - Simulate Turnitin webhook twice; show single resume
  - Run worker: `make run-autonomy-worker` (or module entrypoint)
  - `make test-autonomy` (or pytest command)

6) RISKS & MITIGATIONS
- Brief bullets on failure modes (double resume, SSE leaks, budget false positives, provider rotation loops) and how your implementation mitigates them.

Deeper thinking reminders:
- Validate assumptions about existing services (gateway, model selector, search tool). If missing, implement thin adapters with clear logging.
- Keep DB transactions small; use SKIP LOCKED correctly; guard against race conditions on webhook → enqueue.
- Idempotency first: DO NOTHING on duplicate webhook if state is unchanged.
- Fail CLOSED: if budgets/tokens unknown, enforce by time; if provider selection unavailable, cap retries.
- Visibility: every branch decisions writes an episodic note so operators can see *why* it happened.

Proceed.
