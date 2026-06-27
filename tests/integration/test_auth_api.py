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
async def test_signup_rejects_only_for_exact_same_user_id_and_password() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    app = create_app(store=InMemoryAvatarStore(db_path=str(db_path)))
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-1234", "nickname": "데모", "email": "demo@example.com"},
        )
        assert first.status_code == 200

        duplicate_exact_pair = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-1234", "nickname": "새닉", "email": "another@example.com"},
        )
        same_user_different_password = await client.post(
            "/auth/signup",
            json={"user_id": "demo", "password": "pw-9999", "nickname": "새닉2", "email": "another2@example.com"},
        )

        assert duplicate_exact_pair.status_code == 409
        body = duplicate_exact_pair.json()
        assert body["error"]["code"] == "duplicate_signup_fields"
        assert body["error"]["message"] == "일치합니다."
        assert same_user_different_password.status_code == 200

        login = await client.post("/auth/login", json={"user_id": "demo", "password": "pw-9999"})
        assert login.status_code == 200
