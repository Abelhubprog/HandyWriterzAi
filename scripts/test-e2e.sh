#!/bin/bash

# End-to-End Test Runner for HandyWriterz
# Boots infrastructure, runs backend, frontend, and executes full test suite

set -e  # Exit on any error

echo "🧪 HandyWriterz E2E Test Suite"
echo "=============================="

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

# Store PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""
DOCKER_STARTED=false

# Cleanup function
cleanup() {
    print_step "Cleaning up test environment..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ "$DOCKER_STARTED" = true ]; then
        print_status "Stopping test containers"
        docker-compose -f docker-compose.test.yml down --volumes --remove-orphans
    fi
    
    print_status "Cleanup completed"
}

# Set trap for cleanup on exit
trap cleanup EXIT

# Step 1: Start test infrastructure
print_step "Starting test infrastructure..."

# Create test docker-compose if it doesn't exist
if [ ! -f "docker-compose.test.yml" ]; then
    print_status "Creating test docker-compose..."
    cat > docker-compose.test.yml << EOF
version: '3.8'

services:
  postgres-test:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: handywriterz_test
      POSTGRES_USER: handywriterz
      POSTGRES_PASSWORD: handywriterz_test_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    tmpfs:
      - /var/lib/postgresql/data:noexec,nosuid,size=512m
    
  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    volumes:
      - redis_test_data:/data
    tmpfs:
      - /data:noexec,nosuid,size=128m

volumes:
  postgres_test_data:
  redis_test_data:
EOF
fi

# Start test containers
print_status "Starting test containers..."
docker-compose -f docker-compose.test.yml up -d
DOCKER_STARTED=true

# Wait for containers to be ready
print_status "Waiting for test database to be ready..."
timeout=60
counter=0
while ! docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U handywriterz >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Test database failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

print_status "Test infrastructure ready"

# Step 2: Setup test environment
print_step "Setting up test environment..."

# Ensure test environment file exists
if [ ! -f ".env.test" ]; then
    print_status "Creating test environment file..."
    cat > .env.test << EOF
# Test Environment Configuration
ENVIRONMENT=testing
DATABASE_URL=postgresql://handywriterz:handywriterz_test_password@localhost:5433/handywriterz_test
REDIS_URL=redis://localhost:6380

# Test API keys (use actual test keys for integration tests)
OPENAI_API_KEY=${OPENAI_API_KEY:-"test_key"}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-"test_key"}
GEMINI_API_KEY=${GEMINI_API_KEY:-"test_key"}
PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY:-"test_key"}

# Payment test keys
PAYSTACK_SECRET_KEY=${PAYSTACK_SECRET_KEY:-"sk_test_your_test_key"}
COINBASE_API_KEY=${COINBASE_API_KEY:-"your_test_api_key"}

# Dynamic.xyz test environment
DYNAMIC_ENV_ID=${DYNAMIC_ENV_ID:-"test_env_id"}
DYNAMIC_PUBLIC_KEY=${DYNAMIC_PUBLIC_KEY:-"test_public_key"}

# JWT for testing
JWT_SECRET_KEY=test_jwt_secret_key_for_testing_only

# Test settings
LOG_LEVEL=WARNING
MOCK_EXTERNAL_APIS=false
SKIP_AI_CALLS=false
EOF
fi

export $(cat .env.test | grep -v '^#' | xargs)

# Step 3: Run database migrations
print_step "Running database migrations..."
cd backend

# Install backend dependencies if needed
if [ ! -d ".venv" ] || [ ! -f ".venv/pyvenv.cfg" ]; then
    print_status "Installing backend dependencies..."
    uv sync
fi

# Run migrations
print_status "Applying database migrations..."
uv run alembic upgrade head

cd ..

# Step 4: Start backend server
print_step "Starting backend server..."
cd backend

print_status "Starting FastAPI server..."
uv run uvicorn src.main:app --host 0.0.0.0 --port 8001 --log-level warning &
BACKEND_PID=$!

cd ..

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
timeout=60
counter=0
while ! curl -s http://localhost:8001/health >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

print_status "Backend server ready at http://localhost:8001"

# Step 5: Start frontend server
print_step "Starting frontend server..."
cd frontend

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    pnpm install
fi

# Create test environment for frontend
cat > .env.test.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DYNAMIC_ENV_ID=${DYNAMIC_ENV_ID:-"test_env_id"}
NEXT_PUBLIC_ENVIRONMENT=test
EOF

# Build and start frontend
print_status "Building and starting frontend..."
pnpm build
pnpm start -p 3001 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
timeout=60
counter=0
while ! curl -s http://localhost:3001 >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

print_status "Frontend server ready at http://localhost:3001"

# Step 6: Run backend E2E tests
print_step "Running backend E2E tests..."
cd backend

print_status "Running Python E2E tests..."
uv run pytest src/tests/e2e/ -v --tb=short

cd ..

# Step 7: Run frontend E2E tests
print_step "Running frontend E2E tests..."
cd frontend

# Install Playwright browsers if needed
if [ ! -d "node_modules/@playwright/test" ]; then
    print_status "Installing Playwright..."
    pnpm add -D @playwright/test
    npx playwright install --with-deps
fi

# Run Playwright tests
print_status "Running Playwright E2E tests..."
PLAYWRIGHT_BASE_URL=http://localhost:3001 \
PLAYWRIGHT_API_URL=http://localhost:8001 \
npx playwright test

cd ..

# Step 8: Test Results Summary
print_step "Test Results Summary"

print_status "✅ All E2E tests completed successfully!"
echo ""
echo "📊 Test Coverage:"
echo "  - Backend API endpoints"
echo "  - Database operations"
echo "  - Authentication flow"
echo "  - Payment integration"
echo "  - Frontend user journeys"
echo "  - AI agent workflows"
echo ""
echo "🌐 Test URLs:"
echo "  - Backend: http://localhost:8001"
echo "  - Frontend: http://localhost:3001"
echo "  - API Docs: http://localhost:8001/docs"
echo ""

print_status "E2E test suite completed successfully! 🎉"