from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MoneyEvent:
    user_id: str
    amount: float
    occurred_at: datetime
    kind: str = "payment"


@dataclass(slots=True)
class AvatarState:
    user_id: str
    hp: int = 100
    growth: int = 0
    baseline_amount: float = 30000.0
    last_calculated_at: datetime | None = None
    events: list[MoneyEvent] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class AuditLog:
    user_id: str
    action: str
    target: str
    at: datetime
    meta: dict[str, object] = field(default_factory=dict)
