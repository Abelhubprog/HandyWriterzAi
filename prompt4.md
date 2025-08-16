SYSTEM
Implement runnable but conservative logic. The graph must initialize, persist, and complete a trivial run. Use existing infra when possible.

USER
Objective: Implement core/graph.py to actually:
- create a GraphState checkpoint row per step
- “plan” → create one dummy PlanStep
- “act” → write a no-op Observation
- “reflect” → route to END

Constraints:
- Use runtime/checkpointer_sql.py to read/write a JSON payload for the run (design the schema now).
- Log each state transition to episodic_logs.
- Budget counters exist but do nothing yet (stub in runtime/budgets.py).

TODOs:
1) Implement runtime/checkpointer_sql.py with SQLAlchemy or psycopg2 usage consistent with existing db layer; choose the lighter path that fits current repo.
2) In core/graph.py, compile a StateGraph with nodes, conditional edges, and integrate the checkpointer.
3) Emit SSE events through existing sse_v1 schema IF a simple hook exists; otherwise place a TODO where we will stream later.

Acceptance:
- Diff updates for checkpointer and graph.
- A short code block demonstrating `from autonomy_v2.core.graph import graph; graph.invoke(GraphState(task=...))`.
- Commands to run a “hello world” V2 run from python REPL.

SYSTEM
Implement safe, minimal functionality. Use the new SQL checkpointer + episodic logs. Do not add network calls.

USER
Objective:
- Make backend/src/autonomy_v2/core/graph.py actually persist state transitions using the SQL checkpointer, and append episodic logs for plan/act/reflect.
- Keep Planner/Executor/Critic conservative: produce 1 plan step, 1 observation, then END.

Constraints:
- Use the DB-backed checkpointer you just implemented.
- Log each node entry as an event in autonomy_episodic_logs:
  - role: "plan" | "action" | "observation" | "verdict" | "note"
- Respect V2_BUDGET_DEFAULTS from config but only store counters (no enforcement yet).

TODOs:
1) Update core/graph.py: build_graph() should compile with sql_checkpointer(); ensure .invoke(state) returns a GraphState and each node writes an episodic event.
2) Agents:
   - planner.run: if no plan, add 1 step and set route="act".
   - executor.run: set last_observation {output:"ok"} and route="reflect".
   - critic.run: set route="END".
3) Add a tiny smoke test under backend/src/autonomy_v2/evaluation/harness.py:
   - run_once() calls build_graph().invoke(GraphState(run_id="v2-smoke", task={"goal":"hello"}))
   - assert events exist in episodic logs for that run.

Acceptance:
- Diffs for graph + agents + harness to use persistence.
- Shell block to run:
  - `python -c "from backend.src.autonomy_v2.evaluation.harness import run_once; s=run_once(); print('OK', s.run_id)"`.
- Brief plain-text output of 2–4 episodic events for the smoke run (printed via a helper).
