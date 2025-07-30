#!/bin/bash

# Development Environment Setup Script for HandyWriterz
# Sets up the complete development environment with all required dependencies

set -e  # Exit on any error

echo "🚀 Setting up HandyWriterz development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check system requirements
print_step "Checking system requirements..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    if [[ $PYTHON_VERSION < "3.11" ]]; then
        print_error "Python 3.11+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3.11+ not found. Please install it first."
    exit 1
fi

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d 'v' -f 2)
    if [[ $NODE_VERSION < "20.0" ]]; then
        print_error "Node.js 20+ required. Found: $NODE_VERSION"
        exit 1
    fi
    print_status "Node.js $NODE_VERSION found"
else
    print_error "Node.js 20+ not found. Please install it first."
    exit 1
fi

# Install/check pnpm
if ! command -v pnpm &> /dev/null; then
    print_warning "pnpm not found. Installing..."
    npm install -g pnpm
    print_status "pnpm installed"
else
    PNPM_VERSION=$(pnpm --version)
    print_status "pnpm $PNPM_VERSION found"
fi

# Check uv (Python package manager)
if ! command -v uv &> /dev/null; then
    print_warning "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    print_status "uv installed"
else
    UV_VERSION=$(uv --version | cut -d ' ' -f 2)
    print_status "uv $UV_VERSION found"
fi

# Install global tools (without Clerk)
print_step "Installing global development tools..."
npm install -g @railway/cli wrangler vercel

print_status "Global tools installed successfully"

# Setup backend
print_step "Setting up backend environment..."
cd backend

# Install Python dependencies
print_status "Installing Python dependencies with uv..."
uv sync

# Setup database
print_status "Setting up development database..."
if [ -f ".env" ]; then
    print_status "Found .env file"
else
    print_warning "No .env file found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env with your actual API keys"
    else
        print_error ".env.example not found. Please create .env manually"
    fi
fi

# Run database migrations if DATABASE_URL is set
if grep -q "DATABASE_URL=" .env 2>/dev/null; then
    print_status "Running database migrations..."
    uv run alembic upgrade head || print_warning "Database migrations failed - you may need to set up your database first"
else
    print_warning "DATABASE_URL not set in .env. Skipping database migrations."
fi

cd ..

# Setup frontend
print_step "Setting up frontend environment..."
cd frontend

# Install Node.js dependencies
print_status "Installing frontend dependencies with pnpm..."
pnpm install

# Setup frontend environment
if [ -f ".env.local" ]; then
    print_status "Found frontend .env.local file"
else
    print_warning "No .env.local file found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        print_warning "Please update .env.local with your actual configuration"
    else
        print_error ".env.example not found. Please create .env.local manually"
    fi
fi

cd ..

# Setup Docker for development
print_step "Setting up Docker services..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    print_status "Docker found. Setting up development services..."
    
    # Create docker-compose for development
    cat > docker-compose.dev.yml << EOF
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: handywriterz_dev
      POSTGRES_USER: handywriterz
      POSTGRES_PASSWORD: handywriterz_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

volumes:
  postgres_dev_data:
  redis_dev_data:
EOF
    
    print_status "Starting development services..."
    docker-compose -f docker-compose.dev.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Update .env with local database URLs
    if [ -f "backend/.env" ]; then
        # Update DATABASE_URL if it's not already set to local
        if ! grep -q "DATABASE_URL=postgresql://handywriterz:handywriterz_dev_password@localhost:5432/handywriterz_dev" backend/.env; then
            echo "" >> backend/.env
            echo "# Development database" >> backend/.env
            echo "DATABASE_URL=postgresql://handywriterz:handywriterz_dev_password@localhost:5432/handywriterz_dev" >> backend/.env
            echo "REDIS_URL=redis://localhost:6379" >> backend/.env
        fi
    fi
    
    print_status "Development services started successfully"
else
    print_warning "Docker not found. You'll need to set up PostgreSQL and Redis manually."
fi

# Create development scripts
print_step "Creating development scripts..."

# Backend development script
cat > scripts/dev-backend.sh << EOF
#!/bin/bash
cd backend
echo "🚀 Starting backend development server..."
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x scripts/dev-backend.sh

# Frontend development script
cat > scripts/dev-frontend.sh << EOF
#!/bin/bash
cd frontend
echo "🚀 Starting frontend development server..."
pnpm dev
EOF
chmod +x scripts/dev-frontend.sh

# Full development script
cat > scripts/dev-all.sh << EOF
#!/bin/bash
echo "🚀 Starting full HandyWriterz development environment..."

# Start services in background
echo "Starting backend..."
./scripts/dev-backend.sh &
BACKEND_PID=\$!

echo "Waiting for backend to start..."
sleep 5

echo "Starting frontend..."
./scripts/dev-frontend.sh &
FRONTEND_PID=\$!

echo "✅ Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap 'echo "Stopping servers..."; kill \$BACKEND_PID \$FRONTEND_PID; exit' INT
wait
EOF
chmod +x scripts/dev-all.sh

print_status "Development scripts created"

# Setup testing environment
print_step "Setting up testing environment..."

# Install Playwright
cd frontend
npx playwright install --with-deps
cd ..

# Create test environment file
cat > .env.test << EOF
# Test Environment Configuration
ENVIRONMENT=testing
DATABASE_URL=postgresql://handywriterz:handywriterz_test_password@localhost:5433/handywriterz_test
REDIS_URL=redis://localhost:6380

# Test API keys (use sandbox/test keys)
PAYSTACK_SECRET_KEY=sk_test_your_test_key_here
COINBASE_API_KEY=your_test_api_key_here

# Dynamic.xyz test environment
DYNAMIC_ENV_ID=your_test_env_id
DYNAMIC_PUBLIC_KEY=your_test_public_key

# JWT for testing
JWT_SECRET_KEY=test_jwt_secret_key_for_testing_only

# Disable external services in tests
MOCK_EXTERNAL_APIS=true
SKIP_AI_CALLS=false
EOF

print_status "Test environment configured"

# Final setup completion
print_step "Setup completion"

print_status "✅ Development environment setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Update backend/.env with your API keys:"
echo "   - OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, PERPLEXITY_API_KEY"
echo "   - PAYSTACK_SECRET_KEY, COINBASE_API_KEY"
echo "   - DYNAMIC_ENV_ID, DYNAMIC_PUBLIC_KEY"
echo ""
echo "2. Update frontend/.env.local with your configuration:"
echo "   - NEXT_PUBLIC_DYNAMIC_ENV_ID"
echo ""
echo "3. Start development:"
echo "   ./scripts/dev-all.sh"
echo ""
echo "🧪 Testing:"
echo "   Backend tests: cd backend && uv run pytest"
echo "   Frontend tests: cd frontend && pnpm test"
echo "   E2E tests: pnpm playwright test"
echo ""
echo "📚 Documentation:"
echo "   API Docs: http://localhost:8000/docs"
echo "   README: ./README.md"
echo ""

print_status "Happy coding! 🎉"