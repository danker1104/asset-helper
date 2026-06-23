from __future__ import annotations
from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field

from .domain.models import MoneyEvent
from .store import InMemoryAvatarStore
from .domain.learning import LearningCard


class SignupCreate(BaseModel):
    user_id: str = Field(default="demo")
    password: str | None = None
    nickname: str | None = None
    email: str = ""
    avatar_type: str = Field(default="plant")
    intensity: int = Field(default=1, ge=1, le=3)
    text_mode: bool = False
    daily_alert_cap: int = Field(default=3, ge=0)
    baseline_amount: float = Field(default=30000, gt=0)


class SettingsUpdate(BaseModel):
    user_id: str = Field(default="demo")
    avatar_type: str | None = None
    intensity: int | None = Field(default=None, ge=1, le=3)
    text_mode: bool | None = None
    daily_alert_cap: int | None = Field(default=None, ge=0)
    baseline_amount: float | None = Field(default=None, gt=0)


class AccountRead(BaseModel):
    user_id: str
    email: str
    avatar_type: str
    intensity: int
    text_mode: bool
    daily_alert_cap: int
    baseline_amount: float


class LoginCreate(BaseModel):
    user_id: str
    password: str | None = None
    email: str | None = None


class LoginRead(BaseModel):
    user_id: str
    nickname: str
    email: str
    session_token: str


class AutoSaveRuleCreate(BaseModel):
    user_id: str = Field(default="demo")
    amount: int = Field(gt=0)
    src_account: str
    dst_account: str
    balance_floor: int = Field(ge=0)


class AutoSaveRuleRead(BaseModel):
    id: str
    user_id: str
    amount: int
    src_account: str
    dst_account: str
    balance_floor: int
    status: str
    next_run_at: datetime
    grace_until: datetime


class AutoSavePreviewRead(BaseModel):
    rule_id: str
    amount: int
    next_run_at: datetime
    status: str


class AutoSaveRuleAction(BaseModel):
    action: str


class AutoSaveCancelCreate(BaseModel):
    now: datetime | None = None


class AutoSaveEvaluateCreate(BaseModel):
    balance: int = Field(ge=0)
    now: datetime | None = None


class AutoSaveNotificationRead(BaseModel):
    user_id: str
    kind: str
    payload: dict[str, object]
    sent_at: datetime


class AutoSaveEvaluateRead(BaseModel):
    id: str
    user_id: str
    amount: int
    src_account: str
    dst_account: str
    balance_floor: int
    status: str
    next_run_at: datetime
    grace_until: datetime
    notification: AutoSaveNotificationRead | None


class OpenBankingConnectCreate(BaseModel):
    user_id: str
    authorization_code: str


class OpenBankingAccountRead(BaseModel):
    account_id: str
    account_name: str
    balance: int


class OpenBankingConnectRead(BaseModel):
    user_id: str
    access_token_enc: str
    refresh_token_enc: str
    expires_at: datetime
    accounts: list[OpenBankingAccountRead]


class OpenBankingPollCreate(BaseModel):
    user_id: str = Field(default="demo")
    now: datetime | None = None


class OpenBankingPollRead(BaseModel):
    user_id: str
    polled: bool
    reason: str | None
    accounts: list[OpenBankingAccountRead]
    last_polled_at: datetime | None
    daily_poll_count: int


class OpenBankingRefreshCreate(BaseModel):
    user_id: str = Field(default="demo")
    now: datetime | None = None


class OpenBankingRefreshRead(BaseModel):
    user_id: str
    refreshed: bool
    reason: str | None
    connection: OpenBankingConnectRead


class BankApiTransactionQueryCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bank_code: str = Field(alias="bankCode", min_length=2, max_length=2)
    account_number: str = Field(alias="accountNumber", min_length=1)
    account_password: str = Field(alias="accountPassword", min_length=1)
    resident_number: str = Field(alias="residentNumber", min_length=6, max_length=6)
    start_date: str = Field(alias="startDate", min_length=8, max_length=8)
    end_date: str = Field(alias="endDate", min_length=8, max_length=8)


class BankApiTransactionRead(BaseModel):
    date: str
    time: str
    description: str | None = ""
    displayName: str | None = ""
    counterparty: str | None = ""
    amount: int
    balance: int
    type: str
    branch: str | None = ""
    memo: str | None = ""


class BankApiAccountInfoRead(BaseModel):
    accountNumber: str
    balance: int


