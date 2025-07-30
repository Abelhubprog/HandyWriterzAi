from typing import List, Literal
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=16000)
    mode: Literal[
        "general","essay","report","dissertation","case_study","case_scenario",
        "critical_review","database_search","reflection","document_analysis",
        "presentation","poster","exam_prep"
    ]
    file_ids: List[str] = Field(default_factory=list)
    user_params: dict = Field(default_factory=dict)

class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str

class ChatResponse(BaseModel):
    trace_id: str
    response: str
    sources: List[SourceItem]
    quality_score: float
    workflow: str
    cost_usd: float
