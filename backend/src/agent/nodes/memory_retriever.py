from typing import Dict, Any
from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from ...services.memory_integrator import get_memory_integrator

class MemoryRetrieverNode(BaseNode):
    """Enhanced memory retriever node using the MemoryIntegrator service."""

    def __init__(self):
        super().__init__("memory_retriever", timeout_seconds=30.0, max_retries=2)
        self.memory_service = get_memory_integrator()

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the enhanced memory retriever node.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the retrieved memory context.
        """
        user_id = state.get("user_id")
        if not user_id:
            return {"long_term_memory": None}

        # Extract query context from state
        user_params = state.get("user_params", {})
        query_context = user_params.get("user_prompt", "") or user_params.get("prompt", "")
        
        if not query_context:
            # Use current draft or research agenda as context
            query_context = state.get("current_draft", "") or str(state.get("research_agenda", ""))
        
        if query_context:
            # Retrieve relevant memories
            memories = await self.memory_service.retrieve_memories(
                user_id=user_id,
                query=query_context,
                conversation_id=state.get("conversation_id"),
                k=5,  # Retrieve top 5 memories
                importance_threshold=0.4
            )
            
            # Format for backward compatibility
            memory_content = "\n".join([m["content"] for m in memories])
            
            return {
                "long_term_memory": memory_content,
                "retrieved_memories": memories,
                "memory_count": len(memories)
            }
        
        return {"long_term_memory": None}