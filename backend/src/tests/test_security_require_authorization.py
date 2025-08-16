import asyncio
from typing import Dict, Any

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.services.security_service import require_authorization, security_service


@pytest.fixture(autouse=True)
def _patch_security(monkeypatch):
    async def fake_get_current_user(*args, **kwargs) -> Dict[str, Any]:
        return {"id": "user-1", "roles": ["checker"]}

    async def allow_action(user: Dict[str, Any], action: str) -> bool:
        # Permit 'checker' and deny 'admin' for deterministic test
        return action in ("checker", "checker_access")

    monkeypatch.setattr(security_service, "validate_jwt_token", fake_get_current_user, raising=True)
    monkeypatch.setattr(security_service, "check_user_authorization", allow_action, raising=True)


def _make_app_single():
    app = FastAPI()

    @app.get("/single")
    async def single_route(user = Depends(require_authorization("checker"))):
        return {"ok": True}

    @app.get("/single-deny")
    async def single_deny(user = Depends(require_authorization("admin"))):
        return {"ok": True}

    return app


def _make_app_list():
    app = FastAPI()

    @app.get("/any-allow")
    async def any_allow(user = Depends(require_authorization(["admin", "checker"]))):
        return {"ok": True}

    @app.get("/any-deny")
    async def any_deny(user = Depends(require_authorization(["admin", "superuser"]))):
        return {"ok": True}

    return app


def test_require_authorization_single_allows_checker():
    client = TestClient(_make_app_single())
    r = client.get("/single", headers={"Authorization": "Bearer dummy"})
    assert r.status_code == 200


def test_require_authorization_single_denies_admin():
    client = TestClient(_make_app_single())
    r = client.get("/single-deny", headers={"Authorization": "Bearer dummy"})
    assert r.status_code == 403


def test_require_authorization_list_any_allows():
    client = TestClient(_make_app_list())
    r = client.get("/any-allow", headers={"Authorization": "Bearer dummy"})
    assert r.status_code == 200


def test_require_authorization_list_any_denies():
    client = TestClient(_make_app_list())
    r = client.get("/any-deny", headers={"Authorization": "Bearer dummy"})
    assert r.status_code == 403

