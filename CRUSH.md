# CRUSH.md - Development Guidelines for HandyWriterzAI

## Build Commands (Root)

```bash
# Start frontend dev server
make dev-frontend

# Start backend dev server  
make dev-backend

# Start both dev servers
make dev
```

## Testing Commands

### Backend (Python)
```bash
# Run all tests
cd backend && make test

# Run specific test file
cd backend && make test TEST_FILE=tests/test_file.py

# Run single test function
pytest backend/src/tests/test_api.py::test_chat_validation -v

# Run tests in watch mode
cd backend && make test_watch

# Run with profile
cd backend && make test_profile
```

### Frontend (TypeScript/React)
```bash
# Run unit tests
cd frontend && npm test

# Run e2e tests
cd frontend && npm run test:e2e

# Run e2e headed tests
cd frontend && npm run test:e2e:headed
```

## Code Style Guidelines

### Python (Backend)
- **Formatting**: Use ruff for code formatting
- **Linting**: Use ruff for linting, mypy for type checking
- **Imports**: Use absolute imports from `src` directory
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Use FastAPI exception handlers, structured logging
- **Type Hints**: Required for all functions and variables
- **Docstrings**: Google-style docstrings for all public functions

### TypeScript/React (Frontend)
- **Formatting**: ESLint with Next.js config
- **Type Safety**: Strict TypeScript enabled
- **Imports**: Absolute imports using `@/` alias
- **Components**: PascalCase for components, camelCase for variables/functions
- **Hooks**: Custom hooks should start with `use`
- **Styling**: Tailwind CSS classes, avoid inline styles
- **State Management**: Zustand stores with TypeScript interfaces

## Database & Migration
```bash
# Run Alembic migrations
cd backend && alembic upgrade head

# Create new migration
cd backend && alembic revision --autogenerate -m "description"
```

## Environment Setup
- Use `.env.example` for required environment variables
- Backend: Python 3.12+ with uv for package management
- Frontend: Node.js 18+ with pnpm for package management

## AI & Model Guidelines
- Use the factory pattern for AI provider abstractions
- All model calls must include error handling and retries
- Stream responses using SSE where appropriate
- Validate all inputs with Pydantic schemas

Crush CLI Actions for HandyWriterzAi
This crush.md file lists high‑level code changes for Crush CLI (or similar LLM coding tools) to improve the HandyWriterzAi repository. Follow these tasks sequentially to address the issues identified in the codebase evaluation. Each task includes affected files and guidance; however, apply best practices and preserve functionality. After each task, ensure existing tests still pass.

1. Introduce Task‑based routing
Goal: Replace static role mapping with a Task enum and a TaskPolicy registry.

Steps
Create a new file under backend/src/agent/routing/ called task_router.py with a Task enum (e.g., GENERAL_CHAT, RESEARCH, DRAFTING, CODE_ASSIST, ACADEMIC_TOOLS, DATA_QA, REVIEWER, SUMMARIZER) and a TaskPolicy data class containing:

system_prompt: str

context_policy: ContextPolicy (see below)

allowed_tools: list[str]

candidate_models: list[str]

safety_rules: dict

Add a ContextPolicy data class that defines max_context_tokens, reserved_output_tokens, chunk_size, chunk_overlap, ranking_mode, and allowed file types.

Write a basic TaskRegistry (e.g., a dictionary keyed by task enum) with default policies. Use the recommendations from the report for candidate models and context budgets.

Update backend/src/main.py and relevant routers to accept a task parameter (string) in /api/chat and map legacy role/mode to tasks. Do not break backward compatibility.

Modify backend/src/agent/routing/unified_processor.py:

Remove direct calls to SystemRouter.analyze_request and instead call a new TaskRouter service that accepts the task and complexity (see next task).

When task is provided, bypass the simple/advanced/hybrid selection and use the appropriate pipeline based on the policy; otherwise fall back to complexity‑based routing.

Expose the Task enum to the frontend via /api/writing-types or a new endpoint so that the dropdown can be generated dynamically.

2. Modularize UnifiedProcessor
Goal: Refactor UnifiedProcessor into smaller services for maintainability.

Steps
Create new services under backend/src/services/:

