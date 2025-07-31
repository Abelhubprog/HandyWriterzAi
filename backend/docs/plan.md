# Plan — Transform HandyWriterz Agentic System to Production-Ready

Purpose
- Convert the architecture and implementation described in:
  - [`markdown.agentic.md`](backend/docs/agentic.md:1)
  - [`markdown.flows.md`](backend/docs/flows.md:1)
  - [`markdown.flowith.md`](backend/docs/flowith.md:1)
  - [`markdown.redesign.md`](backend/docs/redesign.md:1)
  - [`markdown.todo100.md`](backend/docs/todo100.md:1)
into a hardened, production-grade system with unified contracts, standardized streaming, provider/model registry alignment, robust error handling, security enforcement, and test coverage.

Scope
- Backend agentic runtime: routing, analyzer, simple/advanced/hybrid flows, providers, SSE streaming, workflow events, RAG/evidence, formatting/QA/Turnitin.
- Non-breaking, additive-first approach (Do-Not-Harm). Backwards compatibility maintained; changes introduced behind flags where appropriate.
- Grounded in current code structure:
  - Entrypoints and SSE: [`python.FastAPI()`](backend/src/main.py:1), [`python.@app.post("/api/chat")`](backend/src/main.py:1), [`python.@app.get("/api/stream/{conversation_id}")`](backend/src/main.py:1)
  - Routing/Analyzer: [`python.class UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), [`python.class ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1)
  - Agents: [`python.build_gemini_graph()`](backend/src/agent/graph.py:1), [`python.GeminiState`](backend/src/agent/state.py:1), [`python.create_handywriterz_graph()`](backend/src/agent/handywriterz_graph.py:1), [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1)
  - Providers: [`python.ProviderFactory`](backend/src/models/factory.py:1), [`python.BaseProvider`](backend/src/models/base.py:1), [`python.OpenRouterProvider`](backend/src/models/openrouter.py:1), [`python.PerplexityProvider`](backend/src/models/perplexity.py:1)
  - Middleware/Services: [`python.RevolutionarySecurityMiddleware`](backend/src/middleware/security_middleware.py:1), [`python.RevolutionaryErrorMiddleware`](backend/src/middleware/error_middleware.py:1), [`python.SecurityService`](backend/src/services/security_service.py:1), [`python.with_retry()`](backend/src/services/error_handler.py:1), [`python.with_circuit_breaker()`](backend/src/services/error_handler.py:1)
  - Config: [`yaml.model_config.yaml`](backend/src/config/model_config.yaml:1), [`json.price_table.json`](backend/src/config/price_table.json:1), [`yaml.composites.yaml`](backend/src/graph/composites.yaml:1)

Key Problems To Solve
- UserParams fragmentation and casing mismatch; analyzer vs state vs nodes use different keys (see [`markdown.agentic.md`](backend/docs/agentic.md:90)).
- Mixed SSE serialization (json vs str(dict)); multiple publishers (see [`markdown.agentic.md`](backend/docs/agentic.md:103)).
- Search agent outputs heterogeneous; Aggregator expects standardized SearchResult (see [`markdown.agentic.md`](backend/docs/agentic.md:153)).
- ModelConfig vs PriceTable ID mismatch; missing registry to map logical→provider IDs (see [`markdown.agentic.md`](backend/docs/agentic.md:186)).
- Import inconsistencies and dead code; missing simple re-exports (see [`markdown.agentic.md`](backend/docs/agentic.md:196)).
- Error-path fragility; unsupported kwargs to broadcasters; finally blocks hazards (see [`markdown.agentic.md`](backend/docs/agentic.md:216)).
- Security posture must be enforced consistently (CSRF/rate limiting/JWT), and budgets per request.

Milestones and Phases

P1 — Contracts & SSE Foundation
Objectives:
- Canonicalize UserParams and insert normalization at routing boundary.
- Introduce a single SSEPublisher for all event emissions.
- Add simple agent re-exports for stable imports.

Changes:
1) Normalization utilities
   - New file: [`python.normalization.py`](backend/src/agent/routing/normalization.py:1)
     - normalize_user_params(inp: dict) → dict
       - Accepts camelCase or snake_case, maps to canonical keys
       - Validates enums (document_type, citation_style, field, region) against [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1)
       - Derives fields (pages, target_sources) if missing
     - validate_user_params(params: dict) → None | raises ValueError
2) SSEPublisher abstraction
   - New file: [`python.sse.py`](backend/src/agent/sse.py:1)
     - class SSEPublisher(redis_client)
       - publish(conversation_id, type, payload) → json, adds timestamp, conv_id
       - Shapes must match canonical frames in [`markdown.flows.md`](backend/docs/flows.md:399)
   - Refactor usage:
     - [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1) to use SSEPublisher for "start", "routing", "content", "done", "error".
     - Provide adapter for nodes (BaseNode.broadcast delegates to SSEPublisher).
3) Simple re-exports
   - New file: [`python.__init__`](backend/src/agent/simple/__init__.py:1)
     - from ..graph import build_gemini_graph as gemini_graph
     - from ..state import GeminiState

