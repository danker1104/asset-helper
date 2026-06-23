from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import httpx
import pytest

from asset_helper.main import create_app
from asset_helper.store import InMemoryAvatarStore


def _build_store() -> InMemoryAvatarStore:
    db_path = Path(gettempdir()) / f"asset-helper-bankapi-{uuid4().hex}.sqlite3"
    return InMemoryAvatarStore(db_path=str(db_path))


@pytest.mark.asyncio
async def test_register_bankapi_account_returns_504_on_timeout() -> None:
    store = _build_store()
    store.create_profile(email="demo@example.com", user_id="demo")

    def raise_timeout(**_: object) -> dict[str, object]:
        raise ValueError("bankapi_timeout:은행 API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")

    store.register_bankapi_link = raise_timeout  # type: ignore[method-assign]
    app = create_app(store=store)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/bankapi/accounts/register",
            json={
                "user_id": "demo",
                "bank_code": "NH",
                "account_number": "1234567890",
                "account_password": "1234",
                "resident_number": "900101",
            },
        )

    assert response.status_code == 504
    assert response.json()["error"] == {
        "code": "bankapi_timeout",
        "message": "은행 API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
    }


@pytest.mark.asyncio
async def test_poll_bankapi_account_returns_504_on_timeout() -> None:
    store = _build_store()
    store.create_profile(email="demo@example.com", user_id="demo")

    def raise_timeout(user_id: str) -> dict[str, object]:
        assert user_id == "demo"
        raise ValueError("bankapi_timeout:은행 API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")

    store.poll_bankapi_linked_account = raise_timeout  # type: ignore[method-assign]
    app = create_app(store=store)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/bankapi/poll", params={"user_id": "demo"})

    assert response.status_code == 504
    assert response.json()["error"] == {
        "code": "bankapi_timeout",
        "message": "은행 API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
    }