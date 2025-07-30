#!/bin/bash

# Docker-based Testing Script for HandyWriterz
# Runs comprehensive tests using Docker containers

set -e

echo "🐳 HandyWriterz Docker Test Suite"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Cleanup function
cleanup() {
    print_step "Cleaning up Docker containers..."
    docker-compose -f docker-compose.test.yml down --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
}

# Set trap for cleanup on exit
trap cleanup EXIT

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop or Docker daemon."
    exit 1
fi

print_status "Docker is running"

# Check if we're in the right directory
if [ ! -f "docker-compose.test.yml" ]; then
    print_error "docker-compose.test.yml not found. Please run from project root."
    exit 1
fi

# Step 1: Clean up any existing containers
print_step "Cleaning up existing containers..."
cleanup

# Step 2: Build test images
print_step "Building Docker images for testing..."

# Build backend image
print_status "Building backend image..."
docker build -f backend/Dockerfile -t handywriterz-backend:test ./backend

# Build frontend image  
print_status "Building frontend image..."
docker build -f frontend/Dockerfile -t handywriterz-frontend:test ./frontend

# Build test runner image
print_status "Building test runner image..."
docker build -f Dockerfile.test -t handywriterz-test-runner:latest .

print_status "All Docker images built successfully"

# Step 3: Start test infrastructure
print_step "Starting test infrastructure..."

# Start database and cache services
print_status "Starting PostgreSQL and Redis..."
docker-compose -f docker-compose.test.yml up -d postgres-test redis-test

# Wait for database to be ready
print_status "Waiting for database to be ready..."
timeout=60
counter=0
while ! docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U handywriterz -d handywriterz_test >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Database failed to start within $timeout seconds"
        docker-compose -f docker-compose.test.yml logs postgres-test
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_status "Database is ready"

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
timeout=30
counter=0
while ! docker-compose -f docker-compose.test.yml exec -T redis-test redis-cli ping >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
        docker-compose -f docker-compose.test.yml logs redis-test
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
    echo -n "."
done
echo ""
print_status "Redis is ready"

# Step 4: Start application services
print_step "Starting application services..."

# Start backend
print_status "Starting backend service..."
docker-compose -f docker-compose.test.yml up -d backend-test

# Wait for backend to be healthy
print_status "Waiting for backend to be ready..."
timeout=120
counter=0
while ! docker-compose -f docker-compose.test.yml exec -T backend-test curl -f http://localhost:8000/health >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        docker-compose -f docker-compose.test.yml logs backend-test
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_status "Backend is ready"

# Start frontend
print_status "Starting frontend service..."
docker-compose -f docker-compose.test.yml up -d frontend-test

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
timeout=120
counter=0
while ! curl -s http://localhost:3001 >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        docker-compose -f docker-compose.test.yml logs frontend-test
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_status "Frontend is ready"

# Step 5: Run comprehensive tests
print_step "Running comprehensive test suite..."

# Run the test suite in the test runner container
print_status "Executing all tests..."
docker-compose -f docker-compose.test.yml run --rm test-runner

# Step 6: Show service logs if tests fail
if [ $? -ne 0 ]; then
    print_error "Tests failed. Showing service logs..."
    
    print_step "Backend logs:"
    docker-compose -f docker-compose.test.yml logs --tail=50 backend-test
    
    print_step "Frontend logs:"
    docker-compose -f docker-compose.test.yml logs --tail=50 frontend-test
    
    print_step "Database logs:"
    docker-compose -f docker-compose.test.yml logs --tail=20 postgres-test
    
    exit 1
fi

# Step 7: Test Results
print_step "Test Execution Complete"

print_status "✅ All Docker-based tests passed!"
echo ""
echo "📋 Services Tested:"
echo "  🗄️  PostgreSQL with pgvector"
echo "  🚀 Redis cache"
echo "  🔧 FastAPI backend"
echo "  ⚛️  Next.js frontend"
echo "  🧪 End-to-end user flows"
echo "  💳 Payment system APIs"
echo "  🔐 Authentication flows"
echo "  🤖 AI agent integration"
echo ""
echo "🚀 System is ready for Railway deployment!"

# Step 8: Optional - Keep services running for manual testing
read -p "Keep services running for manual testing? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Services will remain running. Access:"
    echo "  Frontend: http://localhost:3001"
    echo "  Backend: http://localhost:8001"
    echo "  API Docs: http://localhost:8001/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for user interrupt
    trap 'echo "Stopping services..."; cleanup; exit' INT
    while true; do
        sleep 1
    done
else
    print_status "Stopping all services..."
fi