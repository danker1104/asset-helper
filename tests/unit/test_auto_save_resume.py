from datetime import datetime, timezone

from asset_helper.store import InMemoryAvatarStore


def test_auto_save_rule_can_be_resumed() -> None:
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

    paused = store.pause_auto_save_rule(rule.id)
    resumed = store.resume_auto_save_rule(paused.id)

    assert paused.status == "paused"
    assert resumed.status == "active"
