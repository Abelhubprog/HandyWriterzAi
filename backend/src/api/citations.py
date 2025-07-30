from fastapi import APIRouter
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
from typing import Dict, Any
from utils.csl import format_citations

router = APIRouter(
    prefix="/api",
    tags=["citations"],
)

@router.post("/citations")
def reformat_citations(style: str, csl_json: list) -> Dict[str, Any]:
    """
    Reformats citations and a bibliography based on a new CSL style.
    """
    with tracer.start_as_current_span("reformat_citations") as span:
        span.set_attribute("citation_style", style)
        span.set_attribute("item_count", len(csl_json))
    # In a real application, you would fetch the draft and its CSL JSON
    # from the database based on a document ID.
    
    return format_citations(csl_json, style)