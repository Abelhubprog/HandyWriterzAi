import pytest
from unittest.mock import AsyncMock, patch
from agent.nodes.source_filter import SourceFilterNode
from agent.handywriterz_state import HandyWriterzState

@pytest.fixture
def source_filter_agent():
    """Fixture for SourceFilterNode."""
    with patch('agent.nodes.source_filter.SourceFilterNode._initialize_redis_connection', return_value=None):
        agent = SourceFilterNode()
        agent.redis_client = AsyncMock()
        return agent

@pytest.mark.asyncio
async def test_source_filter_agent_initialization(source_filter_agent: SourceFilterNode):
    """Test that the SourceFilterNode initializes correctly."""
    assert source_filter_agent.name == "source_filter"
    assert source_filter_agent.redis_client is not None

@pytest.mark.asyncio
async def test_source_filter_agent_execute_success(source_filter_agent: SourceFilterNode):
    """Test the successful execution of the SourceFilterNode."""
    # Mock the state and config
    state = HandyWriterzState()
    state["raw_search_results"] = [{"url": "http://example.com", "title": "Test Source"}]
    state["user_params"] = {"field": "science"}
    config = {}

    # Mock the internal methods
    source_filter_agent._advanced_source_filtering = AsyncMock(return_value=[{"url": "http://example.com", "title": "Test Source"}])
    source_filter_agent._extract_and_validate_evidence = AsyncMock(return_value=[{"url": "http://example.com", "title": "Test Source"}])
    source_filter_agent._quality_scoring_and_ranking = AsyncMock(return_value=[{"url": "http://example.com", "title": "Test Source"}])
    source_filter_agent._create_advanced_evidence_map = AsyncMock(return_value={"source_1": {}})
    source_filter_agent._store_evidence_data_advanced = AsyncMock(return_value=None)

    # Execute the agent
    result = await source_filter_agent.execute(state, config)

    # Assert the result
    assert "filtered_sources" in result
    assert len(result["filtered_sources"]) == 1
    assert state["filtered_sources"] is not None