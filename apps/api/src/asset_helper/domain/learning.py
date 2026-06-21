from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .models import AvatarState


@dataclass(frozen=True, slots=True)
class LearningCard:
    id: str
    title: str
    body: str
    duration_sec: int


@dataclass(frozen=True, slots=True)
class LearningProgress:
    user_id: str
    card_id: str
    completed_at: datetime


def create_learning_cards() -> list[LearningCard]:
    return [
        LearningCard(
            id="budget-basics",
            title="예산의 기초",
            body="고정비와 변동비를 나눠 예산을 세워보세요.",
            duration_sec=90,
        ),
        LearningCard(
            id="saving-routine",
            title="저축 루틴",
            body="자동저축 전에 잔액 하한을 확인하세요.",
            duration_sec=120,
        ),
    ]


def get_learning_card(cards: list[LearningCard], card_id: str) -> LearningCard | None:
    for card in cards:
        if card.id == card_id:
            return card
    return None


def complete_learning_card(
    avatar: AvatarState,
    cards: list[LearningCard],
    card_id: str,
    *,
    now: datetime | None = None,
    completed_card_ids: set[str] | None = None,
) -> tuple[AvatarState, bool]:
    if get_learning_card(cards, card_id) is None:
        raise ValueError("unknown_learning_card")

    completed_card_ids = completed_card_ids or set()
    if card_id in completed_card_ids:
        return avatar, False

    completed_card_ids.add(card_id)
    completed_at = now or datetime.now(timezone.utc)
    avatar.growth += 1
    avatar.last_calculated_at = completed_at
    return avatar, True
