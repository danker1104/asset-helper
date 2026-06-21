from datetime import datetime, timezone

from asset_helper.domain.auto_save import create_auto_save_rule, preview_auto_save_rule, pause_auto_save_rule, evaluate_auto_save_rule


def test_create_auto_save_rule_starts_pending_grace() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)

    rule = create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=now,
    )

    assert rule.status == "pending_grace"
    assert rule.grace_until > now


def test_preview_auto_save_rule_returns_next_run_without_mutating() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    rule = create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=now,
    )

    preview = preview_auto_save_rule(rule, now=now)

    assert preview.amount == 100000
    assert preview.next_run_at == rule.next_run_at
    assert rule.status == "pending_grace"


def test_pause_auto_save_rule_changes_status() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    rule = create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=now,
    )

    paused = pause_auto_save_rule(rule)

    assert paused.status == "paused"


def test_evaluate_auto_save_rule_auto_pauses_when_balance_below_floor() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    rule = create_auto_save_rule(
        user_id="demo",
        amount=100000,
        src_account="src-1",
        dst_account="dst-1",
        balance_floor=300000,
        now=now,
    )

    evaluated, notification = evaluate_auto_save_rule(rule, balance=250000, now=now)

    assert evaluated.status == "auto_paused"
    assert notification is not None
    assert notification.kind == "auto_save_balance_alert"
