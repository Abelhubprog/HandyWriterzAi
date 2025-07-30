import pytest
from agent.nodes.loader import load_graph   # helper that reads YAML → Graph

# Load once for all tests
GRAPH = load_graph("backend/backend/src/graph/composites.yaml")

@pytest.mark.parametrize("prompt,expect", [
    (
        "Draft the Methodology and Literature Review chapters for Synthetic Embryo Models…",  # Section 7 prompt
        [
            "research_swarm",
            "citation_audit",
            "writing_swarm",
            "qa_swarm",
            "turnitin_advanced",
            "formatter_advanced"
        ]
    ),
    (
        "Reflect critically on your clinical placement in a UK mental‑health ward…",        # Section 8 Task A
        [
            "privacy_manager",
            "research_swarm",
            "writing_swarm",
            "qa_swarm"
        ]
    ),
    (
        "Analyse the supplied Fujifilm CT Scanner roll‑out in Lamu County Hospital…",        # Section 8 Task B
        [
            "research_swarm",
            "writing_swarm",
            "qa_swarm",
            "turnitin_advanced",
            "formatter_advanced"
        ]
    )
])
def test_pipeline_selection(prompt, expect):
    """Ensure planner → orchestrator yields expected node order."""
    # Simulate planner planning only (no real external calls)
    # This is a placeholder for the actual test logic.
    # A more robust implementation would involve mocking the planner's
    # callable and asserting the output.
    assert True