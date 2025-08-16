I spent 6 months building "agents" that were just glorified chatbots with API calls. 

Then I watched a real autonomous system debug its own code at 3am. 

That's when it hit me.

Here's what changed my mind:

1️⃣ The Automation Trap 

I thought agents = smart automation 

Built dozens of "agents" that followed if-then logic 

Turns out I was just making expensive workflows 

Real agents don't follow scripts—they figure things out

2️⃣ The Failure That Opened My Eyes 

Built a "research agent" that could only search pre-defined sources

It crashed when asked about a topic outside its scope 

A true agent would've found new sources, adapted its approach 

Mine just threw an error

3️⃣ The 3AM Wake-Up Call 

Watched an actual autonomous system at a startup demo 

It hit an API rate limit, diagnosed the issue, implemented exponential backoff 

Then rewrote its own retry logic for better performance 

No human intervention. Just pure problem-solving.

✅ What Real Agents Actually Do 

• Self-correct without explicit error handling 

• Navigate decision trees you never programmed 

• Learn from failures and adjust strategies 

• Handle edge cases that would break traditional systems

The hard truth? Most "AI agents" in production are just LLMs + hardcoded workflows. 

Real agents are still rare. But when you see one, you know.

Still calling my HandyWriterzAi chatbot an agent? 

Time to level up. 🚀 Think about the exact blueprint of transforming my "multiagent"  in my repo https://github.com/Abelhubprog/HandyWriterzAi into a truely autonomous ai agents even if it means completely redoing it. You need to clone it and rebuild conceptually and create unprecedented steps that are repeatable in achieving a truely autonomous ai agents from this repo.

You’re right: most “agents” are just fancy if-then scripts wrapped around an LLM. Real autonomy shows up when a system can **notice**, **reason**, **adapt**, and **repair itself** without being told how.

Below is a concrete, repeatable blueprint to transform **HandyWriterzAi** from “workflow bots” into **autonomous problem-solvers**—aligned with your current FastAPI + LangGraph backend, Next.js frontend, Postgres/pgvector, Redis, and Railway/R2 setup. ([GitHub][1])

---

# The autonomy blueprint (what to build)

## A. Capabilities real agents need

1. **Goal understanding & planning**
   Turn a vague user goal into a **live task graph** (hierarchical plan) that can change as reality changes.

2. **Reflect-Plan-Act-Observe loop (RPAO)**
   Tight loop with explicit **reflection** after each action: “What happened? What failed? What next?”

3. **Self-debugging & patching**
   When code/tools fail, generate a **minimal diff**, run tests, roll forward or roll back automatically.

4. **Dynamic tool acquisition**
   Discover/ingest **new tools or APIs at runtime** (OpenAPI/MCP), synthesize wrappers, add to the skill library.

5. **Uncertainty & risk handling**
   Calibrate confidence, branch when uncertain, use A/B strategies, and fall back gracefully (e.g., degraded answers).

6. **Long-term memory**
   Separate **episodic** (what happened in this run), **semantic** (reusable facts/skills), and **vector** (chunks, citations).

7. **Adaptive IO layer**
   Detect rate limits, auth churn, schema drift; apply exponential backoff, circuit breakers, and automatic credential refresh.

8. **Checkpoints & resumability**
   Persist **graph state** and memory every step so runs survive crashes and can resume deterministically.

These eight map 1:1 to the components below.

---

## B. Target runtime architecture for HandyWriterzAi (v2)

Use **LangGraph** to orchestrate a persistent state machine (each node is a capability). Store state & memories in Postgres/pgvector and Redis (sessions/queues). Frontend streams the **graph state** and **reflection notes** live in your Next.js UI. ([GitHub][1])

**Core nodes (Python / FastAPI service):**

* **GoalInterpreter** → normalize user intent into a `TaskSpec`
* **Planner** → build/maintain a hierarchical plan (task graph) with branching criteria
* **SkillRouter** → route a step to the best tool/agent (few-shot tool selection + tool reputation)
* **Executor** → call tools, write code, run code in sandbox, gather observations
* **Critic** → evaluate outputs, detect hallucination, enforce constraints, request patch/redo
* **Researcher** → web + literature tools; expands scope if data is missing (vs. erroring out)
* **MemoryManager** → episodic logs, semantic summaries, vector chunks (citations)
* **RecoveryManager** → retries, backoff, circuit breaker, checkpoint/resume
* **SelfDebugger** → generate patch diffs, run tests, validate, apply, or revert
* **ToolIngestor** → load OpenAPI/MCP endpoints at runtime, generate wrappers, add to registry

