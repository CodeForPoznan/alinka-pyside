import os
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication, QWidget

from alinka.widget.containers.main_body.content.browser import BrowseDecisionContainer


class DummyBtn:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, val):
        self.enabled = val


def make_container(monkeypatch, row_ids, prev_selected):
    # Use offscreen platform to avoid GUI requirements
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # Ensure QApplication exists
    # app = QApplication.instance() or QApplication([])

    # Prepare parent QWidget with the footer->create_new_btn chain required by the container
    parent = QWidget()
    dummy_btn = DummyBtn()
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

    monkeypatch.setattr("alinka.db.queries.filter_decisions_by_pesel_child_name", fake_query)

    # Instantiate real widget (runs real init) and return it with the dummy button
    c = BrowseDecisionContainer(parent)
    c.selected_decision_id = prev_selected
    return c, dummy_btn


def test_restore_selection_when_present(monkeypatch):
    c, btn = make_container(monkeypatch, ["123"], "123")

    c.entered_filter_by("query")

    selected = c.decision_table.selectionModel().selectedRows()
    assert len(selected) == 1
    assert selected[0].row() == 0
    assert btn.enabled is True
    assert c.selected_decision_id == "123"


def test_disable_button_when_not_present(monkeypatch):
    c, btn = make_container(monkeypatch, ["456"], "123")

    c.entered_filter_by("query")

    selected = c.decision_table.selectionModel().selectedRows()
    assert len(selected) == 0
    assert btn.enabled is False
    # ID should remain remembered
    assert c.selected_decision_id == "123"


def test_disable_when_no_prev_selected(monkeypatch):
    c, btn = make_container(monkeypatch, ["456"], None)

    c.entered_filter_by("query")

    assert btn.enabled is False
    assert c.selected_decision_id is None
