from __future__ import annotations
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .task import Task
from .policy_core import policy_registry, TaskPolicy, CandidateModel
from .factory import get_provider
from .base import ChatMessage
from src.services.policy_loader import get_orchestrator_policies, TaskType


@dataclass
class SelectionResult:
    provider_name: Optional[str]
    model_hint: Optional[str]
    reason: str


class ChatOrchestrator:
    """
    Task-aware chat orchestrator built on existing provider factory.
    - Translates legacy role/provider hints into Task.
    - Selects provider/model per Policy (weights today; health/latency next).
    - Assembles system prompt plus optional context.
    - Dispatches to provider via get_provider().
    """

    def _resolve_task(self, role: Optional[str], explicit_task: Optional[str]) -> Task:
        if explicit_task:
            try:
                return Task(explicit_task)
            except Exception:
                pass
        return Task.from_legacy_role(role)

    def _select_candidate(self, task: Task, model_hint: Optional[str]) -> SelectionResult:
        policy: TaskPolicy = policy_registry.get(task)

        # If explicit model hint given, try to match either model or provider
        if model_hint:
            for cand in policy.candidates:
                if cand.model == model_hint or (model_hint.startswith(cand.provider) or cand.provider in model_hint):
                    return SelectionResult(provider_name=cand.provider, model_hint=cand.model or model_hint, reason="model_hint")
            for cand in policy.candidates:
                if cand.provider == model_hint:
                    return SelectionResult(provider_name=cand.provider, model_hint=cand.model, reason="provider_hint")

        # Apply externalized provider restrictions based on task type
        policies = get_orchestrator_policies()
        task_type_map = {
            Task.GENERAL_CHAT: "GENERAL",
            Task.ACADEMIC_WRITING: "ACADEMIC_WRITING", 
            Task.RESEARCH: "RESEARCH",
            Task.CODE_ANALYSIS: "CODE_ANALYSIS",
            Task.CREATIVE_WRITING: "CREATIVE_WRITING"
        }
        
        task_type = task_type_map.get(task, "GENERAL")
        candidates: List[CandidateModel] = []
        
        for candidate in policy.candidates:
            if policies.is_provider_allowed(candidate.provider, task_type):
                candidates.append(candidate)
            else:
                # Log policy-based exclusion for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Provider {candidate.provider} excluded for task {task_type} by policy")

        if not candidates:
            return SelectionResult(provider_name=None, model_hint=None, reason="fallback_default")

        top = sorted(candidates, key=lambda c: c.weight, reverse=True)[0]
        return SelectionResult(provider_name=top.provider, model_hint=top.model, reason="policy_weight")

    def _assemble_messages(self, user_message: str, policy: TaskPolicy, context_snippets: Optional[List[str]]) -> List[ChatMessage]:
        sys = policy.system_prompt
        if context_snippets:
            joined = "\n\n".join(context_snippets[: policy.context_policy.max_chunks])
            sys = f"{sys}\n\nContext:\n{joined}"
        return [ChatMessage(role="system", content=sys), ChatMessage(role="user", content=user_message)]

    async def chat(
        self,
        message: str,
        role: Optional[str] = None,
        task: Optional[str] = None,
        model_hint: Optional[str] = None,
        context_snippets: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        resolved_task = self._resolve_task(role, task)
        policy = policy_registry.get(resolved_task)
        selection = self._select_candidate(resolved_task, model_hint)
        messages = self._assemble_messages(message, policy, context_snippets)

        provider = get_provider(provider_name=selection.provider_name) if selection.provider_name else get_provider()

        effective_max = max_tokens
        if not effective_max:
            for c in policy.candidates:
                if c.provider == selection.provider_name and (selection.model_hint is None or c.model == selection.model_hint):
                    if c.max_tokens:
                        effective_max = c.max_tokens
                    break
        if not effective_max:
            effective_max = 600

        resp = await provider.chat(messages=messages, max_tokens=effective_max, model=selection.model_hint)

        return {
            "content": resp.content,
            "provider": resp.provider,
            "model": resp.model,
            "usage": resp.usage,
            "policy_task": resolved_task.value,
            "selection_reason": selection.reason,
        }
