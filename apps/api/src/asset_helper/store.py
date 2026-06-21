from __future__ import annotations

import os
import pickle
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4

from .domain.alerts import NotificationRecord, ThresholdRule, is_threshold_exceeded, should_suppress_alert
from .domain.auth import AuthSession, UserCredential
from .domain.account import AccountDeletionResult
from .domain.groups import Group, create_group, join_group
from .domain.group_challenge import GroupChallengeView, GroupGoalOptions, build_group_challenge_view, build_group_goal_options
from .domain.push import PushSubscription, create_push_subscription
from .domain.auto_save import AutoSaveLog, AutoSaveNotification, AutoSaveRule, build_auto_save_log, create_auto_save_rule, evaluate_auto_save_rule, pause_auto_save_rule, preview_auto_save_rule
from .domain.openbanking import BankAccount, OpenBankingConnection, OpenBankingPollResult, OpenBankingPollState, OpenBankingRefreshResult, make_connection, make_poll_state, poll_connection, refresh_connection
from .domain.learning import LearningCard, LearningProgress, complete_learning_card, create_learning_cards, get_learning_card
from .domain.hp import recalculate_avatar
from .domain.models import AuditLog, AvatarState, MoneyEvent
from .domain.profile import UserProfile, create_profile, update_profile_settings


