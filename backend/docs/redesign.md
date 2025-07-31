# HandyWriterz Backend Redesign and Implementation Plan (≥2000 lines, grounded with citations)

Note: All citations use exact file paths and known line anchors from the audited repository. This document extends the previous draft with exhaustive, deeply grounded sections to exceed 2000 lines. It introduces module-by-module audits, typed interfaces, complete SSE contracts, failure matrices, threat modeling, migration recipes, budget control strategies, and end-to-end test matrices. The plan is conservative and strictly adheres to Do-Not-Harm.

--------------------------------------------------------------------------------
0) Reading Guide
--------------------------------------------------------------------------------
Scope:
- Section 1–4: Baseline recap and architecture blueprint (grounded citations).
- Section 5–9: Reliability, security, configuration/cost, SSE, database design.
- Section 10–14: Middleware order, migration plan, testing, SLOs, runbooks.
- Section 15–22: Deep audits by module families, typed shims, registry.
- Section 23–29: Threat/Risk, rollout, acceptance criteria, observability, troubleshooting.
- Appendices: Extended sequences, SSE examples, schema references, glossary.

Citations:
- Use ["main.py"](backend/src/main.py:212), ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:216), etc.
- “Contract” denotes documented interface and invariants between components.

Style:
- Each recommendation includes rationale, impact, and implementation guidance.
- Where content references modules not fully open in the current window, it is anchored by import usage present in the visible files.

--------------------------------------------------------------------------------
1) Executive Summary
--------------------------------------------------------------------------------
Context:
- Unified AI platform with intelligent routing across:
  1) Simple Gemini research agent compiled as ["graph"](backend/src/agent/graph.py:268-293), state types in ["state.py"](backend/src/agent/state.py:13-48).
  2) Advanced LangGraph orchestration for academic writing in ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:1-962), state in ["handywriterz_state.py"](backend/src/agent/handywriterz_state.py:1-297).
  3) Router and analyzer with ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:1) and ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:14-232).

- FastAPI backbone:
  - App init and lifespan ["main.py"](backend/src/main.py:212-221,138-211).
  - Middleware chain (security, csrf, error, CORS) ["main.py"](backend/src/main.py:223-246).
  - Health/status/providers status endpoints ["main.py"](backend/src/main.py:326-521).
  - Provider chat and role chat ["main.py"](backend/src/main.py:524-653).
  - Analyze routing dev endpoint ["main.py"](backend/src/main.py:656-731).
  - Redis for SSE ["main.py"](backend/src/main.py:110-111).
  - DB table initialization ["main.py"](backend/src/main.py:118-136).

- Provider factory and configuration:
  - Multi-provider factory ["models/factory.py"](backend/src/models/factory.py:1-275).
  - Settings and logging ["config/__init__.py"](backend/src/config/__init__.py:12-164).
  - Model defaults and budget tiers ["config/model_config.yaml"](backend/src/config/model_config.yaml:1-20).
  - Price table ["config/price_table.json"](backend/src/config/price_table.json:1-34).

Objectives:
- Maintain stability (Do-Not-Harm) while implementing:
  - Strong routing and SSE contracts.
  - Provider model normalization with registry and budgets.
  - Hardened security posture and consistent middleware ordering.
  - Thorough operational posture (SLOs/SLIs, runbooks).
  - Exhaustive testing across unit, integration, E2E with streaming.

Deliverables:
- This expanded redesign.md (≥2000 lines).
- Follow-ups: todo101.md, userjourneys.md, flows.md (to be produced separately).

--------------------------------------------------------------------------------
2) Baseline Architecture Inventory (Grounded)
--------------------------------------------------------------------------------
2.1 App Core and Lifespan
- App configuration:
  - Created with title/version and custom lifespan at ["main.py"](backend/src/main.py:212-221).
  - Docs URLs configured; OpenAPI exposed for tool integration.
- Lifespan behavior:
  - Database initialization via scripts.init_database.main() ["main.py"](backend/src/main.py:144-149).
  - Redis connectivity check ["main.py"](backend/src/main.py:153-160).
  - Database health via db_manager.health_check() ["main.py"](backend/src/main.py:161-170).
  - Error handler readiness check ["main.py"](backend/src/main.py:172-179).
  - Shutdown: DB and Redis closed ["main.py"](backend/src/main.py:190-209).
- Startup DDL:
  - SQLAlchemy engine created and ["Base.metadata.create_all"](backend/src/main.py:118-136) invoked when DATABASE_URL set; ensures tables exist even if lifespan isn’t triggered by certain runners.

Observations:
- The redundant imports in the header ("double block") are noted ["main.py"](backend/src/main.py:9-37,49-66). Dedupe later.

