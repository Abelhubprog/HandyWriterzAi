from typing import List
from ..core.state import GraphState
from ..core.types import PlanStep
from ..core.prompts import PLANNER_SYSTEM_PROMPT
from ..core.llm import json_call


async def run(state: GraphState) -> GraphState:
    """Produce a minimal plan using LLM JSON if available, else fallback."""
    if not state.plan:
        goal = str(state.task.get("goal", "")).strip()
        user_prompt = (
            "Goal: " + goal + "\nReturn JSON array of 1-3 steps with fields: id, kind in ['research','write','evaluate'], description."
        )
        try:
            steps = json_call(PLANNER_SYSTEM_PROMPT, user_prompt, node_name="autonomy_v2_planner", run_id=state.run_id)
            if isinstance(steps, list) and steps:
                normalized: List[PlanStep] = []
                for i, s in enumerate(steps[:3]):
                    try:
                        normalized.append(PlanStep(
                            id=str(s.get("id") or f"step-{i+1}"),
                            kind=str(s.get("kind") or "research"),
                            description=str(s.get("description") or goal or "Do research")
                        ))
                    except Exception:
                        continue
                if normalized:
                    state.plan = [p.model_dump() for p in normalized]
        except Exception:
            # Fallback below
            pass

        if not state.plan:
            step = PlanStep(id="step-1", kind="research", description="Collect initial context").model_dump()
            state.plan = [step]
        state.notes.append("planner: plan ready")
    # Always route to act next
    state.route = "act"
    return state
