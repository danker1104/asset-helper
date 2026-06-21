from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import MoneyEvent


@dataclass(slots=True)
class ThresholdRule:
    user_id: str
    kind: str = "daily"
    value: float = 0.0


@dataclass(slots=True)
class NotificationRecord:
    user_id: str
    kind: str
    payload: dict[str, object]
    sent_at: datetime
    suppressed_reason: str | None = None


def is_threshold_exceeded(events: list[MoneyEvent], threshold: ThresholdRule, now: datetime) -> bool:
    if threshold.kind != "daily":
        raise ValueError("unsupported threshold kind")

    daily_total = sum(event.amount for event in events if event.user_id == threshold.user_id and event.occurred_at.date() == now.date())
    return daily_total >= threshold.value


def should_suppress_alert(notifications: list[NotificationRecord], user_id: str, daily_cap: int, now: datetime) -> bool:
    if daily_cap <= 0:
        return True

    sent_today = sum(
        1
        for notification in notifications
        if notification.user_id == user_id and notification.suppressed_reason is None and notification.sent_at.date() == now.date()
    )
    return sent_today >= daily_cap
