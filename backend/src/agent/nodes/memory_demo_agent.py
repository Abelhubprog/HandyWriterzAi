"""Minimal memory demo agent to prove round-trip persistence."""

from typing import Dict, Any
from ..base import BaseNode
from ..base_agent import BaseAgent
from ..handywriterz_state import HandyWriterzState


class MemoryDemoAgent(BaseNode, BaseAgent):
    """Demo agent that demonstrates memory persistence capabilities."""

    def __init__(self):
        super().__init__("memory_demo", timeout_seconds=30.0, max_retries=2)

    async def receive_input(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Receive and validate input from the workflow state.

        Args:
            state: Current workflow state containing input data.

        Returns:
            Dictionary containing validated input data.
        """
        return {
            "user_id": state.get("user_id"),
            "conversation_id": state.get("conversation_id"),
            "user_prompt": state.get("user_params", {}).get("user_prompt", ""),
            "previous_memories": state.get("retrieved_memories", [])
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data to produce output.

        Args:
            input_data: Validated input data from receive_input.

        Returns:
            Dictionary containing processing results.
        """
        user_id = input_data["user_id"]
        conversation_id = input_data["conversation_id"]
        user_prompt = input_data["user_prompt"]
        previous_memories = input_data["previous_memories"]

        # Create a demo memory entry
        demo_memory_content = f"User interaction: {user_prompt}"
        if previous_memories:
            demo_memory_content += f" | Previous context: {len(previous_memories)} memories retrieved"

        return {
            "demo_memory_content": demo_memory_content,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "memory_type": "episodic"
        }

    async def emit_output(self, processed_data: Dict[str, Any], state: HandyWriterzState) -> Dict[str, Any]:
        """Emit processed data to update the workflow state.

        Args:
            processed_data: Results from the process method.
            state: Current workflow state to update.

        Returns:
            Dictionary of state updates to apply.
        """
        # In a real implementation, this would write to the memory service
        # For this demo, we'll just return the data to show it would be processed

        self._broadcast_progress(
            state,
            "Memory demo completed",
            100.0
        )

        return {
            "demo_memory_result": processed_data["demo_memory_content"],
            "memory_demo_complete": True,
            "memory_type": processed_data["memory_type"]
        }

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """Execute the memory demo agent."""
        # Use the new agent interface
        input_data = await self.receive_input(state)
        processed_data = await self.process(input_data)
        return await self.emit_output(processed_data, state)