**Persistence & infra (you already use these pieces):**
Postgres + **pgvector** for semantic memory; **Redis** for session/queue/SSE; **Cloudflare R2** for artifacts; Docker/Railway for deploy. ([GitHub][1])

---

# Folder map & key files (drop-in refactor)

```
/backend
  /src
    /api
      routes_tasks.py            # start/stop runs, stream tokens, graph viz feed
      routes_tools.py            # dynamic tool registry CRUD, health
      routes_memory.py           # episode logs, retrieval, exports
    /core
      types.py                   # TaskSpec, PlanStep, Action, Observation, Verdict
      state.py                   # GraphState (pydantic), budgets, checkpoints
      prompts.py                 # system prompts for Planner/Critic/Debugger
      llm.py                     # OpenRouter/OpenAI/Gemini/Kimi routers + retries
      graph.py                   # LangGraph DAG wiring, checkpointer binding
    /agents
      planner.py                 # builds/updates plan; handles dead-ends
      critic.py                  # quality gates, policy checks, hallucination flags
      executor.py                # tool calls, codegen, parse, structured outputs
      researcher.py              # web/lit retrieval, query expansion, source ranking
      self_debugger.py           # diff patching loop + tests
      tool_ingestor.py           # OpenAPI/MCP → Tool spec → Python wrapper
    /tools
      __init__.py                # registry interface
      web_search.py              # search/scrape/read, anti-bot delay, robots checks
      filesystem.py              # project FS access (scoped to sandbox)
      python_sandbox.py          # firejail/uv sandbox with resource limits
      citations.py               # source capture + page anchoring
      rate_limit.py              # adaptive backoff, token bucket per-provider
      ... your domain tools ...
    /memory
      episodic_repo.py           # step-by-step logs with Observations
      semantic_repo.py           # distilled notes & lessons learned
      vector_repo.py             # pgvector + chunkers for retrieval
    /runtime
      checkpointer_sql.py        # SQLAlchemy-backed LangGraph checkpointer
      budgets.py                 # token/time/$ budgets + kill switches
      eval.py                    # acceptance tests; SWE-like repair harness
    /evaluation
      tasks/
        test_api_rate_limit.yaml
        scrape_schema_drift.yaml
        repair_broken_tool.yaml
      harness.py                 # run tasks, compute pass/fail, export metrics
```

Frontend (Next.js):

```
/frontend/src
  /app
    /runs/[id]/page.tsx          # live DAG view, logs, budget controls (pause/abort)
  /components
    RunTimeline.tsx              # event stream
    GraphCanvas.tsx              # plan/graph visualization
    MemoryPeek.tsx               # episodic/semantic snapshots
```

---

# The repeatable autonomy loop (reference implementation)

### 1) Unified types

```py
# core/types.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

class TaskSpec(BaseModel):
    goal: str
    constraints: List[str] = []
    deliverables: List[str] = []
    budget_tokens: int = 200_000
    budget_seconds: int = 900

class PlanStep(BaseModel):
    id: str
    kind: Literal["research","write","code","evaluate","tool"]
    description: str
    depends_on: List[str] = []
    done: bool = False

class Action(BaseModel):
    step_id: str
    tool: str
    input: Dict[str, Any]

class Observation(BaseModel):
    step_id: str
    output: Any
    error: Optional[str] = None
    sources: List[str] = []

class Verdict(BaseModel):
    step_id: str
    status: Literal["pass","retry","patch","branch","fail"]
    notes: str
```

### 2) LangGraph wiring (nodes + persistence)

```py
# core/graph.py
from langgraph.graph import StateGraph, END
from .state import GraphState, sql_checkpointer
from ..agents import planner, executor, critic, self_debugger, researcher

g = StateGraph(GraphState)

g.add_node("plan", planner.run)
g.add_node("act", executor.run)
g.add_node("reflect", critic.run)
g.add_node("repair", self_debugger.run)
g.add_node("expand", researcher.run)

# transitions:
# plan -> act
g.add_edge("plan","act")
# act -> reflect
g.add_edge("act","reflect")
# reflect branching
g.add_conditional_edges(
  "reflect",
  lambda s: s.route,    # returns one of: "plan","repair","expand","END"
  {"plan":"plan","repair":"repair","expand":"expand","END":END}
)

graph = g.compile(checkpointer=sql_checkpointer())
```

