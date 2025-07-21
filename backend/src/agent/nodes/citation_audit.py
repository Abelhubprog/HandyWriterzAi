
from typing import Any
import re
from src.agent.base import BaseNode

class CitationAudit(BaseNode):
    def __init__(self):
        super().__init__("citation_audit")

    async def execute(self, state: dict, config: Any) -> dict:
        in_text = re.findall(r"\(([^),]+?)(?:,\s*|\s+)\d{4}\)", state.get("draft", ""))
        allowed_ids = {s["id"] for s in state.get("sources", [])}
        missing = [c for c in in_text if c not in allowed_ids]
        if missing:
            return {**state, "citation_error": True, "missing": missing}
        return {**state, "citation_error": False}
