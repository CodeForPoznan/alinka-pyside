from pydantic import ValidationError
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHeaderView,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from alinka.db.models import TeamMember
from alinka.db.queries import (
    delete_team_member,
    get_team_members,
    insert_team_member,
    update_team_member,
)
from alinka.schemas import TeamMemberDbCreateSchema, TeamMemberDbSchema
from alinka.widget.components import ValidationMixin


class TeamMemberTableModel(QAbstractTableModel):
    memberAdded = Signal()  # Signal emitted when a new member is successfully added
    memberChanged = Signal()  # Signal emitted when team members list changes
    
    def __init__(self):
        self.insert_row = None
        self.columns = TeamMember.__table__.columns.keys()
        self.header_labels = ["id", "Imię i nazwisko", "Specjalizacja"]
        self._cached_team_members = []
        self._refresh_data()
        super().__init__()

    def _refresh_data(self):
        """Refresh the cached team members data from database."""
        self._cached_team_members = get_team_members()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.columns)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._cached_team_members) + (1 if self.unsaved_insert_row() else 0)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Set flags for each cell."""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> object:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_labels[section]
            if orientation == Qt.Vertical:
                if self.unsaved_insert_row() and self.is_last_row(section):
                    return "*"
                return section + 1
        return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> object:
        """Return the data for the given index."""
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            column_key = self.columns[index.column()]
            if self.unsaved_insert_row() and self.is_last_row(index):
                return self.insert_row.get(column_key, "")
            return self._cached_team_members[index.row()].model_dump()[column_key]
        return None

    def setData(self, index: QModelIndex, value: object, role: int = Qt.EditRole) -> bool:
        if not index.isValid():
            return False

        if self.unsaved_insert_row() and self.is_last_row(index):
            if not value:
                return False
            self.insert_row[self.columns[index.column()]] = value

            # I guess, we should employ Pydantic to check, whether these values are not empty?
            if all(self.insert_row.values()):
                try:
                    tm = TeamMemberDbCreateSchema.model_validate(self.insert_row)
                except ValidationError:
                    pass
                else:
                    insert_team_member(tm)
                    self.insert_row = None
                    self._refresh_data()  # Refresh cached data

                    self.layoutChanged.emit()
                    # Emit signal for successful member addition
                    self.memberAdded.emit()
                    self.memberChanged.emit()  # Emit change signal
                    return True
            return False

        tm_dict = {k: self.data(index.siblingAtColumn(i)) for i, k in enumerate(self.columns)}
        tm_dict[self.columns[index.column()]] = value
        try:
            tm = TeamMemberDbSchema.model_validate(tm_dict)
        except ValidationError:
            return False
        update_team_member(tm)
        self._refresh_data()  # Refresh cached data

        self.dataChanged.emit(index, index)
        self.memberChanged.emit()  # Emit change signal
        return True

    def removeRow(self, row: int) -> bool:
        if self.unsaved_insert_row() and self.is_last_row(row):
            self.insert_row = None
        else:
            db_id = self.data(self.createIndex(row, 0))
            delete_team_member(db_id)
            self._refresh_data()  # Refresh cached data

        self.layoutChanged.emit()
        self.memberChanged.emit()  # Emit change signal
        return True

    def insertRow(self, row: int) -> bool:
        self.insert_row = {}
        self.layoutChanged.emit()
        return True

    def is_last_row(self, element: int | QModelIndex) -> bool:
        if isinstance(element, QModelIndex):
            element = element.row()
        return element + 1 == self.rowCount()

    def unsaved_insert_row(self) -> bool:
        return self.insert_row is not None


class TeamMemberTableGroup(ValidationMixin, QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Członkowie zespołu orzekającego", parent=parent)
        self.team_member_tab_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.table_model = TeamMemberTableModel()

        self.table = QTableView()
        self.table.clicked.connect(self.row_selected_event)
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.hideColumn(0)  # Hide ID column
        
        # Enable alternating row colors and grid lines for better visibility
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        
        # Make borders visible with stylesheet (single border, not double)
        self.table.setStyleSheet("""
            QTableView {
                border: 1px solid #94a3b8;  /* Single border */
                gridline-color: #cbd5e1;  /* Lighter gridlines */
            }
            QTableView::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                color: #000000;  /* Black text for headers */
                border: 1px solid #94a3b8;  /* Single border */
                border-top: none;  /* Remove top border to avoid double */
                border-left: none;  /* Remove left border to avoid double */
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        # Set row height for better readability but don't limit table height
        self.table.verticalHeader().setDefaultSectionSize(40)  # Taller rows for better readability
        # Set reasonable minimum height
        self.table.setMinimumHeight(200)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name - stretch to fill
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Specialization - stretch to fill
        header.setMinimumSectionSize(150)  # Minimum column width

        layout.addWidget(self.table)

    def row_selected_event(self, item, **kwargs):
        # Footer functionality removed since TeamMember tab is no longer
        # in settings
        pass
