# HandyWriterz AI — Agentic Architecture Deep Dive

Note: This document is a comprehensive, line-anchored audit and design narrative for the backend/src agentic system. It is intentionally long-form and exhaustive to serve as the single source of truth for engineering, SRE, QA, and product. It embeds precise observations from code, identifies inconsistencies, and proposes future-proof patterns. It focuses on not harming or altering runtime behavior now; changes are queued in the companion todo100.md.

---

## 1) Executive Summary

---
## Feature Flags — Runtime Controls and Visibility

To enable safe, incremental rollout of critical behavior without breaking clients, the backend exposes feature flags via settings and /api/status.

Flags
- feature.sse_publisher_unified
  - Unifies all SSE emissions to a canonical JSON envelope published by [`python.SSEPublisher.publish()`](backend/src/agent/sse.py:1) and used in [`python.UnifiedProcessor._publish_event()`](backend/src/agent/routing/unified_processor.py:294).
  - Default off in prod; enable in stage first.
- feature.double_publish_sse
  - When enabled, publish legacy JSON frames and unified envelopes in parallel (shadow) to de-risk migration.
- feature.params_normalization
  - Apply canonicalization in routing and write flows via [`python.normalize_user_params()`](backend/src/agent/routing/normalization.py:1); on error, fall back to raw input.
- feature.registry_enforced
  - On startup, validate model_config.yaml vs price_table.json; when strict, fail fast on mismatches.
- feature.search_adapter
  - Normalize search agent outputs through [`python.adapter.to_search_results()`](backend/src/agent/search/adapter.py:1) before Aggregator consumption.

Toggling and Visibility
- Flags can be set via environment or HandyWriterzSettings in [`python.get_settings`](backend/src/config/__init__.py:1).
- /api/status exposes a features.flags subsection for operational visibility in [`python.@app.get("/api/status")`](backend/src/main.py:1).

Rollout Guidance
1) Stage: feature.params_normalization = on; feature.double_publish_sse = on.
2) Validate analyzer parity and client SSE consumption.
3) Enable feature.sse_publisher_unified in prod.
4) Enable feature.registry_enforced after CI audit.
5) Keep feature.search_adapter enabled with Aggregator contract tests.

- HandyWriterz AI implements a multi-agent, multi-provider orchestration for academic writing, with simple, advanced, and hybrid routing paths, a LangGraph-based advanced pipeline, and numerous specialized nodes for search, aggregation, verification, synthesis, writing, evaluation, formatting, memory, and failure handling.
- The architecture is modular but currently exhibits several integration inconsistencies:
  - Schema fragmentation (snake_case vs camelCase; multiple “UserParams” definitions).
  - SSE streaming format divergence (JSON vs stringified dict).
  - Import-path inconsistencies (relative vs absolute, and incorrect relative depth).
  - Data contract misalignments across nodes (raw_search_results vs aggregated_sources vs filtered_sources vs sources).
  - Search result normalization gaps (heterogeneous agent outputs incompatible with Aggregator).
  - Model service/config mismatch (IDs in YAML vs price table vs code-level expectations).
- Despite these issues, the system has a strong foundation to support a robust productionization effort:
  - A clear pipeline for advanced orchestration (HandyWriterzOrchestrator).
  - Rich search agents (Gemini, Perplexity, O3, Claude, OpenAI) and EvidenceGuard components.
  - Extensible BaseNode and BaseSearchNode contracts and utilities.
- This document details the architecture, data flows, nodes, contracts, failure domains, and a roadmap to standardize and harden the platform.

---

## 2) Top-Level Routing and Orchestration

### 2.1 UnifiedProcessor

- UnifiedProcessor routes between simple, advanced, and hybrid systems and provides SSE streaming.
- Key responsibilities:
  - Accepts message, optional files, user_params, user_id, conversation_id.
  - Analyzes request via SystemRouter to determine system path.
  - Publishes events to Redis channel sse:{conversation_id} as JSON via redis.asyncio.
  - Invokes:
    - Simple path: Gemini simple graph pipeline.
    - Advanced path: HandyWriterz LangGraph pipeline.
    - Hybrid path: both in parallel and merges results.
- Observations:
  - The event publishing in UnifiedProcessor uses json.dumps, producing proper JSON for consumers.
  - In contrast, BaseNode’s broadcast uses str(dict), producing non-JSON strings. This divergence can break a unified frontend SSE parser.
  - User params inference method returns camelCase-like keys (writeupType, referenceStyle, educationLevel), which conflicts with other components expecting snake_case or a different schema entirely.

