"""
Integration tests for the HandyWriterz Swarm Intelligence system.

This test suite validates the end-to-end functionality of the swarm
intelligence system, including the coordinator and the specialized agents.
"""

import pytest
from unittest.mock import AsyncMock, patch

from agent.handywriterz_state import HandyWriterzState
from agent.nodes.swarm_intelligence_coordinator import SwarmIntelligenceCoordinator

@pytest.fixture
def swarm_coordinator():
    """Fixture for the SwarmIntelligenceCoordinator."""
    return SwarmIntelligenceCoordinator()

@pytest.fixture
def initial_state():
    """Fixture for the initial state of the workflow."""
    return HandyWriterzState(
        conversation_id="test_conversation",
        user_id="test_user",
        messages=[{"role": "user", "content": "Write a paper on the impact of AI on climate change."}],
        user_params={"field": "Computer Science", "word_count": 1000},
    )

@pytest.mark.asyncio
async def test_swarm_coordinator_execution(swarm_coordinator, initial_state):
    """
    Tests the full execution of the SwarmIntelligenceCoordinator,
    ensuring that all swarms are called and results are synthesized.
    """
    with patch('agent.nodes.swarm_intelligence_coordinator.asyncio.gather', new_callable=AsyncMock) as mock_gather:
        # Mock the return values of the individual agent executions
        mock_gather.return_value = [
            # Research Swarm Results
            {"arxiv_results": [{"title": "Paper 1"}]},
            {"scholar_network_analysis": {"publication_title": "Paper 2"}},
            {"trend_analysis": {"interest_over_time": {}}},
            {"methodology_analysis": [{"analysis": "Qualitative"}]},
            {"cross_disciplinary_analysis": {"synthesis": "Interdisciplinary insights"}},
            # QA Swarm Results
            {"bias_analysis": {"analysis": "No significant bias found."}},
            {"fact_checking_analysis": [{"claim": "Claim 1", "status": "Verified"}]},
            {"argument_validation_analysis": {"analysis": "Arguments are logically sound."}},
            {"ethical_reasoning_analysis": {"analysis": "No ethical concerns."}},
            {"originality_analysis": []},
            # Writing Swarm Results
            {"adapted_content": "This is the adapted content."},
            {"cited_content": "This is the cited content.", "citations": []},
            {"optimized_content": "This is the optimized content."},
            {"enhanced_content": "This is the enhanced content."},
            {"final_content": "This is the final content."},
        ]

        result = await swarm_coordinator.execute(initial_state, config={})

        assert "research_swarm_results" in result
        assert "qa_swarm_results" in result
        assert "writing_swarm_results" in result
        assert "final_content" in result
        assert mock_gather.call_count == 3 # One for each swarm

@pytest.mark.asyncio
async def test_swarm_coordinator_error_handling(swarm_coordinator, initial_state):
    """
    Tests the error handling of the SwarmIntelligenceCoordinator when an
    agent in a swarm fails.
    """
    with patch('agent.nodes.swarm_intelligence_coordinator.asyncio.gather', new_callable=AsyncMock) as mock_gather:
        # Mock an exception being raised by one of the agents
        mock_gather.side_effect = [
            # Research Swarm raises an exception
            [Exception("Arxiv API is down")],
            # QA Swarm runs successfully
            [{"bias_analysis": {"analysis": "No significant bias found."}}],
            # Writing Swarm runs successfully
            [{"final_content": "This is the final content."}],
        ]

        result = await swarm_coordinator.execute(initial_state, config={})

        assert "research_swarm_results" in result
        assert "arxiv_specialist" in result["research_swarm_results"]
        assert "error" in result["research_swarm_results"]["arxiv_specialist"]
        assert "qa_swarm_results" in result
        assert "writing_swarm_results" in result
        assert mock_gather.call_count == 3
