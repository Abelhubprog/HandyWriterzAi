from __future__ import annotations
from typing import Optional, Dict, Any


# NOTE: Stub Workbench bridge for human-in-the-loop fallback.
# Replace with ticketing system integration (e.g., Linear/Jira) and storage watchers.


class WorkbenchBridge:
    def create_ticket(self, title: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        job_id: str = "TEMP"
        if metadata:
            val = metadata.get("job_id")
            if isinstance(val, str) and val:
                job_id = val
        ticket_id: str = f"WB-{job_id}"
        print(f"[WorkbenchBridge] Created ticket {ticket_id}: {title}\n{description}")
        return ticket_id

    async def watch_uploads(self, ticket_id: str, timeout_sec: int = 900) -> Dict[str, Any]:
        # Simulate no manual upload; return empty. Real impl would poll a storage location or webhook.
        return {"ticket_id": ticket_id, "status": "no_upload_detected"}
