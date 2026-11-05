from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Qt,
    QTimer,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from alinka.db.queries import filter_decision_summaries_by_pesel_child_name
from alinka.schemas.db_schema import DecisionSummaryDbSchema
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class DecisionsTableModel(QAbstractTableModel):
    filter_by: str | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_by = None
        self._rows = []

    @staticmethod
    def map_model_to_row_data(decision: DecisionSummaryDbSchema) -> list[str | int]:
        return [
            decision.id,
            decision.child_pesel,
            decision.child_full_name,
            f"{decision.child_town}, {decision.child_address}",
            decision.created_at.strftime("%Y-%m-%d %H:%M") if decision.created_at else "",
        ]

    def reload(self, filter_by: str | None) -> None:
        decisions = filter_decision_summaries_by_pesel_child_name(filter_by)
        rows = [self.map_model_to_row_data(decision) for decision in decisions]

        self.beginResetModel()
        self.filter_by = filter_by
        self._rows = rows
        self.endResetModel()

    def row_for_decision_id(self, decision_id: int | None) -> int | None:
        if decision_id is None:
            return None
        return next((row for row, data in enumerate(self._rows) if data[0] == decision_id), None)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.header_names)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._rows[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

    @property
    def header_names(self):
        return ["id", "PESEL dziecka", "Imię i nazwisko dziecka", "Adres dziecka", "Data utworzenia"]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_names[section]
            else:
                return section + 1


class BrowseDecisionContainer(ValidationMixin, QWidget):
    FILTER_DEBOUNCE_MS = 300

    selected_decision_id: int | None

    def __init__(self, parent: QWidget):
        self.browser_container = parent
        super().__init__(parent)
        self.selected_decision_id = None
        layout = QVBoxLayout(self)
        self.browse_input = LabeledInputComponent("Wyszukaj ucznia", self)
        self.browse_input.line_edit.setPlaceholderText("Wprowadź PESEL lub imię i nazwisko ucznia")
        self.browse_input.line_edit.textChanged.connect(self.entered_filter_by)

        self._pending_filter_by = None
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(self.FILTER_DEBOUNCE_MS)
        self._filter_timer.timeout.connect(self._apply_filter)

        self.table_model = DecisionsTableModel()
        self.selection_model = QItemSelectionModel(self.table_model)
        self.selection_model.selectionChanged.connect(self.decision_selection_changed_event)
        self.decision_table = QTableView(self)
        self.decision_table.setModel(self.table_model)
        self.decision_table.setSelectionModel(self.selection_model)
        self.decision_table.clicked.connect(self.decision_selected_event)
        self.decision_table.setColumnHidden(0, True)
        self.decision_table.resizeColumnsToContents()
        self.decision_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Configure header resize modes and sizes
        header = self.decision_table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Fixed)

        header.setMinimumSectionSize(150)
        header.resizeSection(1, 150)
        header.resizeSection(2, 250)
        header.resizeSection(3, 300)
        header.resizeSection(4, 200)

        layout.addWidget(self.browse_input)
        layout.addWidget(self.decision_table)

    @property
    def create_new_btn(self):
        footer_container = self.browser_container.content_container.main_body_container.footer_container
        return footer_container.browser_footer_container.create_new_btn

    def entered_filter_by(self, text):
        self._pending_filter_by = text
        self._filter_timer.start()

    def _apply_filter(self):
        text = self._pending_filter_by
        if self.table_model.filter_by == text:
            return

        saved_id = self.selected_decision_id
        self.table_model.reload(text)

        row_to_select = self.table_model.row_for_decision_id(saved_id)
        if row_to_select is not None:
            index_to_select = self.table_model.index(row_to_select, 0)
            self.selection_model.select(index_to_select, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.create_new_btn.setEnabled(True)
        else:
            self.create_new_btn.setEnabled(False)

        self.selected_decision_id = saved_id

    def showEvent(self, event):
        self._filter_timer.stop()
        self._pending_filter_by = self.browse_input.text
        self.table_model.reload(self._pending_filter_by)
        self.decision_table.clearSelection()
        self.selected_decision_id = None
        self.create_new_btn.setEnabled(False)
        return super().showEvent(event)

    def decision_selected_event(self, index: QModelIndex):
        self.selected_decision_id = index.siblingAtColumn(0).data()
        self.create_new_btn.setEnabled(True)

    def decision_selection_changed_event(self, selected, deselected) -> None:
        selected_indexes = self.selection_model.selectedRows()

        if not selected_indexes:
            # Disable button without clearing selected_decision_id to keep state between operations
            self.create_new_btn.setEnabled(False)
        else:
            self.decision_selected_event(selected_indexes[0])


class BrowserContainer(QTabWidget):
    def __init__(self, parent: QWidget, content_container, visible: bool = False):
        super().__init__(parent)
        self.content_container = content_container
        self.browse_decision_container = BrowseDecisionContainer(self)
        self.addTab(self.browse_decision_container, "Wyszukaj dokument")

        self.setVisible(visible)