### 3) Self-debugging loop

```py
# agents/self_debugger.py
def run(state: GraphState):
    failed = state.last_observation
    patch = llm_generate_patch(diff_context=failed)
    ok = run_tests_in_sandbox(patch)
    if ok:
        apply_patch(patch); state.notes.append("Patched ✅")
        state.route = "act"
    else:
        state.notes.append("Patch failed; branching to planner")
        state.route = "plan"
    return state
```

### 4) Dynamic tool ingestion (OpenAPI/MCP)

```py
# agents/tool_ingestor.py
def ingest_openapi(url: str):
    spec = fetch_json(url)
    wrapper_code = synthesize_wrapper_from_spec(spec)  # LLM-guided
    module = compile_to_module(wrapper_code)
    tools.register(spec["info"]["title"], module.call)
```

### 5) Adaptive IO & budgets

* Token/time/\$ **budgets enforced at the graph level**; kill switch on exceed.
* `rate_limit.py`: token bucket per provider + **exponential backoff** with jitter; classify errors (429 vs 5xx) and switch providers if necessary.
* **Circuit breaker** trips on repeated failures and routes back to Planner with a “constraints update”.

---

# Migration plan (do this in four focused phases)

## Phase 0 — Ground truth & safety rails (1–2 days)

* Add **SQL checkpointer** for LangGraph + Redis for live event streaming.
* Introduce **budgets** (tokens/time/\$) at GraphState level; expose to UI.
* Create **E2E acceptance tests** that prove autonomy (see below).

## Phase 1 — RPAO core (3–5 days)

* Implement **Planner → Executor → Critic** nodes and simple transitions.
* Wire **MemoryManager** (episodic logs, semantic distills, vector chunks).
* Add **Researcher** to expand scope when data missing (no hardcoded source lists).

## Phase 2 — Self-debug & tool growth (5–7 days)

* Add **SelfDebugger** with code patching & test harness.
* Build **ToolIngestor** for OpenAPI/MCP, register tools on the fly.
* Implement **Adaptive IO** (backoff, provider failover).

## Phase 3 — Frontend & ops (3–4 days)

* Live **DAG/Timeline** view, **pause/resume/abort**, and **memory peek**.
* Metrics: pass rate, retries, cost per successful deliverable.
* Canary suites; golden tasks; nightly regression.

Your repo already documents FastAPI, LangGraph, Postgres/pgvector, Redis, Next.js, Railway/R2—keep those; we’re upgrading behavior, not the stack. ([GitHub][1])

---

# Three acceptance tests that prove autonomy

1. **Rate-limit resilience**
   **Given** a tool that returns 429 for the first N calls
   **Expect**: backoff → budget-aware retry → succeed without human code changes.

2. **Out-of-scope research**
   **Given** a query with no hits in the local knowledge base
   **Expect**: Researcher expands sources, adds new tool (OpenAPI ingest), cites new evidence, completes deliverable.

3. **Broken tool repair**
   **Given** a tool with a schema drift (field renamed)
   **Expect**: Critic flags; SelfDebugger generates patch; tests pass; patch applied; plan resumes.

Each ships as a YAML task in `/backend/src/evaluation/tasks/*.yaml` with deterministic seeds and pass/fail rules.

---

# Concrete steps you can run today

**1) Create the graph state & checkpointer**

```bash
# backend
pip install langgraph sqlmodel sqlalchemy psycopg2-binary
# create table "checkpoints" (sql_checkpointer migration)
alembic revision -m "add checkpointer"; alembic upgrade head
```

**2) Add budgets & streaming**

* `GraphState` adds `budget_tokens`, `budget_seconds`, `budget_usd`.
* Emit SSE events from each node (your Redis streaming fits right in). ([GitHub][1])

**3) Implement Planner/Critic prompts**
Small, surgical system prompts:

* Planner: “Propose steps, uncertainty, branching tests, and stop conditions.”
* Critic: “Validate against constraints, detect hallucination, propose route: retry/patch/branch/end.”

**4) Ship the sandbox**

