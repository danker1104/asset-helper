from asset_helper.store import InMemoryAvatarStore


def test_delete_account_marks_profile_deleted_and_logs_audit() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")

    result = store.delete_account("demo")

    assert result.user_id == "demo"
    assert result.deleted_at is not None
    assert result.audit_action == "account_delete_requested"


def test_delete_account_is_idempotent() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")

    first = store.delete_account("demo")
    second = store.delete_account("demo")

    assert first.deleted_at == second.deleted_at
    assert len(store.list_audit_logs("demo")) == 2
