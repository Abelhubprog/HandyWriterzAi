import uuid
import logging
from typing import Any, Dict, Optional
from sqlalchemy import text

from ..core.state import GraphState
from ..memory.episodic_repo import EpisodicRepo

logger = logging.getLogger(__name__)


def _get_db_manager():
    try:
        from backend.src.db.database import get_db_manager  # type: ignore
        return get_db_manager()
    except Exception as e:  # pragma: no cover
        logger.warning(f"TurnitinCoordinator DB unavailable: {e}")
        return None


async def handoff(state: GraphState) -> GraphState:
    """Create a HITL cycle and upload the current artifact to Workbench.

    Sets route to 'turnitin_pause' after recording the cycle. No direct Turnitin calls.
    """
    await EpisodicRepo(run_id=state.run_id).append({
        "run_id": state.run_id,
        "role": "note",
        "content": {"event": "turnitin_handoff_start"},
    })

    dbm = _get_db_manager()
    artifact_id: Optional[str] = None
    try:
        if dbm is not None:
            # Create a minimal Workbench assignment and artifact representing the draft
            from src.db.repositories.workbench_assignment_repo import WorkbenchAssignmentRepository  # type: ignore
            from src.db.repositories.workbench_artifact_repo import WorkbenchArtifactRepository  # type: ignore
            from src.db.models import WorkbenchDeliveryChannel, WorkbenchArtifactType  # type: ignore

            with dbm.get_db_context() as session:
                assignment_repo = WorkbenchAssignmentRepository(session)
                artifact_repo = WorkbenchArtifactRepository(session)

                tenant_id = uuid.uuid4()
                user_id = uuid.uuid4()

                assignment = assignment_repo.create(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    source_conversation_id=None,
                    title=f"AutonomyV2 run {state.run_id}",
                    requirements={"note": "turnitin handoff"},
                    delivery_channel=WorkbenchDeliveryChannel.WORKBENCH,
                    telegram_message_ref=None,
                    ai_metadata={"run_id": state.run_id}
                )

                object_key = f"autonomy_v2/{state.run_id}/draft.txt"
                artifact = artifact_repo.create(
                    assignment_id=assignment.id,
                    submission_id=None,
                    artifact_type=WorkbenchArtifactType.OTHER,
                    storage_provider="local",
                    object_key=object_key,
                    size_bytes=len((state.last_observation or {}).get("output", "") or ""),
                    mime_type="text/plain",
                    checksum_sha256=None,
                    metadata={"run_id": state.run_id}
                )
                artifact_id = str(getattr(artifact, "id", None))

            # Record a cycle entry
            target = None
            try:
                from src.config import get_settings  # type: ignore
                s = get_settings()
                target = float(state.task.get("target_similarity", getattr(s, "turnitin_target_default", 0.15)))
            except Exception:
                target = float(state.task.get("target_similarity", 0.15))

            with dbm.get_db_context() as session:
                session.execute(text(
                    """
                    INSERT INTO autonomy_turnitin_cycles
                    (run_id, artifact_id, status, target_similarity, observed_similarity, report_path, human_uploader_id)
                    VALUES (:run_id, :artifact_id, :status, :target, NULL, NULL, NULL)
                    """
                ), {
                    "run_id": state.run_id,
                    "artifact_id": artifact_id or "",
                    "status": "awaiting_report",
                    "target": target,
                })
                # Fetch cycle id of the latest entry for this run
                q = session.execute(text(
                    "SELECT id FROM autonomy_turnitin_cycles WHERE run_id = :run ORDER BY created_at DESC LIMIT 1"
                ), {"run": state.run_id})
                row = q.fetchone()
                if row:
                    cycle_id = int(dict(row._mapping)["id"])  # type: ignore
                else:
                    cycle_id = None
    except Exception as e:  # pragma: no cover
        logger.warning(f"Turnitin handoff best-effort failed: {e}")

    await EpisodicRepo(run_id=state.run_id).append({
        "run_id": state.run_id,
        "role": "note",
        "content": {"event": "turnitin_handoff_complete", "artifact_id": artifact_id, "cycle_id": locals().get("cycle_id")},
    })

    state.route = "turnitin_pause"
    return state
