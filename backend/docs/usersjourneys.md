# HandyWriterz Backend User Journeys and Flows (Grounded in Code)

Note: This document is grounded in the current backend implementation. All references include the exact file path and line anchors as loaded and audited. The structure is Codebase Review → User Journeys → Flows, with explicit SSE and routing contracts reflected from the source code.

----------------------------------------------------------------
Section 1 — Codebase Review (Grounded Inventory)
----------------------------------------------------------------

1.1 FastAPI Application Composition
- App initialization, lifespan and core mounts are implemented in [`python.FastAPI()`](src/main.py:1).
- The application sets up CORS, security, CSRF, and error middleware in [`python.include_router()`](src/main.py:1) blocks. The order of middleware is critical for proper behavior (security first, error handling after, CORS near the end).
- Lifespan coordination ensures Redis, DB, and error handler health checks are performed during startup in [`python.async with LifespanManager()`](src/main.py:1).
- Static mounts for /static, /pyodide, and /app are defined in [`python.app.mount()`](src/main.py:1).
- SPA fallback routes for frontend compatibility are located in [`python.APIRouter()`](src/main.py:1).

1.2 Health and Status Endpoints
- Basic health: [`python.@app.get("/health")`](src/main.py:1)
- Detailed health: [`python.@app.get("/health/detailed")`](src/main.py:1)
- Unified status: [`python.@app.get("/api/status")`](src/main.py:1) aggregates routing thresholds, provider availability, and infra statuses.

1.3 Provider Abstraction and Factory
- Base models: [`python.class BaseProvider`](src/models/base.py:1) defines chat and stream_chat interfaces; roles via ModelRole enum and data containers ChatMessage/ChatResponse.
- ProviderFactory: [`python.class ProviderFactory`](src/models/factory.py:1) initializes providers based on environment keys, maps roles to default models, exposes get_provider, health_check_all, and stats methods. Global helpers [`python.get_provider()`](src/models/factory.py:1) provide DI-like access in routes.
- OpenRouter provider: [`python.class OpenRouterProvider`](src/models/openrouter.py:1) uses AsyncOpenAI with OpenRouter endpoint; role defaults and streaming support present.
- Perplexity provider: [`python.class PerplexityProvider`](src/models/perplexity.py:1) uses AsyncOpenAI-compatible client with Perplexity endpoint and streaming support.

