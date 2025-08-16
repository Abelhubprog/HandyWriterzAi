#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

if [[ -z "${REDIS_URL:-}" ]]; then
  echo "ERROR: REDIS_URL is not set" >&2
  exit 1
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is not set" >&2
  exit 1
fi

export PYTHONPATH="$ROOT_DIR/backend:$ROOT_DIR/backend/src:$PYTHONPATH"

QUEUE="${CELERY_TRACES_QUEUE:-traces}"
CONCURRENCY="${CELERY_CONCURRENCY:-4}"

echo "Starting Celery worker on queue '$QUEUE' with concurrency $CONCURRENCY"
exec celery -A backend.src.workers.celery_app:app worker -Q "$QUEUE" -c "$CONCURRENCY" --loglevel=INFO

