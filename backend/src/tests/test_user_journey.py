import sys
import os
import pytest
from httpx import AsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.api.schemas.chat import ChatRequest

@pytest.mark.asyncio
async def test_user_journey_simple_prompt():
    """
    Tests a simple user journey from prompt to result.
    This test simulates a user sending a simple prompt and expects a direct response.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Simulate a simple user prompt
        chat_request = ChatRequest(
            prompt="Explain the theory of relativity in simple terms.",
            user_params={},
            file_ids=[]
        )

        response = await ac.post("/api/chat", json=chat_request.dict())

        # Assert a successful response
        assert response.status_code == 202

        response_data = response.json()

        # Assert that the response contains the expected fields
        assert "success" in response_data
        assert "response" in response_data
        assert "system_used" in response_data

        # Assert that the simple system was used for a simple prompt
        assert response_data["system_used"] == "simple"
        assert response_data["success"] is True
        assert len(response_data["response"]) > 0

@pytest.mark.asyncio
async def test_user_journey_complex_prompt():
    """
    Tests a complex user journey from prompt to result.
    This test simulates a user sending a complex prompt that should trigger the advanced system.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Simulate a complex user prompt
        chat_request = ChatRequest(
            prompt="Write a detailed research paper on the impact of climate change on marine biodiversity, including citations.",
            user_params={"document_type": "research_paper"},
            file_ids=[]
        )

        response = await ac.post("/api/chat", json=chat_request.dict())

        # Assert a successful response
        assert response.status_code == 202

        response_data = response.json()

        # Assert that the response contains the expected fields
        assert "success" in response_data
        assert "response" in response_data
        assert "system_used" in response_data

        # Assert that the advanced system was used for a complex prompt
        assert response_data["system_used"] == "advanced"
        assert response_data["success"] is True
        assert len(response_data["response"]) > 0
