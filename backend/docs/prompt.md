# Production Readiness Transformation Prompt — HandyWriterz Agentic System

Purpose
- Provide a single, comprehensive execution prompt to plan and drive the transformation of the current agentic system to production grade, completing pending development and hardening reliability, security, and observability. The prompt is grounded in existing documentation and code.
- Sources to ground decisions and acceptance:
  - [`markdown.agentic.md`](backend/docs/agentic.md:1)
  - [`markdown.flows.md`](backend/docs/flows.md:1)
  - [`markdown.flowith.md`](backend/docs/flowith.md:1)
  - [`markdown.redesign.md`](backend/docs/redesign.md:1)
  - [`markdown.todo100.md`](backend/docs/todo100.md:1)
  - Backend code: [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), [`python.ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1), [`python.create_handywriterz_graph()`](backend/src/agent/handywriterz_graph.py:1), [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1), [`python.build_gemini_graph()`](backend/src/agent/graph.py:1), [`python.GeminiState`](backend/src/agent/state.py:1), [`python.ProviderFactory`](backend/src/models/factory.py:1), [`python.BaseProvider`](backend/src/models/base.py:1), [`python.FastAPI()`](backend/src/main.py:1).

Context (from current docs)
- Schema fragmentation across three UserParams shapes and mixed casing; see [`markdown.agentic.md`](backend/docs/agentic.md:90) and analyzer expectations.
- SSE event divergence between JSON publishing and stringified dict; see [`markdown.agentic.md`](backend/docs/agentic.md:103).
- Heterogeneous search agent payloads vs Aggregator contract; see [`markdown.agentic.md`](backend/docs/agentic.md:153).
- Model ID mismatch between config YAML vs price table; see [`markdown.agentic.md`](backend/docs/agentic.md:186).
- Import hygiene, dead code (static methods unused) and relative vs absolute import inconsistencies; see [`markdown.agentic.md`](backend/docs/agentic.md:196).
- Error-path issues (unsupported kwargs, finally blocks with undefined locals); see [`markdown.agentic.md`](backend/docs/agentic.md:216).
- Flow coverage in [`markdown.flows.md`](backend/docs/flows.md:25) and end-to-end trace in [`markdown.flowith.md`](backend/docs/flowith.md:22) define target runtime behaviors and SSE contracts.

Primary Objectives
1) Canonical Schemas and Normalization
- Introduce a canonical UserParams schema and a normalization layer that:
  - Accepts external inputs (camelCase, snake_case, enums or strings).
  - Outputs a single normalized dict used by Analyzer, Router, and Graphs.
- Acceptance: Analyzer, UnifiedProcessor, HandyWriterzState, and search nodes consume normalized params without casing/key mismatches.

2) SSE Standardization
- Create a single SSEPublisher abstraction ensuring all event frames are JSON using the same envelope across UnifiedProcessor and graph nodes.
- Acceptance: All SSE frames on sse:{conversation_id} conform to a documented JSON schema; no str(dict) variants.

3) Search Normalization and Aggregation Contract
- Ensure every search agent appends standardized SearchResult dicts to state["raw_search_results"]. Add adapters if agents produce specialized payloads.
- Acceptance: AggregatorNode consumes SearchResult[] from all agents without agent-specific conditionals; SourceVerifier/SourceFilter accept expected keys.

4) Model Registry and Pricing Alignment
- Introduce a model registry mapping logical names to concrete provider IDs with pricing from price_table.json and defaults from model_config.yaml. Validate at startup.
- Acceptance: Requests referencing logical IDs resolve deterministically to provider IDs with pricing, or fail fast with actionable logs.

5) Import Hygiene and Dead Code Removal
- Standardize relative imports within package, remove unused static methods in orchestrator, and add re-exports for simple graph.
- Acceptance: import graph passes; static analysis finds no dead orchestrator method references; simple path imports are stable via agent/simple.

6) Error Path Hardening and Observability
- Unify error decorators usage, remove unsupported kwargs, guard finally blocks, and ensure structured logging with correlation IDs.
- Acceptance: No exceptions caused by error handlers; structured logs include correlation IDs; SSE error frames follow the canonical shape.

7) Security and Budget Controls
- Confirm middleware order; ensure rate limiting, CSRF for non-idempotent verbs, and budget enforcement per request using registry prices.
- Acceptance: Security middleware order verified; budget checks enforce configured caps with sensible error frames.

8) Testing and CI/CD
- Add unit tests for normalization, SSEPublisher, model registry mapping, Aggregator adapters; integration tests for /api/chat and /api/write SSE lifecycles; contract tests for event schema.
- Acceptance: Test suite runs green; CI gate enforces tests and lint; minimal coverage thresholds.

Constraints
- Do-Not-Harm: All changes are additive or behind flags; no breaking removal without adapters.
- Backward Compatibility: Maintain existing endpoints and message shapes; only standardize publishers under the hood.
- Observability: Emit structured logs for all new components.

Workstreams and Prompts

WS1 — Schema Normalization
Inputs: [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), [`python.ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1), [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1), [`markdown.agentic.md`](backend/docs/agentic.md:90)
Task:
- Implement normalization utils with a canonical schema. Map camelCase to snake_case, harmonize enums, and calculate derived fields (pages, target_sources).
- Insert normalization at UnifiedProcessor boundary and write path.
Deliverables:
- normalization.py with normalize_user_params() and validate_user_params().
- Tests covering mixed inputs and expected normalized output.

