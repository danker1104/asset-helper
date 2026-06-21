from asset_helper.store import InMemoryAvatarStore


def test_connect_openbanking_stores_tokens_and_accounts() -> None:
    store = InMemoryAvatarStore()
    store.create_profile(email="demo@example.com", user_id="demo")

    result = store.connect_openbanking(user_id="demo", authorization_code="auth-123")

    assert result.user_id == "demo"
    assert result.access_token_enc.startswith("enc:")
    assert len(result.accounts) >= 1


def test_connect_openbanking_rejects_unknown_user() -> None:
    store = InMemoryAvatarStore()

    try:
        store.connect_openbanking(user_id="demo", authorization_code="auth-123")
        raised = False
    except ValueError:
        raised = True

    assert raised is True