### 2.2 SystemRouter and ComplexityAnalyzer

- SystemRouter defers complexity scoring to ComplexityAnalyzer and chooses simple/advanced/hybrid.
- ComplexityAnalyzer:
  - Calculates a 1-10 score using message length, files, academic/complex keywords, quality keywords, and user_params.
  - Expects user_params with camelCase keys (writeupType, pages, educationLevel, referenceStyle, qualityTier).
- Observations:
  - This analyzer couples to camelCase UserParams. Elsewhere, snake_case appears (e.g., Base.UserParams), and the HandyWriterzState.UserParams dataclass uses a domain-specific schema. A normalization layer is required later.

---

## 3) Advanced Orchestration via LangGraph

### 3.1 Orchestrator: HandyWriterzOrchestrator

- Defines nodes:
  - Memory: retriever, writer
  - Intent: master_orchestrator, enhanced_user_intent, user_intent
  - Planning: planner
  - EvidenceGuard: crossref, pmc, ss (semantic scholar), source_verifier, source_filter, citation_audit, source_fallback_controller
  - Search agents: gemini, perplexity, o3, claude, openai, github, plus scholar_search and legislation_scraper
  - Aggregation: aggregator, rag_summarizer, prisma_filter, casp_appraisal
  - Synthesis: synthesis, methodology_writer
  - Writing and QA: writer, evaluator, formatter_advanced
  - Integrity: turnitin_advanced
  - Robustness: fail_handler_advanced
  - Intelligence: swarm_coordinator, emergent_intelligence
- Dynamic Search Nodes initialization:
  - Reads a “search” config to determine enabled agents, then adds nodes like “search_{agent_name}” using dynamically created methods that call agent_instance.execute.
- Notable wiring:
  - Builder edges establish default pipeline flow from memory -> planner -> orchestrator decision -> intent -> parallel search -> aggregator -> rag_summarizer -> source_verifier -> source_filter or fallback -> writer -> evaluator -> turnitin -> formatter -> memory writer -> END.
  - Dissertation and other pipelines add specialized sequences involving scholar search, legislation scraping, PRISMA, CASP, synthesis, methodology, and formatting.

### 3.2 Orchestrator Inconsistencies

- Orchestrator also implements static methods like _execute_search_gemini, _execute_search_perplexity, etc., referencing attributes such as self.gemini_search_node that are never assigned. These are likely dead code in the current dynamic wiring approach. They should be removed or rewritten to reference the dynamic pattern only, to avoid confusion.

---

## 4) State Management and Schemas

### 4.1 HandyWriterzState Dataclass

- Comprehensive state object with identifiers, messages, user_params (Dict), uploaded_docs/files, planning and research fields, results (search, filtered, verified), content (draft, current_draft), QA (evaluation_results, scores), Turnitin, final outputs, workflow metadata, retries, advanced features, performance metrics, auth/payment, credits_used.
- WorkflowStatus is an Enum with statuses from initiated to completed/failed/cancelled.
- Has helper methods to update status, add messages/results/sources/evaluations, set errors, retry logic, completion checks, percentage progress estimation, and serialization.

### 4.2 Multiple UserParams Definitions

- Three distinct definitions exist:
  1) backend/src/agent/base.py: Pydantic BaseModel with word_count, field, writeup_type, source_age_years, region, language, citation_style; includes convenience properties for target_sources/pages.
  2) backend/src/agent/handywriterz_state.py: Dataclass with a different domain perspective: word_count, document_type (Enum), citation_style (Enum), academic_field (Enum), region (Enum), academic_level, etc.
  3) UnifiedProcessor._infer_user_params returns camelCase fields writeupType, referenceStyle, educationLevel plus language, tone, pages estimation.
- ComplexityAnalyzer expects camelCase structure.
- Consequences:
  - Nodes reading user_params see heterogeneity. For example, BaseSearchNode._build_search_query reads field and writeupType (camelCase).
  - Downstream logic will be fragile without a unification method. We need a central normalization strategy applied right after input or at the router boundary.

---

## 5) SSE Streaming Protocol

- UnifiedProcessor publishes JSON via Redis asyncio client on channel sse:{conversation_id}.
- BaseNode.broadcast_sse_event publishes str(dict) (stringified Python dict) via redis-py sync client.
- Nodes use BaseNode._broadcast_progress/_start/_complete/_error.
- Consequences:
  - Mixed serialization results in two incompatible SSE message forms to the same channel, increasing frontend parsing complexity and potential runtime errors.
  - Solution should standardize to JSON across all emitters, using a single client abstraction and consistent message envelope.

