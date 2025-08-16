"""Python execution sandbox stub.

This is a placeholder that does not execute arbitrary code. In later steps,
we will integrate a constrained environment (e.g., uv/venv + limits).
"""

from typing import Dict, Any


class SandboxResult(Dict[str, Any]):
    pass


def run_tests(_: str) -> SandboxResult:
    """Return a deterministic success without running anything."""
    return SandboxResult(success=True, tests_run=0)

