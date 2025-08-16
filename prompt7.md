SYSTEM
Create a Postgres-backed job queue with per-user concurrency. Keep the worker simple and resilient.

USER
Objective: Implement a minimal queue under job_queue:
- enqueue(run_id, user_id, journey, priority=5)
- a worker loop that picks next job with SKIP LOCKED and runs one graph step
- states: queued|running|waiting_human|retry|done|failed
- per-user concurrency limit

Constraints:
- Use existing db service patterns.
- Log transitions to episodic_logs.
- If a run is in “turnitin_pause”, set job state waiting_human; the webhook will enqueue a resume job.

TODOs:
1) src/workers/autonomy_v2_worker.py with a `main()` loop:
   - claim → run one graph step → requeue or finalize.
2) services/budget hooks: read V2_BUDGET_DEFAULTS and stop runs cleanly when exceeded.
3) Makefile target `run-autonomy-worker`.

Acceptance:
- Diffs for worker + helpers.
- Example `python -m backend.src.workers.autonomy_v2_worker` command to start locally.
SYSTEM
Implement a simple Postgres-backed queue worker for Autonomy V2. Keep changes additive and minimal.

USER
Objective:
- Add `backend/src/workers/autonomy_v2_worker.py` with a main loop:
  - SELECT ... FOR UPDATE SKIP LOCKED from autonomy_job_queue where state='queued' and scheduled_at<=now() ORDER BY priority, scheduled_at LIMIT 1
  - Mark `running`, set `locked_by`, `locked_at`
  - Load last checkpoint; run one graph step; write new checkpoint
  - Transition states:
    - If state.route == 'turnitin_pause' → set job `waiting_human`
    - If state.route in {'END'} → set job `done`
    - On transient failure → increment attempts, exponential backoff, set `queued` with new scheduled_at
- Enforce per-user concurrency using settings.V2_JOB_CONCURRENCY_PER_USER (skip picking jobs for users at limit).
- Log transitions to autonomy_episodic_logs.

Also:
- Add Makefile target `run-autonomy-worker` (start the worker).
- Add small helper functions in a new `backend/src/autonomy_v2/runtime/queue.py`: enqueue(run_id, user_id, journey, priority=5), enqueue_resume(run_id).

Acceptance:
- Diffs for worker, queue helper, Makefile target.
- A markdown block at end with manual testing steps: enqueue a run, start worker, see episodic logs update, see job move to waiting_human when Turnitin is requested.
