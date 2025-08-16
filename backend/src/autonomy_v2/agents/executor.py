from typing import Any, Dict, List
from ..core.state import GraphState
from ..core.llm import complete
from ..tools.registry import choose_tool
from ..memory.vector_repo import VectorRepo
from ..tools.web_search import search as web_search


async def run(state: GraphState) -> GraphState:
    """Execute next step via registry tool and record observation."""
    # Select first undone step
    step: Dict[str, Any] = next((s for s in state.plan if not s.get("done")), None) if state.plan else None
    if not step:
        # Nothing to do; emit simple output
        prompt = str(state.task.get("goal", "")) or "Proceed"
        output = complete([{"role": "user", "content": prompt}])
        state.last_observation = {"output": output, "sources": []}
        state.notes.append("executor: no step; produced fallback output")
    else:
        kind = str(step.get("kind", "research"))
        query = str(state.task.get("goal", "")) or step.get("description", "")
        sources: List[str] = []

        if kind == "research":
            # Check vector memory first
            try:
                repo = VectorRepo(run_id=state.run_id)
                mem_results = await repo.search(query, k=3)
            except Exception:
                mem_results = []
            if not mem_results:
                # Web search and upsert
                results = web_search(query, k=3)
                chunks = [{"text": f"{r.get('title','')}. {r.get('snippet','')}", "url": r.get("url", "")} for r in results]
                try:
                    await repo.upsert_chunks(chunks)
                except Exception:
                    pass
                sources = [r.get("url", "") for r in results]
                output = f"researched {len(sources)} sources"
            else:
                sources = [r.get("url", "") for r in mem_results]
                output = f"retrieved {len(sources)} sources from memory"
        else:
            tool = choose_tool(kind)
            try:
                result = tool(query=query, k=3)  # web_search adapter expects query,k
            except TypeError:
                result = tool(query)  # echo or simpler signature
            sources = result.get("sources", []) if isinstance(result, dict) else []
            output = result.get("output", "ok") if isinstance(result, dict) else str(result)

        state.last_observation = {"output": output, "sources": sources}
        step["done"] = True
        state.notes.append(f"executor: ran {kind} with {len(sources)} sources")
    # Route to reflect
    state.route = "reflect"
    return state