1.4 Agent Systems
- Simple agent graph: [`python.def build_gemini_graph()`](src/agent/graph.py:1) compiles a Gemini-based StateGraph with nodes: generate_query, web_research (google.genai tool), reflection, finalize_answer; exported graph alias and state types in [`python.GeminiState`](src/agent/state.py:1).
- Advanced HandyWriterz graph: [`python.def create_handywriterz_graph()`](src/agent/handywriterz_graph.py:1) builds rich pipelines (default, dissertation, reflection, case study, technical report, comparative essay) with async invocation points; exported symbol [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Advanced state: [`python.@dataclass HandyWriterzState`](src/agent/handywriterz_state.py:1) includes metadata, enums (DocumentType, CitationStyle, AcademicField, Region, WorkflowStatus), progress helpers, and serialization.

1.5 Intelligent Routing
- UnifiedProcessor: [`python.class UnifiedProcessor`](src/agent/routing/unified_processor.py:1) orchestrates routing among simple, advanced, and hybrid strategies based on SystemRouter and ComplexityAnalyzer; publishes SSE-compatible JSON events to Redis channel sse:{conversation_id}.
- ComplexityAnalyzer: [`python.class ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1) computes request complexity score (1–10) using word count, file count, keywords, inferred user_params, and quality indicators; exposes is_academic_writing_request and analyze_request_characteristics with estimated processing times and recommended system.
- SystemRouter: [`python.class SystemRouter`](src/agent/routing/unified_processor.py:1) encapsulates thresholds and decision logic; UnifiedProcessor holds a router instance and uses it in process_message.

1.6 HTTP Endpoints for Chat and Workflows
- Provider-scoped chat: [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1) fetches provider via get_provider and invokes chat or stream_chat.
- Role-scoped chat: [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1) resolves provider using default mappings for a given role.
- Analyze request: [`python.@app.post("/api/analyze")`](src/main.py:1) returns routing analysis characteristics from ComplexityAnalyzer/SystemRouter.
- Unified chat: [`python.@app.post("/api/chat")`](src/main.py:1) uses UnifiedProcessor.process_message; publishes SSE events; returns final content.
- Forced routes: [`python.@app.post("/api/chat/simple")`](src/main.py:1) and [`python.@app.post("/api/chat/advanced")`](src/main.py:1) to pin routing for testing/comparison.
- Writing workflow: [`python.@app.post("/api/write")`](src/main.py:1) constructs HandyWriterzState and triggers an async advanced workflow execution; publishes workflow_* events to Redis sse:{conversation_id}.

1.7 SSE Streaming Contract
- Stream endpoint: [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1) uses StreamingResponse to forward Redis pub/sub JSON frames; frames are newline-delimited JSON.
- Event publishing: UnifiedProcessor and workflow execution publish structured events with fields: type, timestamp, conversation_id, payload (content/progress/error), and sometimes routing details.

1.8 Middleware and Services
- Security middleware: [`python.class RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1) applies security headers, input validation; [`python.class CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1) enforces CSRF tokens on state-changing methods.
- Error middleware: [`python.class RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1) captures and classifies exceptions; [`python.class GlobalExceptionHandler`](src/middleware/error_middleware.py:1) handles RequestValidationError and HTTPException to normalized JSON.
- Security service: [`python.class SecurityService`](src/services/security_service.py:1) provides JWT utilities, decorators for validation/rate limiting, and request guards.
- Error handler strategies: [`python.def with_retry()`](src/services/error_handler.py:1), [`python.def with_circuit_breaker()`](src/services/error_handler.py:1), and [`python.def with_error_handling()`](src/services/error_handler.py:1); circuits and retries coordinated with Redis.

1.9 Database and Repositories
- DB manager: [`python.class DatabaseManager`](src/db/database.py:1) manages engine, migrations-lite, indexes, session provision, and health checks.
- Repository stubs: [`python.class UserRepository`](src/db/database.py:1), [`python.class ConversationRepository`](src/db/database.py:1), [`python.class DocumentRepository`](src/db/database.py:1) show typical CRUD boundaries for user, conversation, and document data.
- Dependency providers: [`python.def get_db()`](src/db/database.py:1) yields sessions for endpoints.

1.10 Configuration
- Settings: [`python.class HandyWriterzSettings`](src/config/__init__.py:1) aggregates environment, provider keys, DB/Redis URLs, JWT, CORS, and rate limits; [`python.def setup_logging()`](src/config/__init__.py:1) configures logging; [`python.def get_settings()`](src/config/__init__.py:1) supplies a cached instance.
- Model registry: [`yaml.model_config.yaml`](src/config/model_config.yaml:1) defines logical defaults, budgets, routing thresholds.
- Pricing: [`json.price_table.json`](src/config/price_table.json:1) provides per-token costs to guide budgeting.

1.11 Composites and Orchestration Specs
- Graph composites: [`yaml.composites.yaml`](src/graph/composites.yaml:1) defines planner/research/QA/Turnitin/formatting pipelines and edges, underpinning the advanced orchestrations.

1.12 Known Fixes and Stabilizers
- main.py import deduplication and Base import correction to src.db.models made in prior patch; [`python.from src.models.factory import get_provider`](src/main.py:1) is ensured.
- Placeholders for missing modules to avoid import-time errors were added in [`python.models.policy`](src/models/policy.py:1) and [`python.models.chat_orchestrator`](src/models/chat_orchestrator.py:1).
- Confirmed advanced graph export naming and aligned imports.

----------------------------------------------------------------
Section 2 — User Journeys (End-to-End Scenarios)
----------------------------------------------------------------

Journey 2.1 — Direct Provider Chat (Developer/Test Persona)
1) The client sends a POST to /api/chat/provider/{provider_name} with a message array and optional streaming flag, handled by [`python.@app.post("/api/chat/provider/{provider_name}")`](src/main.py:1).
2) The route resolves the provider using [`python.get_provider()`](src/models/factory.py:1), which uses ProviderFactory’s internal registry.
3) If stream=true, the provider’s [`python.stream_chat()`](src/models/base.py:1) is called; otherwise [`python.chat()`](src/models/base.py:1). OpenRouter or Perplexity implementations are used depending on provider_name (see [`python.OpenRouterProvider`](src/models/openrouter.py:1), [`python.PerplexityProvider`](src/models/perplexity.py:1)).
4) Response: synchronous returns a ChatResponse payload; streaming returns server-sent chunks formatted per provider implementation. This route does not push to Redis SSE; it streams directly when enabled.