Acceptance:
- /api/chat and /api/write emit only JSON frames over SSE; no str(dict).
- Analyzer, UnifiedProcessor, state construction consume normalized params without casing errors.
- Simple path imports work via agent/simple.

P2 — Model Registry and Budget Enforcement
Objectives:
- Single mapping for logical model IDs to provider-specific IDs with pricing.
- Budget guards per request.

Changes:
1) Registry
   - New file: [`python.registry.py`](backend/src/models/registry.py:1)
     - load(model_config: path, price_table: path) → Registry
     - resolve(logical_id) → { provider, model_id, pricing }
     - validate() → raises on mismatches
   - Startup validation at app init in [`python.FastAPI()`](backend/src/main.py:1)
2) Budget guard
   - New file: [`python.budget.py`](backend/src/services/budget.py:1)
     - guard(estimated_tokens, role/model) → allow/deny with reason
   - Hook in UnifiedProcessor before provider calls; populate denial as SSE error frame.

Acceptance:
- Startup fails fast (non-prod) on registry mismatch with actionable logs; dev mode warns.
- Provider selection paths use registry-resolved IDs; pricing attached to usage reports.
- Requests exceeding budget are denied consistently with well-formed SSE error.

P3 — Search Normalization & Aggregator Alignment
Objectives:
- Ensure each agent yields standardized SearchResult list into state["raw_search_results"].
- Aggregator processes standardized input without knowledge of agent specifics.

Changes:
1) Adapters
   - New file: [`python.adapter.py`](backend/src/agent/search/adapter.py:1)
     - to_search_results(agent_name, payload) → list[SearchResult]
       - Robust mapping for Gemini/Perplexity/O3/Claude/OpenAI shapes.
2) Agent updates
   - Patch agent implementations to call adapter before appending to raw_search_results.
3) Aggregator verification
   - Adjust Aggregator if needed to only consume standardized entries; no agent conditionals.

Acceptance:
- Mixed agent runs produce Aggregator-ready raw_search_results consistently.
- SourceVerifier and SourceFilter consume expected keys seamlessly.

P4 — Error Path Hardening & Observability
Objectives:
- Fix broadcasting kwargs misuse, guard finally blocks, add correlation IDs.

Changes:
1) Decorator consistency
   - Update usage of [`python.with_retry()`](backend/src/services/error_handler.py:1), [`python.with_circuit_breaker()`](backend/src/services/error_handler.py:1), [`python.with_error_handling()`](backend/src/services/error_handler.py:1) to correct signatures.
2) Logging context
   - New helper: [`python.logging_context.py`](backend/src/services/logging_context.py:1)
     - correlation_id from conversation_id; inject into logs and SSE frames.
3) BaseNode broadcast
   - Ensure no unsupported kwargs; catch-and-log publisher failures without masking primary errors.

Acceptance:
- No secondary exceptions from error paths under synthetic failures.
- Logs include correlation_id; SSE error frames conform to schema.

P5 — Security, Middleware Order, and Rate Limits
Objectives:
- Validate middleware order (Security → Error → CORS).
- Enforce CSRF on non-idempotent verbs; apply rate limiting and JWT guards according to route sensitivity.

Changes:
1) Verify and document order in [`python.FastAPI()`](backend/src/main.py:1).
2) Ensure /api/chat, /api/write annotated with appropriate decorators from [`python.SecurityService`](backend/src/services/security_service.py:1).
3) Contract test for CSRF and rate limit responses.

Acceptance:
- Requests missing CSRF on state-changing verbs fail with normalized error.
- Rate limits enforced, producing consistent JSON errors.

P6 — Tests, CI, and Documentation Refresh
Objectives:
- Achieve coverage on normalization, SSE, registry, adapters, and critical flows.
- Update docs to match final behavior.

Changes:
1) Tests
   - Unit:
     - tests/agent/test_normalization.py
     - tests/sse/test_publisher.py
     - tests/models/test_registry.py
     - tests/agent/test_adapter.py
   - Integration:
     - tests/integration/test_chat_sse.py (start→routing→content→done/error)
     - tests/integration/test_write_workflow.py (workflow_start→progress→complete/failed)
     - tests/integration/test_provider_stream.py (stream=true path)
   - Contract:
     - tests/contracts/test_sse_schema.py (validate frames against canonical)
2) CI
   - Add workflow to run tests, lint, and enforce minimum coverage.
3) Docs
   - Update:
     - [`markdown.flows.md`](backend/docs/flows.md:1) SSE schema final
     - [`markdown.flowith.md`](backend/docs/flowith.md:1) journey updates
     - Append checklist deltas to [`markdown.todo100.md`](backend/docs/todo100.md:1) and new todo101.md

Risk Register and Mitigations
- Registry strictness may block startup in prod if misconfigured.
  - Mitigation: fail-fast in non-prod; explicit override flag in prod plus alarms.
