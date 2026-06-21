from __future__ import annotations

from dataclasses import dataclass

from .groups import Group


@dataclass(frozen=True, slots=True)
class GroupChallengeView:
    group_id: str
    name: str
    members: list[str]
    encouragements: list[str]
    has_ranking: bool = False


@dataclass(frozen=True, slots=True)
class GroupGoalOptions:
    group_id: str
    recommended_mode: str
    secondary_modes: list[str]


def build_group_challenge_view(group: Group) -> GroupChallengeView:
    encouragements = [
        "서로의 속도를 존중하며 같이 가요",
        "작은 변화도 충분히 의미 있어요",
        "오늘의 목표는 어제의 나를 넘는 것",
    ]
    if len(group.members) >= 5:
        encouragements.insert(0, "지금 분위기가 좋습니다. 서로 응원만 남겨요")

    return GroupChallengeView(
        group_id=group.id,
        name=group.name,
        members=list(group.members),
        encouragements=encouragements,
        has_ranking=False,
    )


def build_group_goal_options(group: Group) -> GroupGoalOptions:
    _ = group
    return GroupGoalOptions(group_id=group.id, recommended_mode="percent", secondary_modes=["absolute"])
