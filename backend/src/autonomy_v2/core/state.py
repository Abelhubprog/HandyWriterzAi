from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphState(BaseModel):
    """Minimal LangGraph-compatible state for Autonomy V2.

    This is intentionally small and safe. Additional fields can be added later.
    """
    run_id: str
    user_id: Optional[str] = None
    task: Dict[str, Any] = Field(default_factory=dict)
    plan: List[Dict[str, Any]] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    route: str = "plan"  # next route: plan, act, reflect, expand, repair, END
    last_observation: Optional[Dict[str, Any]] = None
    # Budget counters (informational only for now)
    budget_tokens: int = 0
    budget_seconds: int = 0
    budget_usd: float = 0.0
