from typing import Optional
from ..core.state import GraphState


async def run(state: GraphState) -> GraphState:
    """Tool ingestor stub: not wired yet.

    TODO: Implement OpenAPI/MCP ingestion and dynamic tool registration.
    """
    state.notes.append("tool_ingestor: not implemented (stub)")
    return state


def ingest_openapi(url: str) -> Optional[str]:
    """Placeholder for OpenAPI ingestion.

    Returns an identifier for the registered tool, or None on stub.
    """
    # TODO: Implement in later prompt
    return None

