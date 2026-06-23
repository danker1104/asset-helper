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


def test_delete_bankapi_link_clears_saved_state() -> None:
    store = _build_store()
    store.create_profile(email="demo@example.com", user_id="demo")
    store._bankapi_links["demo"] = {
        "bank_code": "NH",
        "account_number": "3521848550713",
        "account_password": "1877",
        "resident_number": "091104",
        "linked_at": "2026-06-24T00:00:00+00:00",
    }
    store._bankapi_balance_history["demo"] = [{"balance": 1000, "polled_at": "2026-06-24T00:00:00+00:00"}]
    store._bankapi_transaction_history["demo"] = [{"date": "20260624", "time": "090000", "amount": 100, "balance": 900, "type": "withdrawal"}]
    store._bankapi_seen_tx_keys["demo"] = {"tx-1"}
    store._bankapi_last_polled_at["demo"] = "2026-06-24T00:00:00+00:00"

    result = store.delete_bankapi_link("demo")

    assert result["success"] is True
    assert result["message"] == "연동된 계좌를 삭제했습니다."
    assert store.get_bankapi_link_summary("demo") is None
    assert "demo" not in store._bankapi_balance_history
    assert "demo" not in store._bankapi_transaction_history
    assert "demo" not in store._bankapi_seen_tx_keys
    assert "demo" not in store._bankapi_last_polled_at