class BankApiTransactionQueryRead(BaseModel):
    success: bool
    transactions: list[BankApiTransactionRead] = []
    accountInfo: BankApiAccountInfoRead | None = None


class BankApiAccountRegisterCreate(BaseModel):
    user_id: str
    bank_code: str = Field(min_length=2, max_length=2)
    account_number: str = Field(min_length=1)
    account_password: str = Field(min_length=1)
    resident_number: str = Field(min_length=6, max_length=6)


class BankApiLinkSummaryRead(BaseModel):
    user_id: str
    bank_code: str
    account_number_masked: str
    linked_at: str
    last_polled_at: str | None = None


class BankApiAccountRegisterRead(BaseModel):
    success: bool
    message: str | None = None
    data: dict[str, object] | None = None
    link: BankApiLinkSummaryRead


class BankApiAccountDeleteRead(BaseModel):
    success: bool
    message: str
    user_id: str
    bank_code: str
    account_number_masked: str


class BankApiBalancePointRead(BaseModel):
    balance: int
    polled_at: str


class BankApiPollRead(BaseModel):
    user_id: str
    current_balance: int
    new_transaction_count: int
    total_hp_drop: int
    hp: int
    polled_at: str


class BankApiBalanceHistoryRead(BaseModel):
    items: list[BankApiBalancePointRead]


class BankApiTransactionHistoryRead(BaseModel):
    items: list[BankApiTransactionRead]


class ThresholdCreate(BaseModel):
    user_id: str = Field(default="demo")
    kind: str = Field(default="daily")
    value: float = Field(gt=0)


class ThresholdRead(BaseModel):
    user_id: str
    kind: str
    value: float


class NotificationRead(BaseModel):
    user_id: str
    kind: str
    payload: dict[str, object]
    sent_at: datetime
    suppressed_reason: str | None = None


class NotificationListRead(BaseModel):
    items: list[NotificationRead]


class LearningCardRead(BaseModel):
    id: str
    title: str
    body: str
    duration_sec: int


class LearningCardListRead(BaseModel):
    items: list[LearningCardRead]


class LearningCompleteCreate(BaseModel):
    user_id: str = Field(default="demo")
    completed_at: datetime | None = None


class GroupCreate(BaseModel):
    name: str
    max_members: int = Field(default=6, ge=2, le=6)


class GroupJoinCreate(BaseModel):
    user_id: str = Field(default="demo")


class GroupRead(BaseModel):
    id: str
    name: str
    max_members: int
    members: list[str]


class GroupChallengeViewRead(BaseModel):
    group_id: str
    name: str
    members: list[str]
    encouragements: list[str]
    has_ranking: bool


class GroupGoalOptionsRead(BaseModel):
    group_id: str
    recommended_mode: str
    secondary_modes: list[str]


class AccountDeleteCreate(BaseModel):
    user_id: str = Field(default="demo")


class AccountDeleteRead(BaseModel):
    user_id: str
    deleted_at: datetime | None
    audit_action: str


class EventCreate(BaseModel):
    user_id: str = Field(default="demo")
    amount: float = Field(gt=0)
    baseline_amount: float | None = Field(default=None, gt=0)
    idempotency_key: str | None = None
    occurred_at: datetime | None = None


class EventPreviewCreate(BaseModel):
    user_id: str = Field(default="demo")
    amount: float = Field(gt=0)
    baseline_amount: float | None = Field(default=None, gt=0)
    occurred_at: datetime | None = None


class EventPreviewRead(BaseModel):
    user_id: str
    hp: int
    growth: int
    baseline_amount: float
    last_calculated_at: datetime | None
    mutates_state: bool


class PushSubscribeCreate(BaseModel):
    user_id: str = Field(default="demo")
    endpoint: str
    p256dh: str
    auth: str


class PushSubscribeRead(BaseModel):
    id: str
    user_id: str
    endpoint: str
    subscribed: bool


class AvatarRead(BaseModel):
    user_id: str
    email: str
    avatar_type: str
    intensity: int
    text_mode: bool
    daily_alert_cap: int
    hp: int
    growth: int
    baseline_amount: float
    last_calculated_at: datetime | None


class MissionCompleteCreate(BaseModel):
    user_id: str


class MissionCompleteRead(BaseModel):
    user_id: str
    completed_count: int


class MissionRankingItemRead(BaseModel):
    rank: int
    user_id: str
    nickname: str
    completed_count: int


class MissionRankingRead(BaseModel):
    items: list[MissionRankingItemRead]


class MissionMyRankRead(BaseModel):
    rank: int
    user_id: str
    nickname: str
    completed_count: int


