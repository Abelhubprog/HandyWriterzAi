import os
from typing import Dict, Any
from langchain_community.chat_models import ChatQwen
from ...agent.handywriterz_state import HandyWriterzState

class QwenSearchAgent:
    """A search agent that uses Qwen for multilingual capabilities."""

    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable not set.")
        self.model = ChatQwen(model="qwen-turbo", qwen_api_key=self.api_key, temperature=0)

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the Qwen search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = state.get("search_queries", [])[-1]
        prompt = f"Provide a multilingual analysis or translation for the following query. Query: {query}"
        
        response = await self.model.ainvoke(prompt)
        
        return {"raw_search_results": [{"source": "Qwen", "content": response.content}]}
