from asset_helper.domain.profile import create_profile, update_profile_settings


def test_create_profile_uses_expected_defaults() -> None:
    profile = create_profile(email="demo@example.com")

    assert profile.email == "demo@example.com"
    assert profile.avatar_type == "plant"
    assert profile.intensity == 1
    assert profile.text_mode is False
    assert profile.baseline_amount == 30000


def test_update_profile_settings_changes_mode_and_intensity() -> None:
    profile = create_profile(email="demo@example.com")

    updated = update_profile_settings(profile, intensity=3, text_mode=True)

    assert updated.intensity == 3
    assert updated.text_mode is True

