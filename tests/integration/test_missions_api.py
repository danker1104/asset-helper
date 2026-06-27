import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_mission_complete_is_idempotent_per_mission_id() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup = await client.post(
            "/auth/signup",
            json={"user_id": "mission-user", "password": "pw-1234", "nickname": "미션유저", "email": "mission@example.com"},
        )
        assert signup.status_code == 200

        first = await client.post(
            "/missions/complete",
            json={"user_id": "mission-user", "mission_id": "2026-06-27-daily-0"},
        )
        assert first.status_code == 200
        first_body = first.json()
        assert first_body["already_completed"] is False
        assert first_body["completed_count"] == 1

        second = await client.post(
            "/missions/complete",
            json={"user_id": "mission-user", "mission_id": "2026-06-27-daily-0"},
        )
        assert second.status_code == 200
        second_body = second.json()
        assert second_body["already_completed"] is True
        assert second_body["completed_count"] == 1

        third = await client.post(
            "/missions/complete",
            json={"user_id": "mission-user", "mission_id": "2026-06-27-daily-1"},
        )
        assert third.status_code == 200
        third_body = third.json()
        assert third_body["already_completed"] is False
        assert third_body["completed_count"] == 2

        completed = await client.get("/missions/completed", params={"user_id": "mission-user"})
        assert completed.status_code == 200
        completed_body = completed.json()
        assert set(completed_body["mission_ids"]) == {"2026-06-27-daily-0", "2026-06-27-daily-1"}
