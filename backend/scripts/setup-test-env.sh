#!/bin/bash
set -e

echo "🔧 Setting up HandyWriterz Test Environment"
echo "==========================================="

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📊 Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" = "3.13" ]; then
    echo "⚠️  Python 3.13 detected - some packages may have compatibility issues"
    echo "   Recommended: Use Python 3.11 or 3.12 for best compatibility"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install additional test dependencies
echo "🧪 Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov httpx

# Verify critical imports
echo "🔍 Verifying critical imports..."
python3 -c "
import redis.asyncio as redis
import asyncpg
from langchain_community.chat_models.groq import ChatGroq
print('✅ All critical imports successful')
"

# Create test database (if using Docker)
if command -v docker &> /dev/null; then
    echo "🐳 Setting up test database..."
    
    # Check if test postgres is running
    if ! docker ps | grep -q "handywriterz-test-db"; then
        echo "   Starting test PostgreSQL container..."
        docker run -d \
            --name handywriterz-test-db \
            -e POSTGRES_USER=handywriterz \
            -e POSTGRES_PASSWORD=handywriterz_test \
            -e POSTGRES_DB=handywriterz_test \
            -p 5433:5432 \
            postgres:15-alpine
        
        echo "   Waiting for database to be ready..."
        sleep 5
    fi
    
    # Check if test redis is running  
    if ! docker ps | grep -q "handywriterz-test-redis"; then
        echo "   Starting test Redis container..."
        docker run -d \
            --name handywriterz-test-redis \
            -p 6380:6379 \
            redis:7-alpine
    fi
else
    echo "⚠️  Docker not found - please ensure PostgreSQL and Redis are running manually"
    echo "   PostgreSQL: localhost:5433 (user: handywriterz, password: handywriterz_test, db: handywriterz_test)"
    echo "   Redis: localhost:6380"
fi

echo ""
echo "✅ Test environment setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env.test and fill in your API keys"
echo "2. Run tests with: python3 test_user_journey.py"
echo "3. Or use: make test"
echo ""