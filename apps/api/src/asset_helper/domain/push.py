from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class PushSubscription:
    id: str
    user_id: str
    endpoint: str
    p256dh: str
    auth: str


def create_push_subscription(user_id: str, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
    return PushSubscription(id=uuid4().hex, user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth)