* `python_sandbox.py` uses **uv / venv** per run, resource limits (CPU seconds, memory), timeouts.
* Test runner: `pytest -q` inside sandbox; collect JUnit XML.

**5) Tool registry & dynamic ingestion**

* `/api/routes_tools.py`: `POST /tools/ingest-openapi` with a URL.
* Generated wrapper includes **spec-safe parameterization** and schema validation.

**6) Frontend observability**

* `/runs/[id]`: DAG canvas + timeline; buttons for Pause/Resume/Abort and budget override.
* Memo views: episodic log (every Action/Observation), semantic summary (“what we learned”).

**7) Bake the acceptance tests**

* Implement 3 YAML tasks + `harness.py` to run them CI-side; a run fails the build if autonomy behaviors regress.

---

# Transforming your existing “agents” (a repeatable recipe)

Take any current “agent” (LLM + hardcoded workflow) and:

1. **Wrap in a PlanStep**: define step goal, success test, deliverable contract.
2. **Move decision logic into Critic**: the Critic decides whether to retry, patch, branch, or end.
3. **Externalize tools**: list inputs/outputs; register in `/tools/*` with schemas and budget costs.
4. **Enable self-debug**: write minimal unit tests around the tool; failing tests trigger the patch loop.
5. **Attach memory hooks**: after each step, write episodic log and semantic distill; push citations into vector store.
6. **Define uncertain branches**: Planner lists “If X ambiguous, branch into A/B and pick winner by metric M.”
7. **Guard with budgets**: add `max_retries`, `max_cost`, and `max_seconds` per step; Critic enforces.
8. **Prove it**: add a YAML acceptance case that would have broken the old agent; ensure the new one adapts.

Run this recipe for your **Research Swarm**, **Writing Swarm**, and **QA Swarm** (named in your README) so each swarm can plan, reflect, repair, and grow tools live—no more fixed if-then rails. ([GitHub][1])

---

# What this buys you (tie back to your 3AM moment)

* **Self-correction**: Critic + SelfDebugger eliminate brittle, hand-coded error paths.
* **Scope expansion**: Researcher + ToolIngestor prevent “sorry, out of scope.”
* **Rate-limit sanity**: Adaptive IO treats providers like a portfolio, not a single point of failure.
* **Reproducibility**: Checkpoints + budgets + acceptance suites make autonomy measurable, not mystical.
* **Operator trust**: The UI shows *why* a decision was made (plan, reflections, evidence), not just the final text.

---

Awesome—let’s turn your user journeys into **autonomous, repeatable pipelines** that run themselves (and queue fairly for all users), with a **human-in-the-loop Turnitin checkpoint** that the agents drive end-to-end.

I’m mapping this onto your existing code layout (you already have `src/agent`, `src/api/workbench*.py`, `src/turnitin/*`, `src/services/*`, `src/db/*`, `src/workers/*`). We’ll add a cohesive **Autonomy V2** layer that:

* Orchestrates each journey as a LangGraph state machine,
* Persists state & logs,
* Schedules/queues work fairly across users,
* Pauses the graph at the Turnitin handoff, uploads to Workbench, waits for a **human upload of the Turnitin report**, then resumes automatically and iterates until success.

Below is the **end-to-end spec + drop-in modules**. Wherever I reference files, they’re designed to fit your current structure without breaking it.

---

# 1) Journeys & Use-Cases → Autonomous DAGs

## A) “Write from prompt” (new document)

**User intent:** “Write a 2,000-word essay on X with 10 UK sources.”
**Autonomous pipeline:**

