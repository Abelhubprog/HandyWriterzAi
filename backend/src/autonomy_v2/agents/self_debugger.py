from ..core.state import GraphState


async def run(state: GraphState) -> GraphState:
    """Self-debugging stub: no-op and route to plan for now."""
    state.notes.append("self_debugger: no-op (stub)")
    state.route = "plan"
    return state

