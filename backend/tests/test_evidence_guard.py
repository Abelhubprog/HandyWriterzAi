
import pytest
from unittest.mock import AsyncMock, MagicMock

from agent.handywriterz_state import HandyWriterzState
from unittest.mock import patch

# Mock MasterOrchestratorAgent to prevent API calls during testing
with patch('agent.nodes.master_orchestrator.MasterOrchestratorAgent._initialize_ai_providers'):
    pass
from agent.nodes.source_verifier import SourceVerifier
from agent.nodes.citation_audit import CitationAudit
from agent.nodes.writer import WriterNode

@pytest.fixture
def state_factory():
    def _factory(**kwargs):
        initial_state = {
            "params": {
                "topic": "test topic",
                "design": "RCT",
                "year_from": 2020,
                "year_to": 2024,
                "region": "UK",
                "min_sources": 3,
                "word_count": 300
            },
            "outline": {"sections": [{"title": "Introduction"}]},
            "raw_hits": [],
            "sources": [],
            "draft": "",
            "citation_error": False,
            "need_fallback": False,
            "fallback_attempts": 0
        }
        initial_state.update(kwargs)
        return HandyWriterzState(**initial_state)
    return _factory

@pytest.mark.asyncio
async def test_source_verifier_success(state_factory):
    verifier = SourceVerifier()
    verifier.enrich = AsyncMock(side_effect=lambda x: {
        **x,
        "design": "RCT",
        "year": 2021,
    })
    verifier.is_link_live = AsyncMock(return_value=(True, "http://example.com"))

    state = state_factory(raw_hits=[
        {"id": "1", "title": "Test 1"},
        {"id": "2", "title": "Test 2"},
        {"id": "3", "title": "Test 3"}
    ])

    result_state = await verifier.execute(state, None)

    assert len(result_state["sources"]) == 3
    assert result_state["need_fallback"] is False

@pytest.mark.asyncio
async def test_source_verifier_fallback(state_factory):
    verifier = SourceVerifier()
    verifier.enrich = AsyncMock(side_effect=lambda x: {
        **x,
        "design": "Case Study", # Mismatch
        "year": 2019, # Mismatch
    })
    verifier.is_link_live = AsyncMock(return_value=(False, ""))

    state = state_factory(raw_hits=[
        {"id": "1", "title": "Test 1"}
    ])

    result_state = await verifier.execute(state, None)

    assert len(result_state["sources"]) == 0
    assert result_state["need_fallback"] is True

@pytest.mark.asyncio
async def test_citation_audit_success(state_factory):
    audit = CitationAudit()
    state = state_factory(
        draft="This is a test (Author, 2022).",
        sources=[{"id": "Author"}]
    )

    result_state = await audit.execute(state, None)

    assert result_state["citation_error"] is False

@pytest.mark.asyncio
async def test_citation_audit_failure(state_factory):
    audit = CitationAudit()
    state = state_factory(
        draft="This is a test (AnotherAuthor, 2022).",
        sources=[{"id": "Author"}]
    )

    result_state = await audit.execute(state, None)

    assert result_state["citation_error"] is True
    assert result_state["missing"] == ["AnotherAuthor"]

@pytest.mark.asyncio
@patch('langchain_google_genai.ChatGoogleGenerativeAI')
async def test_writer_cites_only_allowed(mock_chat_google_generative_ai, state_factory):
    mock_llm_instance = mock_chat_google_generative_ai.return_value
    async def mock_astream_response():
        yield MagicMock(content="This is a draft citing (TestAuthor 2023). The reference is TestAuthor, J. (2023). Title.")
    mock_llm_instance.astream.return_value = mock_astream_response()

    writer = WriterNode()
    writer._broadcast_progress = MagicMock()
    writer._broadcast_token = MagicMock()
    writer.llm = mock_llm_instance

    state = state_factory(sources=[
        {
            "id": "TestAuthor2023",
            "title": "Title",
            "authors": "TestAuthor, J.",
            "year": 2023,
            "journal": "Journal of Testing",
            "doi": "10.1234/test",
            "url": "http://example.com/test",
            "design": "RCT",
            "is_live": True
        }
    ])

    result_state = await writer.execute(state, None)
    draft = result_state["draft"]

    assert "(TestAuthor 2023)" in draft