- SSEPublisher refactor could regress stream delivery.
  - Mitigation: shadow mode (double-publish) behind feature flag for one release.
- Normalization could alter analyzer scoring.
  - Mitigation: A/B compare analyzer outputs pre/post normalization in logs; tune mapping.

Rollout Strategy
- Phase-gate features with flags:
  - feature.sse_publisher_unified
  - feature.params_normalization
  - feature.registry_enforced
  - feature.search_adapter
- Canary deploy in staging; capture metrics and error rates.
- Progressive enablement by route (start with /api/analyze and /api/chat simple).

Acceptance Criteria Summary (Definition of Done)
- SSE: Only JSON frames, conform to canonical in [`markdown.flows.md`](backend/docs/flows.md:399); verified by contract tests.
- Params: Analyzer, Router, Graphs consume normalized params; no casing errors in logs.
- Search: Aggregator ingests SearchResult[] from all agents; SourceVerifier/Filter work unchanged.
- Registry: Startup validation; all provider invocations go through registry; budgets enforced.
- Errors: No decorator/broadcast misuse; correlation_id everywhere; structured logs.
- Security: CSRF/rate limits/JWT enforced per route; middleware order verified.
- Tests/CI: All green; coverage threshold met.

Work Breakdown Checklist

P1 (Contracts & SSE)
- [ ] Implement [`python.normalization.py`](backend/src/agent/routing/normalization.py:1)
- [ ] Implement [`python.sse.py`](backend/src/agent/sse.py:1) and integrate with UnifiedProcessor and BaseNode
- [ ] Add [`python.agent/simple/__init__.py`](backend/src/agent/simple/__init__.py:1)
- [ ] Unit tests for normalization and SSEPublisher
- [ ] Feature flags wired

P2 (Registry & Budget)
- [ ] Implement [`python.registry.py`](backend/src/models/registry.py:1)
- [ ] Implement [`python.budget.py`](backend/src/services/budget.py:1)
- [ ] Validate at startup; add tests
- [ ] Integrate in UnifiedProcessor/provider paths

P3 (Search & Aggregator)
- [ ] Implement [`python.adapter.py`](backend/src/agent/search/adapter.py:1)
- [ ] Patch agents to use adapter
- [ ] Verify Aggregator contract; tests

P4 (Errors & Observability)
- [ ] Fix decorator usages and finally blocks
- [ ] Add [`python.logging_context.py`](backend/src/services/logging_context.py:1)
- [ ] Structured logs with correlation_id; tests

P5 (Security)
- [ ] Validate middleware order
- [ ] Apply CSRF/rate limit/JWT guards
- [ ] Contract tests for security responses

P6 (Tests, CI, Docs)
- [ ] Add unit/integration/contract tests
- [ ] Configure CI workflow
- [ ] Refresh docs: [`markdown.flows.md`](backend/docs/flows.md:1), [`markdown.flowith.md`](backend/docs/flowith.md:1)
- [ ] Update todos in todo100.md and create todo101.md

Cross-References
- Entrypoints and SSE: [`python.@app.post("/api/chat")`](backend/src/main.py:1), [`python.@app.get("/api/stream/{conversation_id}")`](backend/src/main.py:1)
- Router/Analyzer: [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), [`python.ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1)
- Agents: [`python.build_gemini_graph()`](backend/src/agent/graph.py:1), [`python.create_handywriterz_graph()`](backend/src/agent/handywriterz_graph.py:1)
- Providers: [`python.ProviderFactory`](backend/src/models/factory.py:1)
- Config/Pricing: [`yaml.model_config.yaml`](backend/src/config/model_config.yaml:1), [`json.price_table.json`](backend/src/config/price_table.json:1)
- Middleware/Errors: [`python.RevolutionarySecurityMiddleware`](backend/src/middleware/security_middleware.py:1), [`python.RevolutionaryErrorMiddleware`](backend/src/middleware/error_middleware.py:1), [`python.with_retry()`](backend/src/services/error_handler.py:1)

End of plan

---

Feature Flags Summary and Rollout (Authoritative)

Flags
- feature.sse_publisher_unified: unified SSE envelopes for all events; default off in prod.
- feature.double_publish_sse: publish legacy + unified simultaneously; use in staging first.
- feature.params_normalization: apply parameter normalization at routing boundary; default off in prod.
- feature.registry_enforced: fail-fast on registry mismatch at startup; warn-only in prod by default.
- feature.search_adapter: normalize agent outputs to SearchResult[] for Aggregator; default on.

Rollout
1) Stage: feature.params_normalization = on; feature.double_publish_sse = on.
2) Prod: enable feature.sse_publisher_unified after client compatibility proven.
3) Enable feature.registry_enforced after audit and CI green.
4) Keep feature.search_adapter on with integration tests.

Visibility and Ops
- /api/status exposes features.flags and registry status via [`python.@app.get("/api/status")`](backend/src/main.py:1).
- Logs include correlation_id; SSE error frames adhere to schema in [`markdown.flows.md`](backend/docs/flows.md:399).
