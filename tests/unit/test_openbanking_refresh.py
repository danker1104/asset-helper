from datetime import datetime, timedelta, timezone

from asset_helper.store import InMemoryAvatarStore


def test_openbanking_refresh_skips_when_not_within_seven_days() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    connection = store.connect_openbanking(user_id="demo", authorization_code="auth-123")

    result = store.refresh_openbanking(user_id="demo", now=datetime(2026, 6, 1, tzinfo=timezone.utc))

    assert result.refreshed is False
    assert result.reason == "too_early"
    assert store.get_openbanking_connection("demo") == connection


def test_openbanking_refresh_rotates_tokens_within_seven_days() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")
    connection = store.connect_openbanking(user_id="demo", authorization_code="auth-123")

    now = connection.expires_at - timedelta(days=6)
    result = store.refresh_openbanking(user_id="demo", now=now)

    assert result.refreshed is True
    assert result.reason is None
    assert result.connection.access_token_enc.startswith("enc:")
    assert result.connection.access_token_enc != connection.access_token_enc
    assert result.connection.expires_at > connection.expires_at
