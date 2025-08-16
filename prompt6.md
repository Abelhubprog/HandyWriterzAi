SYSTEM
You are ChatGPT-5 in codex CLI. Implement the Turnitin human-in-the-loop flow for Autonomy V2. Read existing Workbench and Turnitin modules before coding. Make minimal, additive changes and output unified diffs.

USER
Context:
- Autonomy V2 graph persists via SQL checkpointer and logs episodic events.
- Tables exist: autonomy_turnitin_cycles, autonomy_checkpoints, autonomy_episodic_logs, autonomy_job_queue.
- A feature-flagged /api/v2 router is mounted only if ENABLE_AUTONOMY_V2=true.

Requirements:
1) Add `backend/src/autonomy_v2/agents/turnitin_coordinator.py` with:
   - `handoff(state)`:
     - Create a new row in autonomy_turnitin_cycles: status='awaiting_report', target from TaskSpec or TURNITIN_TARGET_DEFAULT.
     - Create a Workbench submission using existing repos (read `src/db/repositories/workbench_*` and `src/api/workbench*.py`; adapt to current signatures).
     - Persist an episodic event {role:"note", content:{turnitin_cycle_id, status:"awaiting_report"}}.
     - Set `state.route="turnitin_pause"`.
2) Extend `backend/src/autonomy_v2/core/graph.py`:
   - Add the node `turnitin_pause` (no-op that returns state unchanged).
   - Add conditional edge from critic → `turnitin_pause` when Turnitin is required.
3) Extend `backend/src/api/autonomy_v2.py`:
   - `POST /v2/turnitin/{run_id}/report` with JSON {cycle_id, report_url, observed_similarity?, human_uploader_id?}
   - Mark the cycle `report_ready` with stored URL and observed_similarity (if given).
   - Append episodic event {role:"note", content:{turnitin_cycle_id, status:"report_ready"}}.
   - Resume the run: invoke graph from the latest checkpoint with route='act'.
4) Update `backend/src/autonomy_v2/agents/critic.py`:
   - If TaskSpec includes target_similarity or a policy flag is on, and we haven’t completed a Turnitin cycle yet, route to `turnitin_pause`. Otherwise, proceed with current logic.

Acceptance:
- Diff for new coordinator, graph route, critic logic, API route.
- A short demo snippet in comments:
  - Start a run with {"goal":"...", "target_similarity":0.15} → route hits `turnitin_pause`.
  - POST the webhook → run resumes and reaches END (with current stub logic).

Safety/Style:
- No direct Turnitin API calls; human uploads via Workbench.
- Use existing DB/session helpers and fall back safely if missing.
