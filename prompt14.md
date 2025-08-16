SYSTEM
Prepare a single PR description, a rollout checklist, and a shadow-run plan. No code.

USER
Objective:
- Generate a PR description that enumerates all new files, migrations, and how to run `make bootstrap-autonomy`, `make test-autonomy`, and the worker.
- Provide a 72-hour shadow-run plan:
  - route 10% of users to V2 (feature flag),
  - collect metrics (success, similarity after 1/2/3 cycles, cost),
  - fallback switch.

Deliverables:
- PR description text
- Rollout checklist with boxes
- Shadow-run plan (bullets)
