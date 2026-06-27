from datetime import datetime, timezone

from asset_helper.store import InMemoryAvatarStore


def test_auto_save_rule_can_be_cancelled_during_grace() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    rule = store.create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=datetime(2026, 6, 13, tzinfo=timezone.utc),
    )

    cancelled = store.cancel_auto_save_rule(rule.id, now=datetime(2026, 6, 13, tzinfo=timezone.utc))

    assert cancelled.status == "cancelled"


def test_auto_save_rule_cannot_be_cancelled_after_grace() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    rule = store.create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=datetime(2026, 6, 13, tzinfo=timezone.utc),
    )

    try:
        store.cancel_auto_save_rule(rule.id, now=datetime(2026, 6, 15, tzinfo=timezone.utc))
        raise AssertionError("expected grace_period_expired")
    except ValueError as exc:
        assert str(exc) == "grace_period_expired"
