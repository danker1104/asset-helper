from datetime import datetime, timezone

from asset_helper.domain.alerts import NotificationRecord, ThresholdRule, is_threshold_exceeded, should_suppress_alert
from asset_helper.domain.models import MoneyEvent


def test_is_threshold_exceeded_for_daily_spend() -> None:
    now = datetime(2026, 6, 13, 12, 0, tzinfo=timezone.utc)
    events = [
        MoneyEvent(user_id="demo", amount=20000, occurred_at=now),
        MoneyEvent(user_id="demo", amount=35000, occurred_at=now),
    ]

    assert is_threshold_exceeded(events, ThresholdRule(user_id="demo", kind="daily", value=50000), now=now)


def test_should_suppress_alert_when_daily_cap_reached() -> None:
    now = datetime(2026, 6, 13, 12, 0, tzinfo=timezone.utc)
    notifications = [
        NotificationRecord(user_id="demo", kind="pause_card", payload={"amount": 1}, sent_at=now),
    ]

    assert should_suppress_alert(notifications, user_id="demo", daily_cap=1, now=now)
