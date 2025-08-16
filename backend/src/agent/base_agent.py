"""Base agent class ensuring consistent interface across all agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.agent.handywriterz_state import HandyWriterzState


class BaseAgent(ABC):
    """Base class ensuring all agents have consistent interface."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def receive_input(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Receive and validate input from the workflow state.

        Args:
            state: Current workflow state containing input data.

        Returns:
            Dictionary containing validated input data.
        """
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data to produce output.

        Args:
            input_data: Validated input data from receive_input.

        Returns:
            Dictionary containing processing results.
        """
        pass

    @abstractmethod
    async def emit_output(self, processed_data: Dict[str, Any], state: HandyWriterzState) -> Dict[str, Any]:
        """Emit processed data to update the workflow state.

        Args:
            processed_data: Results from the process method.
            state: Current workflow state to update.

        Returns:
            Dictionary of state updates to apply.
        """
        pass

    async def execute_agent(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Execute the complete agent workflow: receive → process → emit.

        Args:
            state: Current workflow state.

        Returns:
            Dictionary of state updates to apply.
        """
        # Receive and validate input
        input_data = await self.receive_input(state)

        # Process the input data
        processed_data = await self.process(input_data)

        # Emit output to update state
        output_data = await self.emit_output(processed_data, state)

        return output_data
