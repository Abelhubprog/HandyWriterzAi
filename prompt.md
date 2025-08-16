# HandyWriterzAI Chat UI Context

Goal: Give the model a full picture of what exists, what is wrong, and what we actually want. The fixes must match ChatGPT/Kimi K2 level polish.

## Backend Architecture Analysis

### Current Multi-Agent System
The backend implements a sophisticated multi-agent academic writing platform with:

#### Core Architecture
- **FastAPI Backend**: Production-ready with comprehensive error handling
- **Multi-Provider AI**: Gemini, OpenAI, Anthropic, Perplexity integration via factory pattern
- **Dual Graph System**: 
  - Simple Gemini graph for basic queries
  - Advanced HandyWriterz LangGraph for complex academic writing
- **Intelligent Routing**: UnifiedProcessor with ComplexityAnalyzer for optimal system selection

#### Multi-Agent Pipeline
1. **Intent Analysis**: Enhanced user intent → intelligent analyzer → fallback
2. **Planning**: Dynamic graph selection based on complexity
3. **Research Swarm**: Specialized agents (Arxiv, Scholar, CrossRef, PMC, etc.)
4. **Aggregation & RAG**: Vector similarity search with pgvector
5. **Writing Swarm**: Academic tone, citation master, structure optimization
6. **QA & Formatting**: Citation audit, evaluator, formatter
7. **Compliance**: Turnitin integration, privacy management

#### Critical Issues Identified
- **Parameter Fragmentation**: Inconsistent camelCase/snake_case across components
- **SSE Inconsistency**: Mixed JSON/str(dict) event publishing  
- **Search Agent Heterogeneity**: Each provider returns different schemas
- **Missing Components**: Normalization, registry, budget controls
- **Error Path Fragility**: Unsupported kwargs, unguarded finally blocks
- **Import Inconsistencies**: Relative import hazards

#### Development Priorities
1. **Foundation**: Parameter normalization, unified SSE publisher, model registry
2. **Reliability**: Error hardening, structured logging, budget enforcement  
3. **Security**: Middleware validation, rate limiting, CSRF compliance
4. **Completeness**: Missing agent nodes, file processing, Turnitin integration
5. **Testing**: Comprehensive unit/integration/contract test suite



## 1. What we currently have (from screenshots)

- Sidebar shows New chat, Search, some mock conversations, Library, Settings, User account. Most are placeholders. Selecting items does not load real data.
- Composer area:
  - Has a **Tools** button and a separate paperclip.
  - Writer type dropdown is **not** inside the composer row. It sits below or elsewhere.
  - Plus "file" button sometimes opens a large dropzone area instead of native file chooser.
  - Send arrow (↑) is inactive after clicking demo examples.
  - Mic icon exists but no clear dictation workflow.
- After sending, we sometimes get "Failed to fetch".
- Example cards (PhD Dissertation, Market Research, Technical Report) fill the center but the chat stream does not take over after first send.
- Export to PDF / DOCX / MD is not implemented where needed. The first image (ChatGPT export panel) is a feature to add but it should appear **after** a response.
- File rules text says 10 files → OK, but code still mentions 50 in places.
- Library, Settings, Profile are non-functional.
- Reasoning stream (agent thinking) is not visible or toggleable.

## 2. What we want (mental picture)

Think of ChatGPT’s composer and Kimi K2 file handling:

- **Single composer row** (always visible, sticky bottom):
  `[ + files ] [ Write-up type dropdown ] [ textarea auto-grow ] [ mic ] [ send arrow ]`
  - The write-up type dropdown replaces Tools.
  - The plus opens OS file picker directly. No big modal or dropzone. Drag-and-drop still works by hovering over composer.
  - Selected files appear as small chips above the textarea with remove buttons.
- **Send arrow** always activates as soon as:
  - There is text OR files OR an example prompt is injected.
- **Example cards**:
  - Clicking a card pre-fills the textarea, focuses it, and enables the arrow.
  - After first send, the main chat stream scrolls into view. Example cards slide away or shrink.
- **Streaming**:
  - Assistant messages stream token by token.
  - A small “Show reasoning” toggle under each assistant bubble reveals agent thinking text.
  - A subtle status ticker under the first assistant message: “Parsing files… Routing to agents… Drafting… Formatting…”
- **Export and share**:
  - On each assistant response, show a subtle actions row (like ChatGPT’s panel): Copy link, X, LinkedIn, Reddit, Download.
  - Download button opens a mini menu: PDF, DOCX, MD.
  - Also add a top-right Export menu for the whole conversation.
- **Sidebar**:
  - Real conversation list with titles, timestamps.
  - Search filters in memory (later server side).
  - Clicking loads messages without reload.
  - New chat resets composer and state.
- **Library**:
  - Lists saved final outputs. Click to preview or reopen in chat.
- **Profile/Settings**:
  - At least stub real state. Do not leave dead links.

## 3. Component layout
components/chat/
ChatSidebar.tsx
ConversationList.tsx
ConversationItem.tsx
ChatWindow.tsx
MessageBubble.tsx
ReasoningToggle.tsx (optional inside MessageBubble)
MessageInputBar.tsx
WriterTypeSelect.tsx
FileChips.tsx
ExportMenu.tsx (conversation-level)
ResponseActions.tsx (copy/share/download row on each assistant msg)
UploadProgress.tsx


## 4. State contracts

- Store: Zustand (chatStore + uiStore)
  - chatStore: conversations[], activeId, messages[], writerType, pendingFiles[], isStreaming, error
  - uiStore: showExportModal, showLibrary, toasts, sidebarOpen
- Actions:
  - startNewConversation
  - selectConversation
  - sendMessage(text, files)
  - attachFiles(files)
  - removeFile(fileId)
  - setWriterType(type)
  - exportConversation(format)
- Validation:
  - 10 files max
  - 100 MB per file max

## 5. API contracts (confirm or mock)

- POST /chat/send → { conversation_id, stream_url }
- SSE stream: {type: "content"|"thinking"|"done", token: "..."}
- POST /files/upload (multipart, returns file_ids)
- GET /conversations
- GET /conversations/:id/messages
- GET /export/:conversation_id?format=pdf|docx|md

## 6. Acceptance checks

- Composer row unified. No separate Tools button.
- Plus opens file dialog. Chips show. Validation enforced early.
- Example click enables send. No need to type first.
- Stream works. Reasoning toggle works.
- Export row appears on every assistant reply. Export menu also exists near chat title.
- Sidebar loads and switches chats.
- No blank “Failed to fetch” screens. Show toast and retry.
- Library page lists docs.
- Build passes without TS errors. No console warnings.
- Mobile responsive.



Picture ChatGPT or Kimi K2:

Left rail: persistent, polished, shows chats, search, library, profile.

Center: clean conversational thread with friendly bubbles and a discreet toggle to peek at the model’s reasoning.

Bottom: one single elegant composer. The plus opens native file picker instantly. Write type dropdown sits right there, not floating somewhere else. The mic icon records voice. The arrow lights up the instant anything valid is in the box (or after you pick an example).

When you drop a file, the whole composer shows a subtle dashed highlight. After selection, tiny chips show the files, easily removable.

Streaming looks smooth. A tiny “Parsing files… Routing to agents…” ticker under the first assistant bubble gives transparency.

Export lives in top right, next to share. Click, pick PDF or DOCX or MD, boom.

No ugly full-screen error messages. Just a toast and a retry button.



