from datetime import datetime, timezone

import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_threshold_triggers_notification() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )
        assert signup.status_code == 200

        threshold = await client.post(
            "/thresholds",
            json={"user_id": "demo", "kind": "daily", "value": 50000},
        )
        assert threshold.status_code == 200

        first = await client.post(
            "/events",
            json={
                "user_id": "demo",
                "amount": 45000,
                "baseline_amount": 30000,
                "idempotency_key": "one",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert first.status_code == 200

        second = await client.post(
            "/events",
            json={
                "user_id": "demo",
                "amount": 10000,
                "baseline_amount": 30000,
                "idempotency_key": "two",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert second.status_code == 200

        notifications = await client.get("/notifications", params={"user_id": "demo"})
        assert notifications.status_code == 200
        body = notifications.json()
        assert len(body["items"]) == 1
        assert body["items"][0]["kind"] == "pause_card"


@pytest.mark.asyncio
async def test_threshold_notification_is_suppressed_after_daily_cap() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/signup",
            json={"user_id": "demo", "email": "demo@example.com", "baseline_amount": 30000},
        )
        await client.post(
            "/thresholds",
            json={"user_id": "demo", "kind": "daily", "value": 50000},
        )
        await client.patch(
            "/me/settings",
            json={"user_id": "demo", "daily_alert_cap": 1},
        )

        trigger_payload = {
            "user_id": "demo",
            "amount": 60000,
            "baseline_amount": 30000,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }

        first = await client.post("/events", json={**trigger_payload, "idempotency_key": "one"})
        second = await client.post("/events", json={**trigger_payload, "idempotency_key": "two"})

        assert first.status_code == 200
        assert second.status_code == 200

        notifications = await client.get("/notifications", params={"user_id": "demo"})
        assert notifications.status_code == 200
        body = notifications.json()
        assert len(body["items"]) == 1
        assert body["items"][0]["suppressed_reason"] is None
