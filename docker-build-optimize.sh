#!/bin/bash

echo "🔧 HandyWriterz Docker Build Optimization"
echo "========================================="

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

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

# Check system resources and optimize Docker settings
log "🔍 Optimizing Docker build environment..."

# Create buildkit builder if not exists
if ! docker buildx ls | grep -q handywriterz-builder; then
    log "🏗️ Creating optimized buildx builder..."
    docker buildx create --name handywriterz-builder --use --platform linux/amd64
else
    docker buildx use handywriterz-builder
fi

# Prune build cache but keep recent layers
log "🧹 Pruning old build cache (keeping recent layers)..."
docker buildx prune --filter until=24h --force

# Pre-pull and cache base images
log "📥 Pre-pulling and caching base images..."
echo "Pulling Python base image..."
docker pull python:3.11-slim &
echo "Pulling PostgreSQL with pgvector..."
docker pull pgvector/pgvector:pg15 &
echo "Pulling Redis..."
docker pull redis:7-alpine &
echo "Pulling Node.js..."
docker pull node:18-alpine &

# Wait for all pulls to complete
wait
log "✅ Base images cached successfully"

# Create optimized requirements layer for caching
log "📦 Creating requirements layer cache..."
cd backend

# Create a requirements hash for cache busting
REQUIREMENTS_HASH=$(sha256sum requirements.txt | cut -d' ' -f1 | cut -c1-8)
log "Requirements hash: $REQUIREMENTS_HASH"

# Build with cache mount for pip
log "🔨 Building backend with optimized caching..."
docker buildx build \
    --platform linux/amd64 \
    --cache-from type=local,src=/tmp/.buildx-cache \
    --cache-to type=local,dest=/tmp/.buildx-cache,mode=max \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg REQUIREMENTS_HASH=$REQUIREMENTS_HASH \
    -t handywriterz-backend:latest \
    --load \
    . 2>&1 | tee ../backend-build-optimized.log

cd ..

# Build other services with similar optimization
log "🏗️ Building agentic-doc service..."
if [ -d "agentic-doc-service" ]; then
    cd agentic-doc-service
    docker buildx build \
        --platform linux/amd64 \
        --cache-from type=local,src=/tmp/.buildx-cache-agentic \
        --cache-to type=local,dest=/tmp/.buildx-cache-agentic,mode=max \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        -t handywriterz-agentic-doc:latest \
        --load \
        . 2>&1 | tee ../agentic-doc-build.log
    cd ..
else
    warn "agentic-doc-service directory not found, skipping..."
fi

# Build frontend with Node.js optimization
log "🎨 Building frontend with Node.js optimization..."
cd frontend
docker buildx build \
    --platform linux/amd64 \
    --cache-from type=local,src=/tmp/.buildx-cache-frontend \
    --cache-to type=local,dest=/tmp/.buildx-cache-frontend,mode=max \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg NODE_ENV=production \
    -t handywriterz-frontend:latest \
    --load \
    . 2>&1 | tee ../frontend-build.log
cd ..

# Display build summary
log "📊 Build Summary:"
echo "Backend build size:" 
docker images handywriterz-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo "Frontend build size:"
docker images handywriterz-frontend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo "Agentic-doc build size:"
docker images handywriterz-agentic-doc:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "Not built"

log "✅ Optimized Docker build complete!"
log "🚀 Ready to run: docker-compose up -d"

# Provide cache statistics
echo ""
echo -e "${BLUE}📊 Build Cache Statistics:${NC}"
du -sh /tmp/.buildx-cache* 2>/dev/null | head -5 || echo "Cache directories not found"

echo ""
echo -e "${GREEN}💡 Build optimizations applied:${NC}"
echo "   ✅ Multi-stage builds with layer caching"
echo "   ✅ BuildKit enabled for parallel processing" 
echo "   ✅ Requirements layer caching"
echo "   ✅ Base image pre-pulling"
echo "   ✅ Build context optimization via .dockerignore"
echo "   ✅ Platform-specific builds"
echo ""
echo -e "${BLUE}🎯 Next: Run './deploy-production.sh' for full deployment${NC}"