def create_app(store: InMemoryAvatarStore | None = None) -> FastAPI:
    app = FastAPI(title="Asset Helper API", version="0.1.0")
    app.state.store = store or InMemoryAvatarStore()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3100",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3100",
            "https://ca-danker-e2-20260601-web.salmonforest-66a190e0.koreacentral.azurecontainerapps.io",
        ],
        allow_origin_regex=r"https://.*\.azurecontainerapps\.io",
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = sorted({str(error.get("loc", ["unknown"])[-1]) for error in exc.errors()})
        message = ", ".join(fields) if fields else "request validation failed"
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": message,
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict):
            code = detail.get("code", "http_error")
            message = detail.get("message", "request failed")
            details = detail.get("details")
        else:
            code = "http_error"
            message = str(detail)
            details = None

        error_payload = {"code": code, "message": message}
        if details is not None:
            error_payload["details"] = details

        return JSONResponse(status_code=exc.status_code, content={"error": error_payload})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "asset-helper-api", "status": "ok", "health": "/health", "docs": "/docs"}

    @app.post("/auth/signup", response_model=AccountRead)
    def signup(payload: SignupCreate) -> AccountRead:
        password = payload.password or f"{payload.user_id}-pw"
        nickname = payload.nickname or payload.user_id

        try:
            profile = app.state.store.register_account(
                user_id=payload.user_id,
                password=password,
                nickname=nickname,
                email=payload.email,
                avatar_type=payload.avatar_type,
                intensity=payload.intensity,
                text_mode=payload.text_mode,
                daily_alert_cap=payload.daily_alert_cap,
                baseline_amount=payload.baseline_amount,
            )
        except ValueError as exc:
            if str(exc) == "duplicate_signup_fields":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "duplicate_signup_fields",
                        "message": "일치합니다.",
                    },
                ) from exc
            raise

        return AccountRead(
            user_id=profile.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            baseline_amount=profile.baseline_amount,
        )

    @app.post("/auth/login", response_model=LoginRead)
    def login(payload: LoginCreate) -> LoginRead:
        try:
            session = app.state.store.login(payload.user_id, password=payload.password, email=payload.email)
        except ValueError as exc:
            if str(exc) == "invalid_credentials":
                raise HTTPException(
                    status_code=401,
                    detail={
                        "code": "invalid_credentials",
                        "message": "invalid credentials",
                    },
                ) from exc
            raise

        return LoginRead(user_id=session.user_id, nickname=session.nickname, email=session.email, session_token=session.session_token)

    @app.post("/openbanking/connect", response_model=OpenBankingConnectRead)
    def connect_openbanking(payload: OpenBankingConnectCreate) -> OpenBankingConnectRead:
        try:
            connection = app.state.store.connect_openbanking(payload.user_id, payload.authorization_code)
        except Exception as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "user_not_found",
                        "message": "user not found",
                    },
                ) from exc
            raise

        return OpenBankingConnectRead(
            user_id=connection.user_id,
            access_token_enc=connection.access_token_enc,
            refresh_token_enc=connection.refresh_token_enc,
            expires_at=connection.expires_at,
            accounts=[
                OpenBankingAccountRead(
                    account_id=account.account_id,
                    account_name=account.account_name,
                    balance=account.balance,
                )
                for account in connection.accounts
            ],
        )

    @app.get("/me", response_model=AccountRead)
    def get_me(user_id: str = "demo") -> AccountRead:
        profile = app.state.store.get_profile(user_id)
        return AccountRead(
            user_id=profile.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            baseline_amount=profile.baseline_amount,
        )

    @app.patch("/me/settings", response_model=AccountRead)
    def update_me_settings(payload: SettingsUpdate) -> AccountRead:
        profile = app.state.store.update_profile_settings(
            payload.user_id,
            avatar_type=payload.avatar_type,
            intensity=payload.intensity,
            text_mode=payload.text_mode,
            daily_alert_cap=payload.daily_alert_cap,
            baseline_amount=payload.baseline_amount,
        )
        return AccountRead(
            user_id=profile.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            baseline_amount=profile.baseline_amount,
        )

    @app.post("/account/delete", response_model=AccountDeleteRead)
    def delete_account(payload: AccountDeleteCreate) -> AccountDeleteRead:
        result = app.state.store.delete_account(payload.user_id)
        return AccountDeleteRead(
            user_id=result.user_id,
            deleted_at=result.deleted_at,
            audit_action=result.audit_action,
        )

    @app.post("/thresholds", response_model=ThresholdRead)
    def create_threshold(payload: ThresholdCreate) -> ThresholdRead:
        threshold = app.state.store.create_threshold(payload.user_id, payload.kind, payload.value)
        return ThresholdRead(user_id=threshold.user_id, kind=threshold.kind, value=threshold.value)

    @app.get("/notifications", response_model=NotificationListRead)
    def get_notifications(user_id: str = "demo") -> NotificationListRead:
        notifications = app.state.store.list_notifications(user_id)
        return NotificationListRead(
            items=[
                NotificationRead(
                    user_id=item.user_id,
                    kind=item.kind,
                    payload=item.payload,
                    sent_at=item.sent_at,
                    suppressed_reason=item.suppressed_reason,
                )
                for item in notifications
            ]
        )

    @app.post("/openbanking/poll", response_model=OpenBankingPollRead)
    def poll_openbanking(payload: OpenBankingPollCreate) -> OpenBankingPollRead:
        now = payload.now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        try:
            result = app.state.store.poll_openbanking(payload.user_id, now=now)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            if str(exc) == "openbanking_not_connected":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "openbanking_not_connected", "message": "openbanking is not connected"},
                ) from exc
            raise

        return OpenBankingPollRead(
            user_id=result.user_id,
            polled=result.polled,
            reason=result.reason,
            accounts=[
                OpenBankingAccountRead(account_id=account.account_id, account_name=account.account_name, balance=account.balance)
                for account in result.accounts
            ],
            last_polled_at=result.last_polled_at,
            daily_poll_count=result.daily_poll_count,
        )

    @app.post("/openbanking/refresh", response_model=OpenBankingRefreshRead)
    def refresh_openbanking(payload: OpenBankingRefreshCreate) -> OpenBankingRefreshRead:
        try:
            result = app.state.store.refresh_openbanking(payload.user_id, now=payload.now)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            if str(exc) == "openbanking_not_connected":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "openbanking_not_connected", "message": "openbanking is not connected"},
                ) from exc
            raise

        connection = result.connection
        return OpenBankingRefreshRead(
            user_id=result.user_id,
            refreshed=result.refreshed,
            reason=result.reason,
            connection=OpenBankingConnectRead(
                user_id=connection.user_id,
                access_token_enc=connection.access_token_enc,
                refresh_token_enc=connection.refresh_token_enc,
                expires_at=connection.expires_at,
                accounts=[
                    OpenBankingAccountRead(account_id=account.account_id, account_name=account.account_name, balance=account.balance)
                    for account in connection.accounts
                ],
            ),
        )

    @app.post("/openbanking/transactions", response_model=BankApiTransactionQueryRead)
    def query_openbanking_transactions(payload: BankApiTransactionQueryCreate) -> BankApiTransactionQueryRead:
        try:
            result = app.state.store.fetch_bankapi_transactions(
                bank_code=payload.bank_code,
                account_number=payload.account_number,
                account_password=payload.account_password,
                resident_number=payload.resident_number,
                start_date=payload.start_date,
                end_date=payload.end_date,
            )
        except ValueError as exc:
            if str(exc) == "bankapi_credentials_missing":
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "bankapi_credentials_missing",
                        "message": "Set BANKAPI_API_KEY and BANKAPI_SECRET_KEY environment variables",
                    },
                ) from exc
            if str(exc).startswith("bankapi_timeout:"):
                _, _, timeout_message = str(exc).partition(":")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "code": "bankapi_timeout",
                        "message": timeout_message or "Bank API request timed out",
                    },
                ) from exc
            if str(exc).startswith("bankapi_http_"):
                _, tail = str(exc).split("bankapi_http_", maxsplit=1)
                status_code_str, _, upstream_message = tail.partition(":")
                status_code = int(status_code_str) if status_code_str.isdigit() else 502
                mapped_status_code = status_code if 400 <= status_code <= 599 else 502
                raise HTTPException(
                    status_code=mapped_status_code,
                    detail={
                        "code": "bankapi_upstream_error",
                        "message": upstream_message or "bankapi request failed",
                        "upstream_status": status_code,
                    },
                ) from exc
            if str(exc) == "bankapi_request_failed":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_request_failed",
                        "message": "Failed to reach Bank API upstream",
                    },
                ) from exc
            if str(exc) == "bankapi_invalid_response":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_invalid_response",
                        "message": "Bank API returned an invalid response",
                    },
                ) from exc
            raise

        return BankApiTransactionQueryRead(
            success=bool(result.get("success")),
            transactions=result.get("transactions") or [],
            accountInfo=result.get("accountInfo"),
        )

    @app.post("/bankapi/accounts/register", response_model=BankApiAccountRegisterRead)
    def register_bankapi_account(payload: BankApiAccountRegisterCreate) -> BankApiAccountRegisterRead:
        try:
            result = app.state.store.register_bankapi_link(
                user_id=payload.user_id,
                bank_code=payload.bank_code,
                account_number=payload.account_number,
                account_password=payload.account_password,
                resident_number=payload.resident_number,
            )
            summary = app.state.store.get_bankapi_link_summary(payload.user_id)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "user_not_found", "message": "사용자를 찾을 수 없습니다. 먼저 로그인 또는 회원가입을 진행해 주세요."},
                ) from exc
            if str(exc) == "bankapi_credentials_missing":
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "bankapi_credentials_missing",
                        "message": "Set BANKAPI_API_KEY and BANKAPI_SECRET_KEY environment variables",
                    },
                ) from exc
            if str(exc).startswith("bankapi_timeout:"):
                _, _, timeout_message = str(exc).partition(":")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "code": "bankapi_timeout",
                        "message": timeout_message or "Bank API request timed out",
                    },
                ) from exc
            if str(exc).startswith("bankapi_http_"):
                _, tail = str(exc).split("bankapi_http_", maxsplit=1)
                status_code_str, _, upstream_message = tail.partition(":")
                status_code = int(status_code_str) if status_code_str.isdigit() else 502
                mapped_status_code = status_code if 400 <= status_code <= 599 else 502
                raise HTTPException(
                    status_code=mapped_status_code,
                    detail={
                        "code": "bankapi_upstream_error",
                        "message": upstream_message or "bankapi request failed",
                        "upstream_status": status_code,
                    },
                ) from exc
            if str(exc) == "bankapi_request_failed":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_request_failed",
                        "message": "Failed to reach Bank API upstream",
                    },
                ) from exc
            if str(exc) == "bankapi_invalid_response":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_invalid_response",
                        "message": "Bank API returned an invalid response",
                    },
                ) from exc
            raise

        if summary is None:
            raise HTTPException(status_code=500, detail={"code": "bankapi_link_save_failed", "message": "bankapi link not saved"})

        return BankApiAccountRegisterRead(
            success=bool(result.get("success", True)),
            message=(result.get("message") if isinstance(result, dict) else None),
            data=(result.get("data") if isinstance(result, dict) else None),
            link=BankApiLinkSummaryRead(**summary),
        )

    @app.get("/bankapi/accounts/me", response_model=BankApiLinkSummaryRead)
    def get_bankapi_account_link(user_id: str) -> BankApiLinkSummaryRead:
        summary = app.state.store.get_bankapi_link_summary(user_id)
        if summary is None:
            raise HTTPException(status_code=404, detail={"code": "bankapi_link_not_found", "message": "bankapi link not found"})
        return BankApiLinkSummaryRead(**summary)

    @app.delete("/bankapi/accounts/me", response_model=BankApiAccountDeleteRead)
    def delete_bankapi_account_link(user_id: str) -> BankApiAccountDeleteRead:
        try:
            result = app.state.store.delete_bankapi_link(user_id)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            if str(exc) == "bankapi_link_not_found":
                raise HTTPException(status_code=404, detail={"code": "bankapi_link_not_found", "message": "bankapi link not found"}) from exc
            raise

        return BankApiAccountDeleteRead(**result)

    @app.post("/bankapi/poll", response_model=BankApiPollRead)
    def poll_bankapi_account(user_id: str) -> BankApiPollRead:
        try:
            result = app.state.store.poll_bankapi_linked_account(user_id)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            if str(exc) == "bankapi_link_not_found":
                raise HTTPException(status_code=404, detail={"code": "bankapi_link_not_found", "message": "bankapi link not found"}) from exc
            if str(exc) == "bankapi_credentials_missing":
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "bankapi_credentials_missing",
                        "message": "Set BANKAPI_API_KEY and BANKAPI_SECRET_KEY environment variables",
                    },
                ) from exc
            if str(exc).startswith("bankapi_timeout:"):
                _, _, timeout_message = str(exc).partition(":")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "code": "bankapi_timeout",
                        "message": timeout_message or "Bank API request timed out",
                    },
                ) from exc
            if str(exc).startswith("bankapi_http_"):
                _, tail = str(exc).split("bankapi_http_", maxsplit=1)
                status_code_str, _, upstream_message = tail.partition(":")
                status_code = int(status_code_str) if status_code_str.isdigit() else 502
                mapped_status_code = status_code if 400 <= status_code <= 599 else 502
                raise HTTPException(
                    status_code=mapped_status_code,
                    detail={
                        "code": "bankapi_upstream_error",
                        "message": upstream_message or "bankapi request failed",
                        "upstream_status": status_code,
                    },
                ) from exc
            if str(exc) == "bankapi_request_failed":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_request_failed",
                        "message": "Failed to reach Bank API upstream",
                    },
                ) from exc
            if str(exc) == "bankapi_invalid_response":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_invalid_response",
                        "message": "Bank API returned an invalid response",
                    },
                ) from exc
            if str(exc) == "bankapi_upstream_unsuccessful":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "bankapi_upstream_unsuccessful",
                        "message": "Bank API returned success=false",
                    },
                ) from exc
            raise

        return BankApiPollRead(
            user_id=str(result.get("user_id", user_id)),
            current_balance=int(result.get("current_balance", 0)),
            new_transaction_count=int(result.get("new_transaction_count", 0)),
            total_hp_drop=int(result.get("total_hp_drop", 0)),
            hp=int(result.get("hp", 100)),
            polled_at=str(result.get("polled_at", "")),
        )

    @app.get("/bankapi/balance-history", response_model=BankApiBalanceHistoryRead)
    def get_bankapi_balance_history(user_id: str, limit: int = 30) -> BankApiBalanceHistoryRead:
        points = app.state.store.list_bankapi_balance_history(user_id, limit=limit)
        return BankApiBalanceHistoryRead(items=[BankApiBalancePointRead(**point) for point in points])

    @app.get("/bankapi/transactions", response_model=BankApiTransactionHistoryRead)
    def get_bankapi_transaction_history(user_id: str, limit: int = 50) -> BankApiTransactionHistoryRead:
        items = app.state.store.list_bankapi_transaction_history(user_id, limit=limit)
        return BankApiTransactionHistoryRead(items=[BankApiTransactionRead(**item) for item in items if isinstance(item, dict)])

    @app.post("/auto-save/rules", response_model=AutoSaveRuleRead)
    def create_auto_save_rule(payload: AutoSaveRuleCreate) -> AutoSaveRuleRead:
        try:
            rule = app.state.store.create_auto_save_rule(
                user_id=payload.user_id,
                amount=payload.amount,
                src_account=payload.src_account,
                dst_account=payload.dst_account,
                balance_floor=payload.balance_floor,
            )
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "user_not_found", "message": "user not found"},
                ) from exc
            raise

        return AutoSaveRuleRead(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status=rule.status,
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
        )

    @app.get("/auto-save/rules/{rule_id}/preview", response_model=AutoSavePreviewRead)
    def preview_auto_save_rule(rule_id: str) -> AutoSavePreviewRead:
        try:
            preview = app.state.store.preview_auto_save_rule(rule_id)
        except ValueError as exc:
            if str(exc) == "auto_save_rule_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "auto_save_rule_not_found", "message": "auto save rule not found"},
                ) from exc
            raise

        return AutoSavePreviewRead(rule_id=preview.rule_id, amount=preview.amount, next_run_at=preview.next_run_at, status=preview.status)

    @app.patch("/auto-save/rules/{rule_id}", response_model=AutoSaveRuleRead)
    def update_auto_save_rule(rule_id: str, payload: AutoSaveRuleAction) -> AutoSaveRuleRead:
        if payload.action not in {"pause", "resume"}:
            raise HTTPException(
                status_code=400,
                detail={"code": "invalid_action", "message": "unsupported auto save action"},
            )

        try:
            if payload.action == "pause":
                rule = app.state.store.pause_auto_save_rule(rule_id)
            else:
                rule = app.state.store.resume_auto_save_rule(rule_id)
        except ValueError as exc:
            if str(exc) == "auto_save_rule_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "auto_save_rule_not_found", "message": "auto save rule not found"},
                ) from exc
            if str(exc) == "auto_save_rule_not_paused":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "auto_save_rule_not_paused", "message": "auto save rule is not paused"},
                ) from exc
            raise

        return AutoSaveRuleRead(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status=rule.status,
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
        )

    @app.post("/auto-save/rules/{rule_id}/cancel", response_model=AutoSaveRuleRead)
    def cancel_auto_save_rule(rule_id: str, payload: AutoSaveCancelCreate | None = None) -> AutoSaveRuleRead:
        try:
            rule = app.state.store.cancel_auto_save_rule(rule_id, now=(payload.now if payload is not None else None))
        except ValueError as exc:
            if str(exc) == "auto_save_rule_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "auto_save_rule_not_found", "message": "auto save rule not found"},
                ) from exc
            if str(exc) == "grace_period_expired":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "grace_period_expired", "message": "grace period expired"},
                ) from exc
            raise

        return AutoSaveRuleRead(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status=rule.status,
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
        )

    @app.post("/auto-save/rules/{rule_id}/evaluate", response_model=AutoSaveEvaluateRead)
    def evaluate_auto_save_rule(rule_id: str, payload: AutoSaveEvaluateCreate) -> AutoSaveEvaluateRead:
        try:
            rule, notification = app.state.store.evaluate_auto_save_rule(rule_id, balance=payload.balance, now=payload.now)
        except ValueError as exc:
            if str(exc) == "auto_save_rule_not_found":
                raise HTTPException(
                    status_code=404,
                    detail={"code": "auto_save_rule_not_found", "message": "auto save rule not found"},
                ) from exc
            raise

        notification_read = None
        if notification is not None:
            notification_read = AutoSaveNotificationRead(
                user_id=notification.user_id,
                kind=notification.kind,
                payload=notification.payload,
                sent_at=notification.sent_at,
            )

        return AutoSaveEvaluateRead(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status=rule.status,
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
            notification=notification_read,
        )

    @app.get("/learning/cards", response_model=LearningCardListRead)
    def get_learning_cards() -> LearningCardListRead:
        cards = app.state.store.list_learning_cards()
        return LearningCardListRead(
            items=[
                LearningCardRead(id=card.id, title=card.title, body=card.body, duration_sec=card.duration_sec)
                for card in cards
            ]
        )

    @app.post("/learning/cards/{card_id}/complete", response_model=AvatarRead)
    def complete_learning_card(card_id: str, payload: LearningCompleteCreate) -> AvatarRead:
        completed_at = payload.completed_at or datetime.now(timezone.utc)
        if completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)

        profile = app.state.store.get_profile(payload.user_id)
        avatar, _completed = app.state.store.complete_learning_card(payload.user_id, card_id, completed_at)
        return AvatarRead(
            user_id=avatar.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            hp=avatar.hp,
            growth=avatar.growth,
            baseline_amount=avatar.baseline_amount,
            last_calculated_at=avatar.last_calculated_at,
        )

    @app.post("/groups", response_model=GroupRead)
    def create_group(payload: GroupCreate) -> GroupRead:
        group = app.state.store.create_group(name=payload.name, max_members=payload.max_members)
        return GroupRead(id=group.id, name=group.name, max_members=group.max_members, members=group.members)

    @app.post("/groups/{group_id}/members", response_model=GroupRead)
    def join_group(group_id: str, payload: GroupJoinCreate) -> GroupRead:
        try:
            group = app.state.store.join_group(group_id, payload.user_id)
        except ValueError as exc:
            if str(exc) == "max_members_reached":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "max_members_reached",
                        "message": "maximum group size reached",
                    },
                ) from exc
            raise

        return GroupRead(id=group.id, name=group.name, max_members=group.max_members, members=group.members)

    @app.get("/groups/{group_id}/challenge-view", response_model=GroupChallengeViewRead)
    def get_group_challenge_view(group_id: str) -> GroupChallengeViewRead:
        try:
            view = app.state.store.get_group_challenge_view(group_id)
        except ValueError as exc:
            if str(exc) == "group_not_found":
                raise HTTPException(status_code=404, detail={"code": "group_not_found", "message": "group not found"}) from exc
            raise

        return GroupChallengeViewRead(
            group_id=view.group_id,
            name=view.name,
            members=view.members,
            encouragements=view.encouragements,
            has_ranking=view.has_ranking,
        )

    @app.get("/groups/{group_id}/goal-options", response_model=GroupGoalOptionsRead)
    def get_group_goal_options(group_id: str) -> GroupGoalOptionsRead:
        try:
            options = app.state.store.get_group_goal_options(group_id)
        except ValueError as exc:
            if str(exc) == "group_not_found":
                raise HTTPException(status_code=404, detail={"code": "group_not_found", "message": "group not found"}) from exc
            raise

        return GroupGoalOptionsRead(
            group_id=options.group_id,
            recommended_mode=options.recommended_mode,
            secondary_modes=options.secondary_modes,
        )

    @app.get("/avatar", response_model=AvatarRead)
    def get_avatar(user_id: str = "demo") -> AvatarRead:
        profile = app.state.store.get_profile(user_id)
        avatar = app.state.store.get_avatar(user_id)
        return AvatarRead(
            user_id=avatar.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            hp=avatar.hp,
            growth=avatar.growth,
            baseline_amount=avatar.baseline_amount,
            last_calculated_at=avatar.last_calculated_at,
        )

    @app.post("/events", response_model=AvatarRead)
    def create_event(payload: EventCreate) -> AvatarRead:
        occurred_at = payload.occurred_at or datetime.now(timezone.utc)
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        event = MoneyEvent(
            user_id=payload.user_id,
            amount=payload.amount,
            occurred_at=occurred_at,
        )
        profile = app.state.store.get_profile(payload.user_id)
        if payload.baseline_amount is not None:
            profile.baseline_amount = payload.baseline_amount
        try:
            updated_avatar = app.state.store.record_event(event, idempotency_key=payload.idempotency_key)
        except ValueError as exc:
            if str(exc) == "duplicate_event":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "duplicate_event",
                        "message": "duplicate idempotency key",
                    },
                ) from exc
            raise

        return AvatarRead(
            user_id=updated_avatar.user_id,
            email=profile.email,
            avatar_type=profile.avatar_type,
            intensity=profile.intensity,
            text_mode=profile.text_mode,
            daily_alert_cap=profile.daily_alert_cap,
            hp=updated_avatar.hp,
            growth=updated_avatar.growth,
            baseline_amount=updated_avatar.baseline_amount,
            last_calculated_at=updated_avatar.last_calculated_at,
        )

    @app.post("/events/preview", response_model=EventPreviewRead)
    def preview_event(payload: EventPreviewCreate) -> EventPreviewRead:
        occurred_at = payload.occurred_at or datetime.now(timezone.utc)
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        preview_avatar = app.state.store.preview_event(
            user_id=payload.user_id,
            amount=payload.amount,
            baseline_amount=payload.baseline_amount,
            occurred_at=occurred_at,
        )
        return EventPreviewRead(
            user_id=preview_avatar.user_id,
            hp=preview_avatar.hp,
            growth=preview_avatar.growth,
            baseline_amount=preview_avatar.baseline_amount,
            last_calculated_at=preview_avatar.last_calculated_at,
            mutates_state=False,
        )

    @app.post("/events/simulate", response_model=EventPreviewRead)
    def simulate_event(payload: EventPreviewCreate) -> EventPreviewRead:
        return preview_event(payload)

    @app.post("/missions/complete", response_model=MissionCompleteRead)
    def complete_mission(payload: MissionCompleteCreate) -> MissionCompleteRead:
        try:
            completed_count = app.state.store.complete_mission(payload.user_id)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            raise

        return MissionCompleteRead(user_id=payload.user_id, completed_count=completed_count)

    @app.get("/missions/ranking", response_model=MissionRankingRead)
    def get_mission_ranking(limit: int = 20) -> MissionRankingRead:
        ranking_items = app.state.store.list_mission_ranking(limit=limit)
        return MissionRankingRead(
            items=[
                MissionRankingItemRead(
                    rank=int(item["rank"]),
                    user_id=str(item["user_id"]),
                    nickname=str(item["nickname"]),
                    completed_count=int(item["completed_count"]),
                )
                for item in ranking_items
            ]
        )

    @app.get("/missions/ranking/me", response_model=MissionMyRankRead)
    def get_my_mission_rank(user_id: str) -> MissionMyRankRead:
        try:
            my_rank = app.state.store.get_mission_rank(user_id)
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            raise

        return MissionMyRankRead(
            rank=int(my_rank["rank"]),
            user_id=str(my_rank["user_id"]),
            nickname=str(my_rank["nickname"]),
            completed_count=int(my_rank["completed_count"]),
        )

    @app.post("/push/subscribe", response_model=PushSubscribeRead)
    def push_subscribe(payload: PushSubscribeCreate) -> PushSubscribeRead:
        try:
            subscription = app.state.store.subscribe_push(
                user_id=payload.user_id,
                endpoint=payload.endpoint,
                p256dh=payload.p256dh,
                auth=payload.auth,
            )
        except ValueError as exc:
            if str(exc) == "user_not_found":
                raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "user not found"}) from exc
            raise

        return PushSubscribeRead(id=subscription.id, user_id=subscription.user_id, endpoint=subscription.endpoint, subscribed=True)

    return app

app = create_app()
