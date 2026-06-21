import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_account_delete_records_audit_and_deleted_at() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        response = await client.post("/account/delete", json={"user_id": "demo"})

        assert response.status_code == 200
        body = response.json()
        assert body["user_id"] == "demo"
        assert body["audit_action"] == "account_delete_requested"
        assert body["deleted_at"] is not None
