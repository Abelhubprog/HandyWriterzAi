from __future__ import annotations
import asyncio
from typing import Optional
from .models import Preferences, Artifacts, SessionStatus

# NOTE: Stub implementation that simulates a Telegram bot conversation with the Turnitin helper bot.
# It "pretends" to upload a document and receive two PDF reports after a short wait.
# Replace with real automation using Telethon/TDLib message flows.


class BotConversationAgent:
    def __init__(self, timeout_sec: int = 120):
        self.timeout_sec = timeout_sec

    async def submit_and_collect(
        self,
        input_doc_uri: str,
        preferences: Preferences,
        artifacts: Artifacts,
        session_status: Optional[SessionStatus] = None,
    ) -> Artifacts:
        # Basic validation
        if not input_doc_uri or not isinstance(input_doc_uri, str):
            raise ValueError("input_doc_uri must be a non-empty string")

        # Simulate conversation round-trip timings
        await asyncio.sleep(0.5)  # open bot
        await asyncio.sleep(0.5)  # /start, accept policy
        await asyncio.sleep(0.5)  # upload docx
        await asyncio.sleep(1.0)  # wait for processing

        # Produce fake artifact URIs for downstream handling
        # In a real system these would be presigned URLs or storage object keys.
        artifacts.pdf_similarity_uri = f"{input_doc_uri}.turnitin.similarity.pdf"
        artifacts.pdf_full_report_uri = f"{input_doc_uri}.turnitin.full.pdf"

        # Optional: confidence score (simulated)
        artifacts.metadata["confidence"] = 0.85
        artifacts.metadata["similarity_score"] = 12.3

        return artifacts
