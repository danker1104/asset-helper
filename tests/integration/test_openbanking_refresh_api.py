from datetime import datetime, timedelta, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_openbanking_refresh_endpoint_rotates_when_close_to_expiry() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )
        connect_response = await client.post(
            "/openbanking/connect",
            json={"user_id": "demo", "authorization_code": "auth-123"},
        )
        expires_at = connect_response.json()["expires_at"]

        expires_at_dt = datetime.fromisoformat(expires_at)
        refresh_now = (expires_at_dt - timedelta(days=3)).isoformat()

        refresh_response = await client.post(
            "/openbanking/refresh",
            json={"user_id": "demo", "now": refresh_now},
        )

        assert refresh_response.status_code == 200
        body = refresh_response.json()
        assert body["refreshed"] is True
        assert body["reason"] is None
        assert body["connection"]["access_token_enc"].startswith("enc:")
        assert body["connection"]["expires_at"] != expires_at
