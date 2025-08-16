SYSTEM
Expose minimal read-only endpoints to observe V2 runs and a simple SSE stream of episodic events.

USER
Objective:
- Add FastAPI routes in api/autonomy_v2.py:
  - POST /v2/runs  → start a run
  - GET  /v2/runs/{run_id} → current snapshot (task, route, budgets)
  - GET  /v2/runs/{run_id}/events → SSE stream from episodic_logs
- Do NOT change existing v1 endpoints.

Constraints:
- Reuse schemas/sse_v1.json if compatible; else return simple text/event-stream with JSON payloads.

TODOs:
1) Implement routes and wire DB reads.
2) Provide example curl commands to start and watch a run.

Acceptance:
- Diffs for api/autonomy_v2.py.
- Shell demo showing start + stream.

SYSTEM
Expose minimal, read-only API and SSE to observe V2 runs. Keep it additive.

USER
In `backend/src/api/autonomy_v2.py`, add:
- POST /v2/runs {journey, task_spec} → creates a run_id, seeds the checkpoint, enqueues the job.
- GET  /v2/runs/{run_id} → returns the latest checkpoint (task, route, plan, budgets).
- GET  /v2/runs/{run_id}/events → SSE stream of autonomy_episodic_logs for that run (reuse existing SSE service if compatible; else simple text/event-stream).

Acceptance:
- Diffs for new endpoints and minimal schemas.
- Example `curl` to start a run and stream events.
