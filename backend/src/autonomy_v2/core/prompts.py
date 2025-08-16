"""Deterministic, tiny system prompts for Autonomy V2 stubs.

These are placeholders; production prompts will be richer and tested.
"""

PLANNER_SYSTEM_PROMPT = (
    "You are a planner. Produce 1-2 minimal steps to approach the goal."
)

CRITIC_SYSTEM_PROMPT = (
    "You are a critic. If the last step is ok, say pass; else suggest retry."
)

DEBUGGER_SYSTEM_PROMPT = (
    "You are a debugger. Suggest a minimal patch if needed, otherwise noop."
)

