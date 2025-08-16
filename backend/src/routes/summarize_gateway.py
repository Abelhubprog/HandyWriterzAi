"""
API Endpoint for the Summarization Swarm.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..auth.auth import get_current_user
from ..agent.handywriterz_state import HandyWriterzState
from ..agent.nodes.summarization_swarm import SummarizerNode

summarize_gateway_router = APIRouter(prefix="/api/summarize", tags=["summarize", "gateway"])

# Pydantic Models
class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    text: str = Field(..., min_length=50, description="The text to be summarized.")
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    summary: str
    trace_id: str

# Summarization Endpoint
@summarize_gateway_router.post("/", response_model=SummarizeResponse)
async def summarize_text(
    request: SummarizeRequest,
    user: dict = Depends(get_current_user)
):
    """
    Receives text and uses the Summarization Swarm to generate a summary.
    """
    try:
        # 1. Initialize the summarizer node
        summarizer_node = SummarizerNode()

        # 2. Set up the initial state for the workflow
        initial_state = HandyWriterzState(
            text_to_summarize=request.text,
            user_id=user.get("id"),
            trace_id=request.trace_id
        )

        # 3. Execute the node
        # The config parameter is optional and not needed here
        result_state = await summarizer_node.execute(state=initial_state)

        # 4. Extract the summary from the result
        summaries = result_state.get("summaries", [])
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Summarization failed to produce a result."
            )

        return SummarizeResponse(
            summary=summaries[0],
            trace_id=request.trace_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during summarization: {str(e)}"
        )
