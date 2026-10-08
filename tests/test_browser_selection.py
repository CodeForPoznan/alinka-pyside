import sys
import types
import types as _types

import pytest

# Provide minimal PySide6 stubs so tests can import the module without GUI bindings.
Qt_stub = types.SimpleNamespace(DisplayRole=0, TextAlignmentRole=1)
qtcore = _types.ModuleType("PySide6.QtCore")
qtcore.QAbstractTableModel = object
qtcore.QItemSelectionModel = type("QItemSelectionModel", (), {"ClearAndSelect": 1, "Rows": 2})
qtcore.QModelIndex = object
qtcore.Qt = Qt_stub
qtwidgets = _types.ModuleType("PySide6.QtWidgets")
qtwidgets.QAbstractItemView = object
qtwidgets.QHeaderView = object
qtwidgets.QTableView = object
qtwidgets.QTabWidget = object
qtwidgets.QVBoxLayout = object
qtwidgets.QWidget = object

sys.modules["PySide6"] = _types.ModuleType("PySide6")
sys.modules["PySide6.QtCore"] = qtcore
sys.modules["PySide6.QtWidgets"] = qtwidgets

from alinka.widget.containers.main_body.content.browser import BrowseDecisionContainer


class DummyBtn:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, val):
        self.enabled = val


class DummyTable:
    def __init__(self):
        self.cleared = False
        self.selected = None

    def clearSelection(self):
        self.cleared = True

    def selectRow(self, idx):
        self.selected = idx


class DummyModel:
    def __init__(self, data):
        # initial data that should be returned when cache is (re)built
        self.filter_by = None
        self._initial = data
        self._cached_data = data
        self.reset_called = False

    def beginResetModel(self):
        self.reset_called = True

    def endResetModel(self):
        pass

    @property
    def _data(self):
        # mimic DecisionsTableModel memoization: if cache is None, rebuild from initial
        if getattr(self, "_cached_data", None) is None:
            self._cached_data = list(self._initial)
        return self._cached_data


def make_container(table_data, prev_selected):
    # create BrowseDecisionContainer instance without running __init__
    c = object.__new__(BrowseDecisionContainer)

    # build browser_container chain so that the create_new_btn property resolves
    dummy_btn = DummyBtn()
    browser = types.SimpleNamespace(
        content_container=types.SimpleNamespace(
            main_body_container=types.SimpleNamespace(
                footer_container=types.SimpleNamespace(
                    browser_footer_container=types.SimpleNamespace(create_new_btn=dummy_btn)
                )
            )
        )
    )

    c.browser_container = browser
    c.table_model = DummyModel(table_data)
    c.decision_table = DummyTable()
    c.selected_decision_id = prev_selected
    return c, dummy_btn


def test_restore_selection_when_present():
    row = ["123", "pesel", "name", "addr", "date"]
    c, btn = make_container([row], "123")

    c.entered_filter_by("query")

    assert c.decision_table.selected == 0
    assert btn.enabled is True
    assert c.selected_decision_id == "123"


def test_disable_button_when_not_present():
    row = ["456", "pesel", "name", "addr", "date"]
    c, btn = make_container([row], "123")

    c.entered_filter_by("query")

    assert c.decision_table.selected is None
    assert btn.enabled is False
    # ID should remain remembered
    assert c.selected_decision_id == "123"


def test_disable_when_no_prev_selected():
    row = ["456", "pesel", "name", "addr", "date"]
    c, btn = make_container([row], None)

    c.entered_filter_by("query")

    assert btn.enabled is False
    assert c.selected_decision_id is None
