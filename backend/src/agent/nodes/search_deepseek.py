import os
from typing import Dict, Any
from langchain_community.chat_models import ChatDeepseek
from ...agent.handywriterz_state import HandyWriterzState

class DeepseekSearchAgent:
    """A search agent that uses Deepseek for technical and coding expertise."""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set.")
        self.model = ChatDeepseek(model="deepseek-coder", api_key=self.api_key, temperature=0)

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the Deepseek search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = state.get("search_queries", [])[-1]
        prompt = f"Provide a technical analysis or code-based solution for the following query. Query: {query}"
        
        response = await self.model.ainvoke(prompt)
        
        return {"raw_search_results": [{"source": "Deepseek", "content": response.content}]}
