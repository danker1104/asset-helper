from datetime import datetime, timedelta, timezone

from asset_helper.domain.hp import calculate_hp
from asset_helper.domain.models import MoneyEvent


def test_calculate_hp_returns_100_when_spend_matches_baseline() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    events = [
        MoneyEvent(user_id="demo", amount=30000, occurred_at=now - timedelta(days=1)),
    ]

    assert calculate_hp(events, baseline=30000, now=now) == 100


def test_calculate_hp_clamps_to_zero_when_spend_doubles_baseline() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    events = [
        MoneyEvent(user_id="demo", amount=60000, occurred_at=now - timedelta(days=1)),
    ]

    assert calculate_hp(events, baseline=30000, now=now) == 0


def test_calculate_hp_uses_fallback_baseline_when_missing() -> None:
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)
    events = [
        MoneyEvent(user_id="demo", amount=30000, occurred_at=now - timedelta(days=1)),
    ]

    assert calculate_hp(events, baseline=None, now=now) == 100
