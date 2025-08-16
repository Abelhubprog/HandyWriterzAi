SYSTEM
You are ChatGPT-5 running inside codex CLI with full read/write access to the local repository. You must NOT guess or invent files. Before code changes, you MUST read and summarize the relevant files and reference exact paths. Produce zero breaking changes until a plan is agreed.

USER
Context: This is a Python FastAPI + LangGraph backend with extensive modules. Current tree (abridged from user): 
backend/
  README.md, docker files, langgraph.json, models.json, requirements.txt
  src/
    agent/… (orchestrators, nodes, swarms)
    api/… (workbench, files, memory, citations, turnitin endpoints)
    db/… (database, models, repositories)
    services/… (llm, prompt_orchestrator, budget, vector_storage, etc)
    turnitin/… (delivery, orchestrator, telegram bridge)
    tools/… (google_web_search, github_tools, mermaid_diagram_tool, etc)
    tests/ and backend/tests/ (integration, user journeys, e2e)
  scripts/, alembic/, docs/

Goal: Prepare to add an “Autonomy V2” layer (new package) that implements a Reflect-Plan-Act-Observe loop with: Planner, Executor, Critic, Researcher (scope expansion), SelfDebugger (patch+tests), ToolIngestor (OpenAPI/MCP), SQL checkpointer, budgets, SSE streaming, Postgres/pgvector memory, job queue, and a Turnitin coordinator that PAUSES the graph for human upload then RESUMES automatically. We will NOT delete or rewrite src/agent; we will run V2 in parallel.

Constraints:
- Do not change existing public APIs yet.
- Do not break tests in src/tests or backend/tests.
- New code must live under backend/src/autonomy_v2/* with clean imports.
- All changes must be delivered as unified diffs (git apply ready).
- After analysis, present a short “work plan” mapping code locations to tasks.

TODOs for this prompt:
1) Quickly inventory the most relevant existing modules we will reuse (workbench repos, services, db, tools).
2) Identify any collisions to avoid (module names, env vars, settings).
3) Produce a concise plan: the files and folders we will create under src/autonomy_v2/* and minimal glue in src/api/*.
4) List any missing dependencies (e.g., langgraph, pgvector bindings) and propose one migration filename for SQL tables we will need (checkpoints, job_queue, turnitin_cycles, episodic_logs, semantic_notes).

Output format:
- “Findings” bullets tied to exact file paths you opened.
- “Plan” bullets with the exact file paths we will add.
- A single shell block with required pip installs (if any) and the alembic migration filename you’ll generate later.