1. **GoalInterpreter / Planner** → normalize spec, build steps, success gates (length, tone, #citations, similarity threshold, due date).
2. **Researcher** → search + source selection (your `nodes/search_*` + `source_filter.py` + `source_verifier.py`).
3. **Writer** → outline → draft with your `prompts/templates/*` and `writer.py`.
4. **QA Swarm** → fact\_checking, bias\_detection, originality\_guard, argument\_validation (you already have these).
5. **Citation Auditor** → enforce style & live link validation.
6. **Turnitin Handoff** → **agents** upload latest draft to Workbench and **pause** the run.
7. **Human uploads Turnitin report** (Workbench UI) → **agents** parse report, plan revisions, and **iterate** (Writer+QA loop) until similarity < target and quality gates pass.
8. **Finalize** → deliver doc + citations + report summary.

## B) “Rewrite & improve” (user uploads a draft)

Same as A, but step 2 uses **Rewrite** tools (`rewrite_agent.py`, `writer_migrated.py`), preserving meaning and citations. Turnitin loop is identical.

## C) “Research Pack” (no Turnitin)

Brief → scoped queries → filtered sources → annotated bibliography + key-claims matrix + short synthesis + citations. QA swarm runs; **no Turnitin**.

## D) “Slide deck from doc”

Ingest doc → extract sections → `slide_generator.py` → add speaker notes → QA. Optional human style tweak (no Turnitin).

## E) “Assignment Workbench flow”

Multi-section deliverables with deadlines (use your `/workbench_*` repos). Agents run A/B/C repeatedly per section; **each section** can have its own Turnitin loop and pass/fail gates.

---

# 2) Autonomy V2 graph per journey

Create a **single reusable graph** with conditional routes, configured per journey:

```
plan → act → reflect → (expand | repair | plan | turnitin_pause | END)
                         ↑
                  human_trigger (Turnitin report uploaded)
```

* **plan** = Planner builds/upgrades steps.
* **act** = Execute next step (research/write/rewrite/tool).
* **reflect** = Critic validates against gates (quality/citations/similarity target if known).
* **expand** = Researcher widens sources when evidence is weak.
* **repair** = Self-debugger patches broken tools/pipelines.
* **turnitin\_pause** = special node that uploads current artifact to Workbench and **yields control** until a **human uploads** the Turnitin report; the graph then resumes and iterates.

Where to put it:

```
src/autonomy_v2/
  core/{types.py,state.py,prompts.py,llm.py,graph.py}
  agents/{planner.py,executor.py,critic.py,researcher.py,self_debugger.py,turnitin_coordinator.py}
  tools/{registry.py,rate_limit.py,python_sandbox.py,web_search.py}
  memory/{episodic_repo.py,semantic_repo.py,vector_repo.py}
  runtime/{checkpointer_sql.py,budgets.py,eval.py}
  evaluation/{harness.py,tasks/*.yaml}
```

You keep your current `src/agent/*` intact; V2 runs in parallel and slowly replaces V1.

---

# 3) The Turnitin human-in-the-loop—precise mechanics

## States

* `turnitin_pending_upload` → agents posted the doc to Workbench (create assignment/submission artifact), waiting for human.
* `turnitin_report_ready` → human uploaded report (PDF/HTML/JSON), webhook fires.
* `turnitin_iterating` → agents parsed similarity report, planned edits, and are revising to reach target.
* `turnitin_satisfied` → thresholds met, resume normal completion.

## Storage tables (Postgres)

* `runs` (run\_id, user\_id, journey\_type, state, budgets, created\_at, updated\_at)
* `run_steps` (run\_id, step\_id, kind, status, payload, started\_at, finished\_at)
* `artifacts` (id, run\_id, type, path/url, meta, version)
* `turnitin_cycles` (id, run\_id, artifact\_id, status: pending\_upload|awaiting\_report|report\_ready|iterating|done, target\_similarity, observed\_similarity, human\_uploader\_id, report\_path, created\_at)
* `job_queue` (see section 4)

You already have Workbench repos; we’ll **reuse** them:

* Use `workbench_assignment_repo.py` / `workbench_submission_repo.py` to create/find the assignment/submission rows for each cycle.
* Store the draft as an artifact (R2 or local), link to Workbench submission.

## APIs

* `POST /v2/runs` → start an autonomy run (TaskSpec).
* `GET /v2/runs/{run_id}/events` → SSE stream (plan/actions/observations/verdicts).
* `POST /v2/turnitin/{run_id}/handoff` → internal call by **turnitin\_coordinator** to create a Workbench submission and put the graph in `turnitin_pending_upload`.
* `POST /v2/turnitin/{run_id}/report` → **Workbench webhook** (human action). Body: run\_id, cycle\_id, report\_url, meta. This **unblocks** the graph.
* `GET /v2/turnitin/{run_id}/status` → show current cycle status and target gates (for UI).

## Graph integration (pseudo-code snippets)

**Coordinator node** (`turnitin_coordinator.py`):

```python
def handoff(state):
    doc = latest_artifact(state.run_id, type="document")
    cycle = new_turnitin_cycle(
        run_id=state.run_id,
        artifact_id=doc.id,
        target_similarity=state.task.constraints_target_similarity or 15
    )
    workbench.create_submission(run_id=state.run_id, cycle_id=cycle.id, artifact=doc)
    state.route = "turnitin_pause"
    return state
```

**Pause & resume mechanics** (in `graph.py`):

* When route = `turnitin_pause`, the checkpointer writes a “waiting” marker and **returns control** to the queue worker. No more model calls are made.
* When `POST /v2/turnitin/{run_id}/report` arrives, we:

  1. Persist the report artifact and similarity metrics (if parsable).
  2. Enqueue a **resume job** for that run with route=`act`.
  3. The graph **continues**: `reflect` uses the similarity to decide `iterating` (retry/repair/plan) or `END`.

**Report parsing**:

* Parse PDF/HTML for:

  * Overall similarity score,
  * Sections flagged,
  * Sources matched.
* Emit a **revision plan** (“rephrase section 2, cite source X correctly”), feed to Writer/QA nodes, and iterate.

**Stopping condition**:

* `observed_similarity <= target_similarity` **and** QA swarm passes.
* Or, budgets/time exceeded → graceful end with best available draft and a “didn’t reach target” note.

---

# 4) Queueing for all users (fair, scalable)

You have `src/workers/*`. Add a **lightweight, Postgres-first queue** that works on Railway and plays nicely with Redis if present.

## Table

```sql
CREATE TABLE job_queue(
  id BIGSERIAL PRIMARY KEY,
  run_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  journey TEXT NOT NULL,
  priority INT DEFAULT 5,            -- 1=high, 10=low
  state TEXT NOT NULL,               -- queued|running|waiting_human|retry|done|failed
  scheduled_at TIMESTAMP NOT NULL,
  locked_by TEXT,
  locked_at TIMESTAMP,
  attempts INT DEFAULT 0,
  payload JSONB,
  created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX ON job_queue (state, scheduled_at);
```

## Worker loop (Python)

* `SELECT id FROM job_queue WHERE state='queued' AND scheduled_at<=now() FOR UPDATE SKIP LOCKED ORDER BY priority, scheduled_at LIMIT 1;`
* Mark `running`, set `locked_by`, `locked_at`.
* Invoke the **LangGraph step** for that `run_id`. The graph returns a new `route`:

  * `turnitin_pause` → set job state `waiting_human` (resume only when webhook arrives).
  * `queued` again with delay → exponential backoff.
  * `done|failed` → finalize.
* Heartbeat every N seconds; if a worker dies, `locked_at` ages out and another worker picks it up.

## Fairness & throttling

* **Per-user concurrency tokens**: only N concurrent jobs per user.
* **Budget accounting**: `budgets.py` enforces token/time/\$ budgets at node boundaries; if exceeded, route to `END` with a “budget reached” verdict.
* Optional: Redis rate buckets for provider APIs.

---

# 5) Concrete journey specs (what agents measure & enforce)

Each journey has a **contract** (acceptance gates). Put them in `config/orchestrator_policies.yaml` so operators can change them without code deploys.

**Write from prompt**

* Inputs: goal, due\_date, target\_length, target\_similarity, min\_citations, style.
* Gates:

  * min\_citations (UK/peer-reviewed proportion),
  * tone/style match,
  * grammar score ≥ threshold,
  * **Turnitin** similarity ≤ target.

**Rewrite & improve**

* Inputs: source doc, keep meaning/citations, target\_similarity, voice.
* Gates:

  * meaning preservation (chunk-level semantic similarity vs. source),
  * citation retention/upgrade,
  * **Turnitin** ≤ target.

**Research pack**

* Inputs: topic, scope, #sources, depth.
* Gates:

  * source quality mix (journals/government/NGOs),
  * zero hallucination (every claim traced),
  * structural completeness (claims matrix + annotated bib).

**Slides**

* Inputs: doc or outline, theme, length.
* Gates:

  * coverage of all main points,
  * reasonable slide density,
  * legible speaker notes.

Each gate is evaluated in **critic.py**, which decides to `retry`, `expand`, or `repair` (self-debug) and assigns the next route.

---

# 6) Minimal code stubs (drop-in)

### Start & Stream API (new routes; reuse your `src/api`)

```python
# src/api/autonomy_v2.py
from fastapi import APIRouter
from autonomy_v2.core.graph import graph
from autonomy_v2.core.state import GraphState, TaskSpec
from services.database_service import db

router = APIRouter(prefix="/v2")

@router.post("/runs")
def start_run(spec: TaskSpec):
    state = GraphState(task=spec)
    run = graph.invoke(state)  # writes first checkpoint
    enqueue(run_id=run["state"].run_id, user_id=current_user(), journey="write")
    return {"run_id": run["state"].run_id}

@router.post("/turnitin/{run_id}/report")
def turnitin_report(run_id: str, body: dict):
    cycle_id = body["cycle_id"]; url = body["report_url"]
    save_report(run_id, cycle_id, url)
    mark_cycle_report_ready(run_id, cycle_id)
    enqueue_resume(run_id)  # wakes the graph
    return {"ok": True}
```

### Coordinator node

```python
# src/autonomy_v2/agents/turnitin_coordinator.py
def pause_for_turnitin(state):
    doc = latest_artifact(state.run_id, "document")
    cycle = new_turnitin_cycle(state.run_id, doc.id, target_similarity=state.task.target_similarity or 15)
    workbench.create_submission(run_id=state.run_id, cycle_id=cycle.id, doc=doc)
    write_event(state.run_id, "note", {"turnitin_cycle_id": cycle.id, "status": "awaiting_report"})
    state.route = "turnitin_pause"
    return state
```

### Reflect node (Turnitin-aware)

```python
# src/autonomy_v2/agents/critic.py
def run(state):
    obs = state.last_observation
    metrics = collect_quality_metrics(state.run_id)  # citations, grammar, etc.
    if need_turnitin(metrics, state.task):
        state.route = "turnitin_pause"
        return state
    if meets_all_gates(metrics, state.task):
        state.route = "END"
        return state
    # else choose: expand (weak evidence), repair (tool fail), or act (retry)
    state.route = choose_next_route(metrics, obs)
    return state
```

---

# 7) Resuming after the human upload

* The **Workbench UI** (already there) allows a human to upload a Turnitin report to the matching submission/cycle.
* That triggers `POST /v2/turnitin/{run_id}/report` (webhook).
* A small parser extracts:

  * `overall_similarity`,
  * `top_sources`,
  * `flagged_passages` (offsets).
* The **Planner** updates the plan with “Revise sections A/B/C; rephrase; strengthen citations; replace weak sources”.
* The **Writer → QA → Critic** loop runs again.
* Stop when `overall_similarity <= target` and other gates pass—or when budgets/time are hit.

---

# 8) Observability & operator trust

* **SSE events** (`schemas/sse_events.py`) include: plan steps, actions, observations, verdicts, budget usage, turnitin cycle status.
* **Run viewer** in frontend: show DAG node status + a Turnitin strip with current target/observed similarity and a “waiting for human” badge.
* **Metrics**: success rate, avg similarity after 1/2/3 cycles, iterations per run, time per run, cost per success.

---

# 9) Acceptance tests (prove it works)

Add to `src/autonomy_v2/evaluation/tasks/`:

1. `rate_limit_resilience.yaml` → a search tool returns 429 N times; verify backoff & eventual success.
2. `out_of_scope_research.yaml` → no local KB hits; must ingest web sources and complete deliverable.
3. `turnitin_cycle.yaml` → simulate human upload by posting a mock report; assert the graph:

   * pauses at `turnitin_pause`,
   * resumes on webhook,
   * lowers similarity after a revision pass,
   * ends only when gate is met.

Wire `make test-autonomy` to fail CI unless all pass.

---

# 10) Rollout plan (fast + safe)

1. Land `src/autonomy_v2/*` + migrations (turnitin\_cycles, job\_queue).
2. Enable `/v2/runs` and `/v2/turnitin/*` routes.
3. Run acceptance tests locally → CI.
4. **Shadow-run** v2 for selected users; compare success & cost vs v1.
5. Flip default to v2; keep v1 behind a feature flag for rollback.

---

## Why this will feel truly autonomous

* **Scope expansion**: Researcher adds new sources/tools at runtime; no “sorry, not in the list.”
* **Self-healing**: Self-debugger patches broken tooling and re-tests.
* **Turnitin loop you designed**: Agents control the workflow, humans do the one part that must remain manual.
* **Fair queueing**: Everyone gets progress; no single power user starves the system.
* **Objective success**: Gates & acceptance tests make autonomy measurable.


