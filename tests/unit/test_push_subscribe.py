from asset_helper.store import InMemoryAvatarStore


def test_push_subscription_is_stored_per_user() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")

    result = store.subscribe_push(
        user_id="demo",
        endpoint="https://push.example.com/sub/1",
        p256dh="key-p256dh",
        auth="key-auth",
    )

    assert result.user_id == "demo"
    assert result.endpoint.startswith("https://")
    assert store.list_push_subscriptions("demo")