WS2 — SSEPublisher Abstraction
Inputs: [`python.FastAPI()`](backend/src/main.py:1), [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), nodes broadcast code referenced in [`markdown.agentic.md`](backend/docs/agentic.md:103)
Task:
- Build SSEPublisher with publish_event(conversation_id, type, payload) that always json.dumps() and manages timestamps and identifiers.
- Replace existing mixed publishing with a single abstraction.
Deliverables:
- agent/sse.py with SSEPublisher and usage in UnifiedProcessor and BaseNode.
- Event schema reference doc block matching [`markdown.flows.md`](backend/docs/flows.md:399).

WS3 — Search Normalization + Aggregator Adapters
Inputs: [`markdown.agentic.md`](backend/docs/agentic.md:153), Aggregator expectations.
Task:
- Implement adapters that convert specialized agent outputs to standardized SearchResult dicts. Backfill agents to call adapter before appending to raw_search_results.
Deliverables:
- search/adapter.py with to_search_results(payload, agent_name).
- Update agents to use adapter; tests verifying Aggregator can ingest outputs from all agents.

WS4 — Model Registry and Pricing
Inputs: [`yaml.model_config.yaml`](backend/src/config/model_config.yaml:1), [`json.price_table.json`](backend/src/config/price_table.json:1), [`markdown.agentic.md`](backend/docs/agentic.md:186)
Task:
- Create models/registry.py that validates mapping at startup; provide resolve(logical_id) → {provider, model_id, pricing}.
- Introduce a budget guard callable to enforce per-request caps.
Deliverables:
- registry.py with load/validate; budget.py with guard.
- Startup validation and logs; tests for mismatches.

WS5 — Import Hygiene and Re-exports
Inputs: [`markdown.agentic.md`](backend/docs/agentic.md:196)
Task:
- Add `agent/simple/__init__.py` re-exports for gemini_graph and GeminiState. Normalize imports in orchestrator and nodes.
Deliverables:
- agent/simple/__init__.py
- Lint pass for imports.

WS6 — Error-Path Hardening and Observability
Inputs: [`markdown.agentic.md`](backend/docs/agentic.md:216), [`python.RevolutionaryErrorMiddleware`](backend/src/middleware/error_middleware.py:1)
Task:
- Remove unsupported kwargs to _broadcast_progress; guard finally blocks; add correlation IDs to logs and SSE frames.
Deliverables:
- Error decorator fixes; logging context utilities; tests with simulated failures.

WS7 — Security and Budget Controls
Inputs: [`python.security_middleware`](backend/src/middleware/security_middleware.py:1), [`python.SecurityService`](backend/src/services/security_service.py:1)
Task:
- Verify middleware order; ensure CSRF on state-changing routes; add @rate_limited and budget enforcement patches for /api/chat and /api/write.
Deliverables:
- Security checklist; code patches; tests for CSRF/rate limit.

WS8 — Testing and CI
Task:
- Unit tests: normalization, SSEPublisher, registry.
- Integration: /api/chat SSE lifecycle; /api/write workflow events.
- Contract tests: JSON schema validation for SSE events.
Deliverables:
- tests/agent/test_normalization.py, tests/sse/test_publisher.py, tests/models/test_registry.py, tests/integration/test_chat_sse.py, tests/integration/test_write_workflow.py

Acceptance Criteria (Definition of Done)
- All SSE frames are valid JSON and match canonical schema in [`markdown.flows.md`](backend/docs/flows.md:399).
- Analyzer, Router, and Graphs receive normalized UserParams consistently.
- Aggregator processes results from all search agents with no agent-specific branches.
- Model registry validates config/pricing; startup fails clearly on mismatch.
- Error middleware and decorators produce structured, actionable errors; no secondary exceptions.
- Security middleware order validated; CSRF and rate limiting enforced where applicable.
- Test suite green; CI gate enforced; logs structured with correlation IDs.

Rollout and Risk Mitigation
- Feature flags for SSE standardization and normalization; staged rollout by environment.
- Keep adapters until all agents natively emit SearchResult. Remove once coverage reaches 100%.
- Fail-fast on model registry mismatch in non-production; warn in dev with auto-fix suggestions.

Sequencing (High-level)
- P1: SSEPublisher + Normalization + Simple re-exports.
- P2: Model registry + budget guard.
- P3: Search adapters + Aggregator contract verification.
- P4: Error-path hardening + observability.
- P5: Security enforcement + rate limits.
- P6: Integration tests + CI gating.

Artifacts to update as work progresses
- [`markdown.plan.md`](backend/docs/plan.md:1)
- [`markdown.todo100.md`](backend/docs/todo100.md:1) and new todo101.md for incremental tasks
- [`markdown.flows.md`](backend/docs/flows.md:1) to reflect finalized SSE schema and flows
- [`markdown.flowith.md`](backend/docs/flowith.md:1) to reflect end-to-end with new adapters and registry

End of prompt
