from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import uuid4


@dataclass(slots=True)
class Group:
    id: str
    name: str
    max_members: int = 6
    members: list[str] = None

    def __post_init__(self) -> None:
        if self.members is None:
            self.members = []


def create_group(name: str, max_members: int = 6) -> Group:
    if max_members < 2 or max_members > 6:
        raise ValueError("max_members must be between 2 and 6")
    return Group(id=uuid4().hex, name=name, max_members=max_members, members=[])


def join_group(group: Group, user_id: str) -> Group:
    if user_id in group.members:
        return group

    if len(group.members) >= group.max_members:
        raise ValueError("max_members_reached")

    return replace(group, members=[*group.members, user_id])
