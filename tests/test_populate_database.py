from unittest.mock import MagicMock, patch

import pytest

from tools.populate_database import populate_database


def test_populate_database_commits_once_after_all_factories():
    db = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = db
    session_registry = MagicMock(return_value=session_context)

    with (
        patch("tools.populate_database.db_session", session_registry),
        patch("tools.populate_database.random.randint", side_effect=[3, 4, 5]),
        patch("tools.populate_database.trange", side_effect=range),
        patch("tools.populate_database.SupportCenterFactory") as support_center_factory,
        patch("tools.populate_database.TeamMemberFactory") as team_member_factory,
        patch("tools.populate_database.SchoolFactory") as school_factory,
        patch("tools.populate_database.DecisionFactory") as decision_factory,
    ):
        populate_database()

    session_registry.assert_called_once_with()
    support_center_factory.assert_called_once_with()
    assert team_member_factory.call_count == 3
    assert school_factory.call_count == 4
    assert decision_factory.call_count == 5
    db.commit.assert_called_once_with()


def test_populate_database_does_not_commit_partial_data():
    db = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = db
    session_registry = MagicMock(return_value=session_context)

    with (
        patch("tools.populate_database.db_session", session_registry),
        patch("tools.populate_database.random.randint", side_effect=[1, 1, 1]),
        patch("tools.populate_database.trange", side_effect=range),
        patch("tools.populate_database.SupportCenterFactory"),
        patch("tools.populate_database.TeamMemberFactory"),
        patch("tools.populate_database.SchoolFactory"),
        patch(
            "tools.populate_database.DecisionFactory",
            side_effect=RuntimeError("factory failed"),
        ),
    ):
        with pytest.raises(RuntimeError, match="factory failed"):
            populate_database()

    db.commit.assert_not_called()
    session_context.__exit__.assert_called_once()
