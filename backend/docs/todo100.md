# HandyWriterz AI — 100-Item Transformation Roadmap (todo100.md)

Note: This roadmap lists concrete, verifiable tasks to evolve HandyWriterz AI into a robust, world-class, multi-agent academic writing platform. Items are grouped by theme, each with crisp outcomes. Sequencing is designed to minimize risk: audit → contracts → adapters → standardization → resilience → optimization → polish.

---

## A) Contracts, Schemas, and Normalization

1) Establish a single canonical UserParams schema
- Outcome: One normalized Pydantic model with snake_case keys and a translation map from camelCase to snake_case and to the handywriterz_state dataclass enum forms.

2) Implement a normalization utility
- Outcome: normalize_user_params(input_dict) that returns canonical schema, preserving original for provenance.

3) Inject normalization into UnifiedProcessor
- Outcome: Before constructing HandyWriterzState, apply normalization to user_params; ComplexityAnalyzer should accept both but prefer canonical.

4) Update ComplexityAnalyzer to read canonical schema
- Outcome: Analyzer gracefully handles legacy camelCase keys; unit tests for various mixes.

5) Define a cross-node Data Contract Matrix
- Outcome: Design doc and code annotations specifying inputs/outputs for each node with exact keys and types.

6) Standardize raw_search_results schema
- Outcome: All agents append standardized SearchResult dicts. Specialized artifacts are written to additional keys but not used for aggregation.

7) Add a SearchResult adapter layer in Aggregator
- Outcome: Aggregator can ingest heterogeneous agent outputs in the interim, converting to SearchResult dicts before deduplication.

8) Align RAG Summarizer input
- Outcome: Read from aggregated_sources, not aggregated_data.

9) Standardize source keys for downstream nodes
- Outcome: Use verified_sources as canonical for post-verification path; if SourceFilter supersedes, define filtered_sources as canonical and ensure Writer consumes that.

10) Define canonical “sources” at writing time
- Outcome: Writer receives sources_canonical list to ensure CitationAudit alignment.

11) Harmonize “published_date” vs “publication_date”
- Outcome: Normalize to publication_date across the platform; adapters convert legacy keys.

12) Add state.params vs user_params unification
- Outcome: Deprecate ad-hoc state["params"]; use user_params or a structured “search_params” namespace.

13) Provide a schema evolution guide
- Outcome: CONTRIBUTING.md section explaining param evolution and back-compat translations.

---

## B) SSE and Telemetry Standardization

14) Create an SSEPublisher abstraction
- Outcome: One module to publish JSON messages; remove direct redis calls from nodes.

15) Standardize event envelope
- Outcome: { type, timestamp, data, conversation_id, node?, level? }.

16) Update BaseNode to use SSEPublisher
- Outcome: _broadcast_start/progress/complete/error use JSON, no str(dict).

17) Update UnifiedProcessor to use the same publisher
- Outcome: Remove duplicate redis client; pass through abstraction.

18) Define SSE event taxonomy
- Outcome: Node lifecycle, token/chunk, router decisions, warnings/errors with severity.

19) Add correlation/trace IDs
- Outcome: Include trace_id and node execution IDs for debugging.

20) Extend NodeMetrics
- Outcome: Include tokens (if available), retries, and model usage where applicable.

---

## C) Import Path and Packaging Hygiene

21) Audit and fix relative imports
- Outcome: Replace incorrect “...agent.handywriterz_state” with “..handywriterz_state”.

22) Decide on absolute vs relative policy
- Outcome: Within backend/src/agent use relative; expose a package entrypoint if needed.

23) Configure packaging
- Outcome: Ensure Python path or packaging is consistent in dev/test/prod.

24) Lint rule for imports
- Outcome: Pre-commit hook or CI linter ensuring import consistency.

---

## D) Search Layer Standardization

25) Make all AI search agents inherit BaseSearchNode
- Outcome: Gemini, Perplexity, O3, Claude, OpenAI refactored to BaseSearchNode with provider-specific _perform_search and _convert_to_search_result; specialized artifacts still published as extras.

26) Provide provider adapters
- Outcome: For agents that cannot inherit BaseSearchNode soon, add a shim producing standardized SearchResult[].

27) Fix Perplexity credibility key mismatch
- Outcome: Use credibility_scores consistently; update references to source_scores.

28) Remove unsupported _broadcast_progress(error=...)
- Outcome: Nodes call _broadcast_error or progress with a message only; add error reporting via standardized SSEPublisher.

29) Improve OpenAI agent robustness
- Outcome: Handle missing API key gracefully; avoid IndexError on empty search_queries; return empty standardized results.

30) Enrich minimal agents
- Outcome: Claude/OpenAI fill SearchResult fields (title, url, abstract) when possible, even if heuristic.

31) Add testing fixtures for agents
- Outcome: Mock provider responses; verify conversion to SearchResult.

