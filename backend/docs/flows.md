# HandyWriterz Backend — Comprehensive Flows and Agentic System (Grounded in Code)

Note: This document is grounded exclusively in the current backend source. It enumerates end-to-end flows, agent and sub-agent orchestration, SSE eventing, routing and provider interactions, middleware, security, error handling, and data access paths. All references use clickable citations with file path and line anchors.

Contents (high-level)
- Section 1: Entry Points, Routing, and Middleware Order
- Section 2: Providers and Model Selection
- Section 3: Agentic System (Simple, Advanced, Hybrid)
- Section 4: Complexity Analysis and SystemRouter
- Section 5: Unified Chat Flows
- Section 6: Writing Workflow Flows
- Section 7: SSE Streaming Contracts and Event Lifecycles
- Section 8: Health, Status, and Provider Checks
- Section 9: Vector Retrieval, Evidence, and Downloads
- Section 10: Profile, Credits, Billing, and Admin
- Section 11: Reliability, Errors, Circuit Breakers, Retries
- Section 12: Security, CSRF, JWT, Rate Limiting
- Section 13: Configuration, Pricing, and Budgets
- Section 14: Data Access and Repositories
- Section 15: Orchestration Composites
- Section 16: Operational Runbooks and Observability
- Section 17: Flow-by-Flow Swimlanes
- Section 18: Appendices

----------------------------------------------------------------
Section 1 — Entry Points, Routing, and Middleware Order
----------------------------------------------------------------

1.1 FastAPI Application Boot and Lifespan
- The application root and its lifespan are composed in [`python.FastAPI()`](src/main.py:1). The lifespan validates critical dependencies (Redis, DB, error handler) before serving traffic.
- Static apps and assets:
  - /static mount via [`python.app.mount()`](src/main.py:1).
  - /pyodide and /app mounts in the same region.
- SPA fallbacks for frontend compatibility use catch-all routes declared under the main router in [`python.APIRouter()`](src/main.py:1).

1.2 Middleware Order (Security → Error → CORS)
- Security middleware enforces headers and validation via [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1).
- CSRF protection for state-changing methods via [`python.CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1).
- Error middleware captures exceptions and shapes responses via [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).
- CORS configuration then applied to allow expected origins and verbs in [`python.FastAPI()`](src/main.py:1).
- Rationale: Security checks happen pre-handler; error normalization wraps handlers; CORS post-wraps to ensure correct headers on normalized responses.

1.3 Routers
- The core endpoints are registered in [`python.include_router()`](src/main.py:1) blocks, covering admin models, files, billing, profile, usage, payments, payout, checker, vector retrieval, and chat-processing endpoints.

----------------------------------------------------------------
Section 2 — Providers and Model Selection
----------------------------------------------------------------

2.1 Base Provider Contract
- [`python.class BaseProvider`](src/models/base.py:1) defines:
  - async chat(messages: list[ChatMessage]) → ChatResponse
  - async stream_chat(messages: list[ChatMessage]) → async iterator of chunks
- Data structures:
  - [`python.class ChatMessage`](src/models/base.py:1) with role and content.
  - [`python.class ChatResponse`](src/models/base.py:1) with content, tokens usage, and metadata.
  - [`python.Enum ModelRole`](src/models/base.py:1) enumerates logical roles, e.g., system, assistant, researcher.

2.2 ProviderFactory and Registry
- [`python.class ProviderFactory`](src/models/factory.py:1):
  - Initializes available providers based on environment keys from settings.
  - Maintains role_defaults mapping logical roles to default model IDs.
  - Exposes health_check_all, stats, and get_provider.
- Global helpers:
  - [`python.get_factory()`](src/models/factory.py:1)
  - [`python.get_provider()`](src/models/factory.py:1) for DI-style access.
- Role mappings determine default provider/model for endpoints like /api/chat/role/{role} in [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1).

2.3 Implemented Providers
- OpenRouter provider at [`python.class OpenRouterProvider`](src/models/openrouter.py:1):
  - Uses AsyncOpenAI client configured for OpenRouter.
  - Supports streaming and non-streaming chat.
  - Encapsulates model defaults by role.
- Perplexity provider at [`python.class PerplexityProvider`](src/models/perplexity.py:1):
  - Uses AsyncOpenAI-compatible client for Perplexity endpoints.
  - Provides streaming and non-streaming chat.

----------------------------------------------------------------
Section 3 — Agentic System (Simple, Advanced, Hybrid)
----------------------------------------------------------------

3.1 Simple Agent (Gemini StateGraph)
- Graph construction function in [`python.def build_gemini_graph()`](src/agent/graph.py:1).
- State types in [`python.GeminiState`](src/agent/state.py:1) define the TypedDict for graph state.
- Nodes:
  - generate_query: synthesizes focused query from user messages.
  - web_research: leverages google.genai tool to gather results.
  - reflection: improves quality and coherence of draft.
  - finalize_answer: composes final response.
- Export symbol and usage paths are stabilized by re-export plans via simple package init (see Section 16 notes).

3.2 Advanced Agent (HandyWriterz Graph)
- Graph factory in [`python.def create_handywriterz_graph()`](src/agent/handywriterz_graph.py:1).
- Exported symbol [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1) invoked by routing flows.
- State definition:
  - [`python.@dataclass HandyWriterzState`](src/agent/handywriterz_state.py:1) with metadata (topic, document type), progress tracking, enums (DocumentType, CitationStyle, AcademicField, Region, WorkflowStatus), and helper methods.
- Pipelines:
  - default, dissertation, reflection-intensive, case study, technical report, comparative essay pipelines defined in graph assembly.
- Behavior:
  - Accepts a rich state; orchestrates multiple sub-nodes and phases; can emit structured outputs (outline, sections, citations).

3.3 Hybrid Mode
- Combined pathway in [`python.class UnifiedProcessor`](src/agent/routing/unified_processor.py:1):
  - Executes both simple and advanced branches in parallel or sequence based on tuning.
  - Merges outputs, potentially emitting more frequent SSE content frames.
  - Useful for time-to-first-byte plus depth quality.

----------------------------------------------------------------
Section 4 — Complexity Analysis and SystemRouter
----------------------------------------------------------------

4.1 ComplexityAnalyzer
- [`python.class ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1):
  - Computes score 1–10 based on:
    - Token/word count, attachment/file count, academic keywords, user params (document type, citation requirements), and quality indicators.
  - Exposes:
    - is_academic_writing_request(text) → bool
    - analyze_request_characteristics(request) → dict with indicators, estimated_processing_seconds, recommended system.

