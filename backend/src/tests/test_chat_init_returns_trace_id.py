import os
import sys
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Ensure src package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import only the chat router to avoid heavy app deps
import types

# Stub heavy gateway dependency before importing router
fake_gateway = types.SimpleNamespace(
    get_llm_gateway=lambda: None,
    LLMRequest=object,
)
sys.modules['src.services.gateway'] = fake_gateway  # type: ignore[index]

from src.routes.chat_gateway import chat_gateway_router  # type: ignore
from src.services.security_service import get_current_user  # type: ignore


def test_chat_init_returns_trace_id_and_status_accepted():
    # Spin a lightweight app with dependency override for auth
    app = FastAPI()
    app.include_router(chat_gateway_router)

    def _fake_user():
        return {"id": "test-user"}

    app.dependency_overrides[get_current_user] = _fake_user  # type: ignore[index]

    payload = {
        "prompt": "Write a short summary about AI.",
        "mode": "general",
        "file_ids": [],
        "user_params": {"writeupType": "essay", "model": "gpt-5"}
    }

    with TestClient(app) as client:
        res = client.post("/api/chat", json=payload)

    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("status") == "accepted"
    assert isinstance(data.get("trace_id"), str) and len(data["trace_id"]) > 0
