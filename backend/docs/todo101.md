# todo101 — Engineering Backlog to Productionize the Agentic System (Deep, Actionable, Sequenced)

This backlog operationalizes:
- The execution blueprint in [`markdown.plan.md`](backend/docs/plan.md:1).
- The program-level prompt in [`markdown.prompt.md`](backend/docs/prompt.md:1).
- The architecture and issues identified in [`markdown.agentic.md`](backend/docs/agentic.md:1), [`markdown.flows.md`](backend/docs/flows.md:1), and [`markdown.flowith.md`](backend/docs/flowith.md:1).

Principles
- Do-Not-Harm: additive, feature-flagged rollout, zero breaking changes without adapters.
- Contract-first: stabilize data/SSE schemas, then retrofit publishers and consumers.
- Traceable: each task references the intended file or construct with a clickable citation.
- Test-gated: unit + integration + contract tests per milestone.

Legend
- [ ] pending
- [-] in progress
- [x] done
- ⏳ blocked (include blocker note)
- 🧪 test
- 🚦 flag

Flags to introduce (centralized in settings):
- feature.sse_publisher_unified (default: off in prod, on in dev/stage)
- feature.params_normalization (default: off in prod, on in stage)
- feature.registry_enforced (default: warn-only in prod)
- feature.search_adapter (default: on)
- feature.double_publish_sse (shadow legacy + new, default: off; on in stage)

----------------------------------------------------------------
M0 — Foundations and Guardrails (Prep)
----------------------------------------------------------------

Config and Flags
- [ ] Define flags in settings object [`python.HandyWriterzSettings`](backend/src/config/__init__.py:1) and plumb via DI to publishers and router paths.
- [ ] Expose a GET /api/status flags subsection for visibility [`python.@app.get("/api/status")`](backend/src/main.py:1).

Observability Baseline
- [ ] Add run_id / correlation_id generation helper [`python.logging_context.py`](backend/src/services/logging_context.py:1).
- [ ] Ensure request-scoped correlation_id in logs via middleware [`python.RevolutionaryErrorMiddleware`](backend/src/middleware/error_middleware.py:1) hooked with logging context.

🧪 Tests
- [ ] Verify flags wiring through /api/status.
- [ ] Verify correlation_id presence in logs for /health and /api/analyze.

----------------------------------------------------------------
P1 — Contracts & SSE Foundation
----------------------------------------------------------------

