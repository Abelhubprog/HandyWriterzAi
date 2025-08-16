PS D:\HandyWriterzAi> cd backend
PS D:\HandyWriterzAi\backend> make install-deps
make: The term 'make' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS D:\HandyWriterzAi\backend> pytest -q

====================================== ERRORS ====================================== 
_____________ ERROR collecting backend/src/tests/e2e/test_full_flow.py _____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\e2e\test_full_flow.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\e2e\test_full_flow.py:15: in <module>
    from src.main import app
src\main.py:82: in <module>
    from src.db.database import (
src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
__________________ ERROR collecting backend/src/tests/test_api.py __________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_api.py:3: in <module>
    from backend.src.main import app
E   ModuleNotFoundError: No module named 'backend'
___________ ERROR collecting backend/src/tests/test_autonomy_v2_basic.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_autonomy_v2_basic.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_autonomy_v2_basic.py:3: in <module>
    from backend.src.autonomy_v2.core.graph import build_graph
E   ModuleNotFoundError: No module named 'backend'
__________ ERROR collecting backend/src/tests/test_autonomy_v2_vector.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_autonomy_v2_vector.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_autonomy_v2_vector.py:1: in <module>
    from backend.src.autonomy_v2.memory.vector_repo import VectorRepo
E   ModuleNotFoundError: No module named 'backend'
________ ERROR collecting backend/src/tests/test_autonomy_v2_worker_once.py ________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_autonomy_v2_worker_once.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_autonomy_v2_worker_once.py:1: in <module>
    from backend.src.autonomy_v2.runtime.checkpointer_sql import seed
E   ModuleNotFoundError: No module named 'backend'
______ ERROR collecting backend/src/tests/test_chat_init_returns_trace_id.py _______ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_chat_init_returns_trace_id.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/mnt/d/handywriterzai/backend/src/tests/test_chat_init_returns_trace_id.py:22: in <module>
    ???
src\routes\chat_gateway.py:17: in <module>
    from ..services.model_selector import get_model_selector, SelectionContext, SelectionStrategy
src\services\model_selector.py:17: in <module>
    from .model_policy import ModelPolicyRegistry, get_model_policy_registry, NodeCapabilityRequirement
src\services\model_policy.py:20: in <module>
    from .gateway import ModelSpec, ModelCapability, ProviderType
E   ImportError: cannot import name 'ModelSpec' from '<unknown module name>' (unknown location)
__________ ERROR collecting backend/src/tests/test_memory_integration.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_memory_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_memory_integration.py:12: in <module>
    from services.memory_integrator import get_memory_integrator
E   ModuleNotFoundError: No module named 'services'
___________ ERROR collecting backend/src/tests/test_search_perplexity.py ___________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_search_perplexity.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_search_perplexity.py:3: in <module>
    from agent.nodes.search_perplexity import PerplexitySearchAgent
E   ModuleNotFoundError: No module named 'agent'
_______________ ERROR collecting backend/src/tests/test_services.py ________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_services.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_services.py:2: in <module>
    from backend.src.services.model_service import model_service, BudgetExceeded     
E   ModuleNotFoundError: No module named 'backend'
_____________ ERROR collecting backend/src/tests/test_source_filter.py _____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_source_filter.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_source_filter.py:3: in <module>
    from agent.nodes.source_filter import SourceFilterNode
E   ModuleNotFoundError: No module named 'agent'
_________ ERROR collecting backend/src/tests/test_turnitin_idempotency.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_turnitin_idempotency.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_turnitin_idempotency.py:4: in <module>
    from backend.src.api.autonomy_v2 import turnitin_report_webhook, TurnitinWebhook 
E   ModuleNotFoundError: No module named 'backend'
_____________ ERROR collecting backend/src/tests/test_user_journey.py ______________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_user_journey.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_user_journey.py:8: in <module>
    from src.main import app
src\main.py:82: in <module>
    from src.db.database import (
src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
________________ ERROR collecting backend/src/tests/test_writer.py _________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\src\tests\test_writer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\tests\test_writer.py:3: in <module>
    from agent.nodes.writer import RevolutionaryWriterAgent
src\agent\nodes\writer.py:20: in <module>
    from src.services.llm_service import get_llm_client
src\services\llm_service.py:5: in <module>
    from langchain_anthropic import ChatAnthropic
E   ModuleNotFoundError: No module named 'langchain_anthropic'
______ ERROR collecting backend/tests/integration/test_memory_integration.py _______ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_memory_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\integration\test_memory_integration.py:8: in <module>
    from backend.src.agent.nodes.memory_demo_agent import MemoryDemoAgent
E   ModuleNotFoundError: No module named 'backend'
_________ ERROR collecting backend/tests/integration/test_model_config.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_model_config.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\integration\test_model_config.py:9: in <module>
    from backend.src.api.model_config import (
E   ModuleNotFoundError: No module named 'backend'
_________ ERROR collecting backend/tests/integration/test_sse_endpoints.py _________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_sse_endpoints.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\integration\test_sse_endpoints.py:11: in <module>
    from backend.src.agent.sse import SSEPublisher
E   ModuleNotFoundError: No module named 'backend'
_______ ERROR collecting backend/tests/integration/test_streaming_client.py ________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\integration\test_streaming_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\integration\test_streaming_client.py:11: in <module>
    from backend.src.main import app
E   ModuleNotFoundError: No module named 'backend'
________ ERROR collecting backend/tests/test_chunk_splitter_integration.py _________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_chunk_splitter_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_chunk_splitter_integration.py:7: in <module>
    from src.services.chunk_splitter import ChunkSplitter, SplitConfig, SplitStrategysrc\services\chunk_splitter.py:16: in <module>
    import aiofiles
E   ModuleNotFoundError: No module named 'aiofiles'
___________ ERROR collecting backend/tests/test_dissertation_journey.py ____________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_dissertation_journey.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_dissertation_journey.py:6: in <module>
    from src.agent.handywriterz_graph import handywriterz_graph
src\agent\handywriterz_graph.py:12: in <module>
    from .nodes.user_intent import UserIntentNode
src\agent\nodes\user_intent.py:13: in <module>
    from ..base_agent import BaseAgent
src\agent\base_agent.py:5: in <module>
    from ..handywriterz_state import HandyWriterzState
E   ModuleNotFoundError: No module named 'src.handywriterz_state'
____________________ ERROR collecting backend/tests/test_e2e.py ____________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_e2e.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_e2e.py:6: in <module>
    from main import app # Assuming your FastAPI app is in main.py
    ^^^^^^^^^^^^^^^^^^^^
src\main.py:82: in <module>
    from src.db.database import (
src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
______________ ERROR collecting backend/tests/test_evidence_guard.py _______________ 
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
..\backend_env\Lib\site-packages\_pytest\assertion\rewrite.py:186: in exec_module    
    exec(co, module.__dict__)
tests\test_evidence_guard.py:9: in <module>
    with patch('agent.nodes.master_orchestrator.MasterOrchestratorAgent._initialize_ai_providers'):
C:\Python312\Lib\unittest\mock.py:1442: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
C:\Python312\Lib\pkgutil.py:528: in resolve_name
    result = getattr(result, p)
             ^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'      
__________________ ERROR collecting backend/tests/test_health.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_health.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_health.py:3: in <module>
    from backend.src.main import app
E   ModuleNotFoundError: No module named 'backend'
_______________ ERROR collecting backend/tests/test_memory_writer.py _______________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_memory_writer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_memory_writer.py:5: in <module>
    from agent.nodes.memory_writer import MemoryWriter
src\agent\nodes\memory_writer.py:10: in <module>
    from ...services.memory_integrator import get_memory_integrator
E   ImportError: attempted relative import beyond top-level package
__________________ ERROR collecting backend/tests/test_routing.py __________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_routing.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_routing.py:2: in <module>
    from agent.nodes.loader import load_graph   # helper that reads YAML → Graph     
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\agent\nodes\loader.py:2: in <module>
    from langgraph.graph import Graph
E   ImportError: cannot import name 'Graph' from 'langgraph.graph' (d:\HandyWriterzAi\backend_env\Lib\site-packages\langgraph\graph\__init__.py). Did you mean: 'graph'?  
___________________ ERROR collecting backend/tests/test_utils.py ___________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_utils.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_utils.py:5: in <module>
    from utils.chartify import create_chart_svg
src\utils\chartify.py:2: in <module>
    from playwright.async_api import async_playwright
E   ModuleNotFoundError: No module named 'playwright'
_______________ ERROR collecting backend/tests/test_voice_upload.py ________________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\test_voice_upload.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_voice_upload.py:8: in <module>
    from main import app
src\main.py:82: in <module>
    from src.db.database import (
src\db\database.py:14: in <module>
    from .models import Base, User, Conversation, Document
src\db\models.py:11: in <module>
    from pgvector.sqlalchemy import Vector
E   ModuleNotFoundError: No module named 'pgvector'
_________ ERROR collecting backend/tests/unit/test_provider_validation.py __________ 
ImportError while importing test module 'D:\HandyWriterzAi\backend\tests\unit\test_provider_validation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\unit\test_provider_validation.py:7: in <module>
    from backend.scripts.validate_providers import ProviderValidator
E   ModuleNotFoundError: No module named 'backend'
================================= warnings summary ================================= 
..\backend_env\Lib\site-packages\pydantic\fields.py:1093: 32 warnings
  d:\HandyWriterzAi\backend_env\Lib\site-packages\pydantic\fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic 
V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

..\backend_env\Lib\site-packages\pydantic\_internal\_config.py:323
  d:\HandyWriterzAi\backend_env\Lib\site-packages\pydantic\_internal\_config.py:323: 
PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

src\services\prompt_orchestrator.py:161
  D:\HandyWriterzAi\backend\src\services\prompt_orchestrator.py:161: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    @validator('use_cases')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= short test summary info ==============================
ERROR src\tests\e2e\test_full_flow.py
ERROR src\tests\test_api.py
ERROR src\tests\test_autonomy_v2_basic.py
ERROR src\tests\test_autonomy_v2_vector.py
ERROR src\tests\test_autonomy_v2_worker_once.py
ERROR src\tests\test_chat_init_returns_trace_id.py
ERROR src\tests\test_memory_integration.py
ERROR src\tests\test_search_perplexity.py
ERROR src\tests\test_services.py
ERROR src\tests\test_source_filter.py
ERROR src\tests\test_turnitin_idempotency.py
ERROR src\tests\test_user_journey.py
ERROR src\tests\test_writer.py
ERROR tests\integration\test_memory_integration.py
ERROR tests\integration\test_model_config.py
ERROR tests\integration\test_sse_endpoints.py
ERROR tests\integration\test_streaming_client.py
ERROR tests\test_chunk_splitter_integration.py
ERROR tests\test_dissertation_journey.py
ERROR tests\test_e2e.py
ERROR tests\test_evidence_guard.py - AttributeError: module 'agent.nodes' has no attribute 'master_orchestrator'
ERROR tests\test_health.py
ERROR tests\test_memory_writer.py
ERROR tests\test_routing.py
ERROR tests\test_utils.py
ERROR tests\test_voice_upload.py
ERROR tests\unit\test_provider_validation.py
!!!!!!!!!!!!!!!!!!!!! Interrupted: 27 errors during collection !!!!!!!!!!!!!!!!!!!!! 
PS D:\HandyWriterzAi\backend> 
PS D:\HandyWriterzAi\backend> cd..      
PS D:\HandyWriterzAi> cd frontend
PS D:\HandyWriterzAi\frontend> pnpm install
Scope: all 2 workspace projects
Done in 19.5s using pnpm v10.8.0
PS D:\HandyWriterzAi\frontend> pnpm test

> handywriterz@0.1.0 test D:\HandyWriterzAi\frontend
> jest

 PASS  src/__tests__/smoke.test.tsx (16.579 s)
  smoke test
    √ renders a simple component (63 ms)

Test Suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Snapshots:   0 total
Time:        33.815 s, estimated 35 s
Ran all test suites.
PS D:\HandyWriterzAi\frontend> 
PS D:\HandyWriterzAi\frontend> pnpm dev

> handywriterz@0.1.0 dev D:\HandyWriterzAi\frontend
> next dev --turbo

   ▲ Next.js 15.4.2 (Turbopack)
   - Local:        http://localhost:3000
   - Network:      http://192.168.100.27:3000
   - Environments: .env.local, .env.development, .env
   - Experiments (use with caution):
     · turbo
     · optimizePackageImports

 ✓ Starting...
 ⚠ Invalid next.config.mjs options detected: 
 ⚠     Unrecognized key(s) in object: 'swcMinify'
 ⚠ See more info here: https://nextjs.org/docs/messages/invalid-next-config
 ⚠ The config property `experimental.turbo` is deprecated. Move this setting to `config.turbopack` as Turbopack is now stable.
 ✓ Ready in 158.8s
 ○ Compiling /chat ...
 ✓ Compiled /chat in 7.3s
 ○ Compiling /_error ...
 ✓ Compiled /_error in 686ms
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483654 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483655 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483653 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483652 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483658 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483659 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483660 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483661 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483663 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483662 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483665 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483666 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483668 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483667 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483670 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483671 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483673 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483672 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483675 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483676 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483678 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483677 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483680 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483681 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ✓ Compiled / in 3ms
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483683 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483682 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483685 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483686 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483688 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483687 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483690 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483691 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ✓ Compiled /settings in 14ms
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483693 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /settings/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483692 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /settings/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483695 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483696 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ✓ Compiled /settings/billing in 83ms
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483698 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /settings/billing/page 

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483697 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /settings/billing/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483700 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483701 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483703 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /settings/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483702 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /settings/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483705 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483706 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483708 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483707 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483710 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483711 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483713 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /settings/billing/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483712 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /settings/billing/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483715 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483716 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483718 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483717 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483720 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483721 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483723 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483722 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483725 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483726 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483729 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /settings/billing/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483728 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /settings/billing/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483731 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483732 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ✓ Compiled /_not-found/page in 154ms
 ⨯ [Error [TurbopackInternalError]: Failed to write app endpoint /_not-found/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483733 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /_not-found/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483734 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483735 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483736 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483738 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483737 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483740 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483741 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483743 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483742 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483745 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483746 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483748 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483747 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483750 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483751 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483753 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483752 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483755 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483756 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483758 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483757 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483760 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483761 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483763 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483762 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483765 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483766 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483768 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write app endpoint /chat/page

Caused by:
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483767 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /chat/page
- Execution of AppEndpoint::output failed
- Execution of AppEndpoint::app_page_entry failed
- Execution of *get_app_page_entry failed
- Execution of AppProject::rsc_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of *AppProject::get_rsc_transitions failed
- Execution of AppProject::ecmascript_client_reference_transition failed
- Execution of *NextEcmascriptClientReferenceTransition::new failed
- Execution of AppProject::client_transition failed
- Execution of *FullContextTransition::new failed
- Execution of AppProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of AppProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483770 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
[Error [TurbopackInternalError]: Failed to write page endpoint /_app

Caused by:
- content is not available as task execution failed
- content is not available as task execution failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root
Debug info:
- Execution of TaskId { id: 2147483771 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <PageEndpoint as Endpoint>::output failed
- Failed to write page endpoint /_app
- Execution of PageEndpoint::output failed
- Execution of PageEndpoint::client_chunks failed
- Execution of PageEndpoint::client_evaluatable_assets failed
- content is not available as task execution failed
- Execution of PageEndpoint::client_module failed
- content is not available as task execution failed
- Execution of *create_page_loader_entry_module failed
- Execution of PagesProject::client_module_context failed
- Execution of *ModuleAssetContext::new failed
- Execution of PagesProject::client_module_options_context failed
- Execution of *get_client_module_options_context failed
- Execution of Project::execution_context failed
- Execution of Project::node_root failed
- FileSystemPath("").join("../D:\HandyWriterzAi\frontend") leaves the filesystem root]
 ⨯ [Erro
 
 PS D:\HandyWriterzAi> cd backend
PS D:\HandyWriterzAi\backend> make install-deps
make: The term 'make' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS D:\HandyWriterzAi\backend> py -3.11 -m venv .venv
Unable to create process using 'C:\Python311\python.exe -m venv .venv': The system cannot find the file specified.

PS D:\HandyWriterzAi\backend> python -m pip install -r backend\requirements.txt
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'backend\\requirements.txt'
PS D:\HandyWriterzAi\backend> 


PS D:\HandyWriterzAi> cd frontend
PS D:\HandyWriterzAi\frontend> $env:PLAYWRIGHT_BASE_URL="http://localhost:3000"
PS D:\HandyWriterzAi\frontend> $env:PLAYWRIGHT_API_URL="http://localhost:8000" 
PS D:\HandyWriterzAi\frontend> $env:PLAYWRIGHT_NO_WEB_SERVER="1"
PS D:\HandyWriterzAi\frontend> pnpm test:e2e

> handywriterz@0.1.0 test:e2e D:\HandyWriterzAi\frontend
> playwright test


Running 69 tests using 2 workers

  ✘  1 …pload files + prompt -> POST /api/files -> POST /api/chat -> WS stream (1.7m)  ✘  2 …t End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (1.7m)  ✘  3 … Role routing: Researcher -> Perplexity, General -> OpenRouter default (1.8m)  ✘  4 …nd › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response (1.8m)  ✘  5 …ourneys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility (13.7s)  ✘  6 …fallback: invalid model or missing key -> user-facing error with retry (1.8m)  ✘  7 …Writerz User Journey Tests › Homepage loads and displays key elements (13.2s)  ✘  8 …38:7 › HandyWriterz User Journey Tests › Chat interface functionality (12.7s)  ✘  9 …iterz User Journey Tests › Settings page navigation and functionality (12.4s)  ✘  10 …7 › HandyWriterz User Journey Tests › Billing page and pricing tiers (13.8s)  ✓  11 …:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality (1.4s)  ✓  12 …s:135:7 › HandyWriterz User Journey Tests › File upload functionality (2.8s)
  ✘  13 …ey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check (1.5s)  ✓  14 …terz User Journey Tests › Payment flow simulation - Coinbase Commerce (1.2s)  ✓  15 …7 › HandyWriterz User Journey Tests › Responsive design - Mobile view (1.2s)  ✓  16 …2:7 › HandyWriterz User Journey Tests › Error handling and edge cases (2.0s)  ✓  17 … HandyWriterz User Journey Tests › Payment flow simulation - Paystack (1.0s)  ✓  18 …1:7 › HandyWriterz User Journey Tests › Performance and loading times (2.2s)  ✓  19 …8:7 › HandyWriterz User Journey Tests › Authentication state handling (3.5s)Page load time: 736ms
  ✘  20 …rney.spec.ts:308:7 › API Integration Tests › Backend health endpoint (526ms)  ✘  21 …er-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints (629ms)  ✘  22 …y.spec.ts:316:7 › API Integration Tests › API documentation endpoint (603ms)  ✘  23 …-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint (2.0s)  ✘  24 … End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (1.6m)  ✘  25 …load files + prompt -> POST /api/files -> POST /api/chat -> WS stream (1.6m)  ✘  26 …Role routing: Researcher -> Perplexity, General -> OpenRouter default (1.6m)  ✘  27 …d › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response (1.6m)  ✘  28 …allback: invalid model or missing key -> user-facing error with retry (1.9m)
  ✘  29 …urneys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility (23.1s)  ✘  30 …riterz User Journey Tests › Homepage loads and displays key elements (21.4s)  ✘  31 …8:7 › HandyWriterz User Journey Tests › Chat interface functionality (26.9s)  ✘  32 …terz User Journey Tests › Settings page navigation and functionality (21.7s)  ✓  33 …:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality (9.4s)  ✘  34 …7 › HandyWriterz User Journey Tests › Billing page and pricing tiers (19.4s)  ✓  35 …s:135:7 › HandyWriterz User Journey Tests › File upload functionality (4.5s)  ✘  36 …ey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check (3.6s)  ✓  37 …terz User Journey Tests › Payment flow simulation - Coinbase Commerce (6.9s)  ✓  38 … HandyWriterz User Journey Tests › Payment flow simulation - Paystack (9.9s)  ✓  39 …7 › HandyWriterz User Journey Tests › Responsive design - Mobile view (5.4s)  ✓  40 …2:7 › HandyWriterz User Journey Tests › Error handling and edge cases (5.4s)  ✓  41 …1:7 › HandyWriterz User Journey Tests › Performance and loading times (4.5s)Page load time: 1757ms
  ✓  42 …8:7 › HandyWriterz User Journey Tests › Authentication state handling (6.8s)  ✘  43 …urney.spec.ts:308:7 › API Integration Tests › Backend health endpoint (1.6s)  ✘  44 …ey.spec.ts:316:7 › API Integration Tests › API documentation endpoint (1.6s)  ✘  45 …ser-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints (1.5s)  ✘  46 …-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint (1.5s)  ✘  47 …load files + prompt -> POST /api/files -> POST /api/chat -> WS stream (1.5m)  ✘  48 … End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (1.5m)     49 …d-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response     50 …d › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default