current flow
flowchart TD
    %% ───────────────────────── 1  FRONT‑END  ─────────────────────────
    subgraph FE["🖥️  Front‑end (React 19 + Vite)"]
        direction TB
        FE0["User types prompt  
              ⬇️ drags ≤50 files (≤100 MB each)"] --> FE1
        FE1["ContextUploader  
            • tus‑js resumable upload  
            • shows thumbnails + progress"] --> FE2
        FE2["POST /api/files  
            returns file_ids[]"] --> FE3
        FE3["POST /api/chat {prompt, mode, file_ids}"] --> FE4
        FE4["WebSocket /ws/{trace_id}  
            🔄 AgentTimeline + ChatMessages  
            streams Node events"] --> FE5
        FE5["DownloadMenu  
            DOCX / PDF / PPT / ZIP  
            presigned URL"] --> FE6
        FE6["WalletButton (Dynamic.xyz)  
            Coinbase Pay ✚ PayStack"]        
    end

    %% ───────────────────────── 2  FASTAPI CORE  ─────────────────────────
    FE3 --> A_INTENT

    subgraph A_INTENT["Intent Layer"]
        A1["enhanced_user_intent"] --> A2
        A2["intelligent_intent_analyzer"] --> A3
        A3["user_intent (fallback)"]
    end

    A_INTENT --> B_PLAN

    subgraph B_PLAN["Planning Layer"]
        B1["planner"] -->|select graph YAML| B2
        B2["methodology_writer (if research)"]
        B2 --> B3["loader (seed docs)"]
    end

    %% ───────────────  FILE PRE‑PROCESSING (CELERY)  ───────────────
    FE1 -. async .-> C_EMBED

    subgraph C_EMBED["File Chunk & Embed  (Celery)"]
        direction TB
        C1["chunk_splitter  
            • PDF 1 400 char windows  
            • DOC/TXT by paragraph  
            • images → Gemini Vision caption  
            • audio → Whisper transcript"] --> C2
        C2["embedding_service  
            → Supabase pgvector"] --> C3
        C3["vector_storage"],
        style C_EMBED stroke-dasharray: 4 4
    end

    %% ───────────────────────── 3  RUNTIME GRAPH  ─────────────────────────
    B_PLAN --> C_RESEARCH

    subgraph C_RESEARCH["Research Swarm"]
        C_R0["search_base + search_*"] --> C_R1
        C_R1["research_swarm/* specialists"] --> C_R2
        C_R2["source_filter"] --> C_R3
        C_R3["source_verifier"] --> C_R4
        C_R4["prisma_filter"] --> C_R5
        C_R5["privacy_manager"]
    end

    C_RESEARCH --> D_AGG

    subgraph D_AGG["Aggregation & RAG"]
        D1["aggregator"] --> D2["rag_summarizer  
        🔍 pgvector similarity(top 8)"]
        D2 --> D3["memory_retriever"]
        D3 --> D4["memory_writer"]
    end

    D_AGG --> E_AUTHOR

    subgraph E_AUTHOR["Writing Swarm"]
        E1["writer (Gemini 2.5 Pro) 🚀  
            streams paragraphs"] --> E2
        E2["writing_swarm helpers  
             • academic_tone  
             • clarity_enhancer  
             • structure_optimizer  
             • style_adaptation"] --> E3
        E3["citation_master"]
    end

    E_AUTHOR --> F_FORMAT

    subgraph F_FORMAT["Formatting / QA"]
        F1["formatter_advanced"] --> F2
        F2["citation_audit"] --> F3
        F3["qa_swarm/*"] --> F4
        F4["evaluator"] --> F5["evaluator_advanced"]
    end

    F_FORMAT --> G_META

    subgraph G_META["Meta / Recovery"]
        G1["swarm_intelligence_coordinator"] --> G2
        G2["emergent_intelligence_engine"] --> G3
        G3["fail_handler_advanced  
            ↺ retry w/ cheaper model"] --> G4
        G4["source_fallback_controller"] --> G5["synthesis"]
    end

    G_META --> H_DERIV

    subgraph H_DERIV["Derivatives & Compliance"]
        H1["slide_generator"] --> H2
        H2["derivatives (charts, infographics)"] --> H3
        H3["turnitin_advanced  
             • Celery poll → similarity"] --> H4
        H4["arweave (optional)"]
    end

    H_DERIV --> I_RESP

    subgraph I_RESP["📤  UnifiedResponse"]
        I1["JSON -> /api/chat response"] --> I2["WebSocket events  
                • stream  
                • cost_usd  
                • plagiarism_score  
                • derivative_ready"]
    end

    %% ────────── SUPPORTING SERVICES (SIDE‑CHANNELS) ──────────
    subgraph S1["Redis / Cost & Cache"]
        S1a["llm_service → cache(prompt,model)"] 
        S1b["token_tracker → usd ledger"]
    end
    S1a --> E_AUTHOR
    S1a --> C_RESEARCH
    S1b --> I_RESP

    subgraph S2["Admin & Billing"]
        ADM1["/api/admin/models  
              → Redis model_override:*"] --> A_INTENT
        PAY1["/api/payments  
              PayStack / Coinbase"] --> S1b
    end


deeply study and analyse the project and create working solutions to make the agentic system work fully, and the chat UI work all as one multiagent powered app.  study  and analyse the codebase very keenly  @/backend @/frontend  @/backend/src @/frontend/src  all files!
ai have attached comprehensive codebase detail gitingest detaisl to help you study fully, take extended time to read long context in several rounds to avoid max tokens or context window challenges. @/entirbackendrepo.md  @/entirefrontendrepo.md @/Failure\ report.txt  You are to study the project and create working solutions to make the agentic system work fully, and the chat UI work all as one multiagent powered app.  study the repo very keenly. study the codebase fully. 
i have attached comprehensive repo detail gitingest detail to help you study fully, take extended time to read long context in several rounds to avoid max tokens or context window challenges. Then, specifically provide fixes in several ways: 
a comprehensive plan that groups issues in different categories, then write prompts for fixing in every category. todos for every issue that is comprehensive to fix every issue in finer details. i expect you to response in several chat responses, i will ask you to continue.  Then, conduct surgical fixes, you are granted all access. no questions, do all necessary fixes.
Below is a “full-stack narrative” of **how the HandyWriterzAI multi-agent system operates once all fixes are in place.**
I am walking from the user’s click in the browser to the last byte flushed over SSE, showing how every subsystem cooperates.

---

Directory structure:
└── backend/
    ├── README.md
    ├── alembic.ini
    ├── docker-compose.yml
    ├── Dockerfile
    ├── Dockerfile.production
    ├── Dockerfile.railway
    ├── langgraph.json
    ├── LICENSE
    ├── Makefile
    ├── mcp_config.json
    ├── models.json
    ├── quick_start.py
    ├── requirements.txt
    ├── run_server.py
    ├── setup_api_keys.py
    ├── start_server.py
    ├── test_import.py
    ├── test_minimal.py
    ├── test_normalization_standalone.py
    ├── test_phase_implementation.py
    ├── test_production_fixes.py
    ├── test_providers.py
    ├── test_simple_providers.py
    ├── test_user_journey.py
    ├── test_write_endpoint_normalization.py
    ├── .dockerignore
    ├── .env.example
    ├── alembic/
    │   ├── README
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       ├── 2b3c4d5e6f7g_create_versioned_system_prompts_table.py
    │       ├── d2b13d0018af_create_model_map_table.py
    │       └── railway_migration_20250123.py
    ├── docs/
    │   ├── abelhubprog-handywriterzai-fileingest.txt
    │   ├── agentic.md
    │   ├── flow.md
    │   ├── flowith.md
    │   ├── flows.md
    │   ├── plan.md
    │   ├── prompt.md
    │   ├── redesign.md
    │   ├── storage.md
    │   ├── todo100.md
    │   ├── todo101.md
    │   ├── userjourneys.md
    │   ├── usersjourneys.md
    │   └── workbench.md
    ├── scripts/
    │   ├── init-db.sql
    │   ├── init_database.py
    │   ├── install_minimal.py
    │   ├── reset_db.py
    │   ├── setup-test-env.sh
    │   ├── setup.sh
    │   └── test-e2e.sh
    ├── src/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── main.py
    │   ├── unified_processor.py
    │   ├── agent/
    │   │   ├── __init__.py
    │   │   ├── app.py
    │   │   ├── base.py
    │   │   ├── configuration.py
    │   │   ├── handywriterz_graph.py
    │   │   ├── handywriterz_state.py
    │   │   ├── prompts.py
    │   │   ├── sse.py
    │   │   ├── sse_unified.py
    │   │   ├── tools_and_schemas.py
    │   │   ├── utils.py
    │   │   ├── nodes/
    │   │   │   ├── __init__.py
    │   │   │   ├── aggregator.py
    │   │   │   ├── arweave.py
    │   │   │   ├── citation_audit.py
    │   │   │   ├── derivatives.py
    │   │   │   ├── emergent_intelligence_engine.py
    │   │   │   ├── enhanced_user_intent.py
    │   │   │   ├── error_handling.py
    │   │   │   ├── evaluator.py
    │   │   │   ├── evaluator_advanced.py
    │   │   │   ├── fail_handler_advanced.py
    │   │   │   ├── formatter_advanced.py
    │   │   │   ├── intelligent_intent_analyzer.py
    │   │   │   ├── legislation_scraper.py
    │   │   │   ├── loader.py
    │   │   │   ├── master_orchestrator.py
    │   │   │   ├── memory_integrator_node.py
    │   │   │   ├── memory_retriever.py
    │   │   │   ├── memory_writer.py
    │   │   │   ├── methodology_writer.py
    │   │   │   ├── planner.py
    │   │   │   ├── prisma_filter.py
    │   │   │   ├── privacy_manager.py
    │   │   │   ├── rag_summarizer.py
    │   │   │   ├── rewrite_agent.py
    │   │   │   ├── rewrite_o3.py
    │   │   │   ├── search_base.py
    │   │   │   ├── search_claude.py
    │   │   │   ├── search_crossref.py
    │   │   │   ├── search_deepseek.py
    │   │   │   ├── search_gemini.py
    │   │   │   ├── search_github.py
    │   │   │   ├── search_grok.py
    │   │   │   ├── search_o3.py
    │   │   │   ├── search_openai.py
    │   │   │   ├── search_perplexity.py
    │   │   │   ├── search_pmc.py
    │   │   │   ├── search_qwen.py
    │   │   │   ├── search_scholar.py
    │   │   │   ├── search_ss.py
    │   │   │   ├── slide_generator.py
    │   │   │   ├── source_fallback_controller.py
    │   │   │   ├── source_filter.py
    │   │   │   ├── source_verifier.py
    │   │   │   ├── swarm_intelligence_coordinator.py
    │   │   │   ├── synthesis.py
    │   │   │   ├── turnitin_advanced.py
    │   │   │   ├── tutor_feedback_loop.py
    │   │   │   ├── user_intent.py
    │   │   │   ├── writer.py
    │   │   │   ├── writer_migrated.py
    │   │   │   ├── qa_swarm/
    │   │   │   │   ├── argument_validation.py
    │   │   │   │   ├── bias_detection.py
    │   │   │   │   ├── ethical_reasoning.py
    │   │   │   │   ├── fact_checking.py
    │   │   │   │   └── originality_guard.py
    │   │   │   ├── research_swarm/
    │   │   │   │   ├── arxiv_specialist.py
    │   │   │   │   ├── cross_disciplinary.py
    │   │   │   │   ├── methodology_expert.py
    │   │   │   │   ├── scholar_network.py
    │   │   │   │   └── trend_analysis.py
    │   │   │   └── writing_swarm/
    │   │   │       ├── academic_tone.py
    │   │   │       ├── citation_master.py
    │   │   │       ├── clarity_enhancer.py
    │   │   │       ├── structure_optimizer.py
    │   │   │       └── style_adaptation.py
    │   │   ├── orchestration/
    │   │   │   ├── __init__.py
    │   │   │   ├── agent_pool.py
    │   │   │   ├── cache_manager.py
    │   │   │   ├── distributed_coordinator.py
    │   │   │   ├── integration.py
    │   │   │   ├── monitoring.py
    │   │   │   ├── resource_manager.py
    │   │   │   └── swarm_coordinator.py
    │   │   ├── repair/
    │   │   │   ├── __init__.py
    │   │   │   └── repair_controller.py
    │   │   ├── routing/
    │   │   │   ├── __init__.py
    │   │   │   ├── complexity_analyzer.py
    │   │   │   ├── normalization.py
    │   │   │   ├── registry_adapter.py
    │   │   │   ├── system_router.py
    │   │   │   └── unified_processor.py
    │   │   └── search/
    │   │       ├── __init__.py
    │   │       └── adapter.py
    │   ├── api/
    │   │   ├── billing.py
    │   │   ├── checker.py
    │   │   ├── circle.py
    │   │   ├── citations.py
    │   │   ├── evidence.py
    │   │   ├── files.py
    │   │   ├── files_enhanced.py
    │   │   ├── memory.py
    │   │   ├── payments.py
    │   │   ├── payout.py
    │   │   ├── profile.py
    │   │   ├── turnitin.py
    │   │   ├── usage.py
    │   │   ├── vision.py
    │   │   ├── webhook_turnitin.py
    │   │   ├── whisper.py
    │   │   ├── workbench.py
    │   │   ├── workbench_admin.py
    │   │   ├── workbench_auth.py
    │   │   ├── workbench_ingestion.py
    │   │   └── schemas/
    │   │       ├── chat.py
    │   │       ├── workbench.py
    │   │       ├── workbench_auth.py
    │   │       └── worker.py
    │   ├── auth/
    │   │   ├── __init__.py
    │   │   └── workbench_auth.py
    │   ├── blockchain/
    │   │   └── escrow.py
    │   ├── config/
    │   │   ├── __init__.py
    │   │   ├── memory_config.yaml
    │   │   ├── model_config.py
    │   │   ├── model_config.yaml
    │   │   ├── orchestrator_policies.yaml
    │   │   ├── price_table.json
    │   │   └── prompt_policies.yaml
    │   ├── core/
    │   │   └── config.py
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   ├── models.py
    │   │   └── repositories/
    │   │       ├── __init__.py
    │   │       ├── workbench_artifact_repo.py
    │   │       ├── workbench_assignment_repo.py
    │   │       ├── workbench_section_status_repo.py
    │   │       ├── workbench_submission_repo.py
    │   │       └── workbench_user_repo.py
    │   ├── gateways/
    │   │   ├── __init__.py
    │   │   └── telegram_gateway.py
    │   ├── graph/
    │   │   └── composites.yaml
    │   ├── mcp/
    │   │   └── mcp_integrations.py
    │   ├── middleware/
    │   │   ├── error_middleware.py
    │   │   ├── gateway_middleware.py
    │   │   ├── security_middleware.py
    │   │   └── tiered_routing.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── anthropic.py
    │   │   ├── base.py
    │   │   ├── chat_orchestrator.py
    │   │   ├── chat_orchestrator_core.py
    │   │   ├── factory.py
    │   │   ├── gemini.py
    │   │   ├── openai.py
    │   │   ├── openrouter.py
    │   │   ├── perplexity.py
    │   │   ├── policy.py
    │   │   ├── policy_core.py
    │   │   ├── registry.py
    │   │   └── task.py
    │   ├── prompts/
    │   │   ├── evidence_guard_v1.txt
    │   │   ├── sophisticated_agent_prompts.py
    │   │   ├── system_prompts.py
    │   │   └── templates/
    │   │       ├── common_header.jinja
    │   │       ├── header.jinja
    │   │       ├── output_contract_dissertation.jinja
    │   │       ├── output_contract_general.jinja
    │   │       ├── safety.jinja
    │   │       ├── tools_contracts.jinja
    │   │       ├── usecase_dissertation.jinja
    │   │       ├── usecase_general.jinja
    │   │       ├── usecase_research_paper.jinja
    │   │       └── usecase_thesis.jinja
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── admin_gateway.py
    │   │   ├── admin_models.py
    │   │   └── chat_gateway.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── sse_events.py
    │   │   └── sse_v1.json
    │   ├── scripts/
    │   │   └── memory_maintenance.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── advanced_llm_service.py
    │   │   ├── budget.py
    │   │   ├── chunk_splitter.py
    │   │   ├── chunking_service.py
    │   │   ├── database_service.py
    │   │   ├── document_processing_service.py
    │   │   ├── embedding_service.py
    │   │   ├── error_handler.py
    │   │   ├── feature_validator.py
    │   │   ├── gateway.py
    │   │   ├── health_monitor.py
    │   │   ├── highlight_parser.py
    │   │   ├── llm_service.py
    │   │   ├── logging_context.py
    │   │   ├── memory_integrator.py
    │   │   ├── memory_safety.py
    │   │   ├── model_policy.py
    │   │   ├── model_registry.py
    │   │   ├── model_selector.py
    │   │   ├── model_service.py
    │   │   ├── node_integration.py
    │   │   ├── notification_service.py
    │   │   ├── payment_service.py
    │   │   ├── policy_loader.py
    │   │   ├── production_llm_service.py
    │   │   ├── prompt_orchestrator.py
    │   │   ├── railway_db_service.py
    │   │   ├── README_MEMORY.md
    │   │   ├── security_service.py
    │   │   ├── supabase_service.py
    │   │   ├── telegram_gateway.py
    │   │   ├── tracing.py
    │   │   ├── vector_storage.py
    │   │   ├── workbench_auth_service.py
    │   │   └── workbench_service.py
    │   ├── telegram/
    │   │   ├── gateway.py
    │   │   └── workers.py
    │   ├── tests/
    │   │   ├── test_api.py
    │   │   ├── test_memory_integration.py
    │   │   ├── test_phase_1_integration.py
    │   │   ├── test_search_perplexity.py
    │   │   ├── test_services.py
    │   │   ├── test_source_filter.py
    │   │   ├── test_user_journey.py
    │   │   ├── test_writer.py
    │   │   └── e2e/
    │   │       └── test_full_flow.py
    │   ├── tools/
    │   │   ├── action_plan_template_tool.py
    │   │   ├── case_study_framework_tool.py
    │   │   ├── casp_appraisal_tool.py
    │   │   ├── cost_model_tool.py
    │   │   ├── gibbs_framework_tool.py
    │   │   ├── github_tools.py
    │   │   ├── google_web_search.py
    │   │   └── mermaid_diagram_tool.py
    │   ├── turnitin/
    │   │   ├── __init__.py
    │   │   ├── bot_conversation.py
    │   │   ├── delivery.py
    │   │   ├── models.py
    │   │   ├── orchestrator.py
    │   │   ├── telegram_session.py
    │   │   └── workbench_bridge.py
    │   ├── utils/
    │   │   ├── arweave.py
    │   │   ├── chartify.py
    │   │   ├── csl.py
    │   │   ├── file_utils.py
    │   │   └── prompt_loader.py
    │   ├── workers/
    │   │   ├── __init__.py
    │   │   ├── chunk_queue_worker.py
    │   │   ├── payout_batch.py
    │   │   ├── sla_timer.py
    │   │   ├── turnitin_poll.py
    │   │   ├── tutor_finetune.py
    │   │   └── zip_exporter.py
    │   └── workflows/
    │       └── rewrite_cycle.py
    └── tests/
        ├── test_chunk_splitter_integration.py
        ├── test_dissertation_journey.py
        ├── test_e2e.py
        ├── test_evidence_guard.py
        ├── test_health.py
        ├── test_memory_writer.py
        ├── test_prompt_orchestrator.py
        ├── test_routing.py
        ├── test_swarm_intelligence.py
        ├── test_utils.py
        └── test_voice_upload.py


Files Content:

(Files content cropped to 300k characters, download full ingest to see more)
================================================
FILE: backend/README.md
================================================
# 🚀 Unified AI Platform - Revolutionary Multi-Agent System

## Overview

The **Unified AI Platform** is an intelligent multi-agent system that seamlessly combines:

- **Simple Gemini System**: Fast responses for quick queries and basic tasks
- **Advanced HandyWriterz System**: Comprehensive academic writing with 30+ specialized agents
- **Intelligent Routing**: Automatic system selection based on request complexity analysis

## ✨ Key Features

### 🎯 Intelligent Routing
- **Automatic System Selection**: Analyzes request complexity (1-10 scale) and routes optimally
- **Academic Detection**: Essays, research papers automatically use advanced system
- **Hybrid Processing**: Parallel execution for medium-complexity tasks
- **Graceful Fallbacks**: Robust error handling with system switching

### 🧠 Advanced Multi-Agent System
- **30+ Specialized Agents**: Research swarms, QA swarms, writing swarms
- **Master Orchestrator**: 9-phase workflow optimization
- **Swarm Intelligence**: Emergent behavior from agent collaboration
- **Quality Assurance**: Multi-tier evaluation and validation

### ⚡ Performance Optimization
- **Smart Caching**: Redis-based caching for faster responses
- **Parallel Processing**: Hybrid mode runs both systems simultaneously
- **Circuit Breakers**: Automatic failover and recovery
- **Load Balancing**: Optimal resource utilization

## 🏗️ Architecture

```
Unified AI Platform
├── Intelligent Router
│   ├── Complexity Analyzer (1-10 scale)
│   ├── Academic Detection
│   └── System Selection Logic
├── Simple Gemini System
│   ├── Quick Chat Responses
│   ├── Basic Research
│   └── Fast Processing (<3s)
└── Advanced HandyWriterz System
    ├── Master Orchestrator
    ├── Research Swarms (5+ agents)
    ├── QA Swarms (5+ agents)
    ├── Writing Swarms (5+ agents)
    ├── Citation Management
    ├── Quality Assessment
    └── Academic Formatting
```

## 📊 Routing Logic

| Query Type | Complexity Score | System Used | Response Time |
|------------|------------------|-------------|---------------|
| "What is AI?" | 2.0 | Simple | 1-3 seconds |
| "Explain machine learning" | 5.5 | Hybrid | 30-60 seconds |
| "Write a 5-page essay on climate change" | 8.5 | Advanced | 2-5 minutes |
| File uploads + analysis | 6.0+ | Advanced/Hybrid | 1-10 minutes |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Redis (for caching and SSE)
- PostgreSQL with pgvector (for advanced features)

### 1. Automated Setup
```bash
cd backend/backend
python setup.py
```

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
redis-server  # In another terminal
# PostgreSQL setup (optional for advanced features)

# Run the server
python src/main.py
```

### 3. Verify Installation
```bash
# Check system status
curl http://localhost:8000/api/status

# Test routing analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Write a research paper on artificial intelligence"
```

## 🎮 Usage Examples

### Simple Chat Query
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=What is artificial intelligence?"

# Response: Fast answer from Gemini system
```

### Academic Writing Request
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Write a 3-page academic essay on climate change impacts" \
  -d "user_params={\"writeupType\":\"essay\",\"pages\":3,\"field\":\"environmental science\"}"

# Response: Full HandyWriterz workflow with research, writing, and citations
```

### File Analysis
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -F "message=Analyze this document and provide insights" \
  -F "files=@document.pdf"

# Response: Advanced system processes file with context analysis
```

## 📡 API Endpoints

### Core Endpoints
- `POST /api/chat` - Unified chat with intelligent routing
- `POST /api/chat/simple` - Force simple system (fast responses)
- `POST /api/chat/advanced` - Force advanced system (academic writing)
- `GET /api/status` - System status and capabilities
- `POST /api/analyze` - Analyze request complexity (development)

### Advanced Features
- `POST /api/write` - Academic writing workflow
- `POST /api/upload` - File upload and processing
- `GET /api/stream/{conversation_id}` - Real-time SSE updates
- `GET /api/conversation/{conversation_id}` - Conversation status

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check endpoint

## ⚙️ Configuration

### Environment Variables

```bash
# System Configuration
SYSTEM_MODE=hybrid                    # simple, advanced, or hybrid
SIMPLE_SYSTEM_ENABLED=true
ADVANCED_SYSTEM_ENABLED=true

# Routing Thresholds
SIMPLE_MAX_COMPLEXITY=4.0           # Queries ≤ 4.0 use simple system
ADVANCED_MIN_COMPLEXITY=7.0         # Queries ≥ 7.0 use advanced system

# AI Provider Keys
GEMINI_API_KEY=your_gemini_key      # Required for simple system
ANTHROPIC_API_KEY=your_claude_key   # Required for advanced system
OPENAI_API_KEY=your_openai_key      # Optional enhancement
PERPLEXITY_API_KEY=your_perplexity_key  # Optional research

# Database & Cache
DATABASE_URL=postgresql://handywriterz:password@localhost/handywriterz
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your_secure_secret_key
ENVIRONMENT=development
```

### Routing Customization

Adjust complexity thresholds in `.env`:
```bash
SIMPLE_MAX_COMPLEXITY=3.0    # More queries use advanced system
ADVANCED_MIN_COMPLEXITY=8.0  # Fewer queries use advanced system
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/ -v
```

### Integration Tests
```bash
python scripts/test_routing.py
```

### Performance Benchmarks
```bash
python scripts/benchmark.py
```

### Manual Testing
```bash
# Test different query types
python examples/simple_query.py
python examples/advanced_query.py  
python examples/hybrid_query.py
```

## 📊 Monitoring

### System Metrics
```bash
# Get comprehensive system status
curl http://localhost:8000/api/status

# Response includes:
# - System availability (simple/advanced)
# - Routing statistics and thresholds
# - Infrastructure health (Redis, DB)
# - Performance metrics
```

### Routing Analysis
```bash
# Analyze how requests would be routed
curl -X POST "http://localhost:8000/api/analyze" \
  -d "message=Your query here"

# Response includes:
# - Complexity score calculation
# - Routing decision and confidence
# - Estimated processing time
# - System recommendation
```

## 🔧 Development

### Project Structure
```
backend/backend/
├── src/
│   ├── agent/
│   │   ├── simple/                   # Simple system integration
│   │   ├── routing/                  # Intelligent routing logic
│   │   ├── handywriterz_graph.py     # Advanced system
│   │   └── nodes/                    # 30+ specialized agents
│   ├── api/                          # (Future: Organized endpoints)
│   ├── db/                           # Database layer
│   ├── services/                     # Business services
│   ├── middleware/                   # Security & error handling
│   └── main.py                       # Application entry point
├── docs/                             # (Future: Documentation)
├── examples/                         # (Future: Usage examples)
├── scripts/                          # (Future: Utility scripts)
├── .env.example                      # Configuration template
├── requirements.txt                  # Dependencies
├── setup.py                          # Automated setup
└── README.md                         # This file
```

### Adding New Features
1. **New AI Provider**: Add to routing logic in `agent/routing/`
2. **New Endpoints**: Add to `main.py` or create in `api/` module
3. **New Agents**: Add to `agent/nodes/` with swarm integration
4. **Routing Logic**: Modify `ComplexityAnalyzer` in `agent/routing/`

 Update Todos
  ⎿  ☒ Examine backend agentic system - routing, nodes, and graph execution
     ☒ Analyze frontend chat UI - composer, streaming, and state management
     ☒ Check API integration between frontend and backend
     ☒ Identify critical blocking issues and root causes

● Analysis Summary: Why the Agentic System and Chat UI Don't Work

  After examining the codebase, I've identified 7 critical blocking issues that prevent the system from functioning:

  🔥 Critical Blocking Issues

  1. Missing Core Dependencies & Services

  # UnifiedProcessor imports missing services that don't exist:
  from src.services.budget import guard_request, record_usage  # ❌ Missing
  from src.services.logging_context import with_correlation_context  # ❌ Missing
  from src.services.sse_service import get_sse_service  # ❌ Missing
  from src.agent.routing.normalization import normalize_user_params  # ❌ Missing

  2. Non-Functional SSE/Streaming System

  - Backend: Complex SSE publisher with Redis dependency but no actual Redis connection
  - Frontend: Calls /api/stream/${traceId} but backend has no matching endpoint
  - Integration: Frontend expects specific SSE event format but backend emits different schema

  3. Broken API Chain

  Frontend → /api/chat → Backend /api/chat → UnifiedProcessor → HandyWriterz Graph
      ✅         ✅           ❌ (500 errors)      ❌ (missing deps)    ❌ (import failures)

  4. Import/Module Resolution Failures

  # Multiple missing imports throughout the agent system:
  from .complexity_analyzer import ComplexityAnalyzer  # ❌ Missing
  from .nodes.user_intent import UserIntentNode  # ❌ Many node files missing core deps

  5. State Management Inconsistencies

  - Frontend: Uses Zustand store with specific schema
  - Backend: HandyWriterzState expects different field names/types
  - Result: Parameter mismatches cause validation failures

  6. File Upload Chain Broken

  // Frontend uploads to /api/upload
  // But backend file processing service missing key components:
  - File content extraction incomplete
  - Vector embedding service not connected
  - File IDs not properly linked to chat requests

  7. Redis/Database Connection Issues

  - SSE publisher requires Redis but connection string env var missing
  - Vector store (pgvector) mentioned but no connection established
  - Database repositories imported but not initialized

  🛠️  Root Cause Analysis

  The system was over-architected with:
  - Too many abstraction layers (SSE service → SSE publisher → Redis → WebSocket)
  - Feature flags everywhere disabling half the functionality
  - Missing "glue code" between sophisticated components
  - Inconsistent error handling causing silent failures

  💡 Quick Fix Priority

  1. Remove complexity - Bypass SSE service, use direct Redis publish
  2. Fix imports - Create missing service stubs or remove dependencies
  3. Simplify routing - Skip complexity analysis, always use advanced system
  4. Connect file processing - Ensure uploaded files reach the graph
  5. Fix streaming - Make backend /api/stream/{id} endpoint functional
  
  ## 1. High-level roles

| Layer                   | Key responsibility                                                                           | Main code paths                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **Next.js Frontend**    | Gather user input, upload files, open an SSE channel, render streaming tokens                | `pages/chat/*`, `hooks/useAdvancedChat.ts`, `hooks/useStream.ts` |
| **Gateway & API Proxy** | Forward all `/api/*` calls to the Python service, keep a single origin for CORS              | `frontend/src/app/api/*/route.ts`                                |
| **FastAPI Entry**       | Validate the request, store files, create `conversation_id`, publish *early* progress events | `backend/src/main.py  →  chat()`                                 |
| **Unified Processor**   | Pick the correct LangGraph pipeline, pass context, push every agent event to SSE             | `backend/src/agent/routing/unified_processor.py`                 |
| **LangGraph Workflow**  | 30+ specialized nodes (planning, search, writer, evaluator…) that collaborate                | `backend/src/agent/nodes/*` and `handywriterz_graph.py`          |
| **SSE Service**         | One Redis channel per conversation, guarantees JSON event shape, heart-beats                 | `backend/src/services/sse_service.py`                            |
| **Redis**               | Fan-out broker so any node can publish without direct socket knowledge                       | external container                                               |

---

## 2. Timeline of a single chat turn

> The numbered bullets are exact events you will see in logs and in the browser console.

1. **User hits “Send”**
   `useAdvancedChat` calls the Next.js server route `POST /api/chat`.
2. **Next.js proxy** forwards to `http://<BACKEND>/api/chat`.
   The body contains:

   ```json
   {
     "message": "Write a 500-word review of my draft",
     "file_ids": ["f_123", "f_456"],
     "user_params": { "writeupType": "essay" }
   }
   ```
3. **FastAPI validates** the payload, inserts a row in `conversations` table, and generates `conversation_id = "c_OVd..."`.
4. **File processor** loads every file ID, extracts text, stores a hash in Postgres, then immediately emits through **SSEService**:

   ```json
   { "type": "progress", "step": "file_processing", "current": 1, "total": 2 }
   ```
5. **Backend responds** `{"conversation_id": "c_OVd..."}` to the proxy.
6. **Frontend now opens** `EventSource('/api/chat/stream/c_OVd...')`.
   The Next.js stream route pipes bytes from Python `/api/stream/c_OVd...`.
7. **SSE stream starts** with:

   ```json
   { "type": "connected", "timestamp": 1723469045000 }
   ```
8. **Unified Processor** analyzes the request.

   * Complexity score → 8.6 → choose **Advanced LangGraph**.
   * Publishes `progress: "planning_started"`.
9. **Planner node** splits the task, sets sub-goals, and emits:

   ```json
   { "type": "progress", "step": "planner_finished", "outline": ["Intro", "Strengths", "Weaknesses", "Conclusion"] }
   ```
10. **Research swarm** fires web or academic search agents in parallel.
    Each agent’s completion publishes two events:

    * `progress: "search_progress"` with percent
    * `content` snippets summarising sources
11. **Writer node** begins generation. For every token it receives from the selected LLM (e.g., GLM-4.5 via OpenRouter) it calls:

    ```python
    await sse.token(cid, delta)
    ```

    The frontend’s `useStream` appends the delta into the visible assistant bubble in real time.
12. When the Writer finishes a paragraph it emits a full-sentence **content** event so slower networks still see chunks appear quickly.
13. **Evaluator and Formatter** run, checking style, citations, and producing cost metadata. They emit `progress` events users can watch in the *StreamingStatus* panel (token cost, latency, model name).
14. **Unified Processor** publishes the final **done** event:

    ```json
    { "type": "done", "total_tokens": 732, "cost": 0.13 }
    ```
15. **SSE endpoint** detects `type === "done"` and closes the Redis subscribe loop; the Next.js proxy forwards the last bytes and closes the EventSource.
16. **useStream** sets `done = true`, triggering UI polish: “Copy / Download” buttons appear, the cost meter freezes, and the cursor returns to the input box.

---

## 3. How the LangGraph agents cooperate

```
(user request) ─┐
                │
           ┌──► Planner
           │     │
           │     ▼
           │  Search Swarm  ─► Aggregator
           │     │               │
           └─────┴────► Writer ──┤
                                 ▼
                            Evaluator
                                 │
                            Formatter
                                 │
                             (output)
```

* **Planner** – determines the work-plan, selects specialized sub-graphs if the topic is code, legal, or scientific.
* **Search Swarm** – five to eight workers: DeepSeek, Gemini Search, Scholar Scraper, Crossref, GitHub Search, etc. They pull evidence, create citations, and push progress events.
* **Aggregator** – merges raw findings into a structured context slice that fits the LLM context window.
* **Writer** – streams prose. Uses temperature, model, and max-token settings derived from the user’s `writeupType`.
* **Evaluator** – fact-checks and style-audits. Can decide to *loop* the Writer for a quick rewrite if quality is below threshold.
* **Formatter** – injects markdown headings, APA citations, and calls the Turnitin sub-graph if the user toggled originality check.

Every node **publishes** to the same Redis channel `sse:c_OVd...` using `SSEService`.
This keeps perfect ordering for the UI and avoids multiple sockets.

---

## 4. File context path

1. Uploaded files land in Cloudflare R2 or Railway volume, keyed by UUID.
2. `FileContentService` extracts text and stores a truncated preview (first 4 kB) in Postgres for fast search.
3. During planning the text is chunked (1 k tokens with overlap) and the top-K most relevant chunks are forwarded to the Writer via the LangGraph `state.context` field.
4. Individual chunks referenced in the final answer are indicated by inline citations like `[F-1]`.
5. The UI shows a **“Sources”** drawer that maps `[F-1]` to the file name and lets the user click to jump to that section.

---

## 5. Failure-proofing

* **Heart-beat** every 25 s – keeps Cloudflare and browsers from timing out idle EventSource connections.
* **Backoff reconnect** – `useStream` opens a new EventSource if the socket closes without a `done` or `error`.
* **Error cascade** – any uncaught exception in a LangGraph node triggers `SSEService.error(...)`, the UI shows a toast, and the conversation is marked failed so subsequent turns can re-try.
* **Health checks** – `/health/live` (always true if the process runs) and `/health/ready` (fails if Redis or DB are down) are used by Railway and by the Docker compose file for local dev.

---

## 6. Deployment flow

1. **Railway** builds `backend/` Dockerfile; Redis is a sidecar.
2. **Railway** builds `frontend/` with `BACKEND_URL` env pointing to the backend service URL.
3. Next.js runs purely static for the marketing pages, yet all `/api/*` calls are runtime functions executed in the Railway container; they proxy to the backend’s public URL.
4. Scaling: You can add a second backend replica; each keeps an independent Redis connection but since Redis is single, any replica can take over a conversation if the first crashes mid-stream.

---

## 7. Sequence you should see in logs (happy path)

```text
[frontend] POST /api/chat                  200  46 ms
[backend ] new conversation c_OVd…         route=advanced
[backend ] planner_finished                cid=c_OVd…
[backend ] writer token (102/700)          cid=c_OVd…
[frontend] SSE token len=5                 cid=c_OVd…
[backend ] evaluator ok quality=0.91       cid=c_OVd…
[backend ] done                            cost=$0.13
[frontend] SSE closed (done)               cid=c_OVd…
```

---

### You now have the full picture

*One* EventSource, *one* Redis channel, *many* cooperative agents.
When you watch the chat UI after these fixes are merged, you will literally see the planner tick, the searches roll in, the writer type word-by-word, and the cost meter climb — exactly the experience a modern multi-agent assistant should deliver.


```markdown
# ✅ HandyWriterz AI – End-to-End Working-Indicators Checklist  
Use this prompt **as-is** in any evaluation agent (or for manual QA) to verify that a HandyWriterz AI deployment is fully functional.  
Respond with **PASS / FAIL** and brief evidence for each checkpoint.  
---

## 1. Conversation Lifecycle

| Checkpoint | Evidence you must capture |
|------------|--------------------------|
| **1.1** Server returns **`conversation_id`** in JSON after `POST /api/chat` | Copy the full JSON payload |
| **1.2** Browser opens **`/api/chat/stream/{conversation_id}`** and receives first **`connected`** event within 2 s | Show the raw first SSE line |
| **1.3** Stream closes only after a final **`done`** event and HTTP connection ends with `200` | Paste the last two SSE lines and final HTTP code |

## 2. Streaming Quality

- **2.1** At least one **`token`** event arrives every 2 s while Writer is running  
- **2.2** Cumulative assistant text in the UI matches the concatenation of all `token.delta` and `content.text` fields  
- **2.3** No duplicate tokens appear (check for repeated substrings of five words)  

Provide screenshot or console excerpt demonstrating token cadence and final text length.

## 3. Progress & Agent Events

Tick each step you see in the SSE stream:

- [ ] `progress` step `file_processing`
- [ ] `progress` step `planning_started`
- [ ] `progress` step `search_progress`
- [ ] `progress` step `writer_started`
- [ ] `progress` step `writer_finished`
- [ ] `progress` step `workflow_finished`

For any **unchecked** item, mark **FAIL** and note missing step.

## 4. File-Context Integration

1. Upload a PDF containing the unique phrase **“lorem-context-42”**.  
2. Ask: *“Quote the unique phrase from my upload.”*  
3. Confirm the assistant response includes that phrase verbatim and cites `[F-1]` (or similar).

Record the assistant’s sentence that contains the phrase.

## 5. Error Handling

- Kill the backend process mid-stream; the UI must surface **“connection lost”** within 5 s.  
- Restart backend; click *Retry*; conversation should resume or a fresh request should succeed.

State **PASS / FAIL** for reconnection notice and retry success.

## 6. Health Endpoints

| Endpoint | Expected JSON keys | TTL |
|----------|-------------------|-----|
| `/health/live`  | `status:"alive"`   | < 100 ms |
| `/health/ready` | `redis:"ok"`, `db:"ok"` | < 150 ms |

Ping each endpoint twice; provide the response bodies and latency.

## 7. Resource & Cost Telemetry

Verify the SSE **`done`** payload includes all keys:

```

{ "type":"done",
"total\_tokens": <int>,
"cost": <float>,
"duration\_ms": <int> }

````

List the values returned.

## 8. Regression Log

For every **FAIL**, append one sentence describing the probable root cause plus a suggested codepath to inspect.

---

### Final format to return

```yaml
conversation_lifecycle: PASS
streaming_quality: FAIL  # token cadence stalled after 60 s
progress_events: PASS
file_context: PASS
error_handling: PASS
health_endpoints: PASS
telemetry: PASS
regressions:
  - area: streaming_quality
    suspected_cause: Writer node not flushing tokens
    hint: backend/src/agent/nodes/writer.py _generate_with_model
````

```
```
Below is a **dissertation-focused user-journey map**—the first of several I’ll prepare.
It follows the path a doctoral candidate takes —from first visit to final artifact—illustrating which micro-services, agents, UI elements, and events fire at each step.

---

## Dissertation Journey 📚

| Phase                          | User touch-point (UI)                                           | Backend actions & agents                                                                | SSE events                                                                 | Key DB / cache writes                    |
| ------------------------------ | --------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------- |
| **0 — Landing & Auth**         | Visit `/chat?mode=dissertation` → CTA “Start your dissertation” | **Gateway** inserts anonymous `visitor_id`. If OAuth: creates `users` row.              | —                                                                          | `sessions`, `users`                      |
| **1 — Upload sources**         | Drag PDF(s)/DOCX → `RevolutionaryFileUploader.tsx`              | `POST /api/upload` → S3/R2; triggers `FileContentService.extract()`                     | `progress:file_processing` per file                                        | `uploaded_files`, `file_chunks`          |
| **2 — Dissertation brief**     | Form collects title, field, word count, methodology             | `POST /api/chat` with `mode=dissertation` + `file_ids` + params                         | `progress:planning_started`                                                | `conversations` (`conversation_id`)      |
| **3 — Planning**               | “Planning…” indicator                                           | `Planner` node builds 6-chapter outline; `Research Agenda` agent expands each objective | `progress:planner_finished` (outline)                                      | `conversation_state.outline`             |
| **4 — Research swarms**        | Activity timeline scrolls                                       | Swarm agents (Web Search, Scholar, Crossref) fetch sources; store metadata              | multiple `progress:search_progress` + `content` snippets                   | `raw_search_results`, `filtered_sources` |
| **5 — Draft writing**          | Tokens stream into chat bubble                                  | `Writer` streams section-by-section text, citing `[F-n]` and external URLs              | `token` (every ≤2 s), `content` (para), `progress:writer_started/finished` | `draft_sections`                         |
| **6 — QA Swarm**               | Status shows “Fact-check & style”                               | Agents run bias, clarity, citation validation                                           | `progress:evaluator_started`, potential `error` events                     | `qa_flags`                               |
| **7 — Formatter**              | Formatting spinner                                              | `Formatter` applies APA, updates heading levels, creates ToC                            | `progress:workflow_finished`                                               | `final_document` blob                    |
| **8 — Stream end**             | UI shows “Download .docx / .pdf” buttons                        | `done` → SSE closed; `/api/export` can be called to get docx                            | `done`, heartbeat stops                                                    | —                                        |
| **9 — Originality (optional)** | Click “Turnitin check”                                          | Sub-graph `turnitin.orchestrator` uploads doc, polls similarity score                   | `progress:turnitin_submitted`, `content` with percent                      | `originality_reports`                    |

### UX signals

* **StreamingStatus.tsx** bars track planner, search, writer, QA, formatter.
* Cost meter updates on every `progress:cost_update`.
* Error boundary surfaces any `error` event with retry CTA.

### Key success metrics

| Metric                | Where recorded        |
| --------------------- | --------------------- |
| Total tokens, latency | `done` payload        |
| Sources used (%)      | evaluator logs        |
| Similarity score      | `originality_reports` |
| Outline adherence     | QA flag resolution    |

---

### How to test the flow quickly

1. Upload two dummy PDFs (≤ 10 pages).
2. Fill brief: *“Impact of renewable micro-grids in rural Kenya – 15,000 words, Harvard style.”*
3. Observe outline in ≤ 25 s.
4. Confirm first tokens within ≤ 5 s after outline.
5. Verify citations `[F-1]`, `[1]`, etc. link to uploaded files / search results.
6. After **done**, click “Download PDF” – check ToC, Harvard refs.
7. (Optional) Run Turnitin; expect ≤ 15 % similarity for demo content.

---

### Next journeys

| Use-case                   | Unique twists                                       |
| -------------------------- | --------------------------------------------------- |
| **Research-paper**         | shorter word-count, IEEE citation, Turnitin via workbench |
| **Essay**                  | Simple Gemini path for low complexity               |
| **Thesis chapter rewrite** | Uses **Rewrite Swarm** sub-graph only               |
| **Presentation slides**    | `SlideGenerator` node replaces Writer               |
| **Grant proposal**         | Adds **Budget Tool** and **Cost Model Agent**       |
| **Code assist**            | Drops research swarm, adds **Unit-Test Agent**      |

*(I’ll map each of these in follow-up responses as requested.)*
Below are **six additional, fully-detailed user-journey maps**—each one tailored to a distinct HandyWriterz AI use-case.
The format mirrors the dissertation journey you already have, so QA teams can compare step-for-step.

---

## 2. Research-Paper Journey 🔬

| Phase                                              | UI element                             | Backend / agents                                                               | SSE events                                                  | Key writes                    |
| -------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------- | ----------------------------- |
| **0** Landing → “Write research paper” modal       | —                                      | —                                                                              | —                                                           | —                             |
| **1** Upload PDFs + CSVs                           | `RevolutionaryFileUploader`            | `FileContentService.extract()` incl. numeric tables → `vector_storage`         | `progress:file_processing`                                  | `file_chunks`, `vector_store` |
| **2** Brief form (field, target journal, 6k words) | `POST /api/chat` `mode=research_paper` | *Router* raises complexity → Advanced LangGraph                                | `planning_started`                                          | `conversations`               |
| **3** Outline & section metadata                   | `OutlineViewer.tsx`                    | `Planner` builds IMRaD outline; `MethodologyWriter` expands “Methods” template | `planner_finished` (outline JSON)                           | `outline`                     |
| **4** Data-aware R-Swarm                           | Progress bar                           | `search_pmc`, `search_crossref`, `chartify` node extracts figures              | `search_progress`, `content` (figure captions)              | `figures`, `charts`           |
| **5** Writer + Figure-Injector                     | Streaming tokens; figure placeholders  | Writer streams prose; `SlideGenerator` injects `![Fig-1]`                      | `token`, `content`                                          | `draft_sections`              |
| **6** Citation Master & QA                         | “Citing sources…”                      | `citation_master`, `fact_checking`                                             | `progress:evaluator_started`                                | `qa_flags`                    |
| **7** Journal Style Formatter                      | “Formatting for <journal>”             | `formatter_advanced` chooses IEEE / APA / Nature                               | `workflow_finished`                                         | `final_document`              |
| **8** Download & Turnitin                          | Buttons appear                         | If similarity check on: `turnitin_advanced` agent                              | `done`, `progress:turnitin_submitted`, `content` similarity | `originality_reports`         |

Below are **copy-ready, tightly-scoped prompts**—one per use-case—designed to kick off each multi-agent workflow without extra chatter.
Paste any prompt into the chat box; the router will auto-select the right LangGraph.

---

## 📚 Dissertation (start-to-finish draft)

```markdown
# Dissertation Request
Title: “Understanding and Mitigating Complacency in Workplace Safety Practices”
Field: Occupational Psychology
Word-count target: 15 000
Chapters: 6 (Intro, Literature Review, Methodology, Results, Discussion, Conclusion)
Files attached: Systematic-Review.pdf, Eviture-Case-Data.xlsx
Format: Harvard, UK English
Extra: Run originality check
```

---

## 🔬 Research Paper (IMRaD, journal-ready)

```markdown
# Research Paper
Target journal: Nature Energy
Topic: “Micro-grids and Rural Electrification in Sub-Saharan Africa”
Length: 6 000 words
Figures: auto-generate graphs from Microgrid-Survey.csv
Citation style: Nature
Turnitin: Off
```

---

## ✍️ Quick Essay (simple path)

```markdown
Write a 1 000-word argumentative essay on whether compulsory national service should be introduced in Kenya.  
Use clear structure (intro, three points for, rebuttal, conclusion) and persuasive tone.
```

---

## ♻️ Chapter Rewrite (clarity polish)

```markdown
# Rewrite Chapter for Clarity
File: Draft_Chapter3.docx
Goal: Improve readability (Flesch ≥ 60), keep citations intact.
Leave tracked-changes ON.
```

---

## 🎞️ Slide Deck (10 slides)

```markdown
# Slide Deck Request
Topic: “AI Regulation Trends 2023-2025”
Audience: Non-technical executives
Slides: 10
Design: Dark theme, include 1 infographic
Export: PPTX + PDF
```

---

## 💰 Grant Proposal (with budget)

```markdown
# Grant Proposal
Programme: EU Horizon Europe  
Project: “Low-Cost Desalination Using Solar Concentrators”  
Sections needed: Abstract (250 words), Objectives, Methodology, Impact, Budget  
Budget: €1.2 M over 3 years, break down by WP/Staff/Equipment/Dissemination  
Risk matrix: include mitigation plans  
Deliver as styled PDF
```

---

## 🖥️ Code Assist (LLM + tests)

```markdown
# Code Assist
Task: “Implement a Python function `merge_k_sorted_lists(lists)` returning one sorted list.”
Constraints:
  – Use O(N log k) time  
  – Include unit tests covering edge cases  
After implementation, run tests and stream results.  
Language: Python 3.11
```

---

### How to use these prompts

1. **Drag any required files** into the chat **before** sending.
2. Paste the prompt exactly.
3. Watch the **progress bars** and streaming tokens; the system will emit `done` when finished.

These prompts are intentionally concise yet packed with the metadata each sub-graph needs—ensuring the router never misclassifies the task.

## End-to-end Data Flow – Chat UI ➜ Task Completion

Below is a **multi-layer view** that tracks every byte from the moment a user hits **Send** in the browser to the final **done** SSE event. It combines a Mermaid diagram with step-by-step tables so you can trace payloads, headers, and storage side effects.

---

### 1. High-level Flow Diagram

```mermaid
flowchart TD
    subgraph Browser
        A[Chat UI React] --POST /api/chat--> B[Next.js API route]
        B --axios JSON--> C[FastAPI /api/chat]
        A -. EventSource .-> D[/api/chat/stream/{cid}/]
    end

    subgraph FastAPI
        C --> E[FileContentService]
        C --> F[UnifiedProcessor]
        D -- Redis SUB --> H[(Redis Channel sse:{cid})]
    end

    subgraph LangGraph
        F --> G[Planner Node]
        G --> I[Research Swarm]
        I --> K[Writer Node]
        K --> L[Evaluator]
        L --> M[Formatter]
        K --per-token--> H
        G & I & L & M --progress--> H
    end

    E --progress--> H
    M --> N[Export Service]
```

---

### 2. Detailed Sequence

| #  | Component                   | Action                                                              | Payload (shape)                                   | Outgoing link                                |
| -- | --------------------------- | ------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------- |
| 1  | Chat UI (`useAdvancedChat`) | Collect prompt, file IDs                                            | `{ message, file_ids, user_params }` JSON         | POST `/api/chat`                             |
| 2  | Next.js API (server route)  | Forward to backend URL                                              | Same body, `Content-Type: application/json`       | HTTP 1.1                                     |
| 3  | FastAPI `/api/chat`         | - Create `conversation_id`<br>- Store conversation row              | Returns `201 {"conversation_id": "c_XYZ"}`        | HTTP 1.1 response                            |
| 4  | Chat UI                     | Extract `conversation_id`                                           | n/a                                               | Open `EventSource('/api/chat/stream/c_XYZ')` |
| 5  | Next.js stream proxy        | `fetch(BACKEND_URL + /api/stream/c_XYZ)` and pipe                   | `text/event-stream`                               | Stream to browser                            |
| 6  | FastAPI `/api/stream/{cid}` | Redis `SUBSCRIBE sse:c_XYZ`                                         | `data: {"type":"connected"}`                      | First SSE line                               |
| 7  | FileContentService          | For each file ID:<br>- download<br>- extract text<br>- store chunks | `progress file_processing` SSE                    | Redis `PUBLISH`                              |
| 8  | UnifiedProcessor            | Decide route - complexity score                                     | `progress planning_started` SSE                   | Redis                                        |
| 9  | Planner Node                | Create outline                                                      | `progress planner_finished {outline}`             | Redis                                        |
| 10 | Research Swarm              | Parallel search agents                                              | For each agent:<br>`progress search_progress pct` | Redis                                        |
| 11 | Writer Node                 | Call model, receive stream                                          | For each token:<br>`token delta:"..."`            | Redis                                        |
| 12 | Evaluator                   | QA steps                                                            | `progress evaluator_started` etc.                 | Redis                                        |
| 13 | Formatter                   | Apply style, images                                                 | `progress workflow_finished`                      | Redis                                        |
| 14 | UnifiedProcessor            | Wrap up                                                             | `done {total_tokens,cost}`                        | Redis + close stream                         |
| 15 | Browser `useStream`         | Append deltas to UI, stop on `done`                                 | Update React state                                | Render final text                            |
| 16 | Export Service (optional)   | `/api/export?cid=c_XYZ&type=pdf`                                    | binary                                            | Download link                                |

---

### 3. Data Stores Touched

| Store               | Table / key                             | Write stage |
| ------------------- | --------------------------------------- | ----------- |
| Postgres            | `conversations`                         | Step 3      |
| Postgres + pgvector | `file_chunks`                           | Step 7      |
| Redis               | `sse:c_XYZ` channel                     | Steps 6-14  |
| S3 / R2             | Uploaded files                          | Step 7      |
| Postgres            | `draft_sections`, `outline`, `qa_flags` | Nodes 10-14 |

---

### 4. Message Schemas

```jsonc
// token event
{ "type": "token", "delta": "word " }

// content event
{ "type": "content", "text": "Full paragraph." }

// progress event
{ "type": "progress", "step": "writer_started", "timestamp": 17234691 }

// done event
{ "type": "done", "total_tokens": 702, "cost": 0.128, "duration_ms": 41235 }
```

---

### 5. Timing Targets (healthy deployment)

| Milestone               | SLA      |
| ----------------------- | -------- |
| First `connected` event | < 300 ms |
| `planning_started`      | < 2 s    |
| First `token`           | < 5 s    |
| Heart-beat gap          | 25 ± 2 s |
| Whole turn (15k tokens) | < 240 s  |

---

### 6. Failure Paths

| Fault                | Detection                   | Auto-recovery                                      |
| -------------------- | --------------------------- | -------------------------------------------------- |
| Redis down           | `/health/ready` fails       | Kubernetes / Railway restarts pod                  |
| Writer model timeout | Evaluator emits `error` SSE | UI shows toast “generation failed”, user can retry |
| Broken SSE socket    | `useStream` onerror fires   | Exponential backoff reconnect (3 tries)            |

---

### 7. How to Trace in Logs

```bash
# Backend
grep c_XYZ backend.log | cut -c1-120
# Frontend
chrome://net-export   // filter sse:c_XYZ
# Redis
redis-cli monitor | grep sse:c_XYZ
```

---

Use this map when onboarding new devs, writing integration tests, or debugging production.