32) Implement rate limiting awareness
- Outcome: BaseSearchNode rate limiting parameters configurable per provider; doc best practices.

33) Expand EvidenceGuard agents alignment
- Outcome: Ensure CrossRef/PMC/SS convert to SearchResult consistently.

34) Add Source type classifier utility
- Outcome: Shared function to infer “journal/conference/web/preprint” from domain/metadata.

35) URL normalization/dedup helper
- Outcome: Strip UTM, normalize protocols/hosts for dedup stable behavior.

---

## E) Aggregation and Verification

36) Aggregator normalization phase
- Outcome: Pre-pass that detects agent payload patterns (gemini/perplexity/o3) and extracts sources list into SearchResult objects before DOI/URL dedup.

37) Aggregation metrics
- Outcome: Counts before/after, dedup stats, DOI vs URL ratio, source_type distribution.

38) Extend SearchResult with provenance
- Outcome: raw_data contains agent tag and search_id for traceability.

39) SourceVerifier threshold tuning
- Outcome: Make thresholds configurable via user_params or policy; surface verification diagnostics.

40) Add link liveness check utility
- Outcome: Async HTTP HEAD/GET check with timeout; cached results.

---

## F) Source Filtering and Evidence Mapping

41) Align SourceFilter input to verified_sources
- Outcome: Prefer verified_sources; fallback to aggregated_sources; do not pull from raw_search_results directly.

42) Fix finally-block hazards
- Outcome: Guard assignments; initialize locals early to safe defaults.

43) Consolidate published/publication date logic
- Outcome: Use publication_date; add date parsing helper with robust fallbacks.

44) Evidence extraction improvements
- Outcome: NLP-assisted segmentation/scoring behind feature flags; keep heuristic fallback.

45) Redis storage guard
- Outcome: If Redis unavailable, persist to disk or omit; never crash.

46) Evidence schema contract
- Outcome: Document evidence_map schema with versioning for UI.

47) Hover-card constraints
- Outcome: Cap sizes; redact PII; ensure safe HTML where applicable.

48) Quality scoring calibration
- Outcome: Define scoring rubric and add tests; calibrate thresholds to reduce over/under selection.

49) Field-specific tuning hooks
- Outcome: Expand field_credibility_sources and mapping; allow overrides from config.

50) Statistics extraction robustness
- Outcome: Improve regex for numeric data capture; add unit tests.

---

## G) RAG and Summarization

51) Lazy-init SentenceTransformer and Chroma
- Outcome: Initialize on first execution with try/except; log and proceed with fallback summarization if unavailable.

52) Switch input to aggregated_sources
- Outcome: Replace aggregated_data reference; add compatibility shim if needed.

53) Summarization via LLM
- Outcome: Optional LLM-based summarization path with token budgeting.

54) Embedding metadata norms
- Outcome: Include DOI/URL/agent provenance as metadata; configure Chroma collection reuse.

55) Retrieval for writer
- Outcome: Provide top-k evidence passages to Writer; define key names clearly (e.g., rag_context).

---

## H) Writer, Evaluator, and Formatting

56) Writer input alignment
- Outcome: Writer consumes sources_canonical set; ensure citations align with IDs.

57) CitationAudit integration
- Outcome: Define when audit runs; ensure it reads the canonical sources list and draft field; fix key names.

58) Evaluator scoring rubric
- Outcome: Define scoring schema with dimensions; record to evaluation_results consistently.

59) Formatter input/outputs
- Outcome: Define input fields (draft/current_draft) and outputs (formatted_document); ensure docx/pdf channels downstream.

60) Methodology and synthesis contracts
- Outcome: Define input/outputs to provide consistent context to Writer and Evaluator.

---

## I) Turnitin Integration

61) Turnitin node contract
- Outcome: Input: document to check; Output: similarity_passed, ai_detection_passed, revision suggestions; robust error handling without leaking secrets.

62) Retry and backoff
- Outcome: Handle transient errors with capped retry.

63) Telemetry
- Outcome: Record turnaround and status codes; anonymize user info.

64) Dashboard redirection (frontend note)
- Outcome: Ensure orchestrator status changes surface to frontend to redirect on success.

---

## J) Orchestrator and Graph Wiring

65) Remove dead _execute_search_* methods
- Outcome: Rely on dynamic creation only; reduce confusion.

66) Ensure edges match dataflow
- Outcome: Adjust edges to ensure aggregator -> rag_summarizer -> source_verifier -> source_filter order is respected and inputs align.

67) Add conditional to run CitationAudit
- Outcome: Insert audit after writer when citations exist; route to writer for revision if missing.

68) Failure loop guard
- Outcome: Max revision cycles in writer/turnitin path to avoid infinite loops.

69) Swarm routing thresholds
- Outcome: Tune complexity thresholds from orchestration intelligence; make configurable.

70) State minimization between nodes
- Outcome: Clear transient keys; keep state lean to reduce serialization overhead.

