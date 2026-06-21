import httpx
import pytest
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from asset_helper.main import create_app
from asset_helper.store import InMemoryAvatarStore


@pytest.mark.asyncio
async def test_login_returns_session_token_for_signed_up_user() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    app = create_app(store=InMemoryAvatarStore(db_path=str(db_path)))
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-1234", "nickname": "데모", "email": "demo@example.com", "baseline_amount": 30000},
        )
        assert signup.status_code == 200

        login = await client.post("/auth/login", json={"user_id": "demo", "password": "pw-1234"})

        assert login.status_code == 200
        body = login.json()
        assert body["user_id"] == "demo"
        assert body["session_token"]


@pytest.mark.asyncio
async def test_signup_rejects_when_user_id_is_duplicate() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    app = create_app(store=InMemoryAvatarStore(db_path=str(db_path)))
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-1234", "nickname": "데모", "email": "demo@example.com"},
        )
        assert first.status_code == 200

        duplicate_password = await client.post(
            "/auth/signup",
            json={"user_id": "another", "password": "pw-1234", "nickname": "새닉", "email": "another@example.com"},
        )
        duplicate_user_id = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-9999", "nickname": "새닉2", "email": "another2@example.com"},
        )
        assert duplicate_password.status_code == 200

        assert duplicate_user_id.status_code == 409
        body = duplicate_user_id.json()
        assert body["error"]["code"] == "duplicate_signup_fields"
        assert body["error"]["message"] == "일치합니다."
