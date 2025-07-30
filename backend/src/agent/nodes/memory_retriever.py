from typing import Dict, Any
from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from src.services.supabase_service import SupabaseService

class MemoryRetrieverNode(BaseNode):
    """A node that retrieves a user's long-term memory from Supabase."""

    def __init__(self):
        super().__init__("memory_retriever", timeout_seconds=30.0, max_retries=2)
        self.supabase_service = SupabaseService()

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the memory retriever node.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the retrieved memory.
        """
        user_id = state.get("user_id")
        if not user_id:
            return {"long_term_memory": None}

        memory = await self.supabase_service.get_user_memory(user_id)
        
        return {"long_term_memory": memory}