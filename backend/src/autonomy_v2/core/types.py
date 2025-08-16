from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    """Describes a goal-oriented task the agents should complete."""
    goal: str
    constraints: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    budget_tokens: int = 200_000
    budget_seconds: int = 900


class PlanStep(BaseModel):
    """A single step in a task plan, possibly dependent on previous steps."""
    id: str
    kind: Literal["research", "write", "code", "evaluate", "tool"]
    description: str
    depends_on: List[str] = Field(default_factory=list)
    done: bool = False


class Action(BaseModel):
    """An action to perform via a tool/agent."""
    step_id: str
    tool: str
    input: Dict[str, Any]


class Observation(BaseModel):
    """Result of an action execution."""
    step_id: str
    output: Any
    error: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class Verdict(BaseModel):
    """Critic evaluation after an observation."""
    step_id: str
    status: Literal["pass", "retry", "patch", "branch", "fail"]
    notes: str

