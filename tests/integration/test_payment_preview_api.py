from datetime import timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_payment_preview_endpoint_returns_hypothetical_hp() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        response = await client.post(
            "/events/preview",
            json={"user_id": "demo", "amount": 50000, "baseline_amount": 30000, "occurred_at": "2026-06-13T00:00:00+00:00"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["hp"] <= 100
        assert body["mutates_state"] is False


@pytest.mark.asyncio
async def test_events_simulate_alias_returns_same_preview_contract() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        response = await client.post(
            "/events/simulate",
            json={"user_id": "demo", "amount": 50000, "baseline_amount": 30000, "occurred_at": "2026-06-13T00:00:00+00:00"},
        )

        assert response.status_code == 200
        assert response.json()["mutates_state"] is False

