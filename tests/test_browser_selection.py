import os
from types import SimpleNamespace

from PySide6.QtWidgets import QPushButton, QWidget

from alinka.widget.containers.main_body.content.browser import BrowseDecisionContainer


class DummyBtn:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, val):
        self.enabled = val


def make_container(monkeypatch, row_ids, prev_selected):
    # Prepare parent QWidget with the footer->create_new_btn chain required by the container
    parent = QWidget()
    # Use a real QPushButton so isEnabled() behaves like in production
    dummy_btn = QPushButton()
    dummy_btn.setEnabled(False)
    parent.content_container = SimpleNamespace(
        main_body_container=SimpleNamespace(
            footer_container=SimpleNamespace(browser_footer_container=SimpleNamespace(create_new_btn=dummy_btn))
        )
    )

    # Monkeypatch DB query used by DecisionsTableModel to return rows with given ids
    def fake_query(filter_by):
        def make_decision(id_):
            return SimpleNamespace(
                id=id_,
                child_pesel="",
                child_full_name="",
                child_town="",
                child_address="",
                created_at=None,
            )

        return [make_decision(rid) for rid in row_ids]

    # Patch the function where the module under test imported it
    monkeypatch.setattr(
        "alinka.widget.containers.main_body.content.browser.filter_decisions_by_pesel_child_name",
        fake_query,
        raising=True,
    )

    # Instantiate real widget (runs real init) and return it with the dummy button
    c = BrowseDecisionContainer(parent)
    c.selected_decision_id = prev_selected
    return c, dummy_btn


def test_restore_selection_when_present(monkeypatch):
    c, btn = make_container(monkeypatch, ["123"], "123")

    c.entered_filter_by("query")
    # allow Qt to process selection change events
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()

    selected = c.decision_table.selectionModel().selectedRows()
    assert len(selected) == 1
    assert selected[0].row() == 0
    # Use real QPushButton API
    assert btn.isEnabled() is True
    assert c.selected_decision_id == "123"


def test_disable_button_when_not_present(monkeypatch):
    c, btn = make_container(monkeypatch, ["456"], "123")

    c.entered_filter_by("query")
    # allow Qt to process selection change events
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()

    selected = c.decision_table.selectionModel().selectedRows()
    assert len(selected) == 0
    # Use real QPushButton API
    assert btn.isEnabled() is False
    # ID should remain remembered
    assert c.selected_decision_id == "123"


def test_disable_when_no_prev_selected(monkeypatch):
    c, btn = make_container(monkeypatch, ["456"], None)

    c.entered_filter_by("query")

    # Use real QPushButton API
    assert btn.isEnabled() is False
    assert c.selected_decision_id is None
