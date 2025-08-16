# TODO 103.md - HandyWriterzAI Development Roadmap

## Executive Summary

Based on comprehensive analysis of the HandyWriterzAI codebase, this document outlines the critical development tasks needed to transform the platform into a production-ready, ChatGPT/Kimi K2-level academic writing assistant. The analysis reveals significant technical debt in the backend architecture and major UI/UX gaps in the frontend that must be addressed systematically.

## Current State Analysis

### Backend Architecture Issues

#### 1. Routing System Fragmentation
**Files**: `backend/src/agent/routing/unified_processor.py`, `backend/src/agent/routing/complexity_analyzer.py`
**Status**: Critical - Multiple routing patterns causing inconsistency

**Issues Identified**:
- UnifiedProcessor mixes complexity-based and task-based routing logic
- No clear separation between simple Gemini and advanced HandyWriterz workflows
- Missing task enumeration and policy registry system
- ComplexityAnalyzer scoring algorithm is not well-documented or tested

#### 2. SSE Implementation Inconsistencies  
**Files**: Multiple agent nodes, `backend/src/main.py`
**Status**: Critical - Breaking streaming functionality

**Issues Identified**:
- Mixed JSON and str(dict) event publishing across nodes
- No unified SSE publisher with Redis backend
- Missing correlation/trace ID support
- Inconsistent event schemas causing frontend parsing errors

#### 3. Search Agent Heterogeneity
**Files**: `backend/src/agent/nodes/search_*.py`
**Status**: Critical - Aggregation failures

**Issues Identified**:
- Each search agent (Arxiv, Scholar, CrossRef, PMC) returns different schemas
- Inconsistent field names: `credibility_scores` vs `source_scores`
- No standard SearchResult adapter layer
- Aggregator has agent-specific conditionals that should be abstracted

#### 4. Model Management Chaos
**Files**: `backend/src/models/factory.py`, `backend/src/models.json`
**Status**: Critical - Provider management failures

**Issues Identified**:
- Model ID mismatches: `o3-reasoner` vs `sonar-deep`
- No centralized model registry with logical→provider ID mapping
- Missing price table integration for cost tracking
- No health monitoring for provider failover

#### 5. Parameter Normalization Missing
**Files**: Various API endpoints and agent nodes
**Status**: Critical - Runtime errors

**Issues Identified**:
- Mixed camelCase/snake_case parameters across components
- No validation for DocumentType, CitationStyle, AcademicField enums
- Missing derived field validation (pages, target_sources)
- Import path inconsistencies causing runtime failures

### Frontend UX Issues

#### 1. Broken Composer Experience
**Files**: `frontend/src/components/InputForm.tsx`, `frontend/src/components/ImprovedInputForm.tsx`
**Status**: Critical - Core functionality broken

**Issues Identified**:
- Composer row not unified - separate Tools button and paperclip
- Write-up type dropdown not integrated into composer row
- Send arrow (↑) inactive after clicking demo examples
- Plus button opens modal instead of native file picker
- No file chips display for selected files

#### 2. Missing Streaming UI
**Files**: `frontend/src/components/ChatMessagesView.tsx`, `frontend/src/lib/useChatStream.ts`
**Status**: Critical - No real-time feedback

**Issues Identified**:
- Messages don't stream token-by-token
- No "Show reasoning" toggle for agent thinking
- Missing status ticker ("Parsing files... Routing to agents...")
- No export actions row on assistant responses
- Failed to fetch errors without retry mechanism

#### 3. State Management Problems
**Files**: `frontend/src/store/`, Zustand stores
**Status**: High - Inconsistent state

**Issues Identified**:
- Multiple overlapping stores without clear separation
- No proper conversation management (load, switch, new chat)
- Missing file upload state tracking
- No error state handling with toasts
- Inconsistent API response handling

#### 4. Non-functional Navigation
**Files**: `frontend/src/app/`, various page components
**Status**: High - Dead links everywhere

**Issues Identified**:
- Library, Settings, Profile pages are placeholders
- Sidebar conversation list doesn't load real data
- Search functionality not implemented
- No conversation persistence or loading

## Critical Development Roadmap

### Phase 0: Emergency Fixes (Week 1 - IMMEDIATE)

#### 0.1 Fix Broken Imports and Runtime Errors
**Priority**: BLOCKER
**Files**: `backend/src/agent/simple/__init__.py`, various import statements
**Tasks**:
- Fix re-exports for `build_gemini_graph` and `GeminiState`
- Resolve all relative import hazards
- Add proper error handling for missing imports
- Ensure all modules can be imported without errors

#### 0.2 Implement Basic SSE Standardization
**Priority**: BLOCKER  
**Files**: Create `backend/src/agent/sse.py`
**Tasks**:
- Create unified `SSEPublisher` class
- Replace all str(dict) broadcasts with JSON events
- Add basic correlation ID support
- Fix frontend SSE parsing to handle consistent format

