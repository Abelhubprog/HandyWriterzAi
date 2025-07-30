import pytest
from unittest.mock import AsyncMock, patch
from agent.nodes.writer import RevolutionaryWriterAgent
from agent.handywriterz_state import HandyWriterzState

@pytest.fixture
def writer_agent():
    """Fixture for RevolutionaryWriterAgent."""
    with patch('agent.nodes.writer.RevolutionaryWriterAgent._initialize_models', return_value=None):
        agent = RevolutionaryWriterAgent()
        agent.claude_client = AsyncMock()
        agent.gpt_client = AsyncMock()
        agent.gemini_client = AsyncMock()
        return agent

@pytest.mark.asyncio
async def test_writer_agent_initialization(writer_agent: RevolutionaryWriterAgent):
    """Test that the RevolutionaryWriterAgent initializes correctly."""
    assert writer_agent.name == "revolutionary_writer"
    assert writer_agent.claude_client is not None

@pytest.mark.asyncio
async def test_writer_agent_execute_success(writer_agent: RevolutionaryWriterAgent):
    """Test the successful execution of the RevolutionaryWriterAgent."""
    # Mock the state and config
    state = HandyWriterzState()
    state["filtered_sources"] = [{"title": "Test Source"}]
    state["evidence_map"] = {}
    state["user_params"] = {"writeupType": "essay", "wordCount": 500}
    config = {}

    # Mock the internal methods
    writer_agent._design_content_structure = AsyncMock(return_value={"sections": [], "total_words": 500, "academic_field": "science", "citation_style": "apa"})
    writer_agent._revolutionary_content_generation = AsyncMock(return_value={"content": "Test content", "word_count": 2, "model_used": "test_model"})
    writer_agent._quality_assurance_refinement = AsyncMock(return_value={"content": "Refined content", "word_count": 2, "citation_count": 0, "sections_count": 1, "quality_score": 0.9})
    writer_agent._academic_compliance_validation = AsyncMock(return_value={"content": "Final content", "word_count": 2, "citation_count": 0, "sections_count": 1, "quality_score": 0.9, "academic_tone_score": 0.9, "compliance_score": 0.9, "evidence_integration_score": 0.9, "originality_score": 0.9, "revision_count": 0, "model_used": "test_model"})

    # Execute the agent
    result = await writer_agent.execute(state, config)

    # Assert the result
    assert "writing_result" in result
    assert result["writing_result"]["quality_score"] == 0.9
    assert state["generated_content"] == "Final content"