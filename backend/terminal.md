web3aible@WEB3AIBLE:/mnt/d/HandyWriterzAi$ source .venv/bin/activate && python backend/stweb3aible@WEB3AIBLE:/mnt/d/HandyWriterzAi$ source .venv/bin/activate && python backend/start_server.py
🔍 Importing real HandyWriterz multi-agent LangGraph system...
📂 Current directory: /mnt/d/HandyWriterzAi/backend
📂 Source path: /mnt/d/HandyWriterzAi/backend/src
2025-08-16 00:36:03,118 - src.models.factory - INFO - ✅ Gemini provider initialized
2025-08-16 00:36:03,530 - src.models.factory - INFO - ✅ OpenAI provider initialized
2025-08-16 00:36:03,630 - src.models.factory - INFO - ✅ Anthropic provider initialized
2025-08-16 00:36:03,725 - src.models.factory - INFO - ✅ Perplexity provider initialized  
2025-08-16 00:36:03,725 - src.models.factory - INFO - 🔧 Initialized 4 AI providers: ['gemini', 'openai', 'anthropic', 'perplexity']
2025-08-16 00:36:03,725 - src.models.factory - INFO - 🎯 Role mappings configured: {<ModelRole.JUDGE: 'judge'>: 'anthropic', <ModelRole.LAWYER: 'lawyer'>: 'anthropic', <ModelRole.RESEARCHER: 'researcher'>: 'perplexity', <ModelRole.WRITER: 'writer'>: 'anthropic', <ModelRole.REVIEWER: 'reviewer'>: 'anthropic', <ModelRole.SUMMARIZER: 'summarizer'>: 'openai', <ModelRole.GENERAL: 'general'>: 'anthropic'}
2025-08-16 00:36:03,725 - src.main - INFO - 🤖 Multi-provider AI system initialized      
2025-08-16 00:38:07,285 - src.main - INFO - ✅ Simple system permanently disabled - using 
advanced system only
Traceback (most recent call last):
  File "/mnt/d/HandyWriterzAi/backend/start_server.py", line 26, in <module>
    from src.main import app
  File "/mnt/d/HandyWriterzAi/backend/src/main.py", line 76, in <module>
    from src.agent.routing.unified_processor import UnifiedProcessor
  File "/mnt/d/HandyWriterzAi/backend/src/agent/routing/__init__.py", line 10, in <module>
    from .unified_processor import UnifiedProcessor
  File "/mnt/d/HandyWriterzAi/backend/src/agent/routing/unified_processor.py", line 110, 
in <module>
    from ..handywriterz_graph import handywriterz_graph
  File "/mnt/d/HandyWriterzAi/backend/src/agent/handywriterz_graph.py", line 12, in <module>
    from .nodes.user_intent import UserIntentNode
  File "/mnt/d/HandyWriterzAi/backend/src/agent/nodes/user_intent.py", line 13, in <module>
    from ..base_agent import BaseAgent
  File "/mnt/d/HandyWriterzAi/backend/src/agent/base_agent.py", line 5, in <module>      
    from ..handywriterz_state import HandyWriterzState
ModuleNotFoundError: No module named 'src.handywriterz_state'
(.venv) web3aible@WEB3AIBLE:/mnt/d/HandyWriterzAi$ 