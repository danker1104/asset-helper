import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_openbanking_connect_returns_accounts_and_tokens() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        response = await client.post(
            "/openbanking/connect",
            json={"user_id": "demo", "authorization_code": "auth-123"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["user_id"] == "demo"
        assert body["access_token_enc"].startswith("enc:")
        assert len(body["accounts"]) >= 1
