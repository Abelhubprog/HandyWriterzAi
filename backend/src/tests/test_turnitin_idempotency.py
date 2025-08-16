import asyncio
from sqlalchemy import text

from backend.src.api.autonomy_v2 import turnitin_report_webhook, TurnitinWebhook
from backend.src.autonomy_v2.runtime.queue import enqueue_resume
from backend.src.db.database import get_db_manager


def test_turnitin_webhook_idempotent():
    run_id = "v2-idem"
    dbm = get_db_manager()
    # Insert a cycle row in awaiting_report
    with dbm.get_db_context() as session:
        session.execute(text(
            "INSERT INTO autonomy_turnitin_cycles (run_id, artifact_id, status, target_similarity) VALUES (:r, :a, 'awaiting_report', :t)"
        ), {"r": run_id, "a": "artifact-x", "t": 0.15})
        row = session.execute(text(
            "SELECT id FROM autonomy_turnitin_cycles WHERE run_id=:r ORDER BY created_at DESC LIMIT 1"
        ), {"r": run_id}).fetchone()
        cycle_id = int(row[0])

    payload = TurnitinWebhook(cycle_id=cycle_id, report_url="https://example.com/r.pdf", observed_similarity=0.08)
    # First call enqueues
    out1 = asyncio.get_event_loop().run_until_complete(turnitin_report_webhook(run_id, payload))
    jid1 = out1.get("job_id")
    assert jid1 is not None
    # Second call returns ok without enqueueing new job
    out2 = asyncio.get_event_loop().run_until_complete(turnitin_report_webhook(run_id, payload))
    jid2 = out2.get("job_id")
    assert jid2 == jid1 or jid2 is None

