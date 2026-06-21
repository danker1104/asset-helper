import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_group_challenge_routes_return_non_ranking_view() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        group_response = await client.post("/groups", json={"name": "우리 챌린지", "max_members": 6})
        group_id = group_response.json()["id"]

        view_response = await client.get(f"/groups/{group_id}/challenge-view")
        goal_response = await client.get(f"/groups/{group_id}/goal-options")

        assert view_response.status_code == 200
        assert view_response.json()["has_ranking"] is False
        assert view_response.json()["encouragements"]
        assert goal_response.status_code == 200
        assert goal_response.json()["recommended_mode"] == "percent"
