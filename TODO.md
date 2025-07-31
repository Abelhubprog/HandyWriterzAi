# HandyWriterzAI Development TODO

## Executive Summary

Based on comprehensive analysis of the backend architecture, documentation, and existing implementation, this document outlines the critical development tasks needed to transform HandyWriterzAI into a production-ready multi-agent academic writing platform.

## Current State Analysis

### Architecture Overview
- **Frontend**: React 19 + Vite with Dynamic.xyz Web3 integration
- **Backend**: FastAPI with multi-agent LangGraph orchestration
- **Database**: PostgreSQL with Supabase vector storage
- **AI Providers**: Multi-provider system (Gemini, OpenAI, Anthropic, Perplexity)
- **File Processing**: TUS resumable uploads with Celery background processing
- **Communication**: WebSocket SSE streaming for real-time updates

### Key Components Identified
1. **Routing System**: `UnifiedProcessor` and `ComplexityAnalyzer`
2. **Agent Graphs**: Simple Gemini vs Advanced HandyWriterz workflows
3. **Multi-Agent Pipeline**: Intent → Planning → Research → Aggregation → Writing → QA
4. **File Processing**: Chunking, embedding, and vector storage
5. **Security**: CSRF, JWT, rate limiting middleware

## Critical Development Tasks

### Phase 1: Foundation & Contracts (Priority: High)

#### 1.1 Parameter Normalization System
- **File**: Create `backend/src/agent/routing/normalization.py`
- **Status**: Missing - Critical for consistency
- **Tasks**:
  - Implement `normalize_user_params()` function
  - Map camelCase to snake_case conversions
  - Validate enum values (DocumentType, CitationStyle, AcademicField)
  - Add validation for derived fields (pages, target_sources)
- **Impact**: Fixes parameter fragmentation across components

#### 1.2 Unified SSE Publisher
- **File**: Create `backend/src/agent/sse.py`
- **Status**: Missing - Critical for streaming
- **Tasks**:
  - Implement `SSEPublisher` class with Redis backend
  - Standardize JSON-only event publishing
  - Add correlation/trace ID support
  - Replace str(dict) broadcasts in all nodes
- **Impact**: Consistent event streaming and debugging

#### 1.3 Simple Agent Re-exports
- **File**: Update `backend/src/agent/simple/__init__.py`
- **Status**: Incomplete - Import errors
- **Tasks**:
  - Add re-exports for `build_gemini_graph` and `GeminiState`
  - Fix import path consistency issues
  - Remove relative import hazards
- **Impact**: Stable import structure

### Phase 2: Model Registry & Budget Control (Priority: High)

#### 2.1 Model Registry System
- **File**: Create `backend/src/models/registry.py`
- **Status**: Missing - Critical for provider management
- **Tasks**:
  - Implement registry to map logical → provider IDs
  - Load and validate model_config.yaml + price_table.json
  - Add startup validation with fail-fast behavior
  - Resolve model ID mismatches (o3-reasoner, sonar-deep)
- **Impact**: Unified model management and pricing

#### 2.2 Budget Enforcement
- **File**: Create `backend/src/services/budget.py`
- **Status**: Missing - No cost controls
- **Tasks**:
  - Implement token estimation and budget guards
  - Add per-request cost tracking
  - Integrate with UnifiedProcessor for pre-execution checks
  - Generate budget exceeded SSE errors
- **Impact**: Cost control and abuse prevention

### Phase 3: Search Agent Standardization (Priority: High)

#### 3.1 Search Result Adapter Layer
- **File**: Create `backend/src/agent/search/adapter.py`
- **Status**: Missing - Heterogeneous outputs
- **Tasks**:
  - Implement `to_search_results()` for each provider
  - Standardize SearchResult schema across agents
  - Handle Gemini/Perplexity/O3/Claude/OpenAI output formats
  - Fix credibility_scores vs source_scores inconsistency
- **Impact**: Consistent aggregation and filtering

#### 3.2 Agent Output Harmonization
- **Files**: Multiple search agents in `backend/src/agent/nodes/search_*.py`
- **Status**: Inconsistent - Agent-specific outputs
- **Tasks**:
  - Update all search agents to use adapter layer
  - Remove agent-specific conditionals in Aggregator
  - Ensure SourceVerifier consumes standardized inputs
  - Fix SourceFilter to prefer verified_sources
- **Impact**: Simplified downstream processing

### Phase 4: Error Handling & Observability (Priority: Medium)

#### 4.1 Error Path Hardening
- **Files**: Various nodes with error handling issues
- **Status**: Fragile - Secondary exceptions possible
- **Tasks**:
  - Fix unsupported `_broadcast_progress(error=True)` usage
  - Guard finally blocks with proper variable initialization
  - Remove incorrect decorator kwargs in error handlers
  - Add correlation IDs to all logs and events
- **Impact**: Robust error recovery

#### 4.2 Structured Logging
- **File**: Create `backend/src/services/logging_context.py`
- **Status**: Missing - No correlation tracking
- **Tasks**:
  - Implement correlation ID generation from conversation_id
  - Add structured logging with node names and phases
  - Integrate with SSEPublisher for consistent event correlation
  - Add request-scoped logging context
- **Impact**: Improved debugging and monitoring

### Phase 5: Security & Middleware (Priority: Medium)

