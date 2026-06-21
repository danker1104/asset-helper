from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class BankAccount:
    account_id: str
    account_name: str
    balance: int


@dataclass(frozen=True, slots=True)
class OpenBankingConnection:
    user_id: str
    access_token_enc: str
    refresh_token_enc: str
    expires_at: datetime
    accounts: list[BankAccount]


@dataclass(frozen=True, slots=True)
class OpenBankingPollState:
    last_polled_at: datetime | None
    last_polled_day: str | None
    daily_poll_count: int


@dataclass(frozen=True, slots=True)
class OpenBankingPollResult:
    user_id: str
    polled: bool
    reason: str | None
    accounts: list[BankAccount]
    last_polled_at: datetime | None
    daily_poll_count: int


@dataclass(frozen=True, slots=True)
class OpenBankingRefreshResult:
    user_id: str
    refreshed: bool
    reason: str | None
    connection: OpenBankingConnection


def make_connection(user_id: str, authorization_code: str) -> OpenBankingConnection:
    now = datetime.now(timezone.utc)
    token_seed = f"{user_id}:{authorization_code}:{uuid4().hex}"
    return OpenBankingConnection(
        user_id=user_id,
        access_token_enc=f"enc:{token_seed}:access",
        refresh_token_enc=f"enc:{token_seed}:refresh",
        expires_at=now + timedelta(days=30),
        accounts=[
            BankAccount(account_id=f"{user_id}-checking", account_name="주거래 통장", balance=1200000),
            BankAccount(account_id=f"{user_id}-savings", account_name="비상금 통장", balance=350000),
        ],
    )


def make_poll_state() -> OpenBankingPollState:
    return OpenBankingPollState(last_polled_at=None, last_polled_day=None, daily_poll_count=0)


def poll_connection(
    connection: OpenBankingConnection,
    state: OpenBankingPollState,
    *,
    now: datetime,
    daily_cap: int = 200,
) -> tuple[OpenBankingPollState, OpenBankingPollResult]:
    current_time = now
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    current_day = current_time.date().isoformat()
    if state.last_polled_day != current_day:
        state = OpenBankingPollState(last_polled_at=state.last_polled_at, last_polled_day=current_day, daily_poll_count=0)

    if state.daily_poll_count >= daily_cap:
        return state, OpenBankingPollResult(
            user_id=connection.user_id,
            polled=False,
            reason="daily_cap_reached",
            accounts=list(connection.accounts),
            last_polled_at=state.last_polled_at,
            daily_poll_count=state.daily_poll_count,
        )

    if state.last_polled_at is not None and current_time - state.last_polled_at < timedelta(minutes=5):
        return state, OpenBankingPollResult(
            user_id=connection.user_id,
            polled=False,
            reason="too_soon",
            accounts=list(connection.accounts),
            last_polled_at=state.last_polled_at,
            daily_poll_count=state.daily_poll_count,
        )

    updated_state = OpenBankingPollState(
        last_polled_at=current_time,
        last_polled_day=current_day,
        daily_poll_count=state.daily_poll_count + 1,
    )
    return updated_state, OpenBankingPollResult(
        user_id=connection.user_id,
        polled=True,
        reason=None,
        accounts=list(connection.accounts),
        last_polled_at=current_time,
        daily_poll_count=updated_state.daily_poll_count,
    )


def refresh_connection(
    connection: OpenBankingConnection,
    *,
    now: datetime | None = None,
    refresh_window_days: int = 7,
) -> OpenBankingRefreshResult:
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    if connection.expires_at - current_time > timedelta(days=refresh_window_days):
        return OpenBankingRefreshResult(
            user_id=connection.user_id,
            refreshed=False,
            reason="too_early",
            connection=connection,
        )

    token_seed = f"{connection.user_id}:{current_time.isoformat()}:{uuid4().hex}"
    refreshed_connection = OpenBankingConnection(
        user_id=connection.user_id,
        access_token_enc=f"enc:{token_seed}:access",
        refresh_token_enc=f"enc:{token_seed}:refresh",
        expires_at=current_time + timedelta(days=30),
        accounts=list(connection.accounts),
    )
    return OpenBankingRefreshResult(
        user_id=connection.user_id,
        refreshed=True,
        reason=None,
        connection=refreshed_connection,
    )
