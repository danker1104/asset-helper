from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthSession:
    user_id: str
    email: str
    session_token: str


@dataclass(frozen=True, slots=True)
class UserCredential:
    user_id: str
    password: str
    nickname: str
