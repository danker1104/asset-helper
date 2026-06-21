import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_push_subscribe_endpoint_registers_subscription() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        response = await client.post(
            "/push/subscribe",
            json={
                "user_id": "demo",
                "endpoint": "https://push.example.com/sub/1",
                "p256dh": "key-p256dh",
                "auth": "key-auth",
            },
        )

        assert response.status_code == 200
        assert response.json()["subscribed"] is True
