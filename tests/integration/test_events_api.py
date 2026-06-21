from datetime import datetime, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_post_events_updates_avatar_hp() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/events",
            json={
                "user_id": "demo",
                "amount": 60000,
                "baseline_amount": 30000,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["user_id"] == "demo"
        assert body["hp"] == 0

        avatar_response = await client.get("/avatar", params={"user_id": "demo"})
        assert avatar_response.status_code == 200
        assert avatar_response.json()["hp"] == 0


@pytest.mark.asyncio
async def test_post_events_rejects_duplicate_idempotency_key() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "user_id": "demo",
            "amount": 60000,
            "baseline_amount": 30000,
            "idempotency_key": "event-123",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }

        first_response = await client.post("/events", json=payload)
        second_response = await client.post("/events", json=payload)

        assert first_response.status_code == 200
        assert second_response.status_code == 409
        assert second_response.json()["error"]["code"] == "duplicate_event"

        avatar_response = await client.get("/avatar", params={"user_id": "demo"})
        assert avatar_response.status_code == 200
        assert avatar_response.json()["hp"] == 0


@pytest.mark.asyncio
async def test_validation_error_uses_standard_error_shape() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/events",
            json={
                "user_id": "demo",
                "amount": 0,
                "baseline_amount": 30000,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "validation_error"
        assert "amount" in body["error"]["message"]
