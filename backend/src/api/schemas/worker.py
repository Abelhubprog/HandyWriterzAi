from typing import List
from pydantic import BaseModel, Field

class ModelOverride(BaseModel):
    model_id: str = Field(pattern=r"^[\w\-/]+$")

class ChunkMessage(BaseModel):
    doc_id: str
    chunk_id: int
    text: str
    embedding: List[float]
