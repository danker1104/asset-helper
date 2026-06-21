from datetime import datetime, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_auto_save_rule_lifecycle() -> None:
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
        assert create_response.status_code == 200
        rule_id = create_response.json()["id"]

        preview_response = await client.get(f"/auto-save/rules/{rule_id}/preview")
        assert preview_response.status_code == 200
        assert preview_response.json()["amount"] == 100000

        pause_response = await client.patch(f"/auto-save/rules/{rule_id}", json={"action": "pause"})
        assert pause_response.status_code == 200
        assert pause_response.json()["status"] == "paused"


@pytest.mark.asyncio
async def test_auto_save_rule_auto_pauses_when_balance_falls_below_floor() -> None:
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

        evaluate_response = await client.post(
            f"/auto-save/rules/{rule_id}/evaluate",
            json={"balance": 250000, "now": datetime.now(timezone.utc).isoformat()},
        )

        assert evaluate_response.status_code == 200
        body = evaluate_response.json()
        assert body["status"] == "auto_paused"
        assert body["notification"] is not None
