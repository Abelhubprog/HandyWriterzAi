import os
import sys
from pathlib import Path
from celery import Celery

# Ensure 'src' package is importable when running Celery from repo root
this_file = Path(__file__).resolve()
src_dir = this_file.parent.parent  # .../backend/src
backend_dir = src_dir.parent       # .../backend
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def _get_broker() -> str:
    return os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"


def _get_backend() -> str:
    return os.getenv("CELERY_RESULT_BACKEND") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"


app = Celery(
    "handywriterz",
    broker=_get_broker(),
    backend=_get_backend(),
)

app.conf.update(
    task_routes={
        "src.workers.trace_worker.*": {"queue": os.getenv("CELERY_TRACES_QUEUE", "traces")},
    },
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
