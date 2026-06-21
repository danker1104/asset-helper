from datetime import datetime, timezone

from asset_helper.domain.learning import complete_learning_card, create_learning_cards, get_learning_card
from asset_helper.domain.models import AvatarState


def test_learning_cards_catalog_contains_defaults() -> None:
    cards = create_learning_cards()

    assert len(cards) >= 1
    assert get_learning_card(cards, "budget-basics") is not None


def test_complete_learning_card_increments_growth_once() -> None:
    avatar = AvatarState(user_id="demo", growth=0)
    cards = create_learning_cards()
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)

    updated_avatar, completed = complete_learning_card(avatar, cards, "budget-basics", now=now, completed_card_ids=set())

    assert completed is True
    assert updated_avatar.growth == 1


def test_complete_learning_card_does_not_double_reward() -> None:
    avatar = AvatarState(user_id="demo", growth=1)
    cards = create_learning_cards()
    now = datetime(2026, 6, 13, tzinfo=timezone.utc)

    updated_avatar, completed = complete_learning_card(
        avatar,
        cards,
        "budget-basics",
        now=now,
        completed_card_ids={"budget-basics"},
    )

    assert completed is False
    assert updated_avatar.growth == 1