---

## 6) Search Layer: Agents and Contracts

### 6.1 BaseSearchNode and SearchResult

- BaseSearchNode provides:
  - Robust execute with retries, rate limit, progress updates.
  - Query building from state (messages, user_params, uploaded_files via get_file_summary).
  - Provider-specific optimization hook.
  - Provider search hook to return raw list of results.
  - Conversion to standardized SearchResult with titles, authors, abstract, url, publication_date, doi, citation_count, source_type, and computed relevance/credibility.
  - Appends standardized results into state["raw_search_results"].
- Benefits:
  - Uniform downstream expectations for Aggregator and verification layers, if all agents adopt BaseSearchNode.

### 6.2 Current Agents

- GeminiSearchAgent:
  - Uses a dynamic model service and secure prompts to produce a structured “search_result” with analysis, synthesis, credibility assessment, recommendations, and gaps.
  - Updates state with gemini_search_result, research_insights, source_recommendations.
  - Does not inherit BaseSearchNode; it returns a specialized payload.
- PerplexitySearchAgent:
  - Production-style implementation; real-time search with citations, creates PerplexitySearchResult dataclass, and updates state with perplexity_search_result, real_time_sources, credibility_analysis.
  - Key issues:
    - credibility_scores vs source_scores naming mismatch across computations and filters.
    - Uses self._broadcast_progress with error=True parameter not supported by BaseNode.
  - Does not inherit BaseSearchNode; returns specialized payload.
- O3SearchAgent:
  - Deep reasoning-based analysis; updates state with o3_search_result, logical_frameworks, research_hypotheses, academic_reasoning.
  - Same _broadcast_progress error=True misuse.
  - Does not inherit BaseSearchNode; returns specialized payload.
- ClaudeSearchAgent:
  - Uses model_service (but the imported service module doesn’t expose get_model_client() in our inspected file; implies existence of a different implementation).
  - Returns minimal raw_search_results with content and metadata; handles empty queries.
- OpenAISearchAgent:
  - Minimal wrapper over ChatOpenAI, returns raw_search_results with content only.
  - Hard-fails on missing OPENAI_API_KEY; misaligned with graceful-start ethos.
  - Path import issue for HandyWriterzState.
- EvidenceGuard: CrossRef, PMC, SS exist but not fully reviewed in this session; these likely return SearchResult-style data but should be validated.

### 6.3 Aggregation and Verification

- AggregatorNode:
  - Expects standardized SearchResult dicts and deduplicates using DOI > URL > title+authors heuristic.
  - Produces aggregated_sources.
  - Current agent outputs do not conform; aggregator must either normalize or agents should standardize via BaseSearchNode.
- SourceVerifier:
  - Verifies aggregated_sources for credibility, relevance, and liveness.
  - Produces verified_sources and sets need_fallback if below threshold.
- SourceFilterNode:
  - Implements advanced evidence extraction, scoring, ranking, and hover-card evidence map generation, with optional Redis persistence.
  - Currently reads raw_search_results (bypassing aggregation) and contains error-handling bugs described earlier.

---

## 7) RAG, Synthesis, Writing, Evaluation, Turnitin, and Formatting

- RAGSummarizerNode:
  - Heavy synchronous deps on init; expects aggregated_data key rather than aggregated_sources; returns summaries and experiment suggestions.
- SynthesisNode / MethodologyWriterNode / Writer / Evaluator / Formatter / Turnitin:
  - Not all reviewed in the latest batch; orchestrator wiring suggests a typical sequence:
    - After filtering and (potentially) swarm intelligence, content goes to writer.
    - Output evaluated; evaluation routes to Turnitin or fail handler.
    - Turnitin routes to formatter (if passed) or writer/fail handler (if not).
    - Finalized document goes to memory writer and ends.
  - CitationAudit can route writer back for revision if missing citations, but current orchestration path into citation_audit in default flow is not clearly triggered; ensure the branch is reachable under the designed conditions.

---

## 8) Services and Configuration

### 8.1 Model Service

- backend/src/services/model_service.py:
  - ModelService supports “get(node_name, tenant)” returning an LLMClient wrapper with pricing info from price_table.json and defaults from model_config.yaml.
  - This service does not expose get_model_client(), get_agent_config(), or record_usage methods used by Claude/Gemini search agents elsewhere. There must be another service implementation in the repository or a missing file. Alternatively, the code was refactored midstream and not fully aligned.
