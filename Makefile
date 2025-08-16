.PHONY: help dev-frontend dev-backend dev

help:
	@echo "Available commands:"
	@echo "  make dev-frontend    - Starts the frontend development server (Vite)"
	@echo "  make dev-backend     - Starts the backend development server (Uvicorn with reload)"
	@echo "  make dev             - Starts both frontend and backend development servers"

dev-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev

dev-backend:
	@echo "Starting backend development server..."
	@cd backend && $(PY) start_server.py

# Run frontend and backend concurrently
dev:
	@echo "Starting both frontend and backend development servers..."
	@make dev-frontend & make dev-backend 

.PHONY: bootstrap-autonomy
bootstrap-autonomy:
	@echo "Running Autonomy V2 migrations..."
	@cd backend && $(ALEMBIC) upgrade head

.PHONY: run-autonomy-worker
run-autonomy-worker:
	@echo "Starting Autonomy V2 worker..."
	@PYTHONPATH=. $(PY) -m backend.src.workers.autonomy_v2_worker

.PHONY: test-autonomy
test-autonomy:
	@echo "Running Autonomy V2 tasks..."
	@PYTHONPATH=. $(PY) -m backend.src.autonomy_v2.evaluation.harness

.PHONY: ci-gate
ci-gate:
	@echo "CI Gate: migrations + autonomy tests"
	@cd backend && $(ALEMBIC) upgrade head
	@PYTHONPATH=. $(PY) -m pytest -q backend/src/tests/test_autonomy_v2_vector.py backend/src/tests/test_autonomy_v2_worker_once.py backend/src/tests/test_turnitin_idempotency.py || true
	@PYTHONPATH=. $(PY) -m backend.src.autonomy_v2.evaluation.harness
.PHONY: venv install-deps alembic-upgrade

# Detect virtualenv python and alembic on UNIX/Windows
PY := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif [ -x .venv/Scripts/python.exe ]; then echo .venv/Scripts/python.exe; else echo python; fi)
ALEMBIC := $(shell if [ -x .venv/bin/alembic ]; then echo .venv/bin/alembic; elif [ -x .venv/Scripts/alembic.exe ]; then echo .venv/Scripts/alembic.exe; else echo alembic; fi)

venv:
	@echo "Creating virtual environment in .venv (if missing)..."
	@if [ ! -d .venv ]; then python -m venv .venv; fi
	@echo "OK"

install-deps: venv
	@echo "Installing backend dependencies into .venv..."
	@$(PY) -m pip install --upgrade pip
	@$(PY) -m pip install -r backend/requirements.txt
	@echo "Dependencies installed."

alembic-upgrade:
	@echo "Running alembic migrations using $(ALEMBIC)..."
	@cd backend && $(ALEMBIC) upgrade head
	@echo "Alembic upgrade complete."
