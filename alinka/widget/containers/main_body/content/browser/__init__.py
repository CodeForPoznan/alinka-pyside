from PySide6.QtCore import QAbstractTableModel, QItemSelectionModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from alinka.db.queries import filter_decisions_by_pesel_child_name
from alinka.schemas.db_schema import DecisionDbSchema
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class DecisionsTableModel(QAbstractTableModel):
    filter_by: str | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_by = None

    @staticmethod
    def map_model_to_row_data(decision: DecisionDbSchema) -> list[str]:
        return [
            decision.id,
            decision.child_pesel,
            decision.child_full_name,
            f"{decision.child_town}, {decision.child_address}",
        ]

    @property
    def _data(self):
        decisions = filter_decisions_by_pesel_child_name(self.filter_by)
        return [self.map_model_to_row_data(decision) for decision in decisions]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.header_names)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

    @property
    def header_names(self):
        return ["id", "PESEL dziecka", "Imię i nazwisko dziecka", "Adres dziecka"]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_names[section]
            else:
                return section + 1


class BrowseDecisionContainer(ValidationMixin, QWidget):
    selected_decision_id: int | None

    def __init__(self, parent: QWidget):
        self.browser_container = parent
        super().__init__(parent)
        self.selected_decision_id = None
        layout = QVBoxLayout(self)
        browse_input = LabeledInputComponent("Wyszukaj ucznia", self)
        browse_input.line_edit.setPlaceholderText("Wprowadź PESEL lub imię i nazwisko ucznia")
        browse_input.line_edit.textChanged.connect(self.entered_filter_by)

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

        header = self.decision_table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        header.setMinimumSectionSize(150)
        header.resizeSection(1, 150)
        header.resizeSection(2, 250)
        header.resizeSection(3, 300)

        layout.addWidget(browse_input)
        layout.addWidget(self.decision_table)

    @property
    def create_new_btn(self):
        footer_container = self.browser_container.content_container.main_body_container.footer_container
        return footer_container.browser_footer_container.create_new_btn

    def entered_filter_by(self, text):
        # Filtering here clears whole model including selection
        # It's reasonable select row using 'self.selected_decision_id'
        # should be covered by https://github.com/CodeForPoznan/alinka-pyside/issues/148

        if self.table_model.filter_by != text:
            self.table_model.filter_by = text
            self.table_model.beginResetModel()
            self.table_model.endResetModel()
            self.decision_table.clearSelection()
            self.selected_decision_id = None

    def showEvent(self, event):
        self.table_model.beginResetModel()
        self.table_model.endResetModel()
        self.decision_table.clearSelection()
        self.selected_decision_id = None
        self.create_new_btn.setEnabled(False)
        return super().showEvent(event)

    def decision_selected_event(self, index: QModelIndex):
        self.selected_decision_id = index.siblingAtColumn(0).data()
        footer_container = self.browser_container.content_container.main_body_container.footer_container
        footer_container.browser_footer_container.create_new_btn.setEnabled(True)

    def decision_selection_changed_event(self, selected, deselected) -> None:
        selected_indexes = selected.indexes()
        if not selected_indexes:
            self.selected_decision_id = None
            footer_container = self.browser_container.content_container.main_body_container.footer_container
            footer_container.browser_footer_container.create_new_btn.setEnabled(False)
            return

        else:
            self.decision_selected_event(selected_indexes[0])
            self.selected_decision_id = None
            footer_container = self.browser_container.content_container.main_body_container.footer_container
            footer_container.browser_footer_container.create_new_btn.setEnabled(True)


class BrowserContainer(QTabWidget):
    def __init__(self, parent: QWidget, content_container, visible: bool = False):
        super().__init__(parent)
        self.content_container = content_container
        self.browse_decision_container = BrowseDecisionContainer(self)
        self.addTab(self.browse_decision_container, "Wyszukaj dokument")

        self.setVisible(visible)
