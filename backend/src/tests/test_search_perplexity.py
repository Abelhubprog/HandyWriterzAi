import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agent.nodes.search_perplexity import PerplexitySearchAgent
from agent.handywriterz_state import HandyWriterzState

@pytest.fixture
def perplexity_agent():
    """Fixture for PerplexitySearchAgent."""
    with patch('agent.nodes.search_perplexity.PerplexitySearchAgent._initialize_perplexity_client', return_value=None):
        agent = PerplexitySearchAgent()
        agent.http_client = AsyncMock()
        return agent

@pytest.mark.asyncio
async def test_perplexity_agent_initialization(perplexity_agent: PerplexitySearchAgent):
    """Test that the PerplexitySearchAgent initializes correctly."""
    assert perplexity_agent.name == "PerplexitySearch"
    assert perplexity_agent.http_client is not None

@pytest.mark.asyncio
async def test_perplexity_agent_execute_success(perplexity_agent: PerplexitySearchAgent):
    """Test the successful execution of the PerplexitySearchAgent."""
    # Mock the state and config
    state = HandyWriterzState()
    state["user_params"] = {"field": "science"}
    state["messages"] = [MagicMock(content="test query")]
    config = {}

    # Mock the internal methods
    perplexity_agent._optimize_academic_queries = AsyncMock(return_value={"primary_query": "test", "query_variants": []})
    perplexity_agent._conduct_real_time_search = AsyncMock(return_value={"results": [], "insights": {}})
    perplexity_agent._analyze_source_credibility = AsyncMock(return_value={"source_scores": {}})
    perplexity_agent._validate_academic_content = AsyncMock(return_value={"overall_confidence": 0.9})
    perplexity_agent._format_citation_ready_sources = AsyncMock(return_value=[])
    perplexity_agent._generate_follow_up_recommendations = AsyncMock(return_value={"suggestions": []})

    # Execute the agent
    result = await perplexity_agent.execute(state, config)

    # Assert the result
    assert "search_result" in result
    assert result["search_result"]["confidence_score"] == 0.9
    assert state["perplexity_search_result"] is not None