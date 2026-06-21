from datetime import datetime, timedelta, timezone

from asset_helper.store import InMemoryAvatarStore


def test_openbanking_polling_skips_when_called_too_soon() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    store.connect_openbanking(user_id="demo", authorization_code="auth-123")

    first = store.poll_openbanking(user_id="demo", now=datetime(2026, 6, 13, 9, 0, tzinfo=timezone.utc))
    second = store.poll_openbanking(user_id="demo", now=datetime(2026, 6, 13, 9, 4, tzinfo=timezone.utc))

    assert first.polled is True
    assert second.polled is False
    assert second.reason == "too_soon"


def test_openbanking_polling_stops_after_daily_cap() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    store.connect_openbanking(user_id="demo", authorization_code="auth-123")

    now = datetime(2026, 6, 13, 0, 0, tzinfo=timezone.utc)
    result = None
    for offset in range(200):
        result = store.poll_openbanking(user_id="demo", now=now + timedelta(minutes=5 * offset))

    assert result is not None
    assert result.polled is True

    limited = store.poll_openbanking(user_id="demo", now=now + timedelta(minutes=5 * 200))

    assert limited.polled is False
    assert limited.reason == "daily_cap_reached"
