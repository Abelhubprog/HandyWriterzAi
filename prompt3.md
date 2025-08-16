SYSTEM
Create migrations and config glue. Avoid destructive changes.

USER
Objective: Add SQL tables and wiring for V2:
- run_checkpoints / episodic_logs / semantic_notes (pgvector) 
- turnitin_cycles 
- job_queue

Constraints:
- Use Alembic style consistent with backend/alembic/versions
- Do not alter existing tables unless necessary
- Wrap vector DDL in a feature check (CREATE EXTENSION IF NOT EXISTS vector)

TODOs:
1) Generate a new Alembic migration file under alembic/versions/ with a clear name (e.g., 20250813_autonomy_v2_tables.py). Create forward and downgrade ops.
2) In backend/src/services/database_service.py or equivalent, add safe helper(s) if needed to access new tables. If a DB service already exists, extend minimally.
3) Add configuration defaults to backend/src/config.py (or core/config.py) for V2: TURNITIN_TARGET_DEFAULT, V2_JOB_CONCURRENCY_PER_USER, V2_BUDGET_DEFAULTS, ENABLE_AUTONOMY_V2 (feature flag).
4) Provide a Makefile target `bootstrap-autonomy` to run migrations.

Acceptance:
- Diff with migration file content.
- Diff with minimal config additions.
- Diff with Makefile target.
- Shell block to run: `make bootstrap-autonomy && python -m compileall backend/src`