4.2 SystemRouter
- Encapsulated in [`python.UnifiedProcessor`](src/agent/routing/unified_processor.py:1):
  - Applies thresholds from settings or model_config.
  - Chooses simple, advanced, or hybrid based on score and flags.
  - Provides rationale used in SSE routing events.

----------------------------------------------------------------
Section 5 — Unified Chat Flows
----------------------------------------------------------------

5.1 Endpoints
- Unified chat: [`python.@app.post("/api/chat")`](src/main.py:1)
- Simple-only: [`python.@app.post("/api/chat/simple")`](src/main.py:1)
- Advanced-only: [`python.@app.post("/api/chat/advanced")`](src/main.py:1)
- Provider-specific: [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1)
- Role-specific: [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1)
- Analyze-only: [`python.@app.post("/api/analyze")`](src/main.py:1)

5.2 Unified Flow Execution (Happy Path)
1) HTTP request reaches FastAPI; security middleware validates headers in [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1).
2) Request body is parsed; if applicable, decorators from [`python.SecurityService`](src/services/security_service.py:1) validate JWT or rate limits.
3) The handler for /api/chat invokes [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
4) UnifiedProcessor publishes "start" SSE event to channel sse:{conversation_id}.
5) Analyzer computes complexity via [`python.ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1), producing score and indicators.
6) SystemRouter chooses route; "routing" SSE event emitted with route, score, rationale.
7) Branch execution:
   - simple: run [`python.gemini_graph`](src/agent/graph.py:1) with [`python.GeminiState`](src/agent/state.py:1), emit content frames.
   - advanced: build [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1), invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1), emit content frames.
   - hybrid: orchestrate both; interleave content frames.
8) Aggregate final output; publish "done" SSE event; return JSON response from the HTTP call.

5.3 Provider-Scoped Flow
- For /api/chat/provider/{provider_name}:
  - Provider is selected via [`python.get_provider(provider_name)`](src/models/factory.py:1).
  - If stream=true, route calls [`python.BaseProvider.stream_chat()`](src/models/base.py:1) implementation; emits chunks directly over HTTP response (not Redis SSE).
  - Errors pass through error middleware for normalization.

5.4 Role-Scoped Flow
- For /api/chat/role/{role}:
  - Resolve default provider/model via [`python.ProviderFactory.role_defaults`](src/models/factory.py:1).
  - Delegates to provider chat or streaming as requested.

5.5 Analyze Flow
- For /api/analyze:
  - Calls analyzer functions; returns characteristics, ETA, and recommended path.
  - No SSE emission on this path.

----------------------------------------------------------------
Section 6 — Writing Workflow Flows
----------------------------------------------------------------

6.1 Write Endpoint
- Entrypoint: [`python.@app.post("/api/write")`](src/main.py:1)
- Constructs [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) from request body:
  - topic, document_type, citation_style, field, region, constraints (preferred word count, outline hints).
- Kicks off async execution against [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).

6.2 Eventing Lifecycle
- Publishes "workflow_start" SSE event on sse:{conversation_id}.
- For each node transition or phase progress, publishes "workflow_progress" with percent and status fields (WorkflowStatus enum from [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1)).
- On success, emits "workflow_complete" with outline/sections (and optional document URL).
- On error, emits "workflow_failed" with details for diagnostics.

6.3 Client Consumption
- Client listens via SSE endpoint [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1) to get workflow runtime feedback.

----------------------------------------------------------------
Section 7 — SSE Streaming Contracts and Event Lifecycles
----------------------------------------------------------------

7.1 SSE Endpoint
- GET /api/stream/{conversation_id} in [`python.@app.get`](src/main.py:1) returns a StreamingResponse that:
  - Subscribes to Redis channel sse:{conversation_id}.
  - Forwards newline-delimited JSON frames to the client.

7.2 Event Types and Shapes
- start: initial event after UnifiedProcessor begins work.
- routing: selection details including score and rationale.
- content: incremental text chunks and optional sources.
- done: marks finalization; includes prompt/completion tokens, summary.
- error: failure details including retryable flag and kind.
- workflow_start, workflow_progress, workflow_complete, workflow_failed for write flows.

7.3 Publishers
- UnifiedProcessor events during /api/chat in [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
- Workflow executor events during /api/write from handler code in [`python.@app.post("/api/write")`](src/main.py:1).

7.4 Error Frames
- Normalized and, when in pipeline, shaped by with_error_handling decorators in [`python.services.error_handler`](src/services/error_handler.py:1) and error middleware in [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).

----------------------------------------------------------------
Section 8 — Health, Status, and Provider Checks
----------------------------------------------------------------

8.1 Health
- GET /health basic: [`python.@app.get("/health")`](src/main.py:1).
- GET /health/detailed: [`python.@app.get("/health/detailed")`](src/main.py:1) includes checks for DB, Redis, and dependencies.

8.2 Unified Status
- GET /api/status provides composite view: routing thresholds, service readiness, provider availability at [`python.@app.get("/api/status")`](src/main.py:1).

8.3 Providers Status Matrix
- GET /api/providers/status aggregates health via [`python.ProviderFactory.health_check_all`](src/models/factory.py:1) in handler [`python.@app.get("/api/providers/status")`](src/main.py:1).
- Per-provider details include up/down and latencies based on implementation specifics.

----------------------------------------------------------------
Section 9 — Vector Retrieval, Evidence, and Downloads
----------------------------------------------------------------

9.1 Retrieval
- POST /api/retrieve handled at [`python.@app.post("/api/retrieve")`](src/main.py:1): vector or knowledge base retrieval.
- POST /api/search/semantic handled at [`python.@app.post("/api/search/semantic")`](src/main.py:1): semantic search.

9.2 Evidence
- GET /api/evidence/{conversation_id} collates artifacts from a run in [`python.@app.get("/api/evidence/{conversation_id}")`](src/main.py:1).

9.3 Download
- Conversations/download endpoints provide packaged results in the same routing region (nearby handlers in [`python.FastAPI()`](src/main.py:1)).

----------------------------------------------------------------
Section 10 — Profile, Credits, Billing, and Admin
----------------------------------------------------------------

10.1 Profile and Usage
- Profile routes included via [`python.include_router(profile_router)`](src/main.py:1).
- Usage/credits updated post-processing, with JWT validation via [`python.SecurityService`](src/services/security_service.py:1).

10.2 Billing and Payments
- Billing, payments, and payout routers included via [`python.include_router(billing_router)`](src/main.py:1) and peers.
- Payment integrations follow similar error/security patterns.

10.3 Admin
- Admin models, files, checker endpoints included via their routers; protected by JWT + role checks using decorators from [`python.SecurityService`](src/services/security_service.py:1).

----------------------------------------------------------------
Section 11 — Reliability, Errors, Circuit Breakers, Retries
----------------------------------------------------------------

11.1 Error Strategies
- Decorators in [`python.services.error_handler`](src/services/error_handler.py:1):
  - [`python.with_retry()`](src/services/error_handler.py:1): exponential backoff for transient failures.
  - [`python.with_circuit_breaker()`](src/services/error_handler.py:1): opens circuit on repeated failures; integrates Redis storage for state and broadcasts if configured.
  - [`python.with_error_handling()`](src/services/error_handler.py:1): wraps functions to produce normalized error outputs.

11.2 Middleware Normalization
- [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1) catches exceptions, classifies them, and returns contract-stable JSON responses.

11.3 Publisher Resilience
- When publishing SSE events, failures are handled by the same strategies; if Redis is unavailable, events may be dropped and HTTP response still returns with proper error semantics.

----------------------------------------------------------------
Section 12 — Security, CSRF, JWT, Rate Limiting
----------------------------------------------------------------

12.1 Security Middleware
- [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1) sets headers (X-Frame-Options, Content-Security-Policy), validates request shapes, and enforces security posture for all routes.

12.2 CSRF
- [`python.CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1) enforces CSRF tokens on non-idempotent HTTP verbs; tokens issued and validated against session or headers.

