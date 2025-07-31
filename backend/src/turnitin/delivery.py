from __future__ import annotations
import json
import os
from typing import Optional, Dict, Any
import urllib.request
from dataclasses import asdict, is_dataclass
from .models import JobMetadata, Manifest

# NOTE: Stub delivery that posts manifest to a webhook if configured,
# and logs an "email" send to stdout. Replace with real HTTP client and email provider.


class DeliveryAgent:
    def __init__(self) -> None:
        self.webhook_url = os.getenv("TURNITIN_WEBHOOK_URL")
        self.email_from = os.getenv("TURNITIN_EMAIL_FROM", "noreply@handywriterz.ai")

    def _post_webhook(self, payload: Dict[str, Any]) -> Optional[int]:
        if not self.webhook_url:
            return None
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode()

    def _send_email_stub(self, to_email: str, subject: str, body: str) -> None:
        # Replace with SES/SendGrid integration
        print(f"[DeliveryAgent] Email to={to_email} from={self.email_from} subject={subject}\n{body}")

    def deliver(self, job: JobMetadata, manifest: Manifest) -> None:
        job_payload: Dict[str, Any] = asdict(job) if is_dataclass(job) else getattr(job, "dict", lambda: {} )()
        manifest_payload: Dict[str, Any] = asdict(manifest) if is_dataclass(manifest) else getattr(manifest, "dict", lambda: {} )()

        payload: Dict[str, Any] = {
            "job": job_payload,
            "manifest": manifest_payload,
        }
        code = self._post_webhook(payload)
        notify_email = getattr(job, "notify_email", None)
        job_id = job_payload.get("job_id") if job_payload else None
        if notify_email:
            subj = f"Turnitin Report Ready · Job {job_id or 'N/A'}"
            body = f"Your Turnitin reports are ready.\n\nManifest:\n{json.dumps(manifest_payload, indent=2)}"
            self._send_email_stub(str(notify_email), subj, body)
        print(f"[DeliveryAgent] Delivery complete. webhook_status={code}")
