
from typing import Any
from src.agent.base import BaseNode

class SourceFallbackController(BaseNode):
    def __init__(self):
        super().__init__("source_fallback_controller")

    async def execute(self, state: dict, config: Any) -> dict:
        if state.get("need_fallback"):
            params = state.get("params", {})
            fallback_attempts = state.get("fallback_attempts", 0)

            if fallback_attempts == 0:
                # First fallback: widen year span
                params["year_from"] = params.get("year_from", 2018) - 2
                state["params"] = params
                state["fallback_attempts"] = 1
                state["need_fallback"] = False # Reset for the next attempt
            elif fallback_attempts == 1:
                # Second fallback: change evidence design (if possible)
                if "design" in params:
                    del params["design"]
                state["params"] = params
                state["fallback_attempts"] = 2
                state["need_fallback"] = False # Reset for the next attempt
            else:
                # Max fallbacks reached
                state["error_message"] = "Could not find enough sources, even after fallback."
                state["workflow_status"] = "failed"

        return state