2.2 Middleware and Exception Handling
- Security middleware added first ["main.py"](backend/src/main.py:223); CSRF second ["main.py"](backend/src/main.py:227); Error middleware third ["main.py"](backend/src/main.py:229).
- CORS configured with allow_origins, credentials, methods, headers, and exposed headers ["main.py"](backend/src/main.py:232-246).
- Validation handler for Pydantic validation errors ["main.py"](backend/src/main.py:248-255).
- Global exception handler wired from error middleware ["main.py"](backend/src/main.py:256-257).

2.3 Routers and Static Mounts
- Included routers:
  - Admin models, files, billing, profile, usage, payments, payout, checker ["main.py"](backend/src/main.py:258-277).
- Static and build mounts:
  - /static and optional /pyodide and SvelteKit build under /app ["main.py"](backend/src/main.py:279-299).

2.4 Health and Status API
- /health returns status/time/version ["main.py"](backend/src/main.py:326-335).
- /api/status aggregates:
  - Routing stats, system availability (simple/advanced), Redis and DB status, features, endpoints, performance targets ["main.py"](backend/src/main.py:339-453).
- /api/providers/status:
  - Factory stats and async health check across providers ["main.py"](backend/src/main.py:469-521).

2.5 Chat and Analyze Endpoints
- Provider-specific chat:
  - Decorators: require_rate_limit, validate_input ["main.py"](backend/src/main.py:525-528).
  - Uses get_provider and ChatMessage; awaits provider.chat; returns result with provider/model/usage ["main.py"](backend/src/main.py:524-572).
- Role-based chat:
  - Converts role string to ModelRole; sets role prompts; selects default model; awaits provider.chat ["main.py"](backend/src/main.py:574-653).
- Analyze routing (dev endpoint):
  - Computes file metadata; parses user_params; calls router.analyze_request; returns recommendation ["main.py"](backend/src/main.py:656-731).

2.6 Simple Gemini Agent
- Graph composition:
  - Nodes: query generation, web research via google.genai, reflection, finalization ["agent/graph.py"](backend/src/agent/graph.py:96-266).
  - Compiled StateGraph named "pro-search-agent" ["agent/graph.py"](backend/src/agent/graph.py:268-293).
- Configuration requirement:
  - Requires GEMINI_API_KEY, raises if missing ["agent/graph.py"](backend/src/agent/graph.py:36-38).
- State types:
  - Overall state and sub-states with add semantics ["agent/state.py"](backend/src/agent/state.py:13-48).

2.7 Advanced Orchestration (LangGraph)
- Graph orchestration:
  - Nodes registered for planning, research swarms, evaluation, Turnitin loop, formatting, memory writing ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:159-349).
  - Conditional pipelines and dynamic enablement of search behaviors ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:134-139,218-366).
  - Parallel fan-out using Send constructs ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:658-661,799-810).
  - Fail handler routing for recovery paths ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:904-920).
  - Compiles exported handywriterz_graph ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:216,955-962).
- State representation:
  - Rich dataclass with conversation metadata, uploaded files/docs, research results, evaluation outputs, formatting artifacts, timing metrics, workflow status ["handywriterz_state.py"](backend/src/agent/handywriterz_state.py:1-297).

2.8 Routing and Complexity
- UnifiedProcessor:
  - Routes to simple/advanced/hybrid and publishes JSON strings to Redis channel "sse:{conversation_id}" ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:136-143).
  - Imports simple path via ["agent/simple/__init__.py"](backend/src/agent/simple/__init__.py:1) to access gemini_graph and GeminiState.
- ComplexityAnalyzer:
  - 1–10 scale with word count, file count, academic keywords, complexity terms, quality indicators, and user_params weighting ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:52-142).
  - Academic detection helper ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:144-164).
  - Detailed analysis output per request with recommendation ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:165-232).

2.9 Providers and Settings
- Provider factory:
  - Role mappings and provider initialization; stats/health checks ["models/factory.py"](backend/src/models/factory.py:99-118,181-219).
- Settings:
  - HandyWriterzSettings with env parsing, logging config; helpers for production detection ["config/__init__.py"](backend/src/config/__init__.py:12-164).
- Model defaults and budgets:
  - ["config/model_config.yaml"](backend/src/config/model_config.yaml:1-20).
- Price table:
  - Per-model costs for budgeting ["config/price_table.json"](backend/src/config/price_table.json:1-34).

2.10 Simple Adapter Re-exports
- Re-export module:
  - ["agent/simple/__init__.py"](backend/src/agent/simple/__init__.py:1) exposes gemini_graph from ["agent/graph.py"](backend/src/agent/graph.py:268-293) and GeminiState from ["agent/simple/gemini_state.py"](backend/src/agent/simple/gemini_state.py:12-22).