#### 5.1 Security Posture Validation
- **File**: `backend/src/main.py`
- **Status**: Needs verification - Middleware order critical
- **Tasks**:
  - Verify Security → Error → CORS middleware order
  - Ensure CSRF enforcement on state-changing endpoints
  - Apply rate limiting to /api/chat and /api/write
  - Add JWT validation to sensitive routes
- **Impact**: Security compliance

#### 5.2 Rate Limiting & Abuse Prevention
- **Files**: Security middleware and services
- **Status**: Partial - Needs per-route configuration
- **Tasks**:
  - Configure per-IP and per-tenant limits
  - Add burst and sustained rate limiting
  - Implement circuit breakers for failing providers
  - Surface budget denials in responses
- **Impact**: Platform stability and cost control

### Phase 6: Missing Components & Features (Priority: Medium)

#### 6.1 File Processing Pipeline
- **Status**: Identified TODOs in multiple files
- **Tasks**:
  - Complete Arweave integration (utils/arweave.py)
  - Implement Whisper transcription for audio files
  - Add Gemini Vision processing for images/videos
  - Fix chunk splitter for various file formats
- **Impact**: Full file format support

#### 6.2 Agent Node Completions
- **Status**: Multiple TODO markers in agent nodes
- **Tasks**:
  - Complete privacy_manager database integration
  - Implement tutor_feedback_loop storage
  - Add proper error handling in all nodes
  - Complete citation_audit functionality
- **Impact**: Full agent pipeline functionality

#### 6.3 Turnitin Integration
- **Files**: `backend/src/turnitin/` and related nodes
- **Status**: Partial implementation
- **Tasks**:
  - Complete Telegram session management
  - Implement plagiarism checking workflow
  - Add retry logic and error handling
  - Integrate with main writing pipeline
- **Impact**: Plagiarism detection capability

### Phase 7: Testing & Quality Assurance (Priority: Medium)

#### 7.1 Test Suite Development
- **Status**: Minimal test coverage
- **Tasks**:
  - Unit tests for normalization, SSE, registry, adapters
  - Integration tests for chat SSE lifecycle
  - Contract tests for SSE schema validation
  - End-to-end tests for complete workflows
- **Impact**: Quality assurance and regression prevention

#### 7.2 CI/CD Pipeline
- **Status**: Missing
- **Tasks**:
  - GitHub Actions workflow for tests and linting
  - Coverage reporting and thresholds
  - Automated deployment pipeline
  - Environment-specific configuration
- **Impact**: Development workflow automation

### Phase 8: Documentation & Developer Experience (Priority: Low)

#### 8.1 Documentation Updates
- **Files**: Various .md files in backend/docs/
- **Status**: Comprehensive but needs updates
- **Tasks**:
  - Update flows.md with finalized SSE schema
  - Extend user journeys documentation
  - Create API documentation with examples
  - Add troubleshooting guides
- **Impact**: Developer and user experience

#### 8.2 Configuration Management
- **Status**: Environment variables scattered
- **Tasks**:
  - Centralize configuration in settings
  - Add feature flag system
  - Implement secrets management
  - Add configuration validation
- **Impact**: Operational simplicity

## Implementation Priority Matrix

### Immediate (Weeks 1-2)
1. Parameter normalization system
2. Unified SSE publisher
3. Model registry and budget controls
4. Search result adapter layer

### Short-term (Weeks 3-4)
1. Error handling hardening
2. Security middleware validation
3. Agent output standardization
4. Basic test suite

### Medium-term (Weeks 5-8)
1. Complete missing agent components
2. File processing pipeline completion
3. Turnitin integration
4. Comprehensive testing

### Long-term (Weeks 9-12)
1. Performance optimization
2. Advanced monitoring
3. Documentation completion
4. Production deployment

## Success Criteria

### Technical Metrics
- Zero import errors across all modules
- 100% JSON-only SSE events
- Consistent parameter handling across all components
- Sub-500ms routing decisions
- 95%+ test coverage on critical paths

### Business Metrics
- Support for 10+ file formats
- Real-time streaming with <100ms latency
- Cost tracking per request
- Plagiarism detection integration
- Multi-provider failover capability

## Risk Assessment

### High Risk
- Parameter normalization may affect analyzer scoring
- SSE refactor could impact streaming performance
- Model registry changes may break existing integrations

### Medium Risk
- Error handling changes may mask existing issues
- Security middleware order changes could break authentication
- Budget controls may be too restrictive

### Low Risk
- Documentation updates
- Test additions
- Configuration centralization

## Mitigation Strategies

1. **Feature Flags**: Use environment variables to enable new features gradually
2. **A/B Testing**: Compare analyzer outputs before/after normalization
3. **Shadow Mode**: Double-publish SSE events during transition
4. **Rollback Plans**: Maintain ability to revert changes quickly
5. **Monitoring**: Add metrics and alerts for all major changes

## Conclusion

The HandyWriterzAI platform has a solid architectural foundation but requires significant development work to reach production readiness. The identified tasks are well-defined and achievable with proper prioritization and implementation strategy. The focus should be on contracts and standardization first, followed by reliability and security improvements.

---

*Generated on: 2025-01-31*
*Based on: Backend analysis, documentation review, and codebase audit*
