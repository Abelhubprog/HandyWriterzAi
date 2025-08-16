SYSTEM
Apply non-breaking changes only. Create new files and stubs. Use small, compilable code with TODO markers. Use relative imports. Output unified diffs.

USER
Objective: Create the Autonomy V2 package skeleton and minimal compilable stubs.

Constraints:
- Place everything under backend/src/autonomy_v2/*
- Every module must import without side effects
- Add an __init__.py in every folder
- Provide minimal Pydantic models and LangGraph wiring stubs that do nothing dangerous
- Provide a minimal FastAPI router placeholder in backend/src/api/autonomy_v2.py mounted under /v2 but DO NOT register it in app yet

TODOs:
1) Add folders:
   autonomy_v2/{core,agents,tools,memory,runtime,evaluation}
   autonomy_v2/evaluation/tasks (empty for now)
2) Create core/types.py with TaskSpec, PlanStep, Action, Observation, Verdict (as described), and core/state.py with GraphState.
3) Create core/prompts.py with tiny deterministic system prompts for planner, critic, debugger.
4) Create core/llm.py with a pluggable LLM router that delegates to existing services/model_registry if available; otherwise a TODO stub.
5) Create core/graph.py with LangGraph state machine nodes: plan, act, reflect, expand, repair; compile() with a placeholder checkpointer from runtime/checkpointer_sql.py (stub).
6) Create agents/{planner.py,executor.py,critic.py,researcher.py,self_debugger.py,tool_ingestor.py} with minimal pass-through logic and explicit TODOs that point to existing services modules we will reuse later.
7) Create tools/{registry.py,rate_limit.py,python_sandbox.py,web_search.py} with very small, safe stubs (no network calls yet).
8) Create memory/{episodic_repo.py,semantic_repo.py,vector_repo.py} with method signatures only.
9) Create runtime/{checkpointer_sql.py,budgets.py,eval.py} with docstrings.
10) Create evaluation/harness.py that imports the graph and can run a no-op run.

Deliverables:
- Unified diffs adding all files with simple, importable content.
- A shell block with “python -m compileall backend/src” to validate imports.
