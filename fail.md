web3aible@WEB3AIBLE:/mnt/d/HandyWriterzAi$ source .venv/bin/activate && python backend/start_server.py
🔍 Importing real HandyWriterz multi-agent LangGraph system...
📂 Current directory: /mnt/d/HandyWriterzAi/backend
📂 Source path: /mnt/d/HandyWriterzAi/backend/src
2025-08-15 23:38:35,314 - src.models.factory - INFO - ✅ Gemini provider initialized
2025-08-15 23:38:35,644 - src.models.factory - INFO - ✅ OpenAI provider initialized
2025-08-15 23:38:35,880 - src.models.factory - INFO - ✅ Anthropic provider initialized
2025-08-15 23:38:36,215 - src.models.factory - INFO - ✅ Perplexity provider initialized
2025-08-15 23:38:36,215 - src.models.factory - INFO - 🔧 Initialized 4 AI providers: ['gemini', 'openai', 'anthropic', 'perplexity']
2025-08-15 23:38:36,215 - src.models.factory - INFO - 🎯 Role mappings configured: {<ModelRole.JUDGE: 'judge'>: 'anthropic', <ModelRole.LAWYER: 'lawyer'>: 'anthropic', <ModelRole.RESEARCHER: 'researcher'>: 'perplexity', <ModelRole.WRITER: 'writer'>: 'anthropic', <ModelRole.REVIEWER: 'reviewer'>: 'anthropic', <ModelRole.SUMMARIZER: 'summarizer'>: 'openai', <ModelRole.GENERAL: 'general'>: 'anthropic'}
2025-08-15 23:38:36,216 - src.main - INFO - 🤖 Multi-provider AI system initialized      
2025-08-15 23:38:54,437 - src.main - INFO - ✅ Simple system permanently disabled - using 
advanced system only
2025-08-15 23:40:23,813 - src.unified_processor - INFO - ℹ️ Simple Gemini system not avai
lable: No module named 'src.agent.graph'
2025-08-15 23:40:23,995 - src.unified_processor - WARNING - ⚠️ Advanced HandyWriterz syst
em not available: No module named 'src.handywriterz_state'
2025-08-15 23:40:24,879 - src.services.model_service - INFO - Config not found at 'src/config/model_config.yaml', using fallback '/mnt/d/HandyWriterzAi/backend/src/config/model_config.yaml'
2025-08-15 23:40:25,038 - src.services.model_service - INFO - Config not found at 'src/config/price_table.json', using fallback '/mnt/d/HandyWriterzAi/backend/src/config/price_table.json'
2025-08-15 23:40:30,187 - src.services.security_service - INFO - No ENCRYPTION_KEY found; generated ephemeral key for this process
2025-08-15 23:40:30,188 - src.services.security_service - INFO - Revolutionary Security Service initialized
2025-08-15 23:41:01,471 - src.services.embedding_service - INFO - Revolutionary Embedding Service initialized
Traceback (most recent call last):
  File "/mnt/d/HandyWriterzAi/backend/start_server.py", line 26, in <module>
    from src.main import app
  File "/mnt/d/HandyWriterzAi/backend/src/main.py", line 94, in <module>
    from src.routes.chat_gateway import chat_gateway_router
  File "/mnt/d/HandyWriterzAi/backend/src/routes/chat_gateway.py", line 217, in <module>
    @chat_gateway_router.post("/complete", response_model=ChatResponse)
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 995, in decorator
    self.add_api_route(
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 934, in add_api_route
    route = route_class(
            ^^^^^^^^^^^^
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 555, in __init__
    self.dependant = get_dependant(path=self.path_format, call=self.endpoint)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 285, in get_dependant
    param_details = analyze_param(
                    ^^^^^^^^^^^^^^
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 488, in analyze_param
    field = create_model_field(
            ^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/HandyWriterzAi/.venv/lib/python3.12/site-packages/fastapi/utils.py", line 
98, in create_model_field
    raise fastapi.exceptions.FastAPIError(
fastapi.exceptions.FastAPIError: Invalid args for response field! Hint: check that typing.Optional[fastapi.background.BackgroundTasks] is a valid Pydantic field type. If you are 
using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation with the path operation decorator parameter response_model=None. Read more: https://fastapi.tiangolo.com/tutorial/response-model/
(.venv) web3aible@WEB3AIBLE:/mnt/d/HandyWriterzAi$ 