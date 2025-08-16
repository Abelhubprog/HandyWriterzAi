from backend.src.autonomy_v2.runtime.checkpointer_sql import seed
from backend.src.autonomy_v2.core.state import GraphState
from backend.src.autonomy_v2.runtime.queue import enqueue_start
from backend.src.workers.autonomy_v2_worker import process_once


def test_worker_process_once_turnitin_pause():
    run_id = "v2-worker-once"
    # Seed a run that will trigger turnitin (has target_similarity)
    state = GraphState(
        run_id=run_id,
        task={"goal": "test run", "target_similarity": 0.15},
        plan=[],
        notes=["seeded"],
        route="plan",
        last_observation=None,
        budget_tokens=0,
        budget_seconds=0,
    )
    seed(run_id, state.model_dump())
    enqueue_start(run_id, user_id="user-xyz", journey="write")

    # Process one job; it should either pause for HITL or finish
    processed = process_once()
    assert processed is True