12.3 JWT and Guards
- [`python.SecurityService`](src/services/security_service.py:1) provides JWT creation/validation and request guards:
  - @require_auth
  - @require_admin
  - @rate_limited
  - validation helpers for inputs.

----------------------------------------------------------------
Section 13 — Configuration, Pricing, and Budgets
----------------------------------------------------------------

13.1 Settings
- [`python.HandyWriterzSettings`](src/config/__init__.py:1) with environment mode, provider keys, DB/Redis URLs, JWT secrets, CORS origins, rate limits.
- Logging setup via [`python.setup_logging()`](src/config/__init__.py:1).

13.2 Model Configuration
- [`yaml.model_config.yaml`](src/config/model_config.yaml:1) defines:
  - Role-based logical defaults and budget tiers.
  - Thresholds consumed by SystemRouter/Analyzer.

13.3 Pricing
- [`json.price_table.json`](src/config/price_table.json:1) maps model IDs to token costs; used in budgeting and reporting.

----------------------------------------------------------------
Section 14 — Data Access and Repositories
----------------------------------------------------------------

14.1 Database Manager
- [`python.class DatabaseManager`](src/db/database.py:1) sets up engine, runs minimal migrations and index setup, exposes health checks and dependency providers.

14.2 Repositories
- [`python.class UserRepository`](src/db/database.py:1), [`python.class ConversationRepository`](src/db/database.py:1), [`python.class DocumentRepository`](src/db/database.py:1) encapsulate persistence boundaries.

