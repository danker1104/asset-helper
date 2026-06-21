from datetime import datetime, timezone

from asset_helper.domain.models import MoneyEvent
from asset_helper.store import InMemoryAvatarStore


def test_payment_preview_does_not_mutate_avatar_or_events() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo", baseline_amount=30000)

    baseline_avatar = store.get_avatar("demo")
    preview = store.preview_event(user_id="demo", amount=50000, baseline_amount=30000, occurred_at=datetime(2026, 6, 13, tzinfo=timezone.utc))

    after_avatar = store.get_avatar("demo")

    assert preview.hp <= 100
    assert after_avatar.hp == baseline_avatar.hp
    assert after_avatar.events == baseline_avatar.events


def test_payment_preview_matches_recalculate_logic() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo", baseline_amount=30000)

    preview = store.preview_event(user_id="demo", amount=60000, baseline_amount=30000, occurred_at=datetime(2026, 6, 13, tzinfo=timezone.utc))

    assert preview.hp < 100
