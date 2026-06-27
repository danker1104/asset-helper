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


def test_signup_rejects_only_when_user_id_and_password_both_match() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    store = InMemoryAvatarStore(db_path=str(db_path))
    store.register_account(user_id="demo", password="pw-1234", nickname="데모", email="demo@example.com")

    duplicate_exact_pair = False

    try:
        store.register_account(user_id="demo", password="pw-1234", nickname="새닉", email="a@example.com")
    except ValueError as exc:
        duplicate_exact_pair = str(exc) == "duplicate_signup_fields"

    # Same ID with different password is allowed and updates account credentials.
    updated_profile = store.register_account(user_id="demo", password="pw-9999", nickname="새닉", email="b@example.com")
    session = store.login(user_id="demo", password="pw-9999")

    assert duplicate_exact_pair is True
    assert updated_profile.user_id == "demo"
    assert session.user_id == "demo"


def test_signup_allows_login_in_same_store_instance() -> None:
    db_path = Path(gettempdir()) / f"asset-helper-auth-{uuid4().hex}.sqlite3"
    first_store = InMemoryAvatarStore(db_path=str(db_path))
    first_store.register_account(user_id="persist-user", password="persist-pw", nickname="보존", email="persist@example.com")

    session = first_store.login(user_id="persist-user", password="persist-pw")

    assert session.user_id == "persist-user"
    assert session.email == "persist@example.com"
