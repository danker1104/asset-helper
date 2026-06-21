from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from .models import AvatarState, MoneyEvent


def calculate_hp(
    events: list[MoneyEvent],
    baseline: float | None,
    now: datetime | None = None,
    lookback_days: int = 7,
    fallback_baseline: float = 30000.0,
) -> int:
    reference_time = now or datetime.now(timezone.utc)
    baseline_amount = baseline if baseline and baseline > 0 else fallback_baseline
    cutoff = reference_time - timedelta(days=lookback_days)
    recent_events = [event for event in events if event.occurred_at >= cutoff]

    if not recent_events:
        return 100

    daily_average = sum(event.amount for event in recent_events) / len(recent_events)
    impulse_index = max(0.0, min(100.0, (daily_average / baseline_amount - 1) * 100))
    hp = 100 - impulse_index
    return int(round(max(0.0, min(100.0, hp))))


def recalculate_avatar(avatar: AvatarState, event: MoneyEvent) -> AvatarState:
    updated_events = [*avatar.events, event]
    hp = calculate_hp(updated_events, avatar.baseline_amount, now=event.occurred_at)
    return replace(
        avatar,
        hp=hp,
        last_calculated_at=event.occurred_at,
        events=updated_events,
    )
