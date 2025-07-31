import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from .models import JobMetadata, Preferences, Artifacts, Manifest, SessionStatus
from .telegram_session import TelegramSessionAgent
from .bot_conversation import BotConversationAgent
from .delivery import DeliveryAgent


class TurnitinOrchestrator:
    """
    Durable orchestrator for Turnitin workflow:
      DocumentFinalized -> EnsureSession -> BotConversation -> Delivery -> Audit
    """

    def __init__(self):
        self.session_agent = TelegramSessionAgent()
        self.conversation_agent = BotConversationAgent()
        self.delivery_agent = DeliveryAgent()

    async def start_turnitin_check(
        self,
        job: JobMetadata,
        input_doc_uri: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Manifest:
        """
        Entry point. Ensures session, submits document, collects reports, and delivers.

        Args:
            job: Job metadata including preferences, callback_url, email_to
            input_doc_uri: storage URI to .docx
            extra: optional dict for additional context

        Returns:
            Manifest with artifact URIs, hashes, sizes, and summary.
        """
        # 1) Ensure Telegram session
        session: SessionStatus = await self.session_agent.ensure_session()
        if not session.healthy:
            raise RuntimeError(f"Telegram session not healthy: {session.reason or 'unknown'}")

        # 2) Drive bot conversation to submit and collect reports
        artifacts = Artifacts(input_doc_uri=input_doc_uri)
        artifacts = await self.conversation_agent.submit_and_collect(
            input_doc_uri=input_doc_uri,
            preferences=job.preferences,
            artifacts=artifacts,
        )

        # 3) Build manifest
        manifest = Manifest(
            job_id=job.job_id,
            created_at=datetime.utcnow(),
            preferences=job.preferences,
            artifacts=artifacts,
            summary={
                "status": "reports_ready",
                "notes": "Plagiarism and AI reports collected from Telegram bot"
            }
        )

        # 4) Delivery: webhook + email (best-effort, non-blocking failures bubble up)
        await self.delivery_agent.deliver(
            job=job,
            manifest=manifest
        )

        # 5) Return manifest (audit handled inside agents; retention scheduled by DeliveryAgent)
        return manifest


# Singleton accessor
_orchestrator_instance: Optional[TurnitinOrchestrator] = None


def get_orchestrator() -> TurnitinOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = TurnitinOrchestrator()
    return _orchestrator_instance