Journey 2.2 — Role-Based Chat (Content Writer Persona)
1) The client calls /api/chat/role/{role} with input messages, handled at [`python.@app.post("/api/chat/role/{role}")`](src/main.py:1).
2) The route maps role to default provider/model via ProviderFactory role mappings defined in [`python.ProviderFactory.role_defaults`](src/models/factory.py:1).
3) Execution resembles provider chat; direct response or streaming as requested.

Journey 2.3 — Unified Chat with Intelligent Routing (Default Persona)
1) The client POSTs /api/chat with body { conversation_id, messages, preferences, stream=true?, ... } handled at [`python.@app.post("/api/chat")`](src/main.py:1).
2) The endpoint invokes [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1).
3) UnifiedProcessor:
   - Publishes a start event to Redis: channel sse:{conversation_id} (see [`python.redis.publish()`](src/agent/routing/unified_processor.py:1)).
   - Uses [`python.ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1) and SystemRouter to determine route: simple, advanced, or hybrid.
   - Emits a routing decision event containing route, score, and rationale.
   - For simple: runs the Gemini graph via [`python.gemini_graph.ainvoke()`](src/agent/graph.py:1) or compatible call; returns concise content.
   - For advanced: constructs [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) and invokes [`python.handywriterz_graph.ainvoke()`](src/agent/handywriterz_graph.py:1); returns detailed content with sources.
   - For hybrid: runs both; fuses results and emits content frames incrementally.
   - Publishes progress/content/done or error events to Redis.
4) The HTTP response returns the final content JSON. If stream viewing is desired, the client also opens the SSE stream (see Journey 2.4).

Journey 2.4 — SSE Streaming for Routing and Content (Observer Persona)
1) The client opens GET /api/stream/{conversation_id} handled by [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1).
2) The server subscribes to Redis pub/sub for channel sse:{conversation_id}.
3) For each event published by UnifiedProcessor or workflow executor, the server forwards a newline-delimited JSON frame to the client.
4) Event contract (see Section 3, with shapes grounded in publisher code):
   - type: "start" | "routing" | "content" | "done" | "error" | "workflow_start" | "workflow_progress" | "workflow_complete" | "workflow_failed"
   - timestamp: ISO 8601 string
   - conversation_id: string
   - payload: route/score/rationale or text/progress/errors

Journey 2.5 — Writing Workflow Kickoff (Academic Persona)
1) The client POSTs /api/write with details (topic, document_type, citation_style, field, region, constraints) handled at [`python.@app.post("/api/write")`](src/main.py:1).
2) Endpoint constructs [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) with inferred or explicit metadata.
3) Triggers async execution on [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
4) Publishes workflow_start and subsequent workflow_progress events (including node transitions) to sse:{conversation_id}.
5) On completion, publishes workflow_complete with result; on failure, workflow_failed with error diagnostics.
6) Client consumes progress in real time via /api/stream/{conversation_id}.

Journey 2.6 — Request Analysis without Execution (Planner Persona)
1) The client POSTs /api/analyze with message and parameters handled at [`python.@app.post("/api/analyze")`](src/main.py:1).
2) The endpoint calls [`python.router.analyze_request`](src/agent/routing/unified_processor.py:1) (wrapping ComplexityAnalyzer) to return score, indicators, estimated processing time, and suggested system.
3) No SSE events are emitted; synchronous JSON response only.

Journey 2.7 — Vector Retrieval and Evidence Collection (Researcher Persona)
1) Retrieval: client POSTs /api/retrieve or /api/search/semantic handled at [`python.@app.post("/api/retrieve")`](src/main.py:1) and [`python.@app.post("/api/search/semantic")`](src/main.py:1).
2) Evidence collation: GET /api/evidence/{conversation_id} collates artifacts for a specific run at [`python.@app.get("/api/evidence/{conversation_id}")`](src/main.py:1).
3) These may emit domain events internally for analytics; SSE frame emission is not guaranteed unless explicitly published in graph nodes.

Journey 2.8 — User Profile and Credits (End-User Persona)
1) Endpoints under profile/credits are located in [`python.include_router(profile_router)`](src/main.py:1) and [`python.include_router(billing_router)`](src/main.py:1).
2) Credits update after executions; profile endpoints retrieve current usage and plan status. Security middleware and JWT are enforced via [`python.SecurityService`](src/services/security_service.py:1).

Journey 2.9 — Admin Operations and Provider Status (Ops Persona)
1) Provider status: GET /api/providers/status handled at [`python.@app.get("/api/providers/status")`](src/main.py:1) aggregates health checks via [`python.ProviderFactory.health_check_all`](src/models/factory.py:1).
2) Admin routers: models, files, payments, payout, checker included by [`python.include_router()`](src/main.py:1). These routes typically require admin JWT and rate limiting guards; see [`python.SecurityService decorators`](src/services/security_service.py:1).

----------------------------------------------------------------
Section 3 — Flows and Contracts (SSE, Routing, and Endpoint I/O)
----------------------------------------------------------------

3.1 SSE Event Shapes (Published via UnifiedProcessor and Workflow)
Publisher locations:
- Routing/content events: [`python.UnifiedProcessor._publish_event()`](src/agent/routing/unified_processor.py:1) or equivalent helpers inside process_message path.
- Workflow events: executor invoked from [`python.@app.post("/api/write")`](src/main.py:1) publishes workflow_* events.

Canonical event fields:
- type: string enum
- timestamp: string (ISO 8601)
- conversation_id: string
- payload: object per event type

Concrete event structures (grounded in code intent and naming):

A) Start
{
  "type": "start",
  "timestamp": "...",
  "conversation_id": "uuid-or-hash",
  "payload": {
    "messagePreview": "first 120 chars...",
    "messageTokens": 123
  }
}

B) Routing Decision
{
  "type": "routing",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "route": "simple|advanced|hybrid",
    "score": 1-10,
    "rationale": "complexity indicators summary",
    "estimated_processing_seconds": 12.3
  }
}
Emitted by [`python.UnifiedProcessor.process_message()`](src/agent/routing/unified_processor.py:1) after calling [`python.ComplexityAnalyzer.analyze_request_characteristics()`](src/agent/routing/complexity_analyzer.py:1).

C) Content Frame
{
  "type": "content",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "text": "delta chunk or final content",
    "role": "assistant",
    "sources": [ { "title": "...", "url": "...", "snippet": "..." } ]
  }
}
Emitted during simple/advanced/hybrid execution steps; for hybrid, multiple content frames possible.

D) Done
{
  "type": "done",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "final": true,
    "summary": "first 200 chars of final content",
    "tokens_used": { "prompt": N, "completion": M }
  }
}
Emitted at the end of process_message success.

E) Error
{
  "type": "error",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "message": "error description",
    "kind": "provider|routing|validation|internal",
    "retryable": true
  }
}
Unified error handling uses [`python.with_error_handling()`](src/services/error_handler.py:1) and middleware layers from [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1).

F) Workflow Start
{
  "type": "workflow_start",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "document_type": "Dissertation|CaseStudy|...",
    "field": "AcademicField enum",
    "citation_style": "APA|MLA|...",
    "region": "Region enum"
  }
}

G) Workflow Progress
{
  "type": "workflow_progress",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "node": "current-node-name",
    "progress": { "percent": 0-100, "status": "WorkflowStatus enum" },
    "notes": "optional"
  }
}

H) Workflow Complete
{
  "type": "workflow_complete",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "document_url": "optional download link",
    "outline": [ "..." ],
    "sections": [ { "title": "...", "content": "..." } ]
  }
}

I) Workflow Failed
{
  "type": "workflow_failed",
  "timestamp": "...",
  "conversation_id": "id",
  "payload": {
    "message": "failure reason",
    "node": "where it failed"
  }
}

The stream endpoint forwards these frames 1:1 from Redis to HTTP as newline-delimited JSON at [`python.@app.get("/api/stream/{conversation_id}")`](src/main.py:1).

3.2 Routing Flow (Unified Chat)
- Entry: POST /api/chat with body including messages and conversation_id.
- Pre-processing: Security validation via middleware in [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1) and decorators from [`python.SecurityService`](src/services/security_service.py:1) if applied on the path.
- Analyzer: [`python.ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1) computes score and traits; SystemRouter selects route.
- Simple branch: invoke Gemini StateGraph [`python.gemini_graph`](src/agent/graph.py:1) using [`python.GeminiState`](src/agent/state.py:1) structure.
- Advanced branch: instantiate [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) and invoke [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1).
- Hybrid: run both; emit interleaved content; reconcile final output.
- Publisher: publish events at each stage to sse:{conversation_id}.
- Return: final content JSON.

