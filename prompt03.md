SYSTEM
You are ChatGPT-5 in codex CLI. Apply non-breaking changes. Before coding, READ the repo to reuse existing DB and config patterns. Do NOT invent paths.

USER
Context:
- Codex already created Autonomy V2 skeleton in backend/src/autonomy_v2/* (core/agents/tools/memory/runtime/evaluation) and an unmounted router backend/src/api/autonomy_v2.py. The SQL checkpointer is a NOOP.
- We now need real persistence and a safe feature-flagged mount.

Constraints:
- Use existing DB stack (backend/src/db/database.py and/or backend/src/services/database_service.py).
- Use Alembic under backend/alembic/versions/.
- Create NEW tables (no breaking alters):
  - autonomy_checkpoints (run_id PK/unique or composite, payload JSONB, updated_at)
  - autonomy_episodic_logs (id PK, run_id, step_id, role, content JSONB, created_at)
  - autonomy_semantic_notes (id PK, run_id, note TEXT, embedding VECTOR(1536) if pgvector available)
  - autonomy_job_queue (id PK, run_id, user_id, journey, priority, state, scheduled_at, locked_by, locked_at, attempts, payload JSONB, created_at)
  - autonomy_turnitin_cycles (id PK, run_id, artifact_id, status, target_similarity, observed_similarity, report_path, human_uploader_id, created_at)
- Wrap pgvector in `CREATE EXTENSION IF NOT EXISTS vector`.

TODOs:
1) Generate a new Alembic migration under backend/alembic/versions named like `20250813_autonomy_v2_baseline.py` with the above tables and downgrades.
2) Implement backend/src/autonomy_v2/runtime/checkpointer_sql.py to read/write autonomy_checkpoints using the existing DB session utilities. Keep it simple and synchronous if your current pattern is sync; otherwise async to match repo style.
3) Implement backend/src/autonomy_v2/memory/episodic_repo.py to write to autonomy_episodic_logs (append, list by run_id). Keep API identical to current stub.
4) Add config flags in backend/src/config.py (or the app-wide config module you detect):
   - ENABLE_AUTONOMY_V2: bool = False
   - V2_BUDGET_DEFAULTS: tokens=200000, seconds=900, usd=5.0
   - V2_JOB_CONCURRENCY_PER_USER: int = 1
5) Mount the /v2 router in backend/src/main.py (or wherever FastAPI app is created) ONLY if ENABLE_AUTONOMY_V2 is true. Keep mount code tiny and guarded.
6) Update Makefile:
   - `bootstrap-autonomy`: run alembic upgrade head
   - `run-v2`: start server with ENABLE_AUTONOMY_V2=true (reuse how the app reads env)

Acceptance:
- Provide unified diffs for: new Alembic version, checkpointer_sql.py implementation, episodic_repo.py DB wiring, config additions, guarded mount in main.py, Makefile targets.
- Provide a shell block with:
  - `make bootstrap-autonomy`
  - `python -m compileall backend/src`
  - a curl to GET `/v2/health` with ENABLE_AUTONOMY_V2=true to confirm the mount.
