from typing import Dict, Any, List
from ..core.state import GraphState
from ..tools.web_search import search as web_search
from ..memory.vector_repo import VectorRepo


async def run(state: GraphState) -> GraphState:
    """Do initial research: search web, upsert into vector store, and annotate sources."""
    goal = str(state.task.get("goal", "")).strip()
    results = web_search(goal, k=5)
    # Upsert chunks into vector memory
    chunks = [{"text": f"{r.get('title','')}. {r.get('snippet','')}", "url": r.get("url", "")} for r in results]
    try:
        repo = VectorRepo(run_id=state.run_id)
        await repo.upsert_chunks(chunks)
    except Exception:
        pass
    # Set observation with sources
    urls: List[str] = [r.get("url", "") for r in results]
    state.last_observation = {"output": f"gathered {len(urls)} sources", "sources": urls}
    state.notes.append(f"researcher: upserted {len(urls)} sources")
    # Route back to act
    state.route = "act"
    return state
