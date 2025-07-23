import time
import logging
from typing import Dict, Any
from ...agent.handywriterz_state import HandyWriterzState
from src.services.model_service import get_model_service

logger = logging.getLogger(__name__)

class ClaudeSearchAgent:
    """A search agent that uses Anthropic's Claude model for analytical reasoning with dynamic model configuration."""

    def __init__(self):
        self.model_service = get_model_service()
        self.agent_name = "search_claude"
        self.model = None  # Will be loaded dynamically

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the Claude search agent with dynamic model loading.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        start_time = time.time()
        
        try:
            # Get dynamic model client
            model_client = await self.model_service.get_model_client(self.agent_name)
            if not model_client:
                logger.error(f"Failed to get model client for {self.agent_name}")
                raise ValueError(f"Model client not available for {self.agent_name}")
            
            # Get agent configuration for additional parameters
            agent_config = await self.model_service.get_agent_config(self.agent_name)
            
            query = state.get("search_queries", [])[-1] if state.get("search_queries") else ""
            if not query:
                return {"raw_search_results": [{"source": "Claude", "content": "No search query provided", "error": True}]}
            
            prompt = f"""Analyze the following query and provide a detailed, analytical response with synthesized insights.
            
Query: {query}

Please provide:
1. Deep analytical insights
2. Multiple perspectives on the topic
3. Evidence-based reasoning
4. Synthesized conclusions
5. Relevant academic or professional context"""
            
            # Execute with dynamic model
            response = await model_client.ainvoke(prompt)
            
            # Record usage metrics
            response_time = time.time() - start_time
            tokens_used = len(response.content.split()) * 1.3  # Rough estimate
            await self.model_service.record_usage(
                agent_name=self.agent_name,
                tokens_used=int(tokens_used),
                response_time=response_time
            )
            
            logger.info(f"Claude search completed in {response_time:.2f}s using model: {agent_config.model if agent_config else 'unknown'}")
            
            return {
                "raw_search_results": [{
                    "source": "Claude",
                    "content": response.content,
                    "model_used": agent_config.model if agent_config else "unknown",
                    "response_time": response_time,
                    "agent_name": self.agent_name
                }]
            }
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"Claude search agent failed after {error_time:.2f}s: {e}")
            
            return {
                "raw_search_results": [{
                    "source": "Claude",
                    "content": f"Search failed: {str(e)}",
                    "error": True,
                    "response_time": error_time,
                    "agent_name": self.agent_name
                }]
            }
