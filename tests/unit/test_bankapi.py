from io import BytesIO
from pathlib import Path
from tempfile import gettempdir
from urllib.error import HTTPError
from uuid import uuid4

import pytest

from asset_helper.store import InMemoryAvatarStore


def _build_store() -> InMemoryAvatarStore:
    db_path = Path(gettempdir()) / f"asset-helper-bankapi-unit-{uuid4().hex}.sqlite3"
    return InMemoryAvatarStore(db_path=str(db_path))


def test_register_bankapi_link_reuses_already_registered_account(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _build_store()
    store.create_profile(email="demo@example.com", user_id="demo")

    payload = '{"message":"이미 등록된 계좌입니다"}'.encode("utf-8")

    def raise_http_error(*args: object, **kwargs: object) -> object:
        raise HTTPError(
            url="https://api.bankapi.co.kr/v1/accounts",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=BytesIO(payload),
        )

    monkeypatch.setenv("BANKAPI_API_KEY", "key")
    monkeypatch.setenv("BANKAPI_SECRET_KEY", "secret")
    monkeypatch.setattr("asset_helper.store.urlrequest.urlopen", raise_http_error)

    result = store.register_bankapi_link(
        user_id="demo",
        bank_code="NH",
        account_number="3521848550713",
        account_password="1877",
        resident_number="091104",
    )

    assert result == {"success": True, "message": "이미 등록된 계좌를 현재 계정에 연동했습니다."}
    summary = store.get_bankapi_link_summary("demo")
    assert summary is not None
    assert summary["bank_code"] == "NH"
    assert summary["account_number_masked"] == "*********0713"