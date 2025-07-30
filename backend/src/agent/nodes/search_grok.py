import os
from typing import Dict, Any
from langchain_community.chat_models import ChatGrok
from ...agent.handywriterz_state import HandyWriterzState

class GrokSearchAgent:
    """A search agent that uses Grok for real-time information and social context."""

    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable not set.")
        self.model = ChatGrok(grok_api_key=self.api_key, temperature=0)

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the Grok search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = state.get("search_queries", [])[-1]
        prompt = f"Provide real-time information and social context for the following query. Query: {query}"
        
        response = await self.model.ainvoke(prompt)
        
        return {"raw_search_results": [{"source": "Grok", "content": response.content}]}