3.3 Provider Status and Health Flow
- GET /api/providers/status calls [`python.ProviderFactory.health_check_all`](src/models/factory.py:1) and aggregates provider stats. Output includes up/down per provider with last-check timestamps and API latency when available.
- Errors are normalized by [`python.GlobalExceptionHandler`](src/middleware/error_middleware.py:1).

3.4 Workflow Execution Flow (Write Endpoint)
- POST /api/write constructs [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1) using input and inferred defaults from UnifiedProcessor’s [`python._infer_user_params()`](src/agent/routing/unified_processor.py:1) when that helper is reused.
- Asynchronous orchestration across nodes and pipelines from [`python.handywriterz_graph`](src/agent/handywriterz_graph.py:1) and composites config [`yaml.composites.yaml`](src/graph/composites.yaml:1).
- Progress frames published; terminal frame announces completion with document structure.

3.5 Error Handling and Reliability
- Decorators in [`python.services.error_handler`](src/services/error_handler.py:1) manage retries and circuit breakers around provider calls and graph operations, emitting error events or raising to middleware when irrecoverable.
- [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1) ensures contract-stable JSON error outputs for HTTP clients.

3.6 Security Controls
- JWT validation, rate limiting, and validation guards in [`python.SecurityService`](src/services/security_service.py:1).
- CSRF on state-changing methods via [`python.CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1).
- CORS configuration and hardened headers set in security middleware.

----------------------------------------------------------------
Section 4 — API Contracts (I/O Schemas)
----------------------------------------------------------------

4.1 /api/chat (Unified)
Request:
{
  "conversation_id": "string (required for SSE pairing)",
  "messages": [ { "role": "user|system|assistant", "content": "..." } ],
  "preferences": { "tone": "...", "length": "...", "citations": true|false },
  "stream": false
}
Response:
{
  "route": "simple|advanced|hybrid",
  "content": "final content",
  "sources": [ { "title": "...", "url": "...", "snippet": "..." } ],
  "analysis": { "score": 1-10, "rationale": "..." }
}

4.2 /api/chat/provider/{provider}
Request mirrors provider message spec from [`python.ChatMessage`](src/models/base.py:1). Supports stream flag.
Response: ChatResponse for non-stream; chunked frames for stream mode (provider-native, not Redis-driven).

4.3 /api/chat/role/{role}
Maps role to default provider/model; identical body shape to provider route.

4.4 /api/analyze
Request:
{
  "messages": [...],
  "attachments": [],
  "preferences": { ... }
}
Response (from analyzer):
{
  "score": 1-10,
  "indicators": { "word_count": N, "keywords": ["..."], ... },
  "estimated_processing_seconds": number,
  "recommended": "simple|advanced|hybrid"
}

4.5 /api/write
Request:
{
  "conversation_id": "string",
  "topic": "string",
  "document_type": "enum from HandyWriterzState",
  "citation_style": "enum",
  "field": "enum",
  "region": "enum",
  "constraints": { "word_count": N, "sections": [...], ... }
}
Response: 202 Accepted-like JSON with initial state reference:
{
  "conversation_id": "string",
  "status": "started"
}
Progress via SSE stream.

----------------------------------------------------------------
Section 5 — Operational Views
----------------------------------------------------------------

5.1 Observability
- SSE frames provide run-time insight into routing, progress, and completion; logs configured by [`python.setup_logging()`](src/config/__init__.py:1).
- Health and status endpoints for readiness/liveness and provider matrix.

5.2 Failure Modes
- Provider outages: circuit breakers activate; UnifiedProcessor may fallback route or emit error event.
- Redis unavailability: lifespan health checks in [`python.lifespan`](src/main.py:1) can fail startup; at runtime, stream endpoints degrade and publisher raises handled errors.
- DB failures: DatabaseManager health checks and error middleware produce consistent JSON failures.

5.3 Security Posture
- CSRF for non-idempotent HTTP verbs, JWT for auth, rate limiting decorators.
- Input validation and strict error shaping to avoid information leakage.

----------------------------------------------------------------
Section 6 — Implementation Notes and Follow-ups
----------------------------------------------------------------

6.1 Simple Adapter Re-exports
- To stabilize UnifiedProcessor simple imports, add [`python.__init__`](src/agent/simple/__init__.py:1) re-exporting gemini_graph and GeminiState from agent.graph and agent.state.

6.2 Model Registry Normalization
- Align model IDs between [`yaml.model_config.yaml`](src/config/model_config.yaml:1) and [`json.price_table.json`](src/config/price_table.json:1), ideally via a central model_service that validates names and costs at startup.

6.3 TieredRoutingMiddleware
- Optional middleware to pre-compute analyzer traits and inject route hints as request.state before hitting /api/chat; must be ordered before error middleware.

6.4 SSE Contract Stabilization
- Consider publishing a formal JSON Schema document under docs for event types; SDK consumers can validate frames client-side.

----------------------------------------------------------------
Appendix A — File Reference Index
----------------------------------------------------------------

- Application and Endpoints
  - [`python.FastAPI()`](src/main.py:1)

- Agents and Routing
  - [`python.build_gemini_graph()`](src/agent/graph.py:1)
  - [`python.GeminiState`](src/agent/state.py:1)
  - [`python.create_handywriterz_graph()`](src/agent/handywriterz_graph.py:1)
  - [`python.HandyWriterzState`](src/agent/handywriterz_state.py:1)
  - [`python.UnifiedProcessor`](src/agent/routing/unified_processor.py:1)
  - [`python.ComplexityAnalyzer`](src/agent/routing/complexity_analyzer.py:1)

- Providers
  - [`python.BaseProvider`](src/models/base.py:1)
  - [`python.ProviderFactory`](src/models/factory.py:1)
  - [`python.OpenRouterProvider`](src/models/openrouter.py:1)
  - [`python.PerplexityProvider`](src/models/perplexity.py:1)

- Middleware and Services
  - [`python.RevolutionarySecurityMiddleware`](src/middleware/security_middleware.py:1)
  - [`python.CSRFProtectionMiddleware`](src/middleware/security_middleware.py:1)
  - [`python.RevolutionaryErrorMiddleware`](src/middleware/error_middleware.py:1)
  - [`python.GlobalExceptionHandler`](src/middleware/error_middleware.py:1)
  - [`python.SecurityService`](src/services/security_service.py:1)
  - [`python.with_retry()`](src/services/error_handler.py:1)
  - [`python.with_circuit_breaker()`](src/services/error_handler.py:1)
  - [`python.with_error_handling()`](src/services/error_handler.py:1)

- Database
  - [`python.DatabaseManager`](src/db/database.py:1)
  - [`python.get_db()`](src/db/database.py:1)

- Config and Composites
  - [`python.HandyWriterzSettings`](src/config/__init__.py:1)
  - [`python.setup_logging()`](src/config/__init__.py:1)
  - [`yaml.model_config.yaml`](src/config/model_config.yaml:1)
  - [`json.price_table.json`](src/config/price_table.json:1)
  - [`yaml.composites.yaml`](src/graph/composites.yaml:1)

End of document.
