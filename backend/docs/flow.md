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


