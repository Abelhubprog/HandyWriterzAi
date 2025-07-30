#!/bin/bash
# HandyWriterz Production Startup Script - CPU Only
# This script starts the entire HandyWriterz stack in production mode

set -e

echo "🚀 Starting HandyWriterz Production Environment..."
echo "======================================================"

# Check if required environment variables are set
required_vars=(
    "OPENAI_API_KEY"
    "GOOGLE_API_KEY"
    "ANTHROPIC_API_KEY"
)

echo "📋 Checking required environment variables..."
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '   - %s\n' "${missing_vars[@]}"
    echo ""
    echo "Please set these variables in your .env file or export them:"
    echo "export OPENAI_API_KEY='your_key_here'"
    echo "export GOOGLE_API_KEY='your_key_here'"
    echo "export ANTHROPIC_API_KEY='your_key_here'"
    exit 1
fi

echo "✅ All required environment variables are set"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p backend/temp
mkdir -p backend/logs
mkdir -p ssl

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Docker is running"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
services=("handywriterz-postgres" "handywriterz-redis" "handywriterz-backend" "handywriterz-frontend")
for service in "${services[@]}"; do
    echo "Checking $service..."
    if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
        docker logs "$service" --tail 20
    fi
done

# Test API endpoint
echo "🧪 Testing API endpoints..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
    echo "Backend logs:"
    docker logs handywriterz-backend --tail 20
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
    echo "Frontend logs:"
    docker logs handywriterz-frontend --tail 20
fi

echo ""
echo "🎉 HandyWriterz Production Environment is ready!"
echo "======================================================"
echo "📱 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📊 API Docs:     http://localhost:8000/docs"
echo "🗄️  Database:    localhost:5432"
echo "🔄 Redis:        localhost:6379"
echo ""
echo "📝 View logs with:"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🛑 Stop with:"
echo "   docker-compose -f docker-compose.production.yml down"
echo ""
echo "🔍 Monitor resources:"
echo "   docker stats"
echo ""
echo "Ready for YC Demo Day! 🚀"