- model_config.yaml vs price_table.json:
  - The defaults reference identifiers like “o3-reasoner”, “sonar-deep”, “kimi-k2”, “claude-opus”.
  - The price table uses vendor-prefixed IDs like “openai/o3”, “perplexity/sonar-deep-research”, “moonshotai/kimi-k2”, and “anthropic/claude-opus-4”.
  - Without a mapping layer, pricing lookups will fail. A registry should translate logical model names to concrete provider IDs and back.

---

## 9) Import Path and Packaging

- Many nodes incorrectly import handywriterz_state using too-deep relative paths (“...agent.handywriterz_state”) and mix absolute “src.agent.base” style imports with relative ones.
- For Python packaging resilience:
  - Use consistent relative imports within the package.
  - Avoid absolute “src.” unless project installs a package named src or modifies sys.path accordingly.

---

## 10) Data Contracts and Keys

- Key consumers and expected fields:
  - Aggregator consumes standardized SearchResult lists.
  - SourceVerifier consumes aggregated_sources (list of SearchResult dicts).
  - SourceFilter is designed to process results enriched with content/snippets/abstracts and produce filtered_sources, evidence_map, and metadata.
  - CitationAudit expects draft and sources IDs (but current state uses verified_sources or filtered_sources).
- Uniform contracts are essential for correct orchestration. Propose a contract table later in the roadmap.

---

## 11) Error Handling, Timeouts, and Retries

- BaseNode provides:
  - Timeout wrapper via decorator.
  - Retry wrapper with exponential backoff.
  - Metrics capture and SSE event hooks.
  - Raises NodeError with recoverability hints.
- Observed issues:
  - Several nodes pass unsupported kwargs into _broadcast_progress, likely causing exceptions during exception handling.
  - Finally blocks with undefined locals can mask original exceptions; ensure guarded assignments.

---

## 12) Security and Privacy

- Secure prompt loader used by Gemini agent: indicates an effort to sanitize user inputs and sanitize user_params.
- Evidence data persistence in Redis:
  - user_id qualifies keys; ensure TTLs, encryption-at-rest, and PII compliance.
  - A strategy for purging evidence and metadata should be formalized.

---

## 13) Performance and Resource Use

- Heavy models instantiated at import time in RAGSummarizer (SentenceTransformer, Chroma).
- Potential synchronous bottlenecks in processing large raw_search_results without batching or streaming.
- Redis pub/sub across two different clients (sync and asyncio) creates duplicate resource paths.

---

## 14) Testing and CI/CD

- The codebase references Playwright E2E scaffolding earlier in context; unit, integration, and E2E tests around router, policy, SSE, and graph flows are necessary.
- Mocks/stubs for external providers and Redis are needed for deterministic tests.

---

## 15) Roadmap Preview (see todo100.md for full plan)

- Schema normalization across UserParams, state fields, and analyzer expectations.
- SSE JSON standardization and single publisher abstraction.
- Search normalization: enforce BaseSearchNode outputs or add Aggregator normalization layer to consume heterogeneous shapes from existing agents.
- Model registry: map logical model names to provider IDs and pricing; align model_service APIs across agents.
- Import path standardization.
- Data contract matrix: define keys used by each node in and out; add adapters.
- Error-path hardening, guarded finally blocks, and consistent logging/metrics.

---

## 16) Detailed Node-by-Node Notes

The following sections document the key nodes in more detail, their inputs/outputs, and alignment issues. This is designed as a living appendix for developers making changes.

### 16.1 Unified Processor

- Input: message, files, optional user_params, user_id, conversation_id.
- Output: result payload with response, sources, workflow_status, quality_score/metrics, system_type.
- SSE: publishes JSON via redis.asyncio.
- Risks:
  - _infer_user_params returns camelCase; advanced path puts validated_params.dict() into HandyWriterzState.user_params, potentially mixing styles with nodes expecting snake_case or domain enums.

### 16.2 Memory Retriever/Writer

- Memory retriever executes early; not fully inspected here but expected to populate user/persona data or historical context.
- Memory writer stores final artifacts; ensures workflow completion status also set.

### 16.3 Planner

- Determines pipeline (dissertation/reflection/case study/technical/comparative/default).
- The mapping in orchestrator routes to various initial nodes based on task_type in state.

### 16.4 Master Orchestrator and Enhanced User Intent

- Master orchestrator uses workflow intelligence to decide between enhanced/legacy intent paths.
- Enhanced User Intent may request clarification or proceed to parallel searches.
- If unclear “general” mode, it may end the flow by returning clarification questions rather than proceeding – an intentional low-harm mode.

