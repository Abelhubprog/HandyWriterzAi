"""
Real test configuration for the MultiAgentWriterz backend.
Uses actual APIs and services for comprehensive end-to-end testing.
"""

import asyncio
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
import json
import tempfile

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["OPENROUTER_API_KEY"] = "test_api_key"

from src.main import app
from src.agent.handywriterz_state import HandyWriterzState, UserParams
from src.agent.handywriterz_graph import HandyWriterzOrchestrator
from src.db.models import Base, User, Conversation, Document
from langchain_core.messages import HumanMessage


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def real_test_db():
    """Create a real test database for the session."""
    # Use SQLite for testing but could be PostgreSQL in CI
    test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_real.db")
    
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False} if "sqlite" in test_db_url else {},
        poolclass=StaticPool if "sqlite" in test_db_url else None,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    yield TestingSessionLocal
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if "sqlite" in test_db_url and os.path.exists("./test_real.db"):
        os.remove("./test_real.db")


@pytest.fixture
def real_test_client():
    """Create a real test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def real_redis():
    """Real Redis client for testing."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    client = redis.from_url(redis_url, decode_responses=True)
    
    # Test connection
    try:
        await client.ping()
        yield client
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")
    finally:
        await client.close()


@pytest.fixture
def real_user_params():
    """Real user parameters for testing."""
    return UserParams(
        writeupType="essay",
        field="computer science",
        studyLevel="undergraduate",
        citationStyle="harvard",
        wordCount=1000,  # Shorter for testing
        additionalInstructions="Focus on AI ethics and include recent research"
    )


@pytest.fixture
def real_handywriterz_state(real_user_params):
    """Real HandyWriterz state for testing."""
    return HandyWriterzState(
        conversation_id="test_conv_real_123",
        user_id="test_user_real_123",
        wallet_address="0x1234567890abcdef",
        messages=[HumanMessage(content="Write a 1000-word essay about AI ethics in computer science, focusing on current challenges and future implications. Include recent research and use Harvard citation style.")],
        user_params=real_user_params.dict(),
        uploaded_docs=[],
        outline=None,
        research_agenda=[],
        search_queries=[],
        raw_search_results=[],
        filtered_sources=[],
        verified_sources=[],
        draft_content=None,
        current_draft=None,
        revision_count=0,
        evaluation_results=[],
        evaluation_score=None,
        turnitin_reports=[],
        turnitin_passed=False,
        formatted_document=None,
        learning_outcomes_report=None,
        download_urls={},
        current_node=None,
        workflow_status="initiated",
        error_message=None,
        retry_count=0,
        max_iterations=3,  # Shorter for testing
        enable_tutor_review=False,
        start_time=None,
        end_time=None,
        processing_metrics={},
        auth_token="test_token_real",
        payment_transaction_id="test_payment_real_123",
        uploaded_files=[]
    )


@pytest.fixture
def real_orchestrator():
    """Real HandyWriterz orchestrator for testing."""
    return HandyWriterzOrchestrator()


@pytest.fixture
def test_user_data():
    """Test user data for registration."""
    return {
        "wallet_address": "0x1234567890abcdef",
        "user_type": "student",
        "subscription_tier": "free",
        "credits_balance": 10,
        "credits_used": 0,
        "documents_created": 0,
        "avg_quality_score": 0.0,
        "preferences": {
            "default_citation_style": "harvard",
            "default_word_count": 1000
        }
    }


@pytest.fixture
def test_chat_request():
    """Test chat request for API testing."""
    return {
        "prompt": "Write a 1000-word essay about AI ethics in computer science",
        "user_params": {
            "writeupType": "essay",
            "field": "computer science",
            "studyLevel": "undergraduate",
            "citationStyle": "harvard",
            "wordCount": 1000,
            "additionalInstructions": "Focus on current challenges and include recent research"
        },
        "file_ids": []
    }


@pytest.fixture
def test_file_upload():
    """Real file upload for testing."""
    # Create a temporary PDF file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"This is a test PDF file content for AI ethics research.")
        tmp_path = tmp.name
    
    yield {
        "file_path": tmp_path,
        "filename": "test_research.pdf",
        "content_type": "application/pdf"
    }
    
    # Cleanup
    os.unlink(tmp_path)


