from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(slots=True)
class UserProfile:
    user_id: str
    email: str
    avatar_type: str = "plant"
    intensity: int = 1
    text_mode: bool = False
    daily_alert_cap: int = 3
    baseline_amount: float = 30000.0
    deleted_at: datetime | None = None


def create_profile(
    email: str,
    user_id: str = "demo",
    avatar_type: str = "plant",
    intensity: int = 1,
    text_mode: bool = False,
    daily_alert_cap: int = 3,
    baseline_amount: float = 30000.0,
) -> UserProfile:
    return UserProfile(
        user_id=user_id,
        email=email,
        avatar_type=avatar_type,
        intensity=_validate_intensity(intensity),
        text_mode=text_mode,
        daily_alert_cap=daily_alert_cap,
        baseline_amount=baseline_amount,
    )


def update_profile_settings(
    profile: UserProfile,
    *,
    avatar_type: str | None = None,
    intensity: int | None = None,
    text_mode: bool | None = None,
    daily_alert_cap: int | None = None,
    baseline_amount: float | None = None,
) -> UserProfile:
    return replace(
        profile,
        avatar_type=avatar_type if avatar_type is not None else profile.avatar_type,
        intensity=_validate_intensity(intensity) if intensity is not None else profile.intensity,
        text_mode=text_mode if text_mode is not None else profile.text_mode,
        daily_alert_cap=daily_alert_cap if daily_alert_cap is not None else profile.daily_alert_cap,
        baseline_amount=baseline_amount if baseline_amount is not None else profile.baseline_amount,
        deleted_at=profile.deleted_at,
    )


def _validate_intensity(intensity: int) -> int:
    if intensity < 1 or intensity > 3:
        raise ValueError("intensity must be between 1 and 3")
    return intensity
