from datetime import datetime, timezone

from asset_helper.store import InMemoryAvatarStore


def test_auto_save_evaluate_logs_balance_below_threshold() -> None:
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

    store.evaluate_auto_save_rule(rule.id, balance=250000, now=datetime(2026, 6, 13, tzinfo=timezone.utc))

    logs = store.list_auto_save_logs(user_id="demo")
    assert len(logs) == 1
    assert logs[0].reason == "balance_below_threshold"


def test_auto_save_evaluate_skips_duplicate_idempotency_key() -> None:
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

    first_rule, first_log = store.execute_auto_save_rule(
        rule.id,
        idempotency_key="exec-1",
        balance=500000,
        now=datetime(2026, 6, 15, tzinfo=timezone.utc),
    )
    second_rule, second_log = store.execute_auto_save_rule(
        rule.id,
        idempotency_key="exec-1",
        balance=500000,
        now=datetime(2026, 6, 15, tzinfo=timezone.utc),
    )

    assert first_rule.status == "active"
    assert first_log is not None and first_log.reason == "executed"
    assert second_rule.status == "active"
    assert second_log is not None and second_log.reason == "duplicate_skipped"
