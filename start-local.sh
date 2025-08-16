#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting HandyWriterzAI (WSL2/Linux dev)"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate local venv if present
if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  echo "🐍 Activating .venv"
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

# Start Redis via Docker if available
if command -v docker >/dev/null 2>&1; then
  if ! docker ps --format '{{.Names}}' | grep -q '^handywriterz-redis$'; then
    if docker ps -a --format '{{.Names}}' | grep -q '^handywriterz-redis$'; then
      echo "▶️  Starting existing Redis container"
      docker start handywriterz-redis >/dev/null
    else
      echo "🔧 Launching Redis container on :6379"
      docker run -d --name handywriterz-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes >/dev/null
    fi
  else
    echo "✅ Redis already running in Docker"
  fi
else
  echo "⚠️  Docker not found; make sure Redis is running at redis://localhost:6379"
fi

export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
export API_HOST="${API_HOST:-0.0.0.0}"
export API_PORT="${API_PORT:-8000}"
export API_RELOAD="${API_RELOAD:-true}"
export ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-[\"http://localhost:3000\",\"http://localhost:3001\"]}"

cd "$ROOT_DIR"

# Start backend and frontend concurrently
# Run backend using the venv's Python to avoid global uvicorn path issues
( cd backend && echo "▶️  Backend: http://localhost:${API_PORT}" && python start_server.py ) &
BACK_PID=$!

( cd frontend && echo "▶️  Frontend: http://localhost:3000" && pnpm dev ) &
FRONT_PID=$!

trap 'echo; echo "⛔ Stopping..."; kill $BACK_PID $FRONT_PID 2>/dev/null || true; wait || true' INT TERM

wait
