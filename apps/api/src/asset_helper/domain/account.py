from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AccountDeletionResult:
    user_id: str
    deleted_at: datetime | None
    audit_action: str