P1.1 Canonical Params Normalization
- [ ] Implement normalizer [`python.normalize_user_params()`](backend/src/agent/routing/normalization.py:1)
  - Input: mixed camelCase/snake_case, enum strings or friendly names.
  - Output: canonical dict keys aligned to [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1) and [`python.ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1).
  - Map writeupType/document_type, referenceStyle/citation_style, educationLevel/academic_level, field/AcademicField, region/Region.
  - Derive: pages (from word_count), target_sources (from doc type & level).
- [ ] Integrate into [`python.UnifiedProcessor.process_message()`](backend/src/agent/routing/unified_processor.py:1) and /api/write construction path [`python.@app.post("/api/write")`](backend/src/main.py:1) behind 🚦 feature.params_normalization.

🧪 Unit
- [ ] tests/agent/test_normalization.py: mixed inputs → identical canonical dict.
- [ ] Analyzer score parity A/B logs pre/post flag.

P1.2 Unified SSE Publisher
- [ ] Implement [`python.SSEPublisher`](backend/src/agent/sse.py:1)
  - publish(conversation_id, type, payload, *, run_id=None)
  - Always json.dumps, add timestamp ISO 8601, enforce schema from [`markdown.flows.md`](backend/docs/flows.md:187).
- [ ] Retrofit publishers:
  - [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1) → start, routing, content, done, error.
  - BaseNode broadcast path (if present) to delegate to SSEPublisher consistently.
- [ ] Shadow mode: when 🚦 feature.double_publish_sse enabled, publish both legacy and unified (distinct channel suffix sse_legacy:conv).

🧪 Contract
- [ ] tests/contracts/test_sse_schema.py: JSON schema validation for all event types.
- [ ] tests/integration/test_chat_sse.py: start→routing→content→done/error round-trip via [`python.@app.get("/api/stream/{conversation_id}")`](backend/src/main.py:1).

P1.3 Simple Agent Import Stabilizer
- [ ] Add re-exports [`python.agent/simple/__init__.py`](backend/src/agent/simple/__init__.py:1)
  - from ..graph import build_gemini_graph as gemini_graph
  - from ..state import GeminiState
- [ ] Replace fragile imports in router paths if any.

🧪 Smoke
- [ ] tests/agent/test_simple_imports.py ensures UnifiedProcessor can import simple symbols.

----------------------------------------------------------------
P2 — Model Registry and Budget Enforcement
----------------------------------------------------------------

P2.1 Registry and Validation
- [ ] Create registry [`python.models/registry.py`](backend/src/models/registry.py:1)
  - load(model_config.yaml, price_table.json)
  - resolve(logical) → {provider, provider_model_id, pricing object}
  - validate(): fail on mismatch; warn on aliasable differences.
- [ ] Initialize at startup within lifespan [`python.FastAPI()`](backend/src/main.py:1). In dev/stage, fail-fast; in prod, warn unless 🚦 feature.registry_enforced strict.

P2.2 Budget Guard
- [ ] Implement [`python.services/budget.py`](backend/src/services/budget.py:1)
  - guard(estimated_tokens, role/model, tenant) → allow | deny(reason, code)
  - Plug into UnifiedProcessor before provider calls; emit SSE error if denied.

🧪 Tests
- [ ] tests/models/test_registry.py: mismatched IDs, valid mapping, alias resolution.
- [ ] tests/services/test_budget.py: threshold behavior, denial frames.

----------------------------------------------------------------
P3 — Search Normalization & Aggregator Alignment
----------------------------------------------------------------

P3.1 Adapter Layer
- [ ] Implement adapter [`python.agent/search/adapter.py`](backend/src/agent/search/adapter.py:1)
  - to_search_results(agent_name, payload) → list[SearchResult dict]
  - Handle shapes from Gemini/Perplexity/O3/Claude/OpenAI documented in [`markdown.agentic.md`](backend/docs/agentic.md:128).
  - Ensure consistent fields: title, authors, abstract/snippet, url, doi, pub_date, citation_count, source_type, relevance, credibility.

P3.2 Agent Patches
- [ ] Patch GeminiSearchAgent to append standardized entries into state["raw_search_results"].
- [ ] Patch PerplexitySearchAgent, O3SearchAgent, ClaudeSearchAgent, OpenAISearchAgent similarly.
- [ ] Remove or replace any _broadcast_progress(error=True) misuse noted in [`markdown.agentic.md`](backend/docs/agentic.md:136) with correct publisher API.

P3.3 Aggregator/Verifier/Filter Contract
- [ ] Verify Aggregator expects standardized SearchResult[] (no agent conditionals).
- [ ] Verify SourceVerifier consumes aggregated_sources → verified_sources.
- [ ] Align SourceFilter to prefer verified_sources; support aggregated_sources as fallback.

🧪 Tests
- [ ] tests/agent/test_search_adapter.py: synthetic payloads per agent → normalized list.
- [ ] tests/agent/test_aggregator_contract.py: mixed-agent runs → aggregated_sources valid.
- [ ] tests/agent/test_source_filter_contract.py: consumes verified_sources and produces filtered outputs.

----------------------------------------------------------------
P4 — Error Path Hardening & Observability
----------------------------------------------------------------

P4.1 Decorator Correctness
- [ ] Audit usages of [`python.with_retry()`](backend/src/services/error_handler.py:1), [`python.with_circuit_breaker()`](backend/src/services/error_handler.py:1), [`python.with_error_handling()`](backend/src/services/error_handler.py:1) for signature correctness.
- [ ] Remove unsupported kwargs from broadcast helpers per [`markdown.agentic.md`](backend/docs/agentic.md:224).

P4.2 Finally-block Guards
- [ ] Guard references to locals in finally; ensure they’re defined or set to sentinel values.

P4.3 Structured Logging
- [ ] Inject correlation_id in all logs/events.
- [ ] Add node_name and phase to progress/error frames for graph debuggability.

🧪 Tests
- [ ] tests/integration/test_error_paths.py: simulate provider failure → normalized SSE error without secondary exceptions; logs present correlation_id.

----------------------------------------------------------------
P5 — Security, Middleware Order, and Rate Limits
----------------------------------------------------------------

P5.1 Middleware Order Verification
- [ ] Assert Security → Error → CORS order in app assembly [`python.FastAPI()`](backend/src/main.py:1) and document in code comments.

P5.2 CSRF and JWT
- [ ] Ensure CSRF enforced on non-idempotent routes via [`python.CSRFProtectionMiddleware`](backend/src/middleware/security_middleware.py:1).
- [ ] Ensure JWT and @rate_limited decorators from [`python.SecurityService`](backend/src/services/security_service.py:1) on /api/chat, /api/write, and high-cost routes.

P5.3 Abuse/Cost Controls
- [ ] Per-IP/tenant burst + sustained limits on /api/chat and /api/write.
- [ ] Budget guard outcomes surfaced in responses and SSE frames.

🧪 Tests
- [ ] tests/security/test_csrf.py
- [ ] tests/security/test_rate_limits.py
- [ ] tests/security/test_jwt_required.py

----------------------------------------------------------------
P6 — Tests, CI, Docs, and Migration
----------------------------------------------------------------

P6.1 Test Suite Completion
- [ ] Unit: normalization, SSEPublisher, registry, adapters.
- [ ] Integration: chat SSE lifecycle, write workflow lifecycle, provider stream path.
- [ ] Contract: SSE schema validator, Aggregator input schema.

P6.2 CI
- [ ] Add GitHub Actions workflow to run unit/integration tests and code quality checks; cache dependencies; set coverage threshold.

P6.3 Docs
- [ ] Update [`markdown.flows.md`](backend/docs/flows.md:1) to reflect finalized SSE schema and remove truncation tail in File Reference Index (file ends mid-line).
- [ ] Extend [`markdown.flowith.md`](backend/docs/flowith.md:1) after derivatives: response packaging, client SSE consumption patterns, credit/billing updates.
- [ ] Append this backlog evolution to [`markdown.todo100.md`](backend/docs/todo100.md:1) with cross-links.

P6.4 Rollout
- [ ] Stage: enable feature.double_publish_sse and feature.params_normalization; capture diffs and errors.
- [ ] Prod: phased enablement; monitor SSE error rates and routing anomalies.

----------------------------------------------------------------
Backfill / Hygiene Tasks
----------------------------------------------------------------

Imports & Packaging
- [ ] Normalize relative imports across agent nodes to avoid “...agent.handywriterz_state” depth inconsistencies noted in [`markdown.agentic.md`](backend/docs/agentic.md:198).

Dead Code Removal
- [ ] Remove static methods in orchestrator referencing non-existent attributes per [`markdown.agentic.md`](backend/docs/agentic.md:78) or refactor to dynamic pattern only.

SSE Schema Publication
- [ ] Publish schema in docs and optionally as JSON Schema artifact exported by /api/status for SDK consumers.

Redis Clients Unification
- [ ] Consolidate to asyncio client or wrap both behind the SSEPublisher to avoid duplication and drift.

----------------------------------------------------------------
Deliverables Snapshot (Creates/Edits)
----------------------------------------------------------------
Creates:
- [`python.agent/routing/normalization.py`](backend/src/agent/routing/normalization.py:1)
- [`python.agent/sse.py`](backend/src/agent/sse.py:1)
- [`python.agent/simple/__init__.py`](backend/src/agent/simple/__init__.py:1)
- [`python.models/registry.py`](backend/src/models/registry.py:1)
- [`python.agent/search/adapter.py`](backend/src/agent/search/adapter.py:1)
- [`python.services/budget.py`](backend/src/services/budget.py:1)
- [`python.services/logging_context.py`](backend/src/services/logging_context.py:1)
- tests/* as enumerated above

Edits:
- [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1) — normalization, SSEPublisher, budget
- Agents (Gemini/Perplexity/O3/Claude/OpenAI) — adapter calls
- Aggregator/SourceVerifier/SourceFilter — contract enforcement
- [`python.FastAPI()`](backend/src/main.py:1) — registry init/validation, middleware assertions, status flags

----------------------------------------------------------------
Acceptance Criteria (Program-level DoD)
----------------------------------------------------------------
- SSE frames are JSON-only and conform to the schema in [`markdown.flows.md`](backend/docs/flows.md:187); contract tests green.
- Analyzer/Router/Graphs operate on normalized params uniformly; regression in analyzer scoring assessed via A/B logs.
- Aggregator ingests standardized SearchResult[] from all agents; SourceVerifier/Filter operate without agent-specific branches.
- Registry validates model IDs and pricing; requests exceeding budget are consistently denied with actionable SSE error frames.
- Error-handling paths are robust; no secondary exceptions; logs contain correlation_id and node phase.
- Security controls enforced (CSRF/JWT/rate limit); middleware order verified and documented.
- CI passes with coverage gate; docs updated; feature flags allow progressive rollout.

----------------------------------------------------------------
RACI (Condensed)
----------------------------------------------------------------
- Design authority: Architecture Owner (approves schemas and contracts).
- Implementers: Backend Engineers (P1–P5), QA (P6 tests), DevOps (CI).
- Reviewers: SRE (observability, error paths), Security (middleware/guards).

----------------------------------------------------------------
Risk Log (Active)
----------------------------------------------------------------
- Registry strictness can block startup in prod.
  - Mitigation: prod default warn-only; add /api/status registry panel; preflight config test.
- SSEPublisher refactor could regress streaming UX.
  - Mitigation: double-publish flag in stage; monitor client parser metrics; rollback switch.
- Normalization may change analyzer routing.
  - Mitigation: A/B logging and review thresholds before enabling in prod.

End of todo101
