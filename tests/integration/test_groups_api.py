import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_group_creation_and_join_cap() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post("/groups", json={"name": "스터디", "max_members": 6})
        assert create_response.status_code == 200
        group_id = create_response.json()["id"]

        for index in range(6):
            join_response = await client.post(f"/groups/{group_id}/members", json={"user_id": f"user-{index}"})
            assert join_response.status_code == 200

        overflow_response = await client.post(f"/groups/{group_id}/members", json={"user_id": "user-7"})
        assert overflow_response.status_code == 422
        assert overflow_response.json()["error"]["code"] == "max_members_reached"
