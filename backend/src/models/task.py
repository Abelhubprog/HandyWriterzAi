from __future__ import annotations
from enum import Enum


class Task(str, Enum):
    GENERAL_CHAT = "general_chat"
    RESEARCH = "research"
    DRAFTING = "drafting"
    CODE_ASSIST = "code_assist"
    ACADEMIC_TOOLS = "academic_tools"
    DATA_QA = "data_qa"
    REVIEWER = "reviewer"
    SUMMARIZER = "summarizer"

    @staticmethod
    def from_legacy_role(role: str | None) -> "Task":
        if not role:
            return Task.GENERAL_CHAT
        r = role.lower()
        if r in ("judge", "lawyer", "reviewer"):
            return Task.REVIEWER
        if r in ("researcher", "browse", "web"):
            return Task.RESEARCH
        if r in ("writer", "draft", "drafting"):
            return Task.DRAFTING
        if r in ("summarizer", "summary"):
            return Task.SUMMARIZER
        return Task.GENERAL_CHAT