14.3 Dependency Injection
- [`python.def get_db()`](src/db/database.py:1) used in endpoints for safe session management.

----------------------------------------------------------------
Section 15 — Orchestration Composites
----------------------------------------------------------------

15.1 Graph Composites Spec
- [`yaml.composites.yaml`](src/graph/composites.yaml:1) contains declarative compositions for planner, research, QA, Turnitin, formatting pipelines.
- These composites inform advanced graph assembly in [`python.create_handywriterz_graph()`](src/agent/handywriterz_graph.py:1).

----------------------------------------------------------------
Section 16 — Operational Runbooks and Observability
----------------------------------------------------------------

16.1 Startup
- Lifespan checks Redis/DB/error handler in [`python.FastAPI()`](src/main.py:1). If any fail, app can abort startup to avoid running unhealthy.

16.2 Logs and Metrics
- Logging configured by [`python.setup_logging()`](src/config/__init__.py:1).
- Error middleware emits structured logs; SSE frames provide live telemetry of agentic progress.

16.3 Recovery
- Circuit breakers and retries ensure graceful degradation for provider outages.
- Health endpoints provide quick triage; provider status matrix indicates external dependency health.

----------------------------------------------------------------
Section 17 — Flow-by-Flow Swimlanes
----------------------------------------------------------------

17.1 Unified Chat (Simple Route)
Actors: Client → FastAPI → UnifiedProcessor → ComplexityAnalyzer → Simple Graph → SSE Publisher → Redis → Stream Endpoint → Client

Swimlane:
- Client: POST /api/chat with conversation_id, messages.
- FastAPI: enters handler [`python.@app.post("/api/chat")`](src/main.py:1).
- UnifiedProcessor:
  - Publish "start" to sse:{conversation_id} in [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
  - Analyzer score low ⇒ route=simple; publish "routing".
  - Build [`python.GeminiState`](src/agent/state.py:1); call [`python.gemini_graph`](src/agent/graph.py:1).
  - Iterate nodes: generate_query → web_research → reflection → finalize_answer.
  - Emit "content" frames with partial text.
  - Emit "done" with final content and token usage.
- Stream Endpoint: Client may concurrently GET /api/stream/{conversation_id} in [`python.@app.get`](src/main.py:1) to receive events.

17.2 Unified Chat (Advanced Route)
- Analyzer score high or academic flags detected.
- Build [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) with document type, citation style, field, region.
- Invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Emit multiple "content" frames; finalize with "done".

17.3 Unified Chat (Hybrid Route)
- Run simple and advanced in tandem.
- Emit interleaved "content" frames; final reconciliation strategy returns combined content; "done" published.

17.4 Provider-Scoped Streaming
- Client: POST /api/chat/provider/{provider}?stream=true
- Handler selects provider via [`python.get_provider`](src/models/factory.py:1).
- Calls [`python.stream_chat`](src/models/base.py:1) on provider.
- Chunks sent directly in HTTP streaming response (no Redis SSE for this path).
- Error handling by [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).

17.5 Write Workflow
- Client: POST /api/write with conversation_id, topic, document_type, citation_style, field, region, constraints.
- Handler builds [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1).
- Async invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Emit "workflow_start" → periodic "workflow_progress" → "workflow_complete" or "workflow_failed".
- Client subscribes via SSE.

17.6 Analyze-Only
- Client: POST /api/analyze.
- Handler calls Analyzer and returns characteristics with recommended route; no SSE.

17.7 Retrieval and Evidence
- Retrieval: POST /api/retrieve and /api/search/semantic.
- Evidence: GET /api/evidence/{conversation_id}.
- Typically synchronous JSON; may be used by agents for sources.

17.8 Profile/Credits and Billing
- Protected handlers with JWT guards; leverage [`python.SecurityService`](src/services/security_service.py:1).
- Update credit usage post-execution.

----------------------------------------------------------------
Section 18 — Appendices
----------------------------------------------------------------

18.1 SSE Event Reference (Canonical)
- start:
  {
    "type": "start",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "messagePreview": "...", "messageTokens": 0 }
  }