@pytest.fixture
def api_keys():
    """Check if required API keys are available."""
    required_keys = ["GEMINI_API_KEY", "PERPLEXITY_API_KEY"]
    available_keys = {}
    
    for key in required_keys:
        value = os.getenv(key)
        if value:
            available_keys[key] = value
        else:
            pytest.skip(f"Required API key {key} not available")
    
    return available_keys


@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.metrics = {}
        
        def start(self):
            self.start_time = time.time()
        
        def record(self, name, value):
            self.metrics[name] = value
        
        def elapsed(self):
            if self.start_time:
                return time.time() - self.start_time
            return 0
        
        def report(self):
            duration = self.elapsed()
            self.metrics["total_duration"] = duration
            return self.metrics
    
    return PerformanceMonitor()


@pytest.fixture
def temporary_directory():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


# Helper functions for real testing
class RealTestHelpers:
    """Helper functions for real testing."""
    
    @staticmethod
    def create_test_user(db_session, **kwargs):
        """Create a real test user in the database."""
        user_data = {
            "wallet_address": "0x1234567890abcdef",
            "user_type": "student",
            "subscription_tier": "free",
            "credits_balance": 10,
            **kwargs
        }
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_test_conversation(db_session, user_id, **kwargs):
        """Create a real test conversation in the database."""
        conversation_data = {
            "user_id": user_id,
            "title": "Test AI Ethics Essay",
            "workflow_status": "initiated",
            "user_params": {
                "writeupType": "essay",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "citationStyle": "harvard",
                "wordCount": 1000
            },
            **kwargs
        }
        conversation = Conversation(**conversation_data)
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        return conversation
    
    @staticmethod
    def create_test_document(db_session, conversation_id, **kwargs):
        """Create a real test document in the database."""
        document_data = {
            "conversation_id": conversation_id,
            "title": "AI Ethics in Computer Science",
            "content": "This is a comprehensive essay about AI ethics...",
            "word_count": 1000,
            "quality_score": 0.85,
            **kwargs
        }
        document = Document(**document_data)
        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)
        return document
    
    @staticmethod
    async def wait_for_workflow_completion(redis_client, conversation_id, timeout=300):
        """Wait for workflow completion by monitoring Redis SSE events."""
        import asyncio
        import json
        
        pubsub = redis_client.pubsub()
        channel = f"sse:{conversation_id}"
        
        try:
            await pubsub.subscribe(channel)
            
            async def monitor():
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            event_data = json.loads(message["data"])
                            if event_data.get("type") == "workflow_complete":
                                return True
                            elif event_data.get("type") == "workflow_failed":
                                return False
                        except json.JSONDecodeError:
                            continue
                return False
            
            # Wait for completion with timeout
            result = await asyncio.wait_for(monitor(), timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            return False
        finally:
            await pubsub.unsubscribe(channel)
    
    @staticmethod
    def validate_api_response(response, expected_fields):
        """Validate API response structure."""
        if response.status_code != 200:
            return False, f"Unexpected status code: {response.status_code}"
        
        try:
            data = response.json()
            for field in expected_fields:
                if field not in data:
                    return False, f"Missing field: {field}"
            return True, "Response valid"
        except json.JSONDecodeError:
            return False, "Invalid JSON response"
    
    @staticmethod
    def validate_academic_content(content, min_word_count=500):
        """Validate academic content quality."""
        if not content:
            return False, "Empty content"
        
        words = content.split()
        if len(words) < min_word_count:
            return False, f"Content too short: {len(words)} words (min: {min_word_count})"
        
        # Check for academic markers
        academic_markers = [
            "research", "study", "analysis", "conclusion", "methodology",
            "literature", "evidence", "findings", "discussion", "implications"
        ]
        
        content_lower = content.lower()
        found_markers = sum(1 for marker in academic_markers if marker in content_lower)
        
        if found_markers < 3:
            return False, f"Insufficient academic markers: {found_markers}/10"
        
        return True, "Content appears academic"
    
    @staticmethod
    def validate_citations(content, min_citations=2):
        """Validate citation presence and format."""
        import re
        
        # Harvard style citations pattern
        harvard_pattern = r'\([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*,?\s*\d{4}\)'
        citations = re.findall(harvard_pattern, content)
        
        if len(citations) < min_citations:
            return False, f"Insufficient citations: {len(citations)} (min: {min_citations})"
        
        return True, f"Found {len(citations)} citations"


@pytest.fixture
def real_test_helpers():
    """Provide real test helper functions."""
    return RealTestHelpers


# Skip markers for CI/CD environments
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require external APIs"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )