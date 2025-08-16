SYSTEM
Author 3 end-to-end tasks and a simple harness that fail until features are present. Then make them pass.

USER
Objective: Add 3 tasks under autonomy_v2/evaluation/tasks and a harness:
1) rate_limit_resilience.yaml – a tool that 429s N times must succeed with backoff.
2) out_of_scope_research.yaml – no local KB hits → researcher must ingest web docs and proceed.
3) turnitin_cycle.yaml – run must pause, accept a fake webhook, resume, and produce a lower similarity score.

Constraints:
- For #3, simulate similarity by reading a small JSON posted in the webhook (observed_similarity); critic should gate on target_similarity.

TODOs:
1) Implement tasks YAMLs.
2) Implement evaluation/harness.py to run each task via Python entrypoint.
3) Add Makefile target `test-autonomy` and a CI guard script `ci-gate` that runs all tasks.

Acceptance:
- Diffs for tasks + harness + Makefile.
- Command block: `make test-autonomy` output expectations.

SYSTEM
Add three autonomous evaluation tasks and a harness runner.

USER
Create under backend/src/autonomy_v2/evaluation/tasks:
- rate_limit_resilience.yaml
  - use a dummy tool that returns 429 twice then succeeds; verify the run succeeds without manual retries.
- out_of_scope_research.yaml
  - empty local memory; require the researcher to call web_search; assert at least N sources in Observation and route END.
- turnitin_cycle.yaml
  - start a run with target_similarity; ensure route=turnitin_pause; simulate webhook by calling /v2/turnitin/{run_id}/report with observed_similarity; ensure resume and END.

Update evaluation/harness.py:
- load each yaml, start the graph (or enqueue), and assert success conditions.

Makefile:
- add `test-autonomy` target that runs the harness for all three tasks.

Acceptance:
- Diffs for the YAML tasks, harness updates, Makefile target.
- A single command block in output to run: `make test-autonomy`.
