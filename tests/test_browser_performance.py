from types import SimpleNamespace
from unittest.mock import patch

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton, QWidget

from alinka.widget.containers.main_body.content.browser import (
    BrowseDecisionContainer,
    DecisionsTableModel,
)


@pytest.fixture
def decisions():
    return make_decisions(2)


def make_decisions(count):
    return [
        SimpleNamespace(
            id=decision_id,
            child_pesel=str(decision_id),
            child_full_name=f"Child {decision_id}",
            child_town="Poznań",
            child_address="Testowa 1",
            created_at=None,
        )
        for decision_id in range(1, count + 1)
    ]


def make_browser_parent():
    parent = QWidget()
    create_new_btn = QPushButton()
    create_new_btn.setEnabled(False)
    parent.content_container = SimpleNamespace(
        main_body_container=SimpleNamespace(
            footer_container=SimpleNamespace(browser_footer_container=SimpleNamespace(create_new_btn=create_new_btn))
        )
    )
    return parent


def test_model_reuses_loaded_rows_without_new_queries(decisions):
    with patch(
        "alinka.widget.containers.main_body.content.browser.filter_decision_summaries_by_pesel_child_name",
        return_value=decisions,
    ) as query:
        model = DecisionsTableModel()
        model.reload("Child")

        assert query.call_count == 1
        assert model.rowCount() == 2
        assert model.data(model.index(1, 0), Qt.DisplayRole) == 2
        assert model.row_for_decision_id(2) == 1
        assert query.call_count == 1


def test_model_reads_500_rows_with_single_query():
    decisions = make_decisions(500)
    with patch(
        "alinka.widget.containers.main_body.content.browser.filter_decision_summaries_by_pesel_child_name",
        return_value=decisions,
    ) as query:
        model = DecisionsTableModel()
        model.reload(None)

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                model.data(model.index(row, column), Qt.DisplayRole)

        assert model.rowCount() == 500
        assert query.call_count == 1


def test_search_debounces_rapid_changes(decisions):
    with patch(
        "alinka.widget.containers.main_body.content.browser.filter_decision_summaries_by_pesel_child_name",
        return_value=decisions,
    ) as query:
        container = BrowseDecisionContainer(make_browser_parent())
        query.reset_mock()

        container.entered_filter_by("C")
        container.entered_filter_by("Ch")
        container.entered_filter_by("Child")

        assert query.call_count == 0

        QTest.qWait(container.FILTER_DEBOUNCE_MS + 50)

        query.assert_called_once_with("Child")


def test_selection_is_restored_from_cached_rows(decisions):
    with patch(
        "alinka.widget.containers.main_body.content.browser.filter_decision_summaries_by_pesel_child_name",
        return_value=decisions,
    ) as query:
        container = BrowseDecisionContainer(make_browser_parent())
        container.table_model.reload(None)
        selection_flags = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        container.selection_model.select(container.table_model.index(1, 0), selection_flags)
        query.reset_mock()

        container.entered_filter_by("Child 2")
        QTest.qWait(container.FILTER_DEBOUNCE_MS + 50)

        query.assert_called_once_with("Child 2")
        assert container.selected_decision_id == 2
        assert len(container.selection_model.selectedRows()) == 1
