SYSTEM
Compose the V2 graph into a practical journey: write from prompt with Turnitin loop.

USER
Objective:
- Add a small controller under autonomy_v2/runtime/journeys.py that configures the generic graph for journey="write"
- Planner creates steps: research → write → qa → (turnitin_pause if configured) → finalize
- Critic checks: min_citations, tone, and when enabled, target_similarity (from TaskSpec or default)

Constraints:
- Writer may initially call existing writer.py / writer_migrated.py
- QA uses your qa_swarm modules (fact_checking, originality_guard, etc.) but can be mocked in first pass

TODOs:
1) journeys.py exposing start_write_run(task_spec) that sets defaults and enqueues.
2) Update /v2/runs to accept a {journey:"write"} body and call journeys.start_write_run.

Acceptance:
- Diffs for journeys + api changes.
- Demo: curl start → see plan in SSE → emulate webhook → see run END with success gates met.
