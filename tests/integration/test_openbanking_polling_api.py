from datetime import datetime, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_openbanking_polling_endpoint_respects_interval_and_cap() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )
        await client.post(
            "/openbanking/connect",
            json={"user_id": "demo", "authorization_code": "auth-123"},
        )

        first = await client.post("/openbanking/poll", json={"user_id": "demo", "now": datetime(2026, 6, 13, 9, 0, tzinfo=timezone.utc).isoformat()})
        second = await client.post("/openbanking/poll", json={"user_id": "demo", "now": datetime(2026, 6, 13, 9, 4, tzinfo=timezone.utc).isoformat()})

        assert first.status_code == 200
        assert first.json()["polled"] is True
        assert second.status_code == 200
        assert second.json()["polled"] is False
        assert second.json()["reason"] == "too_soon"