#### 0.3 Fix Composer Send Functionality
**Priority**: BLOCKER
**Files**: `frontend/src/components/InputForm.tsx`
**Tasks**:
- Make send arrow activate when text OR examples are present
- Fix demo example click handlers
- Add basic form validation
- Remove "Failed to fetch" errors with proper error handling

### Phase 1: Backend Foundation (Weeks 1-2)

#### 1.1 Parameter Normalization System
**Priority**: HIGH
**File**: Create `backend/src/agent/routing/normalization.py`
**Tasks**:
- Implement `normalize_user_params()` function
- Create camelCase ↔ snake_case mapping
- Add enum validation for DocumentType, CitationStyle, AcademicField
- Validate derived fields (pages, target_sources)
- Integrate with UnifiedProcessor

#### 1.2 Model Registry & Budget Control
**Priority**: HIGH
**Files**: Create `backend/src/models/registry.py`, `backend/src/services/budget.py`
**Tasks**:
- Implement model registry with logical→provider ID mapping
- Load and validate model_config.yaml + price_table.json
- Add startup validation with fail-fast behavior
- Implement token estimation and budget guards
- Integrate budget checks with UnifiedProcessor

#### 1.3 Search Result Standardization
**Priority**: HIGH
**File**: Create `backend/src/agent/search/adapter.py`
**Tasks**:
- Implement `SearchResult` schema and adapter layer
- Create `to_search_results()` for each provider
- Standardize field names (credibility_scores → source_scores)
- Update all search agents to use adapter
- Remove agent-specific conditionals from Aggregator

#### 1.4 Task-Based Routing System
**Priority**: HIGH
**File**: Create `backend/src/agent/routing/task_router.py`
**Tasks**:
- Create Task enum (GENERAL_CHAT, RESEARCH, DRAFTING, etc.)
- Implement TaskPolicy data class with context policies
- Create TaskRegistry with default policies
- Update UnifiedProcessor to use task-based routing
- Expose Task enum via API endpoint

### Phase 2: Frontend UX Overhaul (Weeks 2-3)

#### 2.1 Unified Composer Component
**Priority**: HIGH
**File**: Create `frontend/src/components/chat/MessageInputBar.tsx`
**Tasks**:
- Create single composer row with all elements
- Integrate write-up type dropdown into composer
- Implement native file picker (no modal)
- Add file chips display with remove functionality
- Implement proper send activation logic

#### 2.2 Streaming UI Implementation
**Priority**: HIGH
**Files**: Update `frontend/src/components/chat/`, create new components
**Tasks**:
- Implement token-by-token message streaming
- Add reasoning toggle component in message bubbles
- Create status ticker for agent progress
- Implement export actions row on responses
- Add error toast system with retry

#### 2.3 State Management Refactor
**Priority**: HIGH
**Files**: `frontend/src/store/`
**Tasks**:
- Consolidate into clear chatStore + uiStore separation
- Implement proper conversation management
- Add file upload state tracking
- Create error state management system
- Add TypeScript interfaces for all state

#### 2.4 Navigation Functionality
**Priority**: MEDIUM
**Files**: `frontend/src/app/` pages
**Tasks**:
- Implement real conversation list in sidebar
- Add conversation loading and switching
- Create basic Library page with saved outputs
- Implement Settings and Profile page stubs
- Add search functionality in sidebar

### Phase 3: Advanced Backend Features (Weeks 3-4)

#### 3.1 Prompt Registry & Context Pipeline
**Priority**: MEDIUM
**Files**: Create `backend/src/prompts/`, `backend/src/services/context_pipeline.py`
**Tasks**:
- Create task-specific prompt templates
- Implement prompt loader with Jinja2 support
- Build context pipeline for file chunk retrieval
- Implement top-K chunk selection with token budgeting
- Integrate with task-based routing

#### 3.2 Enhanced Error Handling & Logging
**Priority**: MEDIUM
**Files**: Various agent nodes, create `backend/src/services/logging_context.py`
**Tasks**:
- Fix unsupported kwargs in error handlers
- Guard finally blocks with proper initialization
- Implement correlation ID tracking
- Add structured logging with node names
- Create unified error SSE event format

#### 3.3 Security Middleware Enhancement
**Priority**: MEDIUM
**Files**: `backend/src/main.py`, security middleware
**Tasks**:
- Verify middleware order (Security → Error → CORS)
- Add CSRF enforcement on state-changing endpoints
- Implement rate limiting for /api/chat and /api/write
- Add JWT validation to sensitive routes
- Add per-tenant and per-IP rate limiting

