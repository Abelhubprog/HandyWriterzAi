#!/bin/bash
set -e

echo "🚀 Starting HandyWriterz E2E Test Suite"
echo "======================================"

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Load test environment
if [ -f ".env.test" ]; then
    echo "✅ Loading test environment from .env.test"
    export $(cat .env.test | grep -v ^# | xargs)
else
    echo "⚠️  .env.test not found, using defaults"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📊 Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" = "3.13" ]; then
    echo "⚠️  Python 3.13 detected - some packages may have compatibility issues"
    echo "   Recommended: Use Python 3.11 or 3.12"
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import redis, asyncpg, langchain_community" 2>/dev/null; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Check critical imports
echo "🔍 Testing critical imports..."

python3 -c "
try:
    import redis.asyncio as redis
    print('✅ redis.asyncio import successful')
except ImportError as e:
    print(f'❌ redis.asyncio import failed: {e}')
    exit(1)

try:
    import asyncpg
    print('✅ asyncpg import successful')
except ImportError as e:
    print(f'❌ asyncpg import failed: {e}')
    exit(1)

try:
    from langchain_community.chat_models.groq import ChatGroq
    print('✅ langchain_community.chat_models.groq import successful')
except ImportError as e:
    print(f'❌ langchain_community.chat_models.groq import failed: {e}')
    exit(1)

try:
    from agent.handywriterz_graph import handywriterz_graph
    print('✅ handywriterz_graph import successful')
except Exception as e:
    print(f'❌ handywriterz_graph import failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Critical import test failed"
    exit 1
fi

# Test API connections
echo "🌐 Testing API connections..."

if [ -n "$GEMINI_API_KEY" ] && [ "$GEMINI_API_KEY" != "your_gemini_api_key_here" ]; then
    python3 -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content('Hello, test!')
    print('✅ Gemini API connection successful')
except Exception as e:
    print(f'⚠️  Gemini API test failed: {e}')
"
else
    echo "⚠️  GEMINI_API_KEY not configured - skipping Gemini test"
fi

# Run the actual tests
echo "🧪 Running test suite..."

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio
fi

# Run tests with proper error handling
if [ -d "tests" ]; then
    echo "Running backend tests..."
    python -m pytest tests/ -v --tb=short
else
    echo "⚠️  No tests directory found - running basic system validation"
    python3 -c "
import asyncio
from agent.handywriterz_state import HandyWriterzState

async def test_basic_workflow():
    print('🔬 Testing basic workflow...')
    state = HandyWriterzState(
        conversation_id='test-123',
        user_id='test-user',
        user_params={},
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
        workflow_status='initiated',
        error_message=None,
        retry_count=0,
        max_iterations=5,
    )
    print('✅ State creation successful')
    print(f'   Conversation ID: {state.conversation_id}')
    print(f'   Status: {state.workflow_status}')

asyncio.run(test_basic_workflow())
print('✅ Basic workflow test completed')
"
fi

echo ""
echo "✅ E2E Test Suite Completed!"
echo "=============================="