- routing:
  {
    "type": "routing",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "route": "simple|advanced|hybrid", "score": 1-10, "rationale": "...", "estimated_processing_seconds": 0 }
  }
- content:
  {
    "type": "content",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "text": "...", "role": "assistant", "sources": [ { "title": "...", "url": "...", "snippet": "..." } ] }
  }
- done:
  {
    "type": "done",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "final": true, "summary": "...", "tokens_used": { "prompt": 0, "completion": 0 } }
  }
- error:
  {
    "type": "error",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "message": "...", "kind": "provider|routing|validation|internal", "retryable": true }
  }
- workflow_start:
  {
    "type": "workflow_start",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "document_type": "...", "field": "...", "citation_style": "...", "region": "..." }
  }
- workflow_progress:
  {
    "type": "workflow_progress",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "node": "...", "progress": { "percent": 0, "status": "..." }, "notes": "..." }
  }
- workflow_complete:
  {
    "type": "workflow_complete",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "document_url": "...", "outline": [ "..." ], "sections": [ { "title": "...", "content": "..." } ] }
  }
- workflow_failed:
  {
    "type": "workflow_failed",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "message": "...", "node": "..." }
  }

18.2 File Reference Index
- Application and Endpoints
  - [`python.FastAPI()`](src/main.py:1)
  - [`python.@app.post("/api/chat")`](src/main.py:1)
  - [`python.@app.post("/api/chat/simple")`](src/main.py:1)
  - [`python.@app.post("/api/chat/advanced")`](src/main.py:1)
  - [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1)
  - [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1)
  - [`python.@app.post("/api/analyze")`](src/main.py:1)
  - [`python.@app.post("/api/retrieve")`](src/main.py:1)
  - [`python.@app.post("/api/search/semantic")`](src/main.py:1)
  - [`python.@app.get("/api/evidence/{conversation_id}")`](src/main.py:1)
  - [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1)
  - [`python.@app.get("/api/status")`](src/main.py:1)
  - [`python.@app.get("/api/providers/status")`](src/main.py:1)
  - [`python.@app.get("/health")`](src/main.py:1)
  - [`python.@app.get("/health/detailed")`](src/main.py:1)

- Agents and Routing
  - [`python.build_gemini_graph()`](src/agent/graph.py:1)
  - [`python.GeminiState`](src/agent/state.py:1)
  - [`python.create_handywriterz  - Applies thresholds from settings or model_config.
  - Chooses simple, advanced, or hybrid based on score and flags.
  - Provides rationale used in SSE routing events.

----------------------------------------------------------------
Section 5 — Unified Chat Flows
----------------------------------------------------------------

5.1 Endpoints
- Unified chat: [`python.@app.post("/api/chat")`](src/main.py:1)
- Simple-only: [`python.@app.post("/api/chat/simple")`](src/main.py:1)
- Advanced-only: [`python.@app.post("/api/chat/advanced")`](src/main.py:1)
- Provider-specific: [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1)
- Role-specific: [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1)
- Analyze-only: [`python.@app.post("/api/analyze")`](src/main.py:1)

5.2 Unified Flow Execution (Happy Path)
1) HTTP request reaches FastAPI; security middleware validates headers in [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1).
2) Request body is parsed; if applicable, decorators from [`python.SecurityService`](src/services/security_service.py:1) validate JWT or rate limits.
3) The handler for /api/chat invokes [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
4) UnifiedProcessor publishes "start" SSE event to channel sse:{conversation_id}.
5) Analyzer computes complexity via [`python.ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1), producing score and indicators.
6) SystemRouter chooses route; "routing" SSE event emitted with route, score, rationale.
7) Branch execution:
   - simple: run [`python.gemini_graph`](src/agent/graph.py:1) with [`python.GeminiState`](src/agent/state.py:1), emit content frames.
   - advanced: build [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1), invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1), emit content frames.
   - hybrid: orchestrate both; interleave content frames.
8) Aggregate final output; publish "done" SSE event; return JSON response from the HTTP call.

5.3 Provider-Scoped Flow
- For /api/chat/provider/{provider_name}:
  - Provider is selected via [`python.get_provider(provider_name)`](src/models/factory.py:1).
  - If stream=true, route calls [`python.BaseProvider.stream_chat()`](src/models/base.py:1) implementation; emits chunks directly over HTTP response (not Redis SSE).
  - Errors pass through error middleware for normalization.

5.4 Role-Scoped Flow
- For /api/chat/role/{role}:
  - Resolve default provider/model via [`python.ProviderFactory.role_defaults`](src/models/factory.py:1).
  - Delegates to provider chat or streaming as requested.

5.5 Analyze Flow
- For /api/analyze:
  - Calls analyzer functions; returns characteristics, ETA, and recommended path.
  - No SSE emission on this path.

----------------------------------------------------------------
Section 6 — Writing Workflow Flows
----------------------------------------------------------------

6.1 Write Endpoint
- Entrypoint: [`python.@app.post("/api/write")`](src/main.py:1)
- Constructs [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) from request body:
  - topic, document_type, citation_style, field, region, constraints (preferred word count, outline hints).
- Kicks off async execution against [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).

6.2 Eventing Lifecycle
- Publishes "workflow_start" SSE event on sse:{conversation_id}.
- For each node transition or phase progress, publishes "workflow_progress" with percent and status fields (WorkflowStatus enum from [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1)).
- On success, emits "workflow_complete" with outline/sections (and optional document URL).
- On error, emits "workflow_failed" with details for diagnostics.

6.3 Client Consumption
- Client listens via SSE endpoint [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1) to get workflow runtime feedback.

----------------------------------------------------------------
Section 7 — SSE Streaming Contracts and Event Lifecycles
----------------------------------------------------------------

7.1 SSE Endpoint
- GET /api/stream/{conversation_id} in [`python.@app.get`](src/main.py:1) returns a StreamingResponse that:
  - Subscribes to Redis channel sse:{conversation_id}.
  - Forwards newline-delimited JSON frames to the client.

7.2 Event Types and Shapes
- start: initial event after UnifiedProcessor begins work.
- routing: selection details including score and rationale.
- content: incremental text chunks and optional sources.
- done: marks finalization; includes prompt/completion tokens, summary.
- error: failure details including retryable flag and kind.
- workflow_start, workflow_progress, workflow_complete, workflow_failed for write flows.

