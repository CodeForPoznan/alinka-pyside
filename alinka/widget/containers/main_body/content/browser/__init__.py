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
        # cache for _data to avoid repeated DB queries during view operations
        self._cached_data = None

    @staticmethod
    def map_model_to_row_data(decision: DecisionDbSchema) -> list[str]:
        return [
            decision.id,
            decision.child_pesel,
            decision.child_full_name,
            f"{decision.child_town}, {decision.child_address}",
            decision.created_at.strftime("%Y-%m-%d %H:%M") if decision.created_at else "",
        ]

    @property
    def _data(self):
        # Memoize data so repeated accesses (rowCount/data) don't re-query DB each time.
        if getattr(self, "_cached_data", None) is None:
            decisions = filter_decisions_by_pesel_child_name(self.filter_by)
            self._cached_data = [self.map_model_to_row_data(decision) for decision in decisions]
        return self._cached_data

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
        return ["id", "PESEL dziecka", "Imię i nazwisko dziecka", "Adres dziecka", "Data utworzenia"]

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

        layout.addWidget(browse_input)
        layout.addWidget(self.decision_table)

    @property
    def create_new_btn(self):
        footer_container = self.browser_container.content_container.main_body_container.footer_container
        return footer_container.browser_footer_container.create_new_btn

    def entered_filter_by(self, text):
        if self.table_model.filter_by != text:
            # Save id of the currently selected row before applying the filter
            saved_id = self.selected_decision_id

            # Set new filter and invalidate cached data so the model will rebuild once
            self.table_model.filter_by = text
            if hasattr(self.table_model, "_cached_data"):
                self.table_model._cached_data = None

            # Reset the model to load new filtered data
            self.table_model.beginResetModel()
            self.table_model.endResetModel()

            # Clear graphical selection first
            self.decision_table.clearSelection()

            # Try to restore the selection if it is still in the search results (use cached data)
            if saved_id is not None:
                self.selected_decision_id = saved_id

                row_to_select = None
                for row_index, row in enumerate(self.table_model._data):
                    # row[0] is the hidden id column
                    if row and row[0] == saved_id:
                        row_to_select = row_index
                        break

                if row_to_select is not None:
                    # Restore graphical selection if the record is visible
                    index_to_select = self.table_model.index(row_to_select, 0)
                    # Select via the selection model to ensure selectionModel reflects the change
                    # Perform selection and also set current index to ensure selection is reflected
                    self.selection_model.select(
                        index_to_select, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                    )
                    try:
                        # setCurrentIndex may help in some environments to make selection visible
                        self.selection_model.setCurrentIndex(
                            index_to_select, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                        )
                    except Exception:
                        pass

                    self.selected_decision_id = saved_id
                    self.create_new_btn.setEnabled(True)
                else:
                    # Remember id but disable action because not visible
                    self.selected_decision_id = saved_id
                    self.create_new_btn.setEnabled(False)
            else:
                self.selected_decision_id = None
                self.create_new_btn.setEnabled(False)

    def showEvent(self, event):
        self.table_model.beginResetModel()
        self.table_model.endResetModel()
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