#### 3.4 File Processing Completion
**Priority**: MEDIUM
**Files**: `backend/src/utils/`, `backend/src/services/`
**Tasks**:
- Complete Arweave integration
- Implement Whisper transcription for audio
- Add Gemini Vision processing for images
- Fix chunk splitter for all file formats
- Implement proper file validation and limits

### Phase 4: Integration & Polish (Weeks 4-5)

#### 4.1 Agent Pipeline Completion
**Priority**: MEDIUM
**Files**: Various agent nodes with TODO markers
**Tasks**:
- Complete privacy_manager database integration
- Implement tutor_feedback_loop storage
- Add proper error handling in all nodes
- Complete citation_audit functionality
- Implement proper agent timeout and retry logic

#### 4.2 Turnitin Integration
**Priority**: MEDIUM
**Files**: `backend/src/turnitin/`
**Tasks**:
- Complete Telegram session management
- Implement plagiarism checking workflow
- Add retry logic and error handling
- Integrate with main writing pipeline
- Add plagiarism score display in frontend

#### 4.3 Testing Suite Implementation
**Priority**: MEDIUM
**Files**: `backend/tests/`, `frontend/tests/`
**Tasks**:
- Unit tests for all new backend services
- Integration tests for chat SSE lifecycle
- Contract tests for API schemas
- E2E tests for complete user journeys
- Add test coverage reporting

#### 4.4 Performance Optimization
**Priority**: LOW
**Files**: Various performance bottlenecks
**Tasks**:
- Optimize vector storage queries
- Implement caching for frequently accessed data
- Add database connection pooling
- Optimize frontend bundle size
- Add performance monitoring

## Success Metrics

### Technical Metrics
- ✅ Zero import errors across all modules
- ✅ 100% JSON-only SSE events with proper correlation
- ✅ Consistent parameter handling across all components  
- ✅ Sub-500ms routing decisions
- ✅ 95%+ test coverage on critical paths
- ✅ Unified composer with proper file handling
- ✅ Real-time streaming with <100ms latency
- ✅ Functional navigation and state management

### Business Metrics  
- ✅ Support for 10+ file formats with processing
- ✅ Cost tracking and budget enforcement per request
- ✅ Plagiarism detection integration
- ✅ Multi-provider failover capability
- ✅ ChatGPT/Kimi K2 level UX polish
- ✅ Export functionality (PDF, DOCX, MD)
- ✅ Proper conversation management
- ✅ Mobile responsive design

## Risk Assessment

### High Risk
- Parameter normalization may break existing analyzer scoring
- SSE refactor could impact streaming performance during transition
- Model registry changes may break existing provider integrations
- Frontend state refactor could introduce new bugs

### Medium Risk
- Error handling changes may mask existing issues
- Security middleware order changes could break authentication
- Budget controls may be too restrictive for users
- UI component consolidation may introduce visual regressions

### Low Risk
- Documentation updates
- Test additions
- Configuration centralization
- Performance optimizations

## Mitigation Strategies

1. **Feature Flags**: Use environment variables to enable new features gradually
2. **A/B Testing**: Compare analyzer outputs before/after normalization  
3. **Shadow Mode**: Double-publish SSE events during transition
4. **Rollback Plans**: Maintain ability to revert changes quickly
5. **Staged Deployment**: Deploy backend changes first, then frontend
6. **Monitoring**: Add metrics and alerts for all major changes
7. **User Testing**: Get early feedback on UI changes with power users

## Implementation Timeline

### Week 1: Emergency Foundation
- Fix all blocking import and runtime errors
- Implement basic SSE standardization
- Fix composer send functionality
- Start parameter normalization system

### Week 2: Core Systems
- Complete model registry and budget control
- Implement search result standardization
- Start task-based routing system
- Begin unified composer component

### Week 3: UX Transformation  
- Complete unified composer with file handling
- Implement streaming UI components
- Refactor state management
- Add basic navigation functionality

### Week 4: Advanced Features
- Complete prompt registry and context pipeline
- Enhance error handling and logging
- Complete security middleware
- Finish file processing pipeline

### Week 5: Integration & Polish
- Complete agent pipeline and Turnitin integration
- Implement comprehensive testing suite
- Performance optimization
- Documentation and deployment prep

## Conclusion

The HandyWriterzAI platform requires significant work to reach production readiness, but the path forward is clear. By focusing on emergency fixes first, then building a solid foundation with proper contracts and standardization, followed by the UX transformation needed to match industry standards, we can create a truly competitive academic writing assistant.

The key is systematic implementation with proper testing at each phase, ensuring that technical debt is addressed while simultaneously delivering the user experience improvements that will differentiate the platform in the market.

---

*Generated on: 2025-02-08*  
*Based on: Comprehensive codebase analysis, architecture review, and UX requirements*