7.3 Publishers
- UnifiedProcessor events during /api/chat in [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
- Workflow executor events during /api/write from handler code in [`python.@app.post("/api/write")`](src/main.py:1).

7.4 Error Frames
- Normalized and, when in pipeline, shaped by with_error_handling decorators in [`python.services.error_handler`](src/services/error_handler.py:1) and error middleware in [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).

----------------------------------------------------------------
Section 8 — Health, Status, and Provider Checks
----------------------------------------------------------------

8.1 Health
- GET /health basic: [`python.@app.get("/health")`](src/main.py:1).
- GET /health/detailed: [`python.@app.get("/health/detailed")`](src/main.py:1) includes checks for DB, Redis, and dependencies.

8.2 Unified Status
- GET /api/status provides composite view: routing thresholds, service readiness, provider availability at [`python.@app.get("/api/status")`](src/main.py:1).

8.3 Providers Status Matrix
- GET /api/providers/status aggregates health via [`python.ProviderFactory.health_check_all`](src/models/factory.py:1) in handler [`python.@app.get("/api/providers/status")`](src/main.py:1).
- Per-provider details include up/down and latencies based on implementation specifics.

----------------------------------------------------------------
Section 9 — Vector Retrieval, Evidence, and Downloads
----------------------------------------------------------------

9.1 Retrieval
- POST /api/retrieve handled at [`python.@app.post("/api/retrieve")`](src/main.py:1): vector or knowledge base retrieval.
- POST /api/search/semantic handled at [`python.@app.post("/api/search/semantic")`](src/main.py:1): semantic search.

9.2 Evidence
- GET /api/evidence/{conversation_id} collates artifacts from a run in [`python.@app.get("/api/evidence/{conversation_id}")`](src/main.py:1).

9.3 Download
- Conversations/download endpoints provide packaged results in the same routing region (nearby handlers in [`python.FastAPI()`](src/main.py:1)).

----------------------------------------------------------------
Section 10 — Profile, Credits, Billing, and Admin
----------------------------------------------------------------

10.1 Profile and Usage
- Profile routes included via [`python.include_router(profile_router)`](src/main.py:1).
- Usage/credits updated post-processing, with JWT validation via [`python.SecurityService`](src/services/security_service.py:1).

10.2 Billing and Payments
- Billing, payments, and payout routers included via [`python.include_router(billing_router)`](src/main.py:1) and peers.
- Payment integrations follow similar error/security patterns.

10.3 Admin
- Admin models, files, checker endpoints included via their routers; protected by JWT + role checks using decorators from [`python.SecurityService`](src/services/security_service.py:1).

----------------------------------------------------------------
Section 11 — Reliability, Errors, Circuit Breakers, Retries
----------------------------------------------------------------

11.1 Error Strategies
- Decorators in [`python.services.error_handler`](src/services/error_handler.py:1):
  - [`python.with_retry()`](src/services/error_handler.py:1): exponential backoff for transient failures.
  - [`python.with_circuit_breaker()`](src/services/error_handler.py:1): opens circuit on repeated failures; integrates Redis storage for state and broadcasts if configured.
  - [`python.with_error_handling()`](src/services/error_handler.py:1): wraps functions to produce normalized error outputs.

11.2 Middleware Normalization
- [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1) catches exceptions, classifies them, and returns contract-stable JSON responses.

11.3 Publisher Resilience
- When publishing SSE events, failures are handled by the same strategies; if Redis is unavailable, events may be dropped and HTTP response still returns with proper error semantics.

----------------------------------------------------------------
Section 12 — Security, CSRF, JWT, Rate Limiting
----------------------------------------------------------------

12.1 Security Middleware
- [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1) sets headers (X-Frame-Options, Content-Security-Policy), validates request shapes, and enforces security posture for all routes.

12.2 CSRF
- [`python.CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1) enforces CSRF tokens on non-idempotent HTTP verbs; tokens issued and validated against session or headers.

12.3 JWT and Guards
- [`python.SecurityService`](src/services/security_service.py:1) provides JWT creation/validation and request guards:
  - @require_auth
  - @require_admin
  - @rate_limited
  - validation helpers for inputs.

----------------------------------------------------------------
Section 13 — Configuration, Pricing, and Budgets
----------------------------------------------------------------

13.1 Settings
- [`python.HandyWriterzSettings`](src/config/__init__.py:1) with environment mode, provider keys, DB/Redis URLs, JWT secrets, CORS origins, rate limits.
- Logging setup via [`python.setup_logging()`](src/config/__init__.py:1).

13.2 Model Configuration
- [`yaml.model_config.yaml`](src/config/model_config.yaml:1) defines:
  - Role-based logical defaults and budget tiers.
  - Thresholds consumed by SystemRouter/Analyzer.

13.3 Pricing
- [`json.price_table.json`](src/config/price_table.json:1) maps model IDs to token costs; used in budgeting and reporting.

----------------------------------------------------------------
Section 14 — Data Access and Repositories
----------------------------------------------------------------

14.1 Database Manager
- [`python.class DatabaseManager`](src/db/database.py:1) sets up engine, runs minimal migrations and index setup, exposes health checks and dependency providers.

14.2 Repositories
- [`python.class UserRepository`](src/db/database.py:1), [`python.class ConversationRepository`](src/db/database.py:1), [`python.class DocumentRepository`](src/db/database.py:1) encapsulate persistence boundaries.

14.3 Dependency Injection
- [`python.def get_db()`](src/db/database.py:1) used in endpoints for safe session management.

----------------------------------------------------------------
Section 15 — Orchestration Composites
----------------------------------------------------------------

15.1 Graph Composites Spec
- [`yaml.composites.yaml`](src/graph/composites.yaml:1) contains declarative compositions for planner, research, QA, Turnitin, formatting pipelines.
- These composites inform advanced graph assembly in [`python.create_handywriterz_graph()`](src/agent/handywriterz_graph.py:1).

----------------------------------------------------------------
Section 16 — Operational Runbooks and Observability
----------------------------------------------------------------

16.1 Startup
- Lifespan checks Redis/DB/error handler in [`python.FastAPI()`](src/main.py:1). If any fail, app can abort startup to avoid running unhealthy.

16.2 Logs and Metrics
- Logging configured by [`python.setup_logging()`](src/config/__init__.py:1).
- Error middleware emits structured logs; SSE frames provide live telemetry of agentic progress.

16.3 Recovery
- Circuit breakers and retries ensure graceful degradation for provider outages.
- Health endpoints provide quick triage; provider status matrix indicates external dependency health.

----------------------------------------------------------------
Section 17 — Flow-by-Flow Swimlanes
----------------------------------------------------------------

17.1 Unified Chat (Simple Route)
Actors: Client → FastAPI → UnifiedProcessor → ComplexityAnalyzer → Simple Graph → SSE Publisher → Redis → Stream Endpoint → Client

Swimlane:
- Client: POST /api/chat with conversation_id, messages.
- FastAPI: enters handler [`python.@app.post("/api/chat")`](src/main.py:1).
- UnifiedProcessor:
  - Publish "start" to sse:{conversation_id} in [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
  - Analyzer score low ⇒ route=simple; publish "routing".
  - Build [`python.GeminiState`](src/agent/state.py:1); call [`python.gemini_graph`](src/agent/graph.py:1).
  - Iterate nodes: generate_query → web_research → reflection → finalize_answer.
  - Emit "content" frames with partial text.
  - Emit "done" with final content and token usage.
- Stream Endpoint: Client may concurrently GET /api/stream/{conversation_id} in [`python.@app.get`](src/main.py:1) to receive events.

17.2 Unified Chat (Advanced Route)
- Analyzer score high or academic flags detected.
- Build [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) with document type, citation style, field, region.
- Invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Emit multiple "content" frames; finalize with "done".

17.3 Unified Chat (Hybrid Route)
- Run simple and advanced in tandem.
- Emit interleaved "content" frames; final reconciliation strategy returns combined content; "done" published.

17.4 Provider-Scoped Streaming
- Client: POST /api/chat/provider/{provider}?stream=true
- Handler selects provider via [`python.get_provider`](src/models/factory.py:1).
- Calls [`python.stream_chat`](src/models/base.py:1) on provider.
- Chunks sent directly in HTTP streaming response (no Redis SSE for this path).
- Error handling by [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).

17.5 Write Workflow
- Client: POST /api/write with conversation_id, topic, document_type, citation_style, field, region, constraints.
- Handler builds [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1).
- Async invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Emit "workflow_start" → periodic "workflow_progress" → "workflow_complete" or "workflow_failed".
- Client subscribes via SSE.

17.6 Analyze-Only
- Client: POST /api/analyze.
- Handler calls Analyzer and returns characteristics with recommended route; no SSE.

17.7 Retrieval and Evidence
- Retrieval: POST /api/retrieve and /api/search/semantic.
- Evidence: GET /api/evidence/{conversation_id}.
- Typically synchronous JSON; may be used by agents for sources.

17.8 Profile/Credits and Billing
- Protected handlers with JWT guards; leverage [`python.SecurityService`](src/services/security_service.py:1).
- Update credit usage post-execution.

----------------------------------------------------------------
Section 18 — Appendices
----------------------------------------------------------------

18.1 SSE Event Reference (Canonical)
- start:
  {
    "type": "start",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "messagePreview": "...", "messageTokens": 0 }
  }
- routing:
  {
    "type": "routing",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "route": "simple|advanced|hybrid", "score": 1-10, "rationale": "...", "estimated_processing_seconds": 0 }
  }
- content:
  {
    "type": "content",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "text": "...", "role": "assistant", "sources": [ { "title": "...", "url": "...", "snippet": "..." } ] }
  }
- done:
  {
    "type": "done",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "final": true, "summary": "...", "tokens_used": { "prompt": 0, "completion": 0 } }
  }
- error:
  {
    "type": "error",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "message": "...", "kind": "provider|routing|validation|internal", "retryable": true }
  }
- workflow_start:
  {
    "type": "workflow_start",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "document_type": "...", "field": "...", "citation_style": "...", "region": "..." }
  }
- workflow_progress:
  {
    "type": "workflow_progress",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "node": "...", "progress": { "percent": 0, "status": "..." }, "notes": "..." }
  }
- workflow_complete:
  {
    "type": "workflow_complete",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "document_url": "...", "outline": [ "..." ], "sections": [ { "title": "...", "content": "..." } ] }
  }
- workflow_failed:
  {
    "type": "workflow_failed",
    "timestamp": "...",
    "conversation_id": "...",
    "payload": { "message": "...", "node": "..." }
  }

18.2 File Reference Index

---

18.3 Feature Flags — Runtime Controls for Safe Rollout

Environment flags and behavior:

- feature.sse_publisher_unified (default: off in prod, on in dev/stage)
  Behavior: Unified publisher emits JSON envelopes for all events from [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1) and workflow handlers [`python.@app.post("/api/write")`](backend/src/main.py:1).

- feature.double_publish_sse (default: off; enable in stage)
  Behavior: When true, publish both legacy Redis JSON and unified envelopes (shadow channel) to de-risk migration.

- feature.params_normalization (default: off in prod)
  Behavior: Apply [`python.normalize_user_params()`](backend/src/agent/routing/normalization.py:1) before routing; on error fall back to original input to preserve behavior.

- feature.registry_enforced (default: warn-only in prod)
  Behavior: On startup, compare [`yaml.model_config.yaml`](backend/src/config/model_config.yaml:1) and [`json.price_table.json`](backend/src/config/price_table.json:1); fail fast when enabled and mismatched.

- feature.search_adapter (default: on)
  Behavior: Normalize agent outputs via adapter to standardized SearchResult[] for Aggregator consumption, see [`python.adapter.to_search_results()`](backend/src/agent/search/adapter.py:1).

Operational sequence:
1) Enable feature.params_normalization in staging, validate analyzer parity.
2) Enable feature.double_publish_sse in staging, validate client parsing of unified envelopes.
3) Enable feature.sse_publisher_unified in production after stability.
4) Enable feature.registry_enforced post audit.
5) Keep feature.search_adapter enabled alongside Aggregator contract tests.

Flags visibility:
- Surfaced at [`python.@app.get("/api/status")`](backend/src/main.py:1) under features.flags populated from [`python.HandyWriterzSettings`](backend/src/config/__init__.py:1).
- Application and Endpoints
  - [`python.FastAPI()`](src/main.py:1)
  - [`python.@app.post("/api/chat")`](src/main.py:1)
  - [`python.@app.post("/api/chat/simple")`](src/main.py:1)
  - [`python.@app.post("/api/chat/advanced")`](src/main.py:1)
  - [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1)
  - [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1)
  - [`python.@app.post("/api/analyze")`](src/main.py:1)
  - [`python.@app.post("/api/retrieve")`](src/main.py:1)
  - [`python.@app.post("/api/search/semantic")`](src/main.py:1)
  - [`python.@app.get("/api/evidence/{conversation_id}")`](src/main.py:1)
  - [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1)
  - [`python.@app.get("/api/status")`](src/main.py:1)
  - [`python.@app.get("/api/providers/status")`](src/main.py:1)
  - [`python.@app.get("/health")`](src/main.py:1)
  - [`python.@app.get("/health/detailed")`](src/main.py:1)

- Agents and Routing
  - [`python.build_gemini_graph()`](src/agent/graph.py:1)
  - [`python.GeminiState`](src/agent/state.py:1)
  - [`python.create_handywriterz
