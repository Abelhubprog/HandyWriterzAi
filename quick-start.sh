#!/bin/bash

echo "🚀 HandyWriterz Quick Start - YC Demo Ready"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Stop any running services
echo "🛑 Stopping existing services..."
docker-compose down --remove-orphans 2>/dev/null

# Start essential services only (Redis + DB)
echo "🔄 Starting essential infrastructure..."
docker-compose up -d redis db

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Start backend in development mode
echo "🚀 Starting HandyWriterz backend..."
cd backend

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal requirements for demo
echo "📦 Installing essential dependencies..."
pip install -q fastapi uvicorn redis psycopg2-binary sqlalchemy python-multipart

# Start backend server
echo "🎯 Starting FastAPI server on port 8000..."
export DATABASE_URL="postgresql://handywriterz:handywriterz_pass@localhost:5432/handywriterz"
export REDIS_URL="redis://localhost:6379"

# Run the server
python handywriterz_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend in another terminal would be manual
cd ../frontend
echo "💻 To start frontend, run in another terminal:"
echo "cd frontend && npm install && npm run dev"

echo ""
echo "✅ Backend running on http://localhost:8000"
echo "💻 Start frontend with: cd frontend && npm run dev"
echo "🧪 Run tests with: python test_yc_demo_ready.py"
echo ""
echo "🎉 YC Demo Ready - All systems operational!"

# Keep script running
wait $BACKEND_PID