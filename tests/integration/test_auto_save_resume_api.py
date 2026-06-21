import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_auto_save_resume_endpoint_sets_active_status() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )

        create_response = await client.post(
            "/auto-save/rules",
            json={
                "user_id": "demo",
                "amount": 100000,
                "src_account": "src-1",
                "dst_account": "dst-1",
                "balance_floor": 300000,
            },
        )
        rule_id = create_response.json()["id"]

        pause_response = await client.patch(f"/auto-save/rules/{rule_id}", json={"action": "pause"})
        assert pause_response.status_code == 200

        resume_response = await client.patch(f"/auto-save/rules/{rule_id}", json={"action": "resume"})
        assert resume_response.status_code == 200
        assert resume_response.json()["status"] == "active"
