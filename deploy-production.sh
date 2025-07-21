#!/bin/bash

echo "🚀 HandyWriterz Production Deployment"
echo "====================================="

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Error handling
set -e
trap 'echo -e "${RED}❌ Deployment failed at line $LINENO${NC}"; exit 1' ERR

# Function to log with timestamp
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check prerequisites
log "🔍 Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Check available system resources
log "💻 Checking system resources..."
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
if [ "$AVAILABLE_MEM" -lt 4096 ]; then
    warn "Available memory (${AVAILABLE_MEM}MB) is less than recommended 4GB"
    warn "Build process may be slower or fail"
fi

# Cleanup previous deployment
log "🧹 Cleaning up previous deployment..."
docker-compose down --remove-orphans --volumes 2>/dev/null || true
docker system prune -f --volumes 2>/dev/null || true

# Build with optimized layer caching
log "🔨 Building optimized Docker images..."

# Pre-pull base images to cache them
log "📥 Pre-pulling base images for caching..."
docker pull python:3.11-slim &
docker pull pgvector/pgvector:pg15 &
docker pull redis:7-alpine &
docker pull node:18-alpine &
wait

# Build backend with multi-stage optimization
log "🏗️ Building backend service (multi-stage build)..."
docker-compose build --parallel --compress backend 2>&1 | tee backend-build.log

# Build other services in parallel
log "🏗️ Building remaining services in parallel..."
docker-compose build --parallel --compress agentic-doc-service frontend 2>&1 | tee services-build.log

# Start infrastructure services first
log "🚀 Starting infrastructure services..."
docker-compose up -d db redis

# Wait for infrastructure to be ready
log "⏳ Waiting for infrastructure to be healthy..."
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps db redis | grep -q "healthy"; then
        break
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    error "Infrastructure services failed to become healthy within ${timeout}s"
    docker-compose logs db redis
    exit 1
fi

log "✅ Infrastructure services are healthy"

# Start application services
log "🚀 Starting application services..."
docker-compose up -d agentic-doc-service backend

# Wait for backend services to be ready
log "⏳ Waiting for backend services to be healthy..."
timeout=180
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps backend agentic-doc-service | grep -q "healthy.*healthy"; then
        break
    fi
    sleep 10
    elapsed=$((elapsed + 10))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    error "Backend services failed to become healthy within ${timeout}s"
    docker-compose logs backend agentic-doc-service
    exit 1
fi

log "✅ Backend services are healthy"

# Start frontend service
log "🚀 Starting frontend service..."
docker-compose up -d frontend

# Final health check
log "🔍 Performing final health checks..."
sleep 30

# Check all services
log "📊 Service status:"
docker-compose ps

# Test endpoints
log "🧪 Testing service endpoints..."

# Test backend health
if curl -f -s http://localhost:8000/health > /dev/null; then
    log "✅ Backend health check passed"
else
    warn "❌ Backend health check failed"
fi

# Test agentic-doc service
if curl -f -s http://localhost:8001/health > /dev/null; then
    log "✅ Agentic-doc service health check passed"
else
    warn "❌ Agentic-doc service health check failed"
fi

# Test frontend
if curl -f -s http://localhost:3000 > /dev/null; then
    log "✅ Frontend health check passed"
else
    warn "❌ Frontend health check failed"
fi

# Display deployment summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE"
echo "====================="
echo -e "${BLUE}📍 Service URLs:${NC}"
echo "   🌐 Frontend:          http://localhost:3000"
echo "   🔧 Backend API:       http://localhost:8000"
echo "   📄 API Docs:          http://localhost:8000/docs"
echo "   📝 Agentic-Doc API:   http://localhost:8001"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps
echo ""
echo -e "${BLUE}🔍 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""
echo -e "${GREEN}🚀 HandyWriterz is now running in production mode!${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "   • Run validation: python test_yc_demo_ready.py"
echo "   • Check logs: docker-compose logs -f"
echo "   • Monitor: docker stats"
echo "   • Stop: docker-compose down"
echo ""
echo -e "${GREEN}✨ Ready for YC Demo Day demonstration!${NC}"