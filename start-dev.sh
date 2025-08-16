#!/bin/bash
# Development startup script for HandyWriterzAI

echo "🚀 Starting HandyWriterzAI Development Environment"
echo "================================================"

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Redis for SSE streaming
echo "🔧 Starting Redis for SSE streaming..."
if ! docker ps | grep -q "redis"; then
    docker run -d --name handywriterz-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes
    echo "✅ Redis started on port 6379"
else
    echo "✅ Redis already running"
fi

# Check if Redis is responding
echo "🔍 Testing Redis connection..."
if timeout 5 docker exec handywriterz-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding - SSE streaming will not work"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Backend: cd backend && python -m uvicorn src.main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Or use Docker: docker-compose up"
echo ""
echo "📝 Important:"
echo "- Redis is required for chat streaming to work"
echo "- Make sure REDIS_URL=redis://localhost:6379 in backend/.env"
echo "- Backend will fail gracefully if Redis is unavailable"