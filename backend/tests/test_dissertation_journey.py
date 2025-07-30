import asyncio
import pytest
from unittest.mock import patch, MagicMock

from src.agent.handywriterz_state import HandyWriterzState
from src.agent.handywriterz_graph import handywriterz_graph

@pytest.mark.asyncio
async def test_full_dissertation_journey():
    """
    A comprehensive end-to-end test that simulates the full dissertation user journey
    as described in userjourneys.md.
    """
    # 1. Initial State (from userjourneys.md)
    initial_state = HandyWriterzState(
        messages=[{
            "role": "user",
            "content": "I need a comprehensive 8000-word doctoral dissertation on 'The Intersection of Artificial Intelligence and International Cancer Treatment Protocols...'"
        }],
        user_params={
            "writeupType": "dissertation",
            "field": "law",
            "wordCount": 8000,
            "citationStyle": "Harvard",
            "educationLevel": "doctoral"
        },
        uploaded_files=[
            {"filename": "research_paper_1.pdf", "content": b"PDF content about AI in oncology..."},
            {"filename": "interview_audio.mp3", "content": b"Audio content of an interview..."}
        ]
    )

    # Mock external dependencies
    with patch('src.agent.nodes.search_base.BaseSearchNode._perform_search') as mock_search, \
         patch('src.services.llm_service.get_llm_client') as mock_llm:

        # Mock search results
        mock_search.return_value = [
            {"title": "AI in Cancer Treatment", "authors": ["Smith, J."], "year": 2023, "abstract": "An abstract...", "url": "http://example.com/paper1", "doi": "10.1234/1234", "citationCount": 10},
            {"title": "Legal Frameworks for AI", "authors": ["Doe, A."], "year": 2022, "abstract": "Another abstract...", "url": "http://example.com/paper2", "doi": "10.1234/5678", "citationCount": 5}
        ]

        # Mock LLM responses
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.side_effect = [
            # EnhancedUserIntentAgent response
            '{"should_proceed": true, "clarifying_questions": []}',
            # MasterOrchestrator academic analysis
            '{"academic_complexity": 8.5, "quality_benchmark": 90.0}',
            # MasterOrchestrator workflow strategy
            '{"primary_strategy": "research_intensive"}',
            # Writer content plan
            '{"writeup_type": "dissertation", "total_words": 8000, "sections": [{"name": "Introduction", "target_words": 1000}]}',
            # Writer content generation
            "This is the generated dissertation content...",
            # Evaluator response
            '{"Academic_Rigor": 92.0, "Content_Quality": 88.0, "Structure_Organization": 90.0, "Citation_Excellence": 95.0, "Writing_Quality": 89.0, "Innovation_Impact": 85.0}',
        ]
        mock_llm.return_value = mock_llm_instance

        # 2. Execute the graph
        final_state = await handywriterz_graph.ainvoke(initial_state)

        # 3. Assertions
        assert final_state is not None
        assert final_state.get("workflow_status") == "completed"
        
        # Enhanced User Intent
        assert final_state.get("intent_analysis_result", {}).get("should_proceed") is True
        
        # Research Phase
        assert len(final_state.get("raw_search_results", [])) > 0
        assert len(final_state.get("aggregated_sources", [])) > 0
        assert len(final_state.get("verified_sources", [])) > 0
        assert len(final_state.get("filtered_sources", [])) > 0
        
        # Writing Phase
        assert "This is the generated dissertation content..." in final_state.get("generated_content", "")
        
        # Evaluation Phase
        assert final_state.get("evaluation_score", 0) > 85.0
        
        # Turnitin (Simulated)
        assert final_state.get("turnitin_passed") is True
        
        # Formatting
        assert final_state.get("formatted_document") is not None
        assert final_state.get("formatted_document", {}).get("primary_format") == "pdf_thesis"

if __name__ == "__main__":
    asyncio.run(test_full_dissertation_journey())