task_router_service.py: encapsulate the logic for selecting simple/advanced/hybrid pipeline based on complexity and TaskPolicy.

budget_service.py: wrap get_budget_guard, guard_request and record_usage calls.

sse_service.py: unify SSE event publishing. Remove duplication in _publish_event and enforce JSON event envelopes.

prompt_service.py: implement PromptAssembler that merges system prompts, user message and top‑K context chunks.

Refactor UnifiedProcessor to delegate to these services. For example, call budget_service.check_and_track(...), then task_router_service.route(...), then use prompt_service.assemble_prompt(...) for the selected provider.

Split long methods into smaller private functions. Remove the try/except fallback that silently falls back to the advanced path; instead propagate errors to the client via unified error SSE events.

Add docstrings and type hints for clarity.

3. Implement PromptRegistry and ContextPipeline
Goal: Manage prompt templates and context retrieval per task.

Steps
Under backend/src/prompts/, create a directory structure and files for each task (e.g., general_chat.txt, research_browsing.txt, drafting_writer.txt, etc.). These templates should include system instructions tailored to each task (tone, citation policy, etc.).

Write a prompt_loader.py utility to load templates and render them (optionally using Jinja2 for parameter substitution).

Write a context_pipeline.py in backend/src/services/ that:

Accepts uploaded file IDs and a task.

Retrieves file chunks from the vector store (Supabase) using a ranking algorithm (BM25 + embeddings if possible).

Selects top‑K chunks fitting within ContextPolicy.max_context_tokens minus reserved output tokens.

Returns the context text and metadata (sources) to the prompt assembler.

Update chat and write endpoints to use the new prompt and context pipeline.

4. Enhance provider selection and health checks
Goal: Use provider metrics to choose optimal models.

Steps
Extend ProviderFactory (in backend/src/models/factory.py) to record statistics such as latency, error rate and cost per provider/model. Add a method get_provider_stats(model_id: str) -> ProviderStats.

Add periodic background tasks (e.g., using Celery Beat or FastAPI startup tasks) to update health metrics by pinging each provider.

Modify the task router to choose the best candidate model for a task based on TaskPolicy priorities and provider health; include fallback logic when a provider is unhealthy.

Restrict Gemini models to GENERAL_CHAT tasks only, as recommended.

5. Expand unit tests and API contract tests
Goal: Ensure new functionality works and prevent regressions.

Steps
Add tests for the new TaskRouter, PromptAssembler, ContextPipeline and SSEService under backend/tests/.

Update test_user_journey.py and other e2e tests to cover each task type and ensure proper provider selection and streaming behaviour.

Add tests to verify that the system rejects unsupported tasks and returns a clear error.

6. Update the frontend for task selection and improved UX
Goal: Surface the new task API and provide intuitive user flows.

Steps
Modify frontend/src/components/InputForm.tsx to replace the existing mode/dropdown with a Task selector. Fetch the task list from the new API and display human‑readable labels and descriptions.

Consolidate InputForm and ImprovedInputForm into a single component that handles file uploads, task selection and prompt input. Remove unused components to reduce clutter.

Update the chat API route (frontend/src/app/api/chat/send/route.ts) to include the selected task in the payload (task instead of mode). Maintain compatibility for older clients by mapping unknown values to GENERAL_CHAT.

Add UI feedback showing the selected model/provider (e.g., “Powered by OpenRouter Kimi K2”) and the task being executed.

Integrate the originality check (Turnitin Workbench) into the chat view. Present plagiarism scores and suggestions inline rather than opening a new tab.

7. Miscellaneous improvements
Standardize error handling: return SSE events with fields type, message, code and optionally details. Remove stringified dictionaries.

Add rate limiting and authentication checks to /api/chat and /api/write endpoints.

Document environment variables in backend/README.md and frontend/README.md to improve developer experience.

Use consistent naming conventions (snake_case in Python, camelCase in TypeScript) and add type hints where missing.

When using Crush CLI, load this crush.md to provide instructions. Each section should be treated as a separate task to implement. Make sure to cross‑reference relevant files and maintain backwards compatibility. Run existing tests and add new ones to validate your changes.