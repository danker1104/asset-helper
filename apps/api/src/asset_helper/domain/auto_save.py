from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class AutoSaveRule:
    id: str
    user_id: str
    amount: int
    src_account: str
    dst_account: str
    balance_floor: int
    status: str
    next_run_at: datetime
    grace_until: datetime


@dataclass(frozen=True, slots=True)
class AutoSavePreview:
    rule_id: str
    amount: int
    next_run_at: datetime
    status: str


@dataclass(frozen=True, slots=True)
class AutoSaveNotification:
    user_id: str
    kind: str
    payload: dict[str, object]
    sent_at: datetime


@dataclass(frozen=True, slots=True)
class AutoSaveLog:
    id: str
    rule_id: str
    idempotency_key: str | None
    status: str
    reason: str
    executed_at: datetime


def create_auto_save_rule(
    *,
    user_id: str,
    amount: int,
    src_account: str,
    dst_account: str,
    balance_floor: int,
    now: datetime | None = None,
) -> AutoSaveRule:
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    return AutoSaveRule(
        id=uuid4().hex,
        user_id=user_id,
        amount=amount,
        src_account=src_account,
        dst_account=dst_account,
        balance_floor=balance_floor,
        status="pending_grace",
        next_run_at=current_time + timedelta(hours=23),
        grace_until=current_time + timedelta(hours=24),
    )


def preview_auto_save_rule(rule: AutoSaveRule, *, now: datetime | None = None) -> AutoSavePreview:
    _ = now
    return AutoSavePreview(rule_id=rule.id, amount=rule.amount, next_run_at=rule.next_run_at, status=rule.status)


def pause_auto_save_rule(rule: AutoSaveRule) -> AutoSaveRule:
    return replace(rule, status="paused")


def build_auto_save_log(
    *,
    rule_id: str,
    idempotency_key: str | None,
    status: str,
    reason: str,
    executed_at: datetime,
) -> AutoSaveLog:
    current_time = executed_at
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    return AutoSaveLog(
        id=uuid4().hex,
        rule_id=rule_id,
        idempotency_key=idempotency_key,
        status=status,
        reason=reason,
        executed_at=current_time,
    )


def evaluate_auto_save_rule(
    rule: AutoSaveRule,
    *,
    balance: int,
    now: datetime | None = None,
) -> tuple[AutoSaveRule, AutoSaveNotification | None]:
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    if balance >= rule.balance_floor:
        return rule, None

    updated_rule = replace(rule, status="auto_paused")
    notification = AutoSaveNotification(
        user_id=rule.user_id,
        kind="auto_save_balance_alert",
        payload={"balance": balance, "balance_floor": rule.balance_floor, "rule_id": rule.id},
        sent_at=current_time,
    )
    return updated_rule, notification
