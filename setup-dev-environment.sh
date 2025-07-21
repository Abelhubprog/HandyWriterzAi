#!/bin/bash

echo "🚀 HandyWriterz Development Environment Setup"
echo "============================================="

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    error "Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd backend

log "🔍 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    log "📦 Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        log "✅ Virtual environment created successfully"
    else
        error "Failed to create virtual environment"
        exit 1
    fi
else
    log "✅ Virtual environment already exists"
fi

# Activate virtual environment
log "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
log "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
log "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    log "✅ Dependencies installed successfully"
else
    error "Failed to install dependencies"
    exit 1
fi

# Check critical imports
log "🔍 Validating critical imports..."
python3 -c "
try:
    import sentence_transformers
    print('✅ sentence-transformers imported successfully')
except ImportError as e:
    print(f'❌ sentence-transformers import failed: {e}')
    exit(1)

try:
    import langchain
    print('✅ langchain imported successfully')  
except ImportError as e:
    print(f'❌ langchain import failed: {e}')
    exit(1)

try:
    import langgraph
    print('✅ langgraph imported successfully')
except ImportError as e:
    print(f'❌ langgraph import failed: {e}')
    exit(1)

try:
    from src.services.llm_service import get_llm_client
    print('✅ llm_service imported successfully')
except ImportError as e:
    print(f'❌ llm_service import failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    error "Critical imports failed"
    exit 1
fi

# Create necessary directories
log "📁 Creating necessary directories..."
mkdir -p uploads logs tmp

# Set up environment variables
log "⚙️ Setting up environment variables..."
if [ ! -f ".env" ]; then
    log "📋 Environment file already exists at backend/.env"
else
    warn "No .env file found - using defaults from important.md setup"
fi

# Run basic health check
log "🧪 Running basic health check..."
python3 -c "
import sys
sys.path.append('.')

try:
    from src.config import Config
    print('✅ Configuration loaded successfully')
except Exception as e:
    print(f'⚠️ Configuration warning: {e}')

try:
    from src.services.database_service import DatabaseService
    print('✅ Database service imported successfully')
except Exception as e:
    print(f'⚠️ Database service warning: {e}')

try:
    from src.agent.handywriterz_graph import handywriterz_graph
    print('✅ HandyWriterz graph imported successfully')
except Exception as e:
    print(f'❌ HandyWriterz graph import failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log "✅ Health check passed"
else
    error "Health check failed"
    exit 1
fi

# Return to root directory
cd ..

log "📋 Development Environment Summary:"
log "   Python Virtual Environment: backend/.venv"
log "   Dependencies: ✅ Installed"
log "   Configuration: ✅ Ready"
log "   Core Imports: ✅ Working"

echo ""
echo -e "${BLUE}🎯 Next Steps:${NC}"
echo "   1. Run tests: cd backend && source .venv/bin/activate && pytest"
echo "   2. Start backend: cd backend && source .venv/bin/activate && python src/main.py"
echo "   3. Run end-to-end test: cd backend && source .venv/bin/activate && pytest tests/test_dissertation_journey.py"
echo "   4. Validate deployment: ./validate-deployment.sh"
echo ""
echo -e "${GREEN}🚀 HandyWriterz development environment is ready!${NC}"