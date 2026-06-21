import httpx
import pytest

from asset_helper.main import create_app


@pytest.mark.asyncio
async def test_signup_settings_and_avatar_flow() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup_response = await client.post(
            "/auth/signup",
            json={"email": "demo@example.com", "user_id": "demo"},
        )

        assert signup_response.status_code == 200
        assert signup_response.json()["email"] == "demo@example.com"

        settings_response = await client.patch(
            "/me/settings",
            json={"user_id": "demo", "intensity": 3, "text_mode": True},
        )

        assert settings_response.status_code == 200
        assert settings_response.json()["intensity"] == 3
        assert settings_response.json()["text_mode"] is True

        me_response = await client.get("/me", params={"user_id": "demo"})
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "demo@example.com"

        avatar_response = await client.get("/avatar", params={"user_id": "demo"})
        assert avatar_response.status_code == 200
        avatar = avatar_response.json()
        assert avatar["hp"] == 100
        assert avatar["avatar_type"] == "plant"
        assert avatar["intensity"] == 3
        assert avatar["text_mode"] is True
