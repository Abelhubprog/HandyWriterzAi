#!/bin/bash
# HandyWriterz Development Environment Startup Script
# Quick startup for local development and testing

set -e

echo "🔧 Starting HandyWriterz Development Environment..."
echo "======================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.production.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "Required keys: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY"
    exit 1
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Docker is running"

# Start services in development mode
echo "🚀 Starting development services..."

# Backend development
cd backend
echo "📦 Installing backend dependencies..."
pip install -r requirements-cpu.txt > /dev/null 2>&1

echo "🔧 Starting backend server..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Test backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

cd ..

# Frontend development
echo "🎨 Starting frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

echo "🚀 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
sleep 10

echo ""
echo "🎉 HandyWriterz Development Environment is ready!"
echo "======================================================"
echo "🎨 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📊 API Docs:     http://localhost:8000/docs"
echo ""
echo "🧪 To run the dissertation test:"
echo "   python test-dissertation-journey.py"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or press Ctrl+C"
echo ""

# Keep script running
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" INT

wait