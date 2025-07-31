# flowith — End-to-end User Journey Trace (Frontend Prompt → Backend Agentic System → SSE → Outputs)

Goal
- Provide a comprehensive, code-grounded expansion of the existing flow in [`markdown.current flow`](backend/docs/flow.md:1), tracing a concrete use case from the Frontend Chat UI prompt to all backend layers and agentic components.
- Use the same mermaid style and sectioning, but extend to include SSE, UnifiedProcessor routing, simple/advanced graphs, provider selection, vector retrieval, formatting, QA, meta recovery, derivatives, billing/credits, and admin overrides.
- When issues or improvements are identified, add actionable items to todo101.md.

References (backend)
- FastAPI app, endpoints, SSE: [`python.FastAPI()`](backend/src/main.py:1), [`python.@app.post("/api/chat")`](backend/src/main.py:1), [`python.@app.post("/api/analyze")`](backend/src/main.py:1), [`python.@app.get("/api/stream/{conversation_id}")`](backend/src/main.py:1), [`python.@app.post("/api/write")`](backend/src/main.py:1)
- Unified routing and analyzer: [`python.class UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:1), [`python.class ComplexityAnalyzer`](backend/src/agent/routing/complexity_analyzer.py:1)
- Agents (simple/advanced): [`python.build_gemini_graph()`](backend/src/agent/graph.py:1), [`python.GeminiState`](backend/src/agent/state.py:1), [`python.create_handywriterz_graph()`](backend/src/agent/handywriterz_graph.py:1), [`python.HandyWriterzState`](backend/src/agent/handywriterz_state.py:1)
- Providers: [`python.ProviderFactory`](backend/src/models/factory.py:1), [`python.BaseProvider`](backend/src/models/base.py:1), [`python.OpenRouterProvider`](backend/src/models/openrouter.py:1), [`python.PerplexityProvider`](backend/src/models/perplexity.py:1)
- Middleware/security/errors: [`python.RevolutionarySecurityMiddleware`](backend/src/middleware/security_middleware.py:1), [`python.CSRFProtectionMiddleware`](backend/src/middleware/security_middleware.py:1), [`python.RevolutionaryErrorMiddleware`](backend/src/middleware/error_middleware.py:1), [`python.SecurityService`](backend/src/services/security_service.py:1), [`python.with_retry()`](backend/src/services/error_handler.py:1), [`python.with_circuit_breaker()`](backend/src/services/error_handler.py:1)
- Config/pricing/composites: [`yaml.model_config.yaml`](backend/src/config/model_config.yaml:1), [`json.price_table.json`](backend/src/config/price_table.json:1), [`yaml.composites.yaml`](backend/src/graph/composites.yaml:1)
- Database: [`python.DatabaseManager`](backend/src/db/database.py:1), [`python.get_db()`](backend/src/db/database.py:1)

Use Case
- “Research and write a 1,500-word comparative essay on renewable energy adoption in Germany vs. Spain, APA citations, with 8 sources. Include figures suggestions and a slide deck.”

We assume the user can drag files (supporting context) and request streaming output in UI. The flow uses unified /api/chat with SSE and may trigger /api/write for long-form structure based on routing heuristics.

Mermaid Flow (Comprehensive)
flowchart TD
    %% ───────────────────────── 1  FRONT‑END  ─────────────────────────
    subgraph FE["🖥️ Front‑end (Chat UI)"]
        direction TB
        FE0["User types prompt:
             “Comparative essay: Germany vs Spain renewable adoption,
              1,500 words, APA, 8 sources, include slides and figures.”
             ⬇️ optionally drags files (≤50 files, ≤100MB each)"] --> FE1
        FE1["ContextUploader
            • resumable uploads (tus-js or native)
            • progress thumbnails
            • returns file_ids[] via POST /api/files"] --> FE2
        FE2["POST /api/analyze {messages, file_ids}
            → previews route & ETA"] --> FE3
        FE3["SSE: GET /api/stream/{conversation_id}
            subscribe to live events before sending /api/chat"] --> FE4
        FE4["POST /api/chat {conversation_id, messages, file_ids, preferences,
            stream=false}
            • backend publishes SSE frames to the same conversation_id"] --> FE5
        FE5["Live Timeline (Agent events)
            • 'start' → 'routing' → 'content' → 'done'|'error'
            • shows analyzer score, route, progress"] --> FE6
        FE6["Downloads Menu
            • DOCX / PDF / PPT / ZIP (presigned URLs)
            • Evidence/References JSON"] --> FE7
        FE7["Wallet/Payments (Dynamic.xyz UI)
            • supports PayStack / Coinbase (via backend routes)"]
    end

    %% ───────────────────────── 2  FASTAPI CORE  ─────────────────────────
    FE4 --> A_ENTRY

    subgraph A_ENTRY["FastAPI Entrypoints"]
        A1["/api/chat
            Handler calls UnifiedProcessor.process_message()"] --> A2
        A2["/api/analyze
            returns score, indicators, recommended route"] --> A3
        A3["/api/write
            long-form workflow using HandyWriterzState"] --> A4
        A4["/api/stream/{conversation_id}
            StreamingResponse of Redis pub/sub frames"]
    end

    %% ───────────────────── 3  MIDDLEWARE / SECURITY  ───────────────────
    subgraph B_SEC["Middleware / Security / Error Normalization"]
        B1["RevolutionarySecurityMiddleware
            • security headers, validation"] --> B2
        B2["CSRFProtectionMiddleware
            • enforces tokens on state-changing verbs"] --> B3
        B3["RevolutionaryErrorMiddleware
            • catch + normalize errors to JSON
            • logs and classifications"]
    end
    A_ENTRY -.passes through .-> B_SEC

    %% ───────────────────── 4  ROUTING & ANALYZER  ──────────────────────
    B_SEC --> C_ROUTE

    subgraph C_ROUTE["Unified Routing & Analyzer"]
        C1["ComplexityAnalyzer
            • word count, attachments, academic cues
            • estimates processing time
            • score 1–10"] --> C2
        C2["SystemRouter (inside UnifiedProcessor)
            • choose simple | advanced | hybrid
            • rationale for 'routing' SSE event"] --> C3
        C3["Publisher
            • Redis publish to sse:{conversation_id}
            • emits 'start', then 'routing'"]
    end

    %% ───────────────────── 5  AGENTS & SUBAGENTS  ───────────────────────
    C_ROUTE --> D_AGENTS

    subgraph D_AGENTS["Agentic System"]
        direction TB
        D_S["Simple Agent (Gemini StateGraph)
            • build_gemini_graph()
            • nodes: generate_query → web_research → reflection → finalize_answer
            • emits concise, fast content"] --> D_P
        D_A["Advanced Agent (HandyWriterz Graph)
            • create_handywriterz_graph()
            • HandyWriterzState (DocumentType, CitationStyle, Field, Region)
            • pipelines: default, dissertation, reflection, case-study, tech-report, comparative-essay
            • deep orchestration, rich outputs"] --> D_P
        D_H["Hybrid
            • run simple + advanced in tandem
            • interleave 'content' frames
            • reconcile final output"] --> D_P
        D_P["Provider Abstraction
            • ProviderFactory → get_provider()
            • OpenRouterProvider / PerplexityProvider
            • BaseProvider.chat/stream_chat"]
    end

    %% ───────────────────── 6  RAG / RETRIEVAL  ─────────────────────────
    D_AGENTS --> E_RAG

    subgraph E_RAG["Retrieval & Evidence"]
        E1["vector retrieval (/api/retrieve, /api/search/semantic)
            • top-k similarity (pgvector)
            • unify sources"] --> E2
        E2["evidence collation
            /api/evidence/{conversation_id}"] --> E3
        E3["cache & costs
            • optional response cache by prompt/model
            • token tracking to USD ledger"]
    end

    %% ───────────────────── 7  WRITING / FORMATTING / QA  ────────────────
    E_RAG --> F_WRITE

    subgraph F_WRITE["Writing, Formatting, QA"]
        F1["writer (e.g., Gemini 2.5 Pro via provider)
            • streams paragraphs"] --> F2
        F2["writing helpers
            • academic_tone, clarity_enhancer
            • structure_optimizer, style_adaptation"] --> F3
        F3["citation_master
            • APA/MLA/Chicago
            • reference normalization"] --> F4
        F4["formatter_advanced
            • headings, figures placeholders
            • slide outline drafting"] --> F5
        F5["qa_swarm + evaluators
            • automated checks
            • evaluator_advanced"] --> F6
        F6["meta & recovery
            • retry with cheaper model
            • source fallback controller"] --> F7
        F7["derivatives
            • slide_generator, infographics
            • Turnitin (poll similarity)
            • optional Arweave persistence"]
    end

    %% ─────────────────────

%% ───────────────────── 8  RESPONSE PACKAGING & DOWNLOADS  ───────────────
subgraph G_PACK["Response Packaging and Download Artifacts"]
    G1["Final assembly
        • Select formatted_document | current_draft | draft_content
        • Attach verified_sources, citations, evaluation_score"] --> G2
    G2["Packaging
        • DOCX/PDF export (server side)
        • Slide outline to PPT template (if enabled)"] --> G3
    G3["Download URLs
        • Presigned URLs emitted in workflow_complete payload
        • Endpoint: [`python.@app.get("/api/evidence/{conversation_id}")`](backend/src/main.py:1) for artifacts JSON"]
end

%% ───────────────────── 9  SSE CLIENT CONSUMPTION  ───────────────────────
subgraph H_SSE["SSE Client Consumption Patterns"]
    H1["GET /api/stream/{conversation_id}"] --> H2["Handle frames (JSON only) per canonical schema in [`json.sse.schema.json`](backend/docs/sse.schema.json:1)"]
    H2 --> H3["UI Timeline rendering
        • start → routing → content* → done|error
        • show score, rationale, progress"]
    H2 --> H4["Resilience
        • auto-reconnect with backoff
        • idempotent frame handling via timestamps and last_event_id"]
end

%% ───────────────────── 10  CREDITS & BILLING  ───────────────────────────
subgraph I_BILL["Credits/Billing Update Flow"]
    I1["Budget estimate
        • guard_request before heavy work in [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:149)"] --> I2
    I2["Record usage
        • record_usage after result in [`python.UnifiedProcessor`](backend/src/agent/routing/unified_processor.py:235)"] --> I3
    I3["Frontend summaries
        • /app/api/billing/summary (Next.js) for user dashboard
        • Error states reflect BudgetExceededError SSE frames"]
end

%% ───────────────────── 11  PROVIDER HEALTH & DEGRADATION  ───────────────
subgraph J_HEALTH["Provider Health/Degradation Branches"]
    J1["GET /api/providers/status"] --> J2["Matrix of provider availability via [`python.ProviderFactory.health_check_all`](backend/src/models/factory.py:1)"]
    J2 --> J3["Router awareness (future)
        • degrade to cheaper provider on latency/outage
        • surfaced in routing.reason"]
end

%% ───────────────────── 12  ERROR RECOVERY & RETRIES  ────────────────────
subgraph K_ERR["Error Recovery and Retries"]
    K1["Decorators: [`python.with_retry()`](backend/src/services/error_handler.py:1),
        [`python.with_circuit_breaker()`](backend/src/services/error_handler.py:1),
        [`python.with_error_handling()`](backend/src/services/error_handler.py:1)"] --> K2
    K2["SSE error frames
        • type=error with kind and retryable
        • emitted by [`python.UnifiedProcessor._publish_event()`](backend/src/agent/routing/unified_processor.py:294)"] --> K3
    K3["Fallback
        • UnifiedProcessor attempts advanced fallback when simple fails
        • Controlled and logged with correlation_id"]
end
