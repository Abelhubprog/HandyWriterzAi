import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from ...agent.handywriterz_state import HandyWriterzState

class OpenAISearchAgent:
    """A search agent that uses OpenAI's GPT-4 for general intelligence."""

    def __init__(self):
        self._model: Optional[ChatOpenAI] = None

    @property
    def model(self) -> ChatOpenAI:
        """Lazy initialization of OpenAI model."""
        if self._model is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for OpenAISearchAgent.")
            self._model = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=api_key)
        return self._model

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the OpenAI search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = state.get("search_queries", [])[-1]
        prompt = f"Provide a comprehensive and intelligent response to the following query. Query: {query}"
        
        response = await self.model.ainvoke(prompt)
        
        return {"raw_search_results": [{"source": "OpenAI", "content": response.content}]}