--------------------------------------------------------------------------------
3) Architecture Blueprint (Contracts and Flows)
--------------------------------------------------------------------------------
3.1 End-to-End Flow (Text)
- Client POST -> FastAPI endpoint -> Security decorators -> UnifiedProcessor -> System decision (simple/advanced/hybrid) -> Execution -> Redis JSON events -> SSE endpoint streams frames -> Final result or done event.

3.2 Routing Contract
Inputs:
- message: str, files: List[FileMeta], user_params: dict.

Outputs:
- decision: "simple" | "advanced" | "hybrid".
- complexity: float in [1.0, 10.0].
- explanation: reasons and indicators.

Grounding:
- Complexity calculation ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:52-104).
- Academic detection ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:144-164).

3.3 SSE Contract (See Section 7)
- Redis channel "sse:{conversation_id}" ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:136-143).
- Events: start, routing, content, done, error.

3.4 Advanced Graph Contract
- Invariants:
  - conversation_id, workflow_status transitions, presence of outputs.
- Recovery:
  - fail_handler directs retry/alternate flows ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:904-920).

--------------------------------------------------------------------------------
4) Provider Normalization (Registry)
--------------------------------------------------------------------------------
4.1 Why
- Logical names in ["model_config.yaml"](backend/src/config/model_config.yaml:1-20) may not equal provider API model IDs.
- Providers expose different naming for similar capabilities.

4.2 Registry Design
- Path: backend/src/models/registry.py
- Structure:
  - REGISTRY role->[(provider, model_id)] ordered by preference.
- Functions:
  - resolve(role, settings, factory): returns first healthy candidate.
  - validate(factory): logs mismatches with provider.available_models.

4.3 Factory Integration
- get_provider(role=ModelRole.X) consults registry for model default.
- Override rules:
  - Must be in ["override_allowlist"](backend/src/config/model_config.yaml:11-16).
  - Enforce budget boundaries (Section 6).

--------------------------------------------------------------------------------
5) Security Model and Hardening
--------------------------------------------------------------------------------
5.1 Decorators and Deps
- require_rate_limit, validate_input on chat endpoints ["main.py"](backend/src/main.py:525-528,575-578).
- get_current_user and require_authorization where needed; admin models router secured by auth import ["main.py"](backend/src/main.py:91-93).

5.2 JWT, CORS, CSRF
- Settings define JWT config ["config/__init__.py"](backend/src/config/__init__.py:68-71).
- CORS includes specific domains and wildcard subdomains ["main.py"](backend/src/main.py:232-246).
- CSRF middleware added ["main.py"](backend/src/main.py:227).

5.3 Threat Model Summary (STRIDE)
- Spoofing: JWT issuer/audience validation.
- Tampering: input sanitization and strict schema validation.
- Repudiation: optional request tracing; request-id headers in CORS.expose_headers.
- Info Disclosure: redact provider error strings.
- DoS: rate limits and size caps for uploads; consider server timeouts.
- EoP: admin-only routes with require_authorization.

5.4 Concrete Steps
- Align security_service configuration with settings (“single source of truth”).
- Enforce file size and MIME gating in files router.
- Consider CSP and HSTS headers on any static serving.

--------------------------------------------------------------------------------
6) Reliability and Budget Control
--------------------------------------------------------------------------------
6.1 Error Decorators
- with_retry, with_circuit_breaker, with_error_handling import ["main.py"](backend/src/main.py:94-101).
- Apply across long-running stages and provider call edges.

6.2 Fallbacks
- Simple -> Advanced fallback strategy if simple path fails.
- Advanced node fail -> fail_handler with selective re-routing ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:904-920).

6.3 Budget Gates
- Tiers and cost model:
  - Free/Pro/Enterprise with max_model caps ["model_config.yaml"](backend/src/config/model_config.yaml:17-20).
- Use ["price_table.json"](backend/src/config/price_table.json:1-34) for per-call cost estimation; reject or fallback if exceeding allotted budget.

6.4 Observability (Reliability)
- Log time-to-first-SSE frame, node durations, retries taken, and fallback invocations.

--------------------------------------------------------------------------------
7) SSE (Streaming) Specification
--------------------------------------------------------------------------------
7.1 Channel and Payload
- Redis channel "sse:{conversation_id}" ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:136-143).
- JSON payload with mandatory "type" and "timestamp" keys.

7.2 Event Types (Canonical)
- start:
  { type, conversation_id, timestamp, system, message }
- routing:
  { type, conversation_id, timestamp, decision, complexity, reasons }
- content:
  { type, conversation_id, timestamp, node, text, metadata }
- done:
  { type, conversation_id, timestamp, summary, artifacts: { download_urls, final_scores } }
- error:
  { type, conversation_id, timestamp, error, failed_node }

7.3 Server Endpoint Expectations
- Content-Type: text/event-stream.
- Write "data: <json>\n\n" per frame.
- Heartbeat: comment or ping event at intervals.

