from dataclasses import fields

from asset_helper.store import InMemoryAvatarStore


def test_group_challenge_view_omits_ranking_and_includes_encouragements() -> None:
    store = InMemoryAvatarStore()
    group = store.create_group(name="우리 챌린지", max_members=6)
    store.join_group(group.id, "demo")
    store.join_group(group.id, "friend-1")
    store.join_group(group.id, "friend-2")

    view = store.get_group_challenge_view(group.id)

    assert view.group_id == group.id
    assert view.has_ranking is False
    assert view.encouragements
    forbidden = {"rank", "ranking", "score", "scores", "position"}
    assert forbidden.isdisjoint({field.name for field in fields(view)})


def test_group_goal_options_recommend_percent_over_absolute() -> None:
    store = InMemoryAvatarStore()
    group = store.create_group(name="우리 챌린지", max_members=6)

    options = store.get_group_goal_options(group.id)

    assert options.recommended_mode == "percent"
    assert "absolute" in options.secondary_modes
