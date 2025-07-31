from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from .task import Task


@dataclass
class ContextPolicy:
    max_context_tokens: int = 8000
    reserved_output_tokens: int = 512
    chunk_size: int = 1200
    chunk_overlap: int = 200
    max_files: int = 10
    max_chunks: int = 16
    allow_browsing: bool = False
    allow_tools: List[str] = field(default_factory=list)


@dataclass
class CandidateModel:
    provider: str
    model: Optional[str] = None
    weight: float = 1.0
    max_tokens: Optional[int] = None
    cost_bias: float = 1.0
    latency_slo_ms: Optional[int] = None


@dataclass
class TaskPolicy:
    system_prompt: str
    context_policy: ContextPolicy
    candidates: List[CandidateModel]
    safety_rules: List[str] = field(default_factory=list)
    output_mode: Optional[str] = None  # e.g., "json" for structured tasks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "context_policy": asdict(self.context_policy),
            "candidates": [asdict(c) for c in self.candidates],
            "safety_rules": list(self.safety_rules),
            "output_mode": self.output_mode,
        }


class PolicyRegistry:
    """
    Central registry for task policies. Provides per-task system prompts,
    context budgets, eligible model candidates, and safety rules.
    """
    def __init__(self) -> None:
        self._policies: Dict[Task, TaskPolicy] = {}
        self._bootstrap_defaults()

    def _bootstrap_defaults(self) -> None:
        # GENERAL_CHAT — only place Gemini is allowed
        self._policies[Task.GENERAL_CHAT] = TaskPolicy(
            system_prompt=(
                "You are HandyWriterz Assistant. Be concise, helpful, and safe. "
                "Avoid hallucinations. If uncertain, ask clarifying questions."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=6000,
                reserved_output_tokens=600,
                chunk_size=1000,
                chunk_overlap=150,
                max_files=6,
                max_chunks=8,
                allow_browsing=False,
                allow_tools=[]
            ),
            candidates=[
                CandidateModel(provider="gemini", model=None, weight=1.0, latency_slo_ms=1500, cost_bias=0.6),
                CandidateModel(provider="openrouter", model="moonshot-v1-8k", weight=0.9, latency_slo_ms=1800),
                CandidateModel(provider="openai", model="gpt-4o-mini", weight=0.7, latency_slo_ms=1700, cost_bias=1.2),
            ],
            safety_rules=[
                "No medical, legal, or financial advice; suggest consulting a professional.",
                "Refuse unsafe or disallowed content politely."
            ],
        )

        # RESEARCH — web access focused
        self._policies[Task.RESEARCH] = TaskPolicy(
            system_prompt=(
                "You are a research agent with web access. Provide citations and links. "
                "Prefer primary sources; summarize objectively. Use stepwise reasoning but keep it concise."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=12000,
                reserved_output_tokens=800,
                chunk_size=1400,
                chunk_overlap=200,
                max_files=12,
                max_chunks=18,
                allow_browsing=True,
                allow_tools=["web_browse", "cite"]
            ),
            candidates=[
                CandidateModel(provider="perplexity", model="sonar", weight=1.0, latency_slo_ms=2500),
                CandidateModel(provider="openrouter", model="qwen/qwen-2.5-72b-instruct", weight=0.9, latency_slo_ms=2200),
                CandidateModel(provider="openai", model="gpt-4.1-mini", weight=0.7, latency_slo_ms=2400, cost_bias=1.3),
            ],
            safety_rules=[
                "Always include citations with URLs when referencing web content.",
                "If browsing is not available, state limitations and use best-effort from provided context."
            ],
        )

        # DRAFTING — long-form writing
        self._policies[Task.DRAFTING] = TaskPolicy(
            system_prompt=(
                "You are a senior writing assistant. Produce clear, well-structured drafts with headings, "
                "evidence, and actionable language. Follow instructions precisely and maintain tone."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=16000,
                reserved_output_tokens=1200,
                chunk_size=1800,
                chunk_overlap=250,
                max_files=15,
                max_chunks=20,
                allow_browsing=False,
                allow_tools=["style_check"]
            ),
            candidates=[
                CandidateModel(provider="openrouter", model="moonshot-v1-8k", weight=1.0, latency_slo_ms=2600),
                CandidateModel(provider="openrouter", model="zhipuai/glm-4-5", weight=0.95, latency_slo_ms=2600),
                CandidateModel(provider="openai", model="gpt-4.1", weight=0.85, latency_slo_ms=3000, cost_bias=1.6),
            ],
        )

        # CODE_ASSIST — code generation/refactor
        self._policies[Task.CODE_ASSIST] = TaskPolicy(
            system_prompt=(
                "You are an expert code assistant. Provide correct, runnable code with minimal explanations. "
                "Always include imports and complete functions. Highlight assumptions."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=12000,
                reserved_output_tokens=800,
                chunk_size=1200,
                chunk_overlap=200,
                max_files=20,
                max_chunks=24,
                allow_browsing=False,
                allow_tools=["unit_test_suggest"]
            ),
            candidates=[
                CandidateModel(provider="openrouter", model="qwen/qwen-2.5-72b-instruct", weight=1.0, latency_slo_ms=2200),
                CandidateModel(provider="openai", model="gpt-4.1-mini", weight=0.85, latency_slo_ms=2300),
            ],
        )

        # ACADEMIC_TOOLS — Turnitin/citations hub
        self._policies[Task.ACADEMIC_TOOLS] = TaskPolicy(
            system_prompt=(
                "You are an academic assistant. Follow strict formatting, cite properly, and avoid plagiarism. "
                "Dispatch Turnitin operations to the Turnitin orchestration endpoint; do not fabricate results."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=10000,
                reserved_output_tokens=700,
                chunk_size=1200,
                chunk_overlap=200,
                max_files=15,
                max_chunks=16,
                allow_browsing=False,
                allow_tools=["turnitin", "citations"]
            ),
            candidates=[
                CandidateModel(provider="openai", model="gpt-4o-mini", weight=0.9, latency_slo_ms=1800),
                CandidateModel(provider="openrouter", model="moonshot-v1-8k", weight=0.85, latency_slo_ms=1900),
            ],
        )

        # DATA_QA — structured extraction/JSON
        self._policies[Task.DATA_QA] = TaskPolicy(
            system_prompt=(
                "You are a structured extraction and QA agent. Output strictly follows the requested JSON schema. "
                "If uncertain, set fields to null and explain briefly."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=12000,
                reserved_output_tokens=1000,
                chunk_size=1400,
                chunk_overlap: int = 200,
                max_files=20,
                max_chunks=28,
                allow_browsing=False,
                allow_tools=["json_mode"]
            ),
            candidates=[
                CandidateModel(provider="openai", model="gpt-4o-mini", weight=1.0, latency_slo_ms=1700),
                CandidateModel(provider="openrouter", model="qwen/qwen-2.5-72b-instruct", weight=0.9, latency_slo_ms=1900),
            ],
            output_mode="json",
        )

        # REVIEWER — critique/judge
        self._policies[Task.REVIEWER] = TaskPolicy(
            system_prompt=(
                "You are a critical reviewer and reasoning expert. Provide stepwise critique, highlight issues, "
                "propose improvements, and justify recommendations with evidence."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=14000,
                reserved_output_tokens=900,
                chunk_size=1600,
                chunk_overlap=250,
                max_files=12,
                max_chunks=18,
                allow_browsing=False,
                allow_tools=["critique"]
            ),
            candidates=[
                CandidateModel(provider="anthropic", model="claude-3-5-sonnet", weight=1.0, latency_slo_ms=2800),
                CandidateModel(provider="openrouter", model="moonshot-v1-8k", weight=0.9, latency_slo_ms=2500),
            ],
        )

        # SUMMARIZER — fast faithful summaries
        self._policies[Task.SUMMARIZER] = TaskPolicy(
            system_prompt=(
                "You are a precision summarizer. Produce faithful, concise summaries with bullet points and "
                "section headers. Include key numbers and decisions."
            ),
            context_policy=ContextPolicy(
                max_context_tokens=9000,
                reserved_output_tokens=700,
                chunk_size=1200,
                chunk_overlap=200,
                max_files=20,
                max_chunks=30,
                allow_browsing=False,
                allow_tools=[]
            ),
            candidates=[
                CandidateModel(provider="openai", model="gpt-4o-mini", weight=1.0, latency_slo_ms=1500, cost_bias=0.8),
                CandidateModel(provider="openrouter", model="qwen/qwen-2.5-72b-instruct", weight=0.9, latency_slo_ms=1600),
            ],
        )

    def get(self, task: Task) -> TaskPolicy:
        return self._policies[task]

    def set(self, task: Task, policy: TaskPolicy) -> None:
        self._policies[task] = policy


# Shared singleton registry
policy_registry = PolicyRegistry()
