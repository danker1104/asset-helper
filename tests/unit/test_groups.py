from asset_helper.domain.groups import create_group, join_group


def test_create_group_defaults_to_two_to_six_members() -> None:
    group = create_group(name="스터디")

    assert group.name == "스터디"
    assert group.max_members == 6
    assert group.members == []


def test_join_group_adds_member_until_capacity() -> None:
    group = create_group(name="스터디", max_members=6)

    for index in range(6):
        group = join_group(group, user_id=f"user-{index}")

    assert len(group.members) == 6


def test_join_group_rejects_seventh_member() -> None:
    group = create_group(name="스터디", max_members=6)

    for index in range(6):
        group = join_group(group, user_id=f"user-{index}")

    try:
        join_group(group, user_id="user-7")
        raised = False
    except ValueError:
        raised = True

    assert raised is True