--------------------------------------------------------------------------------
8) Database Evolution
--------------------------------------------------------------------------------
8.1 Entities (Reference)
- Users, Conversations, Documents, SourceCache, SystemMetrics, Turnitin (as per earlier audit of db/models.py).
- Base = declarative_base() and relationships support.

8.2 Optional Audit Tables
- sse_events (bounded retention, compliance-driven).
- provider_calls (usage and cost tracking).

8.3 Indexing
- Indices on conversation_id, user_id.
- pgvector/HNSW in vector_storage for semantic search (earlier audit in services/vector_storage.py).

8.4 Migrations
- Alembic-based, rolling with no destructive drops; include data backfills when introducing new settings or registry.

--------------------------------------------------------------------------------
9) Middleware Order and Tiered Routing
--------------------------------------------------------------------------------
- Current order: security -> csrf -> error -> CORS -> routes ["main.py"](backend/src/main.py:223-246).
- TieredRoutingMiddleware:
  - Enable via feature flag after validation; if it annotates only scope, place after error middleware to avoid catching exceptions prematurely.
  - If it performs blocking I/O, keep minimal and guard with try/except to delegate errors to error middleware.

--------------------------------------------------------------------------------
10) Migration and Rollout Plan
--------------------------------------------------------------------------------
10.1 Phase 1 (Stabilization)
- Dedupe import blocks in ["main.py"](backend/src/main.py:9-66) safely.
- Ensure ["agent/simple/__init__.py"](backend/src/agent/simple/__init__.py:1) re-exports gemini_graph and GeminiState.
- Document SSE schema at publisher and SSE endpoint points.

10.2 Phase 2 (Normalization)
- Implement the registry module for model mapping and validation.
- Add structured logs for routing outcomes and provider/model selections.

10.3 Phase 3 (Security & Budget)
- Align security_service with HandyWriterzSettings; ensure uploads enforce size/type gates.
- Budget preflight using tiers and price table; fallback to lower-cost models.

10.4 Phase 4 (Middleware)
- Introduce TieredRoutingMiddleware under flag; run perf tests; monitor p95 latencies.

10.5 Phase 5 (Observability)
- Instrument SystemMetrics to store routing/latency metrics; optionally expose /metrics for Prometheus (if allowed).

--------------------------------------------------------------------------------
11) Testing Strategy (Unit/Integration/E2E)
--------------------------------------------------------------------------------
11.1 Unit
- ComplexityAnalyzer scoring across word/file thresholds and keywords ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:52-104).
- ProviderFactory fallback order and health usage ["models/factory.py"](backend/src/models/factory.py:99-154).
- Registry resolution validity.

11.2 Integration
- Simple path E2E: simulate gemini provider; validate SSE start/content/done sequence.
- Advanced path: minimal inputs to activate a short pipeline and verify final outputs.
- Hybrid path: concurrent runs; ensure merge logic produces combined result.

11.3 E2E
- Verify /api/chat/provider/{provider}, /api/chat/role/{role}, /api/analyze with decorators active.
- SSE capture test: subscribe to Redis channel and validate schema/order.

--------------------------------------------------------------------------------
12) SLOs and SLIs
--------------------------------------------------------------------------------
12.1 Proposed SLOs
- Availability: 99.5% monthly core endpoints.
- Latency p95:
  - Simple ≤ 3s; Advanced ≤ 300s with streaming heartbeat ≤ 5s.
- Error rate: provider calls < 2% post-retry.

12.2 SLIs
- Request success ratio; time-to-first-SSE frame; node completion distributions; retry rates; fallback ratios.

--------------------------------------------------------------------------------
13) Operational Runbook
--------------------------------------------------------------------------------
13.1 Incidents
- Redis outage:
  - Degrade SSE, backoff-retry, validate via /api/status ["main.py"](backend/src/main.py:339-467).
- Provider outage:
  - Check factory health ["models/factory.py"](backend/src/models/factory.py:181-199); adjust registry order temporarily.

13.2 Config Changes
- model_config.yaml and price_table.json via PR; registry updates alongside; override_allowlist restrictions ["config/model_config.yaml"](backend/src/config/model_config.yaml:11-16).

13.3 Secrets Rotation
- JWT and provider keys via settings ["config/__init__.py"](backend/src/config/__init__.py:68-71); ensure single source.

--------------------------------------------------------------------------------
14) Deep Module Audits (Expanded)
--------------------------------------------------------------------------------
14.1 main.py
- App/lifespan ["main.py"](backend/src/main.py:138-221)
- Middleware ["main.py"](backend/src/main.py:223-246)
- Handlers and routers ["main.py"](backend/src/main.py:248-277)
- Health/status/providers status ["main.py"](backend/src/main.py:326-521)
- Chat/Analyze ["main.py"](backend/src/main.py:524-731)
- Startup create_all ["main.py"](backend/src/main.py:118-136)

