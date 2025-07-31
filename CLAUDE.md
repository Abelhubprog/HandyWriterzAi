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

