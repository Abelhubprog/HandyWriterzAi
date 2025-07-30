import pytest
from httpx import AsyncClient
from backend.src.main import app

@pytest.mark.asyncio
async def test_chat_validation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={"prompt": "Hi", "mode": "essay"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_billing_summary():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/billing/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "pro"
    assert data["usage_usd"] == 42.50

@pytest.mark.asyncio
async def test_list_payment_methods():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/billing/methods")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["brand"] == "Visa"

@pytest.mark.asyncio
async def test_add_payment_method():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/billing/methods", json={"stripeToken": "tok_123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_list_invoices():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/billing/invoices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["total"] == 50.00

@pytest.mark.asyncio
async def test_get_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"

@pytest.mark.asyncio
async def test_update_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch("/api/profile", json={"name": "Jane Smith"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_get_usage_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/usage")
    assert response.status_code == 200
    data = response.json()
    assert len(data["daily"]) == 2
    assert data["daily"][0]["usd"] == 2.50
