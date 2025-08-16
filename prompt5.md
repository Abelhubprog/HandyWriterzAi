SYSTEM
Hook into existing services where possible. Keep prompts minimal. Use deterministic JSON mode where supported.

USER
Objective: Make Planner/Executor/Critic actually work with your LLM services and tool registry.

Constraints:
- Use services/model_registry.py or services/llm_service.py if present; otherwise add thin adapters in core/llm.py that call existing providers (openrouter/openai/gemini/anthropic).
- Executor must pick a tool via tools/registry.py; implement a trivial registry with one built-in tool (e.g., “echo” tool or google_web_search wrapper if available).
- Critic must decide pass/END vs retry/plan with simple rules.

TODOs:
1) core/llm.py: implement json_call/text_call with retries (use tools/rate_limit.py).
2) tools/registry.py: implement register_tool(name, func, schema), choose_tool(step) – start with a simple mapping (“research” → web_search; “write” → echo).
3) agents/*.py: replace stubs with working calls (planner builds 1–3 steps; executor calls the tool; critic routes END if output non-empty else plan).
4) Add minimal unit tests under src/tests or backend/tests validating “plan→act→reflect→END”.

Acceptance:
- Diffs for llm, registry, agents.
- Tests and a single `pytest -q` command block.
SYSTEM
Connect to existing LLM gateway and search tool. Handle rate limits with backoff. Keep prompts tiny and deterministic.

USER
Objective:
- Wire core/llm.py to your unified gateway (services/gateway.py + services/model_selector.py) if present; otherwise keep a safe fallback but prefer the real path.
- Wire tools/registry.py + tools/web_search.py to call your existing search tool (backend/src/tools/google_web_search.py) instead of the stub, if available.
- Update agents so Planner uses LLM JSON output (simple) and Executor uses the search tool for a "research" step and records URLs as sources. Critic ends if at least one source is found; otherwise route="plan".

Constraints:
- Before coding, READ:
  - backend/src/services/gateway.py
  - backend/src/services/model_selector.py
  - backend/src/tools/google_web_search.py
- Add rate-limit backoff in llm.complete() using autonomy_v2/tools/rate_limit.py.
- Keep network calls minimal and respect existing env/config (API keys already configured in repo).

TODOs:
1) core/llm.py: implement complete() and (if used) json_call()/text_call() using gateway+selector. Add backoff on 429/5xx.
2) tools/web_search.py: if google_web_search.py exists, wrap it; else fallback to the stub with a clear note in logs.
3) agents/planner.py: request 1–3 steps max with a tiny system prompt (already in prompts.py). If LLM errors, fallback to the single "research" step.
4) agents/executor.py: if next step.kind == "research", call web_search.search(). Set last_observation.output and .sources from returned URLs. Route to reflect.
5) agents/critic.py: END if `sources` present; else set route="plan".

Acceptance:
- Diffs for llm, web_search, planner, executor, critic.
- A new test under backend/src/tests or autonomy_v2/evaluation that runs one real cycle and prints 1+ sources.
- Shell block to run the test with `pytest -q` (or a python one-liner if tests folder structure is strict).