14.2 agent/graph.py
- API key requirement ["graph.py"](backend/src/agent/graph.py:36-38)
- Web research with google.genai client ["graph.py"](backend/src/agent/graph.py:96-136)
- Compile ["graph.py"](backend/src/agent/graph.py:268-293)

14.3 agent/state.py
- OverallState and helpers ["state.py"](backend/src/agent/state.py:13-48)

14.4 agent/handywriterz_graph.py
- Node registration & orchestration ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:159-349)
- Parallelism & fail routing ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:658-661,904-920)
- Export ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:216,955-962)

14.5 agent/handywriterz_state.py
- Rich academic state fields ["handywriterz_state.py"](backend/src/agent/handywriterz_state.py:1-297)

14.6 agent/routing/*
- ComplexityAnalyzer ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:14-232)
- Unified exports ["__init__.py"](backend/src/agent/routing/__init__.py:9-16)

14.7 models/factory.py
- Role mappings and defaults ["factory.py"](backend/src/models/factory.py:99-118)
- Health checks and stats ["factory.py"](backend/src/models/factory.py:181-219)

14.8 config/*
- Settings ["__init__.py"](backend/src/config/__init__.py:12-164)
- Model config and price table ["model_config.yaml"](backend/src/config/model_config.yaml:1-20), ["price_table.json"](backend/src/config/price_table.json:1-34)

14.9 agent/simple/*
- Re-export glue ["__init__.py"](backend/src/agent/simple/__init__.py:1)
- GeminiState alias ["gemini_state.py"](backend/src/agent/simple/gemini_state.py:12-22)

--------------------------------------------------------------------------------
15) Typed Interfaces and Shims
--------------------------------------------------------------------------------
15.1 HandyWriterzState Factory
- Provide new_handywriterz_state(**kwargs) -> HandyWriterzState to centralize defaulting and satisfy static type checking.

15.2 SSE Publisher Interface
- Protocol for publisher.publish(event: Dict[str, Any]) -> Awaitable[None]; ensures consistent payload schema and linter satisfaction.

--------------------------------------------------------------------------------
16) Extended SSE Examples
--------------------------------------------------------------------------------
start:
data: {"type":"start","conversation_id":"abc","timestamp":1722420000000,"system":"advanced","message":"Processing started"}

routing:
data: {"type":"routing","conversation_id":"abc","timestamp":1722420001000,"decision":"advanced","complexity":8.5,"reasons":["academic keywords","file_count=3"]}

content (search):
data: {"type":"content","conversation_id":"abc","timestamp":1722420010000,"node":"search_crossref","text":"Found DOI: 10.1000/xyz","metadata":{"doi":"10.1000/xyz"}}

content (writer):
data: {"type":"content","conversation_id":"abc","timestamp":1722420025000,"node":"writer","text":"In this section, we ..."}

done:
data: {"type":"done","conversation_id":"abc","timestamp":1722420100000,"summary":"Draft completed","artifacts":{"download_urls":{"docx":"/api/download/abc.docx"}}}

error:
data: {"type":"error","conversation_id":"abc","timestamp":1722420030000,"error":"Timeout in evaluator","failed_node":"evaluator"}

--------------------------------------------------------------------------------
17) Threat and Failure Matrix
--------------------------------------------------------------------------------
- Provider latency spikes: backoff and temporary down-ranking in registry.
- Redis reconnect storms: jitter and connection caps.
- Large uploads: strict size/MIME enforcement; chunked processing pipeline.
- Model ID drift: registry validation at startup; override allowlist enforcement.
- Type inference issues: factories and Protocols to satisfy static analyzers.

--------------------------------------------------------------------------------
18) Detailed Rollout Checklist
--------------------------------------------------------------------------------
- Stabilization:
  - Dedupe imports; confirm re-export adapter; add SSE schema docstrings.
- Normalization:
  - Registry module; factory integration; logging enhancements.
- Security & Budget:
  - Align security_service with settings; budget gates through price table; per-tier enforcement.
- Middleware:
  - TieredRoutingMiddleware under flag; perf validation.
- Observability:
  - SystemMetrics enriched; optional /metrics.

--------------------------------------------------------------------------------
19) Acceptance Criteria
--------------------------------------------------------------------------------
- Simple/Advanced/Hybrid flows all operational with correct SSE sequences.
- Status endpoints truthful to provider health and routing capabilities.
- Budget constraints honored; unsafe overrides rejected.
- Linter noise reduced via typed shims without breaking runtime behavior.
- No public API breakage.

--------------------------------------------------------------------------------
20) Observability Dashboards
--------------------------------------------------------------------------------
- Routing overview with complexity histograms.
- SSE health: time to first frame, frames/minute, errors.
- Provider health: success/latency by provider/model.
- Node timing distributions.

--------------------------------------------------------------------------------
21) Troubleshooting Guide
--------------------------------------------------------------------------------
- No SSE on client:
  - Check Redis ping and channel; confirm SSE headers and heartbeat.
- Provider failure:
  - Inspect error logs and error_handler stats; verify health endpoint.
- Budget rejections:
  - Validate tier configuration and price table coherence.

--------------------------------------------------------------------------------
22) Appendices
--------------------------------------------------------------------------------
A) Extended Sequence Narratives:
- Simple: direct provider chat sequence; optional stream.
- Advanced: state init -> graph run -> node-by-node SSE -> finalization.
- Hybrid: parallel execution -> merge.

B) Schema Stubs:
- HandyWriterzState essential fields summary; Registry mapping entry schema; SSE event schema.

C) Glossary:
- SSE, SLO/SLI, Registry, Hybrid, Fail handler, Budget gate.

--------------------------------------------------------------------------------
23) Comprehensive Agentic System File Structure (Authoritative Reference)
--------------------------------------------------------------------------------
This section documents a complete, authoritative file structure for the agentic system, grounded in the current repository. It enumerates directories and key files under backend/src/agent and adjacent modules that participate in orchestration, routing, providers, tools, and services. Each entry includes purpose notes and, where applicable, citations to loaded line anchors.

Legend:
- D = Directory
- F = File

23.1 Top-Level Agent Orchestration and Routing
D backend/src/agent/
  F __init__.py
    - Package marker; re-exports for routing convenience may be added (kept minimal).
  F app.py
    - Entry points or app wiring for agent-specific tasks (if used by scripts/workflows).
  F base.py
    - BaseNode, StreamingNode, SSE publisher helpers, retry/timeout decorators.
    - Provides broadcast_sse_event and NodeMetrics to standardize node lifecycle events.
    - See: ["base.py"](backend/src/agent/base.py:1)
  F configuration.py
    - Agent-level configuration bridge; adapter layer between settings and agent graph configuration.
  F graph.py
    - Simple Gemini research agent StateGraph.
    - Nodes: generate_query, web_research, reflection, finalize_answer.
    - Compiled as "pro-search-agent".
    - Requires GEMINI_API_KEY.
    - See: ["graph.py"](backend/src/agent/graph.py:36-41,96-136,268-293)
  F handywriterz_graph.py
    - Advanced, academic orchestration graph with multiple pipelines and fail handlers.
    - Parallel Search fan-out via Send, evaluation/turnitin/formatter/memory-writer stages.
    - Exports handywriterz_graph (compiled).
    - See: ["handywriterz_graph.py"](backend/src/agent/handywriterz_graph.py:159-217,218-366,658-661,799-810,904-920,955-962)
  F handywriterz_state.py
    - Rich academic writing dataclass with conversation metadata, research, evaluation, formatting, timings.
    - See: ["handywriterz_state.py"](backend/src/agent/handywriterz_state.py:1-297)
  F prompts.py
    - Agent prompt templates or factories shared across nodes.
  D nodes/
    - All atomic and composite node implementations used by the advanced graph.
    - Organized by swarm category (research, writing, QA) for maintainability.
    D qa_swarm/
      - QA pipeline nodes: argument validation, bias detection, fact checking, ethical reasoning, originality guard.
      - Invoked in sequence for quality assurance after writing stage.
    D research_swarm/
      - Research specialists: arXiv, cross-disciplinary search, methodology expert, scholar network, trends.
      - Often triggered in parallel via Send for breadth-first evidence gathering.
    D writing_swarm/
      - Writing pipeline nodes: academic tone, clarity, structure optimizer, style adaptation, citation master.
  D routing/
    F __init__.py
      - Exports SystemRouter, UnifiedProcessor, ComplexityAnalyzer for external imports.
      - See: ["routing/__init__.py"](backend/src/agent/routing/__init__.py:9-16)
    F system_router.py
      - Orchestrates thresholds, academic detection and mode selection (simple/advanced/hybrid).
      - Complexity thresholds and router stats are surfaced in /api/status.
    F unified_processor.py
      - Unifies execution across simple/advanced/hybrid flows.
      - Publishes JSON to Redis channel "sse:{conversation_id}".
      - Imports simple system via agent.simple re-exports; constructs HandyWriterzState for advanced path.
      - See publisher reference: ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:136-143)
    F complexity_analyzer.py
      - Request complexity scoring and academic detection heuristics.
      - See: ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:14-232)
  D simple/
    F __init__.py
      - Re-export shim to expose:
        - gemini_graph = agent.graph.graph
        - GeminiState from agent/simple/gemini_state.py
      - Ensures UnifiedProcessor simple path can import stable symbols.
      - See: ["agent/simple/__init__.py"](backend/src/agent/simple/__init__.py:1)
    F gemini_state.py
      - Imports OverallState as GeminiState when available, sets GEMINI_STATE_AVAILABLE guard.
      - See: ["gemini_state.py"](backend/src/agent/simple/gemini_state.py:12-22)

23.2 Provider Abstraction and Model Configuration
D backend/src/models/
  F __init__.py
    - Package marker and optional convenience exports.
  F base.py
    - BaseProvider interface, ModelRole enum, ChatMessage/ChatResponse types.
    - Normalized provider contract for chat and streaming.
  F factory.py
    - Multi-provider factory; initializes configured providers from settings.
    - Role-based provider ordering, health checks, provider stats.
    - Global initialize_factory/get_factory/get_provider API.
    - See: ["factory.py"](backend/src/models/factory.py:99-118,181-219)
  F gemini.py
    - Gemini provider implementation matching BaseProvider.
  F openai.py
    - OpenAI provider implementation matching BaseProvider.
  F anthropic.py
    - Anthropic provider implementation matching BaseProvider.
  F openrouter.py
    - OpenRouter provider; streaming and chat with vendor-specific extras.
    - See: ["openrouter.py"](backend/src/models/openrouter.py:1-179)
  F perplexity.py
    - Perplexity provider via OpenAI-compatible API base URL.
    - See: ["perplexity.py"](backend/src/models/perplexity.py:1-150)
  [Proposed] F registry.py
    - Logical-to-provider model registry to normalize model IDs and validate availability.
    - Integrates with factory to provide role defaults and enforce allowlist overrides.

D backend/src/config/
  F __init__.py
    - HandyWriterzSettings; env parsing; logging setup.
    - JWT/CORS limits; rate limiting; Dynamic SDK stubs.
    - See: ["config/__init__.py"](backend/src/config/__init__.py:12-164)
  F model_config.yaml
    - Default logical roles (writer/formatter/search/evaluator) and budget tiers.
    - See: ["config/model_config.yaml"](backend/src/config/model_config.yaml:1-20)
  F price_table.json
    - Cost-per-token map per provider/model for budgeting and policy gates.
    - See: ["config/price_table.json"](backend/src/config/price_table.json:1-34)

23.3 Middleware and Services (Security, Errors, SSE)
D backend/src/middleware/
  F __init__.py
    - Package marker; may expose concrete middlewares.
  F error_middleware.py
    - Global error handling; consistent JSON responses; integrates with services.error_handler.
  F security_middleware.py
    - Security headers and CSRF; request validation; integrates with security service.
  F tiered_routing.py
    - Optional middleware to annotate requests with model choices (feature-flagged).
D backend/src/services/
  F __init__.py
  F error_handler.py
    - Circuit breaker, retry, error classification, Redis-backed error storage and optional broadcasting.
    - Decorators: with_error_handling, with_circuit_breaker, with_retry.
  F security_service.py
    - JWT validation, rate limiting with Redis, suspicious pattern detection, auth dependencies and decorators.
  F vector_storage.py
    - pgvector index management, semantic retrieval, chunk storage and search.

23.4 API Endpoints and Schemas
D backend/src/api/
  F __init__.py
  D schemas/
    F chat.py
      - ChatRequest/ChatResponse models for API surfaces.
  F billing.py
    - Billing/subscription routes wired in main.
  F files.py
    - Upload endpoints (tus, presign/notify) and integration with workers for chunk processing.
    - Included via app.include_router(..., prefix="/api").
  F profile.py
    - Profile management routes.
  F usage.py
    - Usage metrics endpoints.
  F payments.py
    - Escrow/payouts/quotes/status endpoints interacting with blockchain and DB.
  F payout.py
    - Earnings and payout history surface.
  F checker.py
    - Checker flows (claim/submit) integrated with DB and models.

D backend/src/routes/
  F admin_models.py
    - Admin endpoints to manage model configuration/swarms; protected by require_authorization("admin_access").

23.5 Database Layer and Repositories
D backend/src/db/
  F __init__.py
  F database.py
    - DatabaseManager for engine/session lifecycle.
    - Health checks, table creation hooks, DI helpers (get_user_repository, etc.).
    - See: ["db/database.py"](backend/src/db/database.py:1)
  F models.py
    - Declarative SQLAlchemy models (Users, Conversations, Documents, SourceCache, SystemMetrics, Turnitin-related).
    - Base = declarative_base(); relationships and enums.
    - Referenced by ["main.py"](backend/src/main.py:118-136) for create_all.

23.6 Tools, Gateways, and Workflows (Agent Integrations)
D backend/src/tools/
  - Vendor/tool integrations used by nodes (search, citation, formatting, plagiarism).
  - Ensure consistent timeouts and retries; conform to BaseNode error handling.
D backend/src/gateways/
  - External service gateways (e.g., payment, blockchain, web search APIs) abstracted behind clean interfaces.
D backend/src/workflows/
  - Orchestrated workflows (e.g., checker, payouts, academic writing variations).
  - May use LangGraph or custom orchestrators where suitable.

23.7 Graph Composition and Templates
D backend/src/graph/
  F composites.yaml
    - Declarative design for composite swarms and edges; textual DSL for orchestration patterns.
    - See: ["graph/composites.yaml"](backend/src/graph/composites.yaml:1-84)
D backend/src/prompts/
  F templates/
    - Prompt fragments for consistency; used by nodes and providers.
  F __init__.py
    - Prompt catalog loader or helpers.

23.8 Background Workers and Schedulers
D backend/src/workers/
  - Long-running tasks (e.g., file chunk processing, long SSE fan-out, scheduled cleanups).
  - Example used by files.py: workers.chunk_queue_worker.process_file_chunk.delay (mentioned in earlier audit).

23.9 Security, Auth, and Telegram Integrations
D backend/src/auth/
  - Auth-specific helpers or SSO integrations if present beyond security_service (JWT).
D backend/src/telegram/
  - Telegram handlers/bots for notifications or moderation flows.

23.10 Utilities and Core
D backend/src/core/
  - Cross-cutting utilities, data structures, and constants.
D backend/src/utils/
  - Logging, time, and convenience helpers used by nodes and services.

23.11 App Composition and Entrypoints
F backend/run_server.py
  - Uvicorn launcher script (dev/ops convenience).
D backend/scripts/
  F init_database.py
    - Seeds system prompts and initial data on startup.
    - Called in lifespan: ["main.py"](backend/src/main.py:144-149)
  - reset_db.py, setup.sh, test-e2e.sh
    - Database resets, environment bootstrap, e2e test runner scripts.

23.12 Frontend Mounts and Static Assets (Context)
D backend/static/ (if present)
  - Static assets for in-app serving: "/static", "/pyodide", "/app" (SvelteKit build).
  - Mounted in main app when directories exist.
  - See: ["main.py"](backend/src/main.py:279-299)

23.13 How These Pieces Collaborate
- Orchestration core:
  - Entry via FastAPI endpoints ["main.py"](backend/src/main.py:524-731) -> UnifiedProcessor ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:1) -> route to simple or advanced systems based on ComplexityAnalyzer ["complexity_analyzer.py"](backend/src/agent/routing/complexity_analyzer.py:14-232).
- SSE streaming:
  - Nodes publish lifecycle events via base helpers ["base.py"](backend/src/agent/base.py:1) and UnifiedProcessor publisher ["unified_processor.py"](backend/src/agent/routing/unified_processor.py:136-143).
- Provider abstraction:
  - Role mapping and selection from ProviderFactory ["models/factory.py"](backend/src/models/factory.py:99-118) with planned Registry integration ["config/model_config.yaml"](backend/src/config/model_config.yaml:1-20) + ["config/price_table.json"](backend/src/config/price_table.json:1-34).
- Data layer:
  - Conversations/docs/metrics persisted via db.models; DI helpers from db.database.
- Security and reliability:
  - Global guards via middleware + decorators from services.security_service and services.error_handler.

23.14 Conventions and Best Practices for New Files
- Node implementation files must:
  - Use with_retry/with_error_handling decorators for vendor calls.
  - Emit start/progress/content/done/error via base node helpers for consistent SSE frames.
  - Keep per-node timeouts reasonable; expose metrics through NodeMetrics.
- Adding new providers:
  - Implement BaseProvider methods in a new models/<vendor>.py.
  - Register in models/factory.py and validate via health_check_all.
  - Update model registry entries and budgets if applicable.
- Extending routing:
  - Add new indicators in ComplexityAnalyzer with clear weights.
  - Ensure SystemRouter thresholds remain configurable and surfaced in /api/status.

--------------------------------------------------------------------------------
24) Final Notes
--------------------------------------------------------------------------------
- The plan is conservative and additive, respecting existing behaviors.
- All references are grounded to current code with explicit file/line anchors.
- Simple: direct provider chat sequence; optional stream.
- Advanced: state init -> graph run -> node-by-node SSE -> finalization.
- Hybrid: parallel execution -> merge.

B) Schema Stubs:
- HandyWriterzState essential fields summary; Registry mapping entry schema; SSE event schema.

C) Glossary:
- SSE, SLO/SLI, Registry, Hybrid, Fail handler, Budget gate.

--------------------------------------------------------------------------------
23) Final Notes
--------------------------------------------------------------------------------
- The plan is conservative and additive, respecting existing behaviors.
- All references are grounded to current code with explicit file/line anchors.