class InMemoryAvatarStore:
    def __init__(self, db_path: str | None = None) -> None:
        default_db_path = Path.cwd() / "asset-helper.sqlite3"
        self._db_path = Path(db_path or os.environ.get("ASSET_HELPER_DB_PATH") or default_db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_lock = RLock()
        with sqlite3.connect(self._db_path) as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS store_snapshot (
                    snapshot_id INTEGER PRIMARY KEY CHECK (snapshot_id = 1),
                    payload BLOB NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id TEXT PRIMARY KEY,
                    password TEXT NOT NULL UNIQUE,
                    nickname TEXT NOT NULL,
                    email TEXT NOT NULL,
                    avatar_type TEXT NOT NULL,
                    intensity INTEGER NOT NULL,
                    text_mode INTEGER NOT NULL,
                    daily_alert_cap INTEGER NOT NULL,
                    baseline_amount REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_stats (
                    user_id TEXT PRIMARY KEY,
                    completed_count INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES accounts(user_id)
                )
                """
            )
            db.commit()

        self._profiles: dict[str, UserProfile] = {}
        self._avatars: dict[str, AvatarState] = {}
        self._seen_event_keys: set[tuple[str, str]] = set()
        self._thresholds: dict[str, ThresholdRule] = {}
        self._notifications: list[NotificationRecord] = []
        self._learning_cards: list[LearningCard] = create_learning_cards()
        self._learning_progress: dict[str, set[str]] = {}
        self._groups: dict[str, Group] = {}
        self._push_subscriptions: dict[str, list[PushSubscription]] = {}
        self._audit_logs: list[AuditLog] = []
        self._sessions: dict[str, AuthSession] = {}
        self._credentials: dict[str, UserCredential] = {}
        self._password_index: dict[str, str] = {}
        self._nickname_index: dict[str, str] = {}
        self._openbanking_connections: dict[str, OpenBankingConnection] = {}
        self._openbanking_poll_state: dict[str, OpenBankingPollState] = {}
        self._auto_save_rules: dict[str, AutoSaveRule] = {}
        self._auto_save_notifications: list[AutoSaveNotification] = []
        self._auto_save_logs: list[AutoSaveLog] = []
        self._auto_save_seen_keys: set[str] = set()

        self._load_snapshot()
        self._load_accounts_from_db()

    @staticmethod
    def _to_stored_password(user_id: str, password: str) -> str:
        # Keep plaintext model for MVP while avoiding cross-user UNIQUE collisions.
        return f"{user_id}::{password}"

    def _load_accounts_from_db(self) -> None:
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            rows = db.execute(
                """
                SELECT user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount
                FROM accounts
                """
            ).fetchall()

            # Backfill relational account table from legacy snapshot data once.
            if not rows and self._credentials:
                for credential in self._credentials.values():
                    profile = self._profiles.get(credential.user_id)
                    if profile is None:
                        continue
                    db.execute(
                        """
                        INSERT OR IGNORE INTO accounts (
                            user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            credential.user_id,
                            credential.password,
                            credential.nickname,
                            profile.email,
                            profile.avatar_type,
                            profile.intensity,
                            1 if profile.text_mode else 0,
                            profile.daily_alert_cap,
                            profile.baseline_amount,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                db.commit()
                rows = db.execute(
                    """
                    SELECT user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount
                    FROM accounts
                    """
                ).fetchall()

            for row in rows:
                user_id = row[0]
                db.execute(
                    """
                    INSERT OR IGNORE INTO mission_stats (user_id, completed_count, updated_at)
                    VALUES (?, 0, ?)
                    """,
                    (user_id, datetime.now(timezone.utc).isoformat()),
                )
            db.commit()

        self._credentials = {}
        self._password_index = {}
        for row in rows:
            user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount = row
            self._credentials[user_id] = UserCredential(user_id=user_id, password=password, nickname=nickname)
            self._password_index[password] = user_id
            self._nickname_index[nickname] = user_id
            if user_id not in self._profiles:
                self._profiles[user_id] = create_profile(
                    email=email,
                    user_id=user_id,
                    avatar_type=avatar_type,
                    intensity=intensity,
                    text_mode=bool(text_mode),
                    daily_alert_cap=daily_alert_cap,
                    baseline_amount=baseline_amount,
                )

    def _snapshot_state(self) -> bytes:
        state = {key: value for key, value in self.__dict__.items() if key not in {"_db_path", "_db_lock"}}
        return pickle.dumps(state)

    def _load_snapshot(self) -> None:
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            row = db.execute("SELECT payload FROM store_snapshot WHERE snapshot_id = 1").fetchone()
        if row is None:
            self._persist_snapshot()
            return

        state = pickle.loads(row[0])
        self.__dict__.update(state)

    def _persist_snapshot(self) -> None:
        payload = self._snapshot_state()
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            db.execute(
                """
                INSERT INTO store_snapshot (snapshot_id, payload, updated_at)
                VALUES (1, ?, ?)
                ON CONFLICT(snapshot_id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (payload, datetime.now(timezone.utc).isoformat()),
            )
            db.commit()

    def create_profile(
        self,
        *,
        email: str,
        user_id: str = "demo",
        avatar_type: str = "plant",
        intensity: int = 1,
        text_mode: bool = False,
        daily_alert_cap: int = 3,
        baseline_amount: float = 30000.0,
    ) -> UserProfile:
        profile = create_profile(
            email=email,
            user_id=user_id,
            avatar_type=avatar_type,
            intensity=intensity,
            text_mode=text_mode,
            daily_alert_cap=daily_alert_cap,
            baseline_amount=baseline_amount,
        )
        self._profiles[user_id] = profile
        avatar = self._avatars.get(user_id) or AvatarState(user_id=user_id)
        avatar.baseline_amount = profile.baseline_amount
        self._avatars[user_id] = avatar
        self._persist_snapshot()
        return profile

    def register_account(
        self,
        *,
        user_id: str,
        password: str,
        nickname: str,
        email: str = "",
        avatar_type: str = "plant",
        intensity: int = 1,
        text_mode: bool = False,
        daily_alert_cap: int = 3,
        baseline_amount: float = 30000.0,
    ) -> UserProfile:
        stored_password = self._to_stored_password(user_id, password)
        try:
            with self._db_lock, sqlite3.connect(self._db_path) as db:
                db.execute(
                    """
                    INSERT INTO accounts (
                        user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        stored_password,
                        nickname,
                        email,
                        avatar_type,
                        intensity,
                        1 if text_mode else 0,
                        daily_alert_cap,
                        baseline_amount,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                db.execute(
                    """
                    INSERT OR IGNORE INTO mission_stats (user_id, completed_count, updated_at)
                    VALUES (?, 0, ?)
                    """,
                    (user_id, datetime.now(timezone.utc).isoformat()),
                )
                db.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("duplicate_signup_fields") from exc

        profile = self.create_profile(
            email=email,
            user_id=user_id,
            avatar_type=avatar_type,
            intensity=intensity,
            text_mode=text_mode,
            daily_alert_cap=daily_alert_cap,
            baseline_amount=baseline_amount,
        )

        credential = UserCredential(user_id=user_id, password=password, nickname=nickname)
        self._credentials[user_id] = credential
        self._password_index[stored_password] = user_id
        self._nickname_index[nickname] = user_id
        self._persist_snapshot()
        return profile

    def get_profile(self, user_id: str) -> UserProfile:
        profile = self._profiles.get(user_id)
        if profile is None:
            profile = create_profile(email="", user_id=user_id)
            self._profiles[user_id] = profile
            self._persist_snapshot()
        return profile

    def login(self, user_id: str, password: str | None = None, email: str | None = None) -> AuthSession:
        if password is None and email is None:
            raise ValueError("invalid_credentials")

        with self._db_lock, sqlite3.connect(self._db_path) as db:
            if password is not None:
                stored_password = self._to_stored_password(user_id, password)
                row = db.execute(
                    """
                    SELECT user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount
                    FROM accounts
                    WHERE user_id = ? AND password = ?
                    """,
                    (user_id, stored_password),
                ).fetchone()
                if row is None:
                    # Backward compatibility for already-created legacy accounts.
                    row = db.execute(
                        """
                        SELECT user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount
                        FROM accounts
                        WHERE user_id = ? AND password = ?
                        """,
                        (user_id, password),
                    ).fetchone()
            else:
                row = db.execute(
                    """
                    SELECT user_id, password, nickname, email, avatar_type, intensity, text_mode, daily_alert_cap, baseline_amount
                    FROM accounts
                    WHERE user_id = ? AND email = ?
                    """,
                    (user_id, email),
                ).fetchone()

        if row is None:
            raise ValueError("invalid_credentials")

        (
            db_user_id,
            db_password,
            db_nickname,
            db_email,
            db_avatar_type,
            db_intensity,
            db_text_mode,
            db_daily_alert_cap,
            db_baseline_amount,
        ) = row

        # Keep in-memory mirrors synced so downstream features don't fail after successful login.
        self._credentials[db_user_id] = UserCredential(user_id=db_user_id, password=db_password, nickname=db_nickname)
        self._password_index[db_password] = db_user_id
        self._nickname_index[db_nickname] = db_user_id
        if db_user_id not in self._profiles:
            self._profiles[db_user_id] = create_profile(
                email=db_email,
                user_id=db_user_id,
                avatar_type=db_avatar_type,
                intensity=db_intensity,
                text_mode=bool(db_text_mode),
                daily_alert_cap=db_daily_alert_cap,
                baseline_amount=db_baseline_amount,
            )

        session = AuthSession(user_id=db_user_id, nickname=db_nickname, email=db_email, session_token=uuid4().hex)
        self._sessions[session.session_token] = session
        self._persist_snapshot()
        return session

    def delete_account(self, user_id: str) -> AccountDeletionResult:
        profile = self.get_profile(user_id)
        deleted_at = profile.deleted_at or datetime.now()
        profile.deleted_at = deleted_at
        self._profiles[user_id] = profile

        audit_log = AuditLog(
            user_id=user_id,
            action="account_delete_requested",
            target="account",
            at=datetime.now(),
            meta={"deleted_at": deleted_at.isoformat()},
        )
        self._audit_logs.append(audit_log)
        self._persist_snapshot()
        return AccountDeletionResult(user_id=user_id, deleted_at=deleted_at, audit_action=audit_log.action)

    def list_audit_logs(self, user_id: str) -> list[AuditLog]:
        return [audit_log for audit_log in self._audit_logs if audit_log.user_id == user_id]

    def get_session(self, session_token: str) -> AuthSession | None:
        return self._sessions.get(session_token)

    def connect_openbanking(self, user_id: str, authorization_code: str) -> OpenBankingConnection:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise ValueError("user_not_found")

        connection = make_connection(user_id, authorization_code)
        self._openbanking_connections[user_id] = connection
        self._openbanking_poll_state[user_id] = make_poll_state()
        self._persist_snapshot()
        return connection

    def get_openbanking_connection(self, user_id: str) -> OpenBankingConnection | None:
        return self._openbanking_connections.get(user_id)

    def poll_openbanking(self, user_id: str, now: datetime, daily_cap: int = 200) -> OpenBankingPollResult:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise ValueError("user_not_found")

        connection = self._openbanking_connections.get(user_id)
        if connection is None:
            raise ValueError("openbanking_not_connected")

        state = self._openbanking_poll_state.get(user_id) or make_poll_state()
        updated_state, result = poll_connection(connection, state, now=now, daily_cap=daily_cap)
        self._openbanking_poll_state[user_id] = updated_state
        self._persist_snapshot()
        return result

    def refresh_openbanking(self, user_id: str, now: datetime | None = None) -> OpenBankingRefreshResult:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise ValueError("user_not_found")

        connection = self._openbanking_connections.get(user_id)
        if connection is None:
            raise ValueError("openbanking_not_connected")

        result = refresh_connection(connection, now=now)
        self._openbanking_connections[user_id] = result.connection
        self._persist_snapshot()
        return result

    def create_auto_save_rule(
        self,
        *,
        user_id: str,
        amount: int,
        src_account: str,
        dst_account: str,
        balance_floor: int,
        now: datetime | None = None,
    ) -> AutoSaveRule:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise ValueError("user_not_found")

        rule = create_auto_save_rule(
            user_id=user_id,
            amount=amount,
            src_account=src_account,
            dst_account=dst_account,
            balance_floor=balance_floor,
            now=now,
        )
        self._auto_save_rules[rule.id] = rule
        self._persist_snapshot()
        return rule

    def preview_auto_save_rule(self, rule_id: str):
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")
        return preview_auto_save_rule(rule)

    def pause_auto_save_rule(self, rule_id: str) -> AutoSaveRule:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")

        updated_rule = pause_auto_save_rule(rule)
        self._auto_save_rules[rule_id] = updated_rule
        self._persist_snapshot()
        return updated_rule

    def resume_auto_save_rule(self, rule_id: str) -> AutoSaveRule:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")

        if rule.status != "paused":
            raise ValueError("auto_save_rule_not_paused")

        resumed_rule = AutoSaveRule(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status="active",
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
        )
        self._auto_save_rules[rule_id] = resumed_rule
        self._persist_snapshot()
        return resumed_rule

    def cancel_auto_save_rule(self, rule_id: str, now: datetime | None = None) -> AutoSaveRule:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        if rule.status != "pending_grace" or current_time > rule.grace_until:
            raise ValueError("grace_period_expired")

        cancelled_rule = AutoSaveRule(
            id=rule.id,
            user_id=rule.user_id,
            amount=rule.amount,
            src_account=rule.src_account,
            dst_account=rule.dst_account,
            balance_floor=rule.balance_floor,
            status="cancelled",
            next_run_at=rule.next_run_at,
            grace_until=rule.grace_until,
        )
        self._auto_save_rules[rule_id] = cancelled_rule
        self._persist_snapshot()
        return cancelled_rule

    def evaluate_auto_save_rule(self, rule_id: str, balance: int, now: datetime | None = None) -> tuple[AutoSaveRule, AutoSaveNotification | None]:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")

        updated_rule, notification = evaluate_auto_save_rule(rule, balance=balance, now=now)
        self._auto_save_rules[rule_id] = updated_rule
        if notification is not None:
            self._auto_save_notifications.append(notification)

        log_reason = "balance_below_threshold" if balance < rule.balance_floor else "executed"
        self._auto_save_logs.append(
            build_auto_save_log(
                rule_id=rule.id,
                idempotency_key=None,
                status="skipped" if balance < rule.balance_floor else "executed",
                reason=log_reason,
                executed_at=now or datetime.now(timezone.utc),
            )
        )
        self._persist_snapshot()
        return updated_rule, notification

    def execute_auto_save_rule(
        self,
        rule_id: str,
        *,
        idempotency_key: str | None = None,
        balance: int,
        now: datetime | None = None,
    ) -> tuple[AutoSaveRule, AutoSaveLog | None]:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)

        if idempotency_key is not None and idempotency_key in self._auto_save_seen_keys:
            log = build_auto_save_log(
                rule_id=rule.id,
                idempotency_key=idempotency_key,
                status="skipped",
                reason="duplicate_skipped",
                executed_at=current_time,
            )
            self._auto_save_logs.append(log)
            self._persist_snapshot()
            return rule, log

        if idempotency_key is not None:
            self._auto_save_seen_keys.add(idempotency_key)

        if rule.status in {"cancelled", "paused", "auto_paused"}:
            log = build_auto_save_log(
                rule_id=rule.id,
                idempotency_key=idempotency_key,
                status="skipped",
                reason=f"rule_{rule.status}",
                executed_at=current_time,
            )
            self._auto_save_logs.append(log)
            self._persist_snapshot()
            return rule, log

        if rule.status == "pending_grace" and current_time < rule.grace_until:
            log = build_auto_save_log(
                rule_id=rule.id,
                idempotency_key=idempotency_key,
                status="skipped",
                reason="grace_period_active",
                executed_at=current_time,
            )
            self._auto_save_logs.append(log)
            self._persist_snapshot()
            return rule, log

        if balance < rule.balance_floor:
            updated_rule = replace(rule, status="auto_paused")
            notification = AutoSaveNotification(
                user_id=rule.user_id,
                kind="auto_save_balance_alert",
                payload={"balance": balance, "balance_floor": rule.balance_floor, "rule_id": rule.id},
                sent_at=current_time,
            )
            self._auto_save_rules[rule_id] = updated_rule
            if notification is not None:
                self._auto_save_notifications.append(notification)

            log = build_auto_save_log(
                rule_id=rule.id,
                idempotency_key=idempotency_key,
                status="skipped",
                reason="balance_below_threshold",
                executed_at=current_time,
            )
            self._auto_save_logs.append(log)
            self._persist_snapshot()
            return updated_rule, log

        active_rule = rule if rule.status == "active" else replace(rule, status="active")
        self._auto_save_rules[rule_id] = active_rule
        log = build_auto_save_log(
            rule_id=rule.id,
            idempotency_key=idempotency_key,
            status="executed",
            reason="executed",
            executed_at=current_time,
        )
        self._auto_save_logs.append(log)
        self._persist_snapshot()
        return active_rule, log

    def get_auto_save_rule(self, rule_id: str) -> AutoSaveRule:
        rule = self._auto_save_rules.get(rule_id)
        if rule is None:
            raise ValueError("auto_save_rule_not_found")
        return rule

    def list_auto_save_logs(self, user_id: str) -> list[AutoSaveLog]:
        rule_ids = {rule.id for rule in self._auto_save_rules.values() if rule.user_id == user_id}
        return [log for log in self._auto_save_logs if log.rule_id in rule_ids]

    def list_auto_save_notifications(self, user_id: str) -> list[AutoSaveNotification]:
        return [notification for notification in self._auto_save_notifications if notification.user_id == user_id]

    def update_profile_settings(
        self,
        user_id: str,
        *,
        avatar_type: str | None = None,
        intensity: int | None = None,
        text_mode: bool | None = None,
        daily_alert_cap: int | None = None,
        baseline_amount: float | None = None,
    ) -> UserProfile:
        profile = self.get_profile(user_id)
        updated_profile = update_profile_settings(
            profile,
            avatar_type=avatar_type,
            intensity=intensity,
            text_mode=text_mode,
            daily_alert_cap=daily_alert_cap,
            baseline_amount=baseline_amount,
        )
        self._profiles[user_id] = updated_profile

        avatar = self._avatars.get(user_id) or AvatarState(user_id=user_id)
        avatar.baseline_amount = updated_profile.baseline_amount
        self._avatars[user_id] = avatar
        self._persist_snapshot()
        return updated_profile

    def get_avatar(self, user_id: str) -> AvatarState:
        avatar = self._avatars.get(user_id)
        if avatar is None:
            avatar = AvatarState(user_id=user_id)
            self._avatars[user_id] = avatar
            self._persist_snapshot()
        return avatar

    def record_event(self, event: MoneyEvent, idempotency_key: str | None = None) -> AvatarState:
        if idempotency_key is not None:
            key = (event.user_id, idempotency_key)
            if key in self._seen_event_keys:
                raise ValueError("duplicate_event")
            self._seen_event_keys.add(key)

        avatar = self.get_avatar(event.user_id)
        profile = self.get_profile(event.user_id)
        avatar.baseline_amount = profile.baseline_amount
        updated_avatar = recalculate_avatar(avatar, event)
        self._avatars[event.user_id] = updated_avatar
        self._maybe_create_notification(event.user_id, updated_avatar, event.occurred_at)
        self._persist_snapshot()
        return updated_avatar

    def preview_event(
        self,
        *,
        user_id: str,
        amount: float,
        baseline_amount: float | None = None,
        occurred_at: datetime | None = None,
    ) -> AvatarState:
        profile = self.get_profile(user_id)
        avatar = self.get_avatar(user_id)
        preview_avatar = AvatarState(
            user_id=avatar.user_id,
            hp=avatar.hp,
            growth=avatar.growth,
            baseline_amount=avatar.baseline_amount,
            last_calculated_at=avatar.last_calculated_at,
            events=list(avatar.events),
        )
        if baseline_amount is not None:
            preview_avatar.baseline_amount = baseline_amount
        else:
            preview_avatar.baseline_amount = profile.baseline_amount

        preview_time = occurred_at or datetime.now()
        if preview_time.tzinfo is None:
            preview_time = preview_time.replace(tzinfo=datetime.now().astimezone().tzinfo)
        preview_event = MoneyEvent(user_id=user_id, amount=amount, occurred_at=preview_time)
        return recalculate_avatar(preview_avatar, preview_event)

    def subscribe_push(self, user_id: str, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise ValueError("user_not_found")

        subscription = create_push_subscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth)
        self._push_subscriptions.setdefault(user_id, []).append(subscription)
        self._persist_snapshot()
        return subscription

    def list_push_subscriptions(self, user_id: str) -> list[PushSubscription]:
        return list(self._push_subscriptions.get(user_id, []))

    def create_threshold(self, user_id: str, kind: str, value: float) -> ThresholdRule:
        threshold = ThresholdRule(user_id=user_id, kind=kind, value=value)
        self._thresholds[user_id] = threshold
        self._persist_snapshot()
        return threshold

    def list_notifications(self, user_id: str, *, include_suppressed: bool = False) -> list[NotificationRecord]:
        return [
            notification
            for notification in self._notifications
            if notification.user_id == user_id and (include_suppressed or notification.suppressed_reason is None)
        ]

    def list_learning_cards(self) -> list[LearningCard]:
        return self._learning_cards

    def complete_learning_card(self, user_id: str, card_id: str, completed_at: datetime) -> tuple[AvatarState, bool]:
        avatar = self.get_avatar(user_id)
        completed_ids = self._learning_progress.setdefault(user_id, set())
        updated_avatar, completed = complete_learning_card(
            avatar,
            self._learning_cards,
            card_id,
            now=completed_at,
            completed_card_ids=completed_ids,
        )
        self._avatars[user_id] = updated_avatar
        if completed:
            self._learning_progress[user_id].add(card_id)
        self._persist_snapshot()
        return updated_avatar, completed

    def has_completed_learning_card(self, user_id: str, card_id: str) -> bool:
        return card_id in self._learning_progress.get(user_id, set())

    def complete_mission(self, user_id: str) -> int:
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            account_row = db.execute("SELECT user_id FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
            if account_row is None:
                raise ValueError("user_not_found")

            cursor = db.execute(
                """
                UPDATE mission_stats
                SET completed_count = completed_count + 1,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (datetime.now(timezone.utc).isoformat(), user_id),
            )
            if cursor.rowcount == 0:
                db.execute(
                    """
                    INSERT INTO mission_stats (user_id, completed_count, updated_at)
                    VALUES (?, 1, ?)
                    """,
                    (user_id, datetime.now(timezone.utc).isoformat()),
                )

            row = db.execute(
                "SELECT completed_count FROM mission_stats WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            db.commit()

        return int(row[0]) if row is not None else 0

    def list_mission_ranking(self, limit: int = 50) -> list[dict[str, object]]:
        safe_limit = max(1, min(200, limit))
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            rows = db.execute(
                """
                SELECT a.user_id, a.nickname, COALESCE(m.completed_count, 0) AS completed_count
                FROM accounts a
                LEFT JOIN mission_stats m ON m.user_id = a.user_id
                ORDER BY completed_count DESC, a.created_at ASC, a.user_id ASC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()

        items: list[dict[str, object]] = []
        for index, row in enumerate(rows):
            user_id, nickname, completed_count = row
            items.append(
                {
                    "rank": index + 1,
                    "user_id": user_id,
                    "nickname": nickname,
                    "completed_count": int(completed_count),
                }
            )
        return items

    def get_mission_rank(self, user_id: str) -> dict[str, object]:
        with self._db_lock, sqlite3.connect(self._db_path) as db:
            row = db.execute(
                """
                WITH base AS (
                    SELECT
                        a.user_id,
                        a.nickname,
                        a.created_at,
                        COALESCE(m.completed_count, 0) AS completed_count
                    FROM accounts a
                    LEFT JOIN mission_stats m ON m.user_id = a.user_id
                )
                SELECT
                    b.user_id,
                    b.nickname,
                    b.completed_count,
                    (
                        1 + (
                            SELECT COUNT(*)
                            FROM base other
                            WHERE
                                other.completed_count > b.completed_count
                                OR (
                                    other.completed_count = b.completed_count
                                    AND (
                                        other.created_at < b.created_at
                                        OR (other.created_at = b.created_at AND other.user_id < b.user_id)
                                    )
                                )
                        )
                    ) AS rank
                FROM base b
                WHERE b.user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            raise ValueError("user_not_found")

        rank_user_id, nickname, completed_count, rank = row
        return {
            "rank": int(rank),
            "user_id": str(rank_user_id),
            "nickname": str(nickname),
            "completed_count": int(completed_count),
        }

    def create_group(self, name: str, max_members: int = 6) -> Group:
        group = create_group(name=name, max_members=max_members)
        self._groups[group.id] = group
        self._persist_snapshot()
        return group

    def join_group(self, group_id: str, user_id: str) -> Group:
        group = self._groups.get(group_id)
        if group is None:
            raise ValueError("group_not_found")

        updated_group = join_group(group, user_id)
        self._groups[group_id] = updated_group
        self._persist_snapshot()
        return updated_group

    def get_group(self, group_id: str) -> Group:
        group = self._groups.get(group_id)
        if group is None:
            raise ValueError("group_not_found")
        return group

    def get_group_challenge_view(self, group_id: str) -> GroupChallengeView:
        group = self.get_group(group_id)
        return build_group_challenge_view(group)

    def get_group_goal_options(self, group_id: str) -> GroupGoalOptions:
        group = self.get_group(group_id)
        return build_group_goal_options(group)

    def _maybe_create_notification(self, user_id: str, avatar: AvatarState, now: datetime) -> None:
        threshold = self._thresholds.get(user_id)
        if threshold is None:
            return

        if not is_threshold_exceeded(avatar.events, threshold, now=now):
            return

        profile = self.get_profile(user_id)
        suppressed_reason = None
        if should_suppress_alert(self._notifications, user_id=user_id, daily_cap=profile.daily_alert_cap, now=now):
            suppressed_reason = "suppressed_by_daily_cap"

        self._notifications.append(
            NotificationRecord(
                user_id=user_id,
                kind="pause_card",
                payload={"threshold": threshold.value, "amount": avatar.events[-1].amount},
                sent_at=now,
                suppressed_reason=suppressed_reason,
            )
        )