---

## K) Model Policy, Pricing, and Health

71) Logical model registry
- Outcome: Map “o3-reasoner”, “sonar-deep” to provider IDs in price_table, unify naming.

72) Reconcile model_service API
- Outcome: Provide get_model_client(), get_agent_config(), record_usage or adapt agents to the simpler ModelService or introduce a new ProductionModelService.

73) PriceGuard integration in nodes
- Outcome: Estimate tokens and charge; enforce budget, raise BudgetExceeded with recoverable flags.

74) Health checks and routing bias
- Outcome: Record latency and success to Redis/in-memory; prefer healthy/cheaper models when suitable.

75) Circuit breakers
- Outcome: Temporarily disable failing providers; auto-recover after cooldown.

76) Task-aware policy routing
- Outcome: Choose different models for search vs writing vs evaluation; integrate with Task enum.

---

## L) Error Handling and Resilience

77) Remove unsupported kwargs in broadcast calls
- Outcome: Replace error=True usages with explicit error events.

78) Guard finally blocks
- Outcome: Initialize variables and wrap assignments.

79) Consistent NodeError usage
- Outcome: Set recoverable flags appropriately; orchestrator reacts to retry vs fail.

80) Typed exceptions
- Outcome: Distinguish provider errors, network errors, parsing errors.

81) Comprehensive logging
- Outcome: Structured logs with correlation IDs and node names; redact secrets.

---

## M) Testing and QA

82) Unit tests for normalization
- Outcome: Inputs in camelCase/snake_case produce the same canonical dict.

83) Agent adapter tests
- Outcome: Given agent payloads, Aggregator normalization produces SearchResult[].

84) SSE consumer tests
- Outcome: Ensure JSON-only messages parse; verify schema.

85) Orchestrator end-to-end test
- Outcome: Synthetic run from message to formatted_document with mocked providers.

86) Evidence map UI contract test
- Outcome: Validate hover-card data structure against versioned schema.

87) Model policy tests
- Outcome: Route to proper models based on task and health; simulate failover.

88) Turnitin flow test
- Outcome: Validate pass/fail routing and retry caps.

89) Performance tests
- Outcome: Load test with concurrent sessions; measure latency distribution.

90) Regression suite
- Outcome: Guard critical flows: router, aggregator, writer paths.

---

## N) Observability and Ops

91) Metrics emission
- Outcome: Prometheus-friendly metrics on node durations, retries, provider latencies.

92) Tracing
- Outcome: OpenTelemetry spans per node; link to conversation_id.

93) Dashboards
- Outcome: Grafana panels for throughput, errors, latency; provider health.

94) Alerting
- Outcome: PagerDuty/SMS on error spikes or provider failure.

95) Feature flags
- Outcome: Toggle new summarization or adapters; gradual rollout.

---

## O) Security and Compliance

96) Secret management
- Outcome: Use env var vault; remove secrets from code; rotate keys.

97) Evidence PII handling
- Outcome: Redaction, TTL, opt-out; document policy.

98) Audit logs
- Outcome: Track access and mutation of evidence; retention policy.

---

## P) Developer Experience

99) CONTRIBUTING.md updates
- Outcome: Document contracts, coding standards, import rules, testing.

100) Code owners and review checklists
- Outcome: Enforce reviews for orchestrator/contract changes; pre-merge checklist.

---

## Q) Execution Plan and Milestones

- Phase 1 (Contracts and SSE): Tasks 1-10, 14-20, 21-24
- Phase 2 (Search and Aggregation): Tasks 25-35, 36-40
- Phase 3 (Source Filter/RAG/Writer): Tasks 41-60
- Phase 4 (Turnitin/Graph/Policy): Tasks 61-76
- Phase 5 (Resilience/Testing/Observability/Security): Tasks 77-98
- Phase 6 (DX and Governance): Tasks 99-100

Each phase should include a short stabilization sprint with regression tests before proceeding.

---

## Appendix: Contract Snippets

A. Canonical UserParams (example Pydantic model)
- Fields: word_count:int, field:str, writeup_type:str, citation_style:str, region:str, language:str, academic_level:str, pages:int optional
- Translation map from camelCase aliases: writeupType->writeup_type, referenceStyle->citation_style, educationLevel->academic_level

B. SearchResult dict schema
- Required: title, authors[], abstract, url
- Optional: publication_date, doi, citation_count, source_type, credibility_score, relevance_score, raw_data{agent,search_id,provider_specific}

C. SSE Envelope
- { type, timestamp, conversation_id, node?, data, level? }

D. Evidence Map v1
- { source_id: { source_metadata{}, quality_metrics{}, evidence_content{}, citation_data{}, hover_card_data{} } }

---

This todo100.md provides a clear, prioritized path to elevate HandyWriterz AI to a reliable, scalable, secure, and maintainable system with consistent developer ergonomics and excellent user outcomes.
