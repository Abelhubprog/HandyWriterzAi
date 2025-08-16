from ..core.state import GraphState
from ..core.state import GraphState
from typing import Any
import logging

logger = logging.getLogger(__name__)


async def run(state: GraphState) -> GraphState:
    """Critic: END if sources present; else route back to plan."""
    obs = state.last_observation or {}
    sources = obs.get("sources") or []
    if isinstance(sources, list) and len(sources) > 0:
        # If policy requires Turnitin, request handoff instead of END
        need_turnitin = False
        try:
            from src.config import get_settings  # type: ignore
            s = get_settings()
            # Treat presence of default as policy enabled
            if getattr(s, "turnitin_target_default", None) is not None:
                need_turnitin = True
        except Exception:
            pass
        if state.task.get("target_similarity") is not None:
            need_turnitin = True

        if need_turnitin:
            # If a completed cycle exists with satisfactory similarity, END
            try:
                from sqlalchemy import text  # type: ignore
                from src.db.database import get_db_manager  # type: ignore
                dbm = get_db_manager()
                with dbm.get_db_context() as session:
                    row = session.execute(text(
                        """
                        SELECT target_similarity, observed_similarity, status
                        FROM autonomy_turnitin_cycles
                        WHERE run_id = :run
                        ORDER BY created_at DESC
                        LIMIT 1
                        """
                    ), {"run": state.run_id}).fetchone()
                    if row:
                        target = float((row[0] if row[0] is not None else state.task.get("target_similarity") or 0.15))
                        observed = row[1]
                        status = str(row[2] or "")
                        if status == "report_ready" and observed is not None and float(observed) <= target:
                            state.notes.append("critic: similarity OK; END")
                            state.route = "END"
                            return state
            except Exception:
                pass
            state.notes.append("critic: sources found; requesting turnitin handoff")
            state.route = "turnitin"
        else:
            state.notes.append("critic: pass (sources found)")
            state.route = "END"
    else:
        state.notes.append("critic: no sources; back to plan")
        state.route = "plan"
    return state
