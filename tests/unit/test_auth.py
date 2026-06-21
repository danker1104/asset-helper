from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from asset_helper.store import InMemoryAvatarStore


def test_login_issues_session_for_existing_profile() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    store = InMemoryAvatarStore(db_path=str(db_path))
    store.register_account(user_id="demo", password="pw-1234", nickname="데모", email="demo@example.com")

    result = store.login(user_id="demo", password="pw-1234")

    assert result.user_id == "demo"
    assert result.email == "demo@example.com"
    assert result.session_token


def test_login_rejects_unknown_user() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    store = InMemoryAvatarStore(db_path=str(db_path))

    try:
        store.login(user_id="demo", password="pw-1234")
        raised = False
    except ValueError:
        raised = True

    assert raised is True


def test_signup_rejects_duplicate_user_id_only() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    store = InMemoryAvatarStore(db_path=str(db_path))
    store.register_account(user_id="demo", password="pw-1234", nickname="데모", email="demo@example.com")

    duplicate_user_id = False
    duplicate_password = False

    try:
        store.register_account(user_id="demo", password="pw-9999", nickname="새닉", email="a@example.com")
    except ValueError as exc:
        duplicate_user_id = str(exc) == "duplicate_signup_fields"

    try:
        store.register_account(user_id="new-user", password="pw-1234", nickname="새닉", email="b@example.com")
    except ValueError as exc:
        duplicate_password = str(exc) == "duplicate_signup_fields"

    assert duplicate_user_id is True
    assert duplicate_password is False


def test_signup_persists_account_and_allows_login_after_store_restart() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    first_store = InMemoryAvatarStore(db_path=str(db_path))
    first_store.register_account(user_id="persist-user", password="persist-pw", nickname="보존", email="persist@example.com")

    second_store = InMemoryAvatarStore(db_path=str(db_path))
    session = second_store.login(user_id="persist-user", password="persist-pw")

    assert session.user_id == "persist-user"
    assert session.email == "persist@example.com"