### 16.5 Parallel Search Fan-out

- Sends to EvidenceGuard (crossref/pmc/ss) and enabled AI agents (gemini, perplexity, o3, claude, openai, github) plus scholar_search.
- Expectation: All search nodes should append standardized SearchResult dicts to raw_search_results. Current non-BaseSearchNode agents do not, which breaks downstream.

### 16.6 Aggregator

- Deduplicates based on DOI/URL/title+authors. Produces aggregated_sources.
- Must be able to ingest SearchResult dicts; not agent-specific nested payloads.

### 16.7 RAG Summarizer

- Expects aggregated_data but should consume aggregated_sources. Returns summaries and experiment suggestions; does not feed into later nodes per the current contracts. Candidate for rework as an intermediate summarization auxiliary.

### 16.8 Source Verifier

- Verifies aggregated_sources and sets need_fallback. Sets verified_sources.
- Consumes SearchResult fields, so upstream normalization is mandatory.

### 16.9 Source Fallback Controller

- Mutates state.params (not user_params) to relax constraints; increments fallback attempts; sets error after exhaustion.
- Should coordinate with SourceVerifier’s determination of fallback.

### 16.10 Source Filter

- Deep evidence pipeline producing filtered_sources, evidence_map, and quality metadata; publishes to Redis if configured.
- Currently reads raw_search_results and not outputs of verifier/aggregator; integrate contract alignment later.

### 16.11 Swarm Coordinator and Emergent Intelligence

- Provide optional swarm reasoning and emergent intelligence paths for complex problems before writing.

### 16.12 Writer

- Produces draft/current_draft or formatted_document later. Should ensure drafts carry in-text citations consistent with selected sources to make CitationAudit effective.

### 16.13 Evaluator

- Determines if ready for Turnitin vs fail handler; sets is_complete or similar flags for routing.

### 16.14 Turnitin Advanced

- Executes similarity and AI detection checks, sets turnitin_passed/similarity_passed/ai_detection_passed, and revision routing.

### 16.15 Formatter Advanced

- Produces final formatted_document and triggers memory write.

### 16.16 Fail Handler

- Recovery strategies: route to writer/search/swarm or END; escalate on critical failure.

---

## 17) Data Contract Reference (Draft)

This section summarizes the expected keys between major pipeline stages. It highlights current vs desired.

- Search nodes:
  - Current: heterogeneous outputs including nested “result” objects and separate state keys (gemini_search_result, o3_search_result, perplexity_search_result).
  - Desired: in addition to specialized artifacts, each agent must append standardized SearchResult[] to state["raw_search_results"] for aggregator processing.
- Aggregator:
  - Input: raw_search_results as SearchResult[].
  - Output: aggregated_sources: SearchResult[].
- RAG Summarizer:
  - Should consume aggregated_sources and emit summarized insights to a well-named key (e.g., rag_summaries), not aggregated_data.
- Source Verifier:
  - Input: aggregated_sources.
  - Output: verified_sources: SearchResult[]; need_fallback: bool.
- Source Filter:
  - Input: verified_sources (preferred) or aggregated_sources; output: filtered_sources, evidence_map, filtering_metadata.
- Writer -> Evaluator -> Turnitin -> Formatter:
  - Inputs and outputs should reference “filtered_sources” for citation compliance; ensure CitationAudit integrates with whichever “sources” list is canonical at writing time.

---

## 18) Provider and Policy Layer

- A PolicyRegistry-like abstraction decides suitable providers/models per task, with budget and health considerations.
- ModelService (observed) manages model mappings and pricing; however, the API referenced by agents differs from the observed implementation. A unification effort should define:
  - A provider registry mapping logical model keys to (provider, concrete model ID, pricing entry).
  - Health checks and weights (latency, success rate).
  - Budget/cost bias and circuit breaker logic.
- This policy layer should integrate with router/hybrid modes to provide optimal performance vs cost vs quality.

---

## 19) Security and Compliance Considerations

- Ensure no PII is stored without consent. Evidence Redis writes should include a TTL and anonymization for any user-provided content (e.g., document extracts).
- Turnitin and AI detection flows must maintain user confidentiality; any tokens/credentials in .env should be scoped and rotated.

---

## 20) Conclusion

HandyWriterz has a powerful multi-agent backbone and clear orchestrations but requires:
- Schema and contract standardization,
- SSE message standardization,
- Search normalization,
- Model service alignment,
- Error path hardening,
- Import consistency.

These will unlock reliable, high-quality academic writing assistance at production scale. The companion todo100.md spells out the stepwise plan.
