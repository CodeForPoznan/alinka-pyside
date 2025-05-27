from pydantic import ValidationError
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHeaderView,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from alinka.db.models import TeamMember
from alinka.db.queries import delete_team_member, get_team_members, upsert_team_members
from alinka.schemas import TeamMemberDbCreateSchema, TeamMemberDbSchema


class TeamMemberTableModel(QAbstractTableModel):
    def __init__(self):
        self.insert_row = None
        self.columns = TeamMember.__table__.columns.keys()
        self.header_labels = ["id", "Imię i nazwisko", "Specjalizacja"]
        super().__init__()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.columns)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(get_team_members()) + (1 if self.unsaved_insert_row() else 0)

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
            return get_team_members()[index.row()].model_dump()[column_key]
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
                    upsert_team_members([tm])
                    self.insert_row = None

                    self.layoutChanged.emit()
                    return True
            return False

        tm_dict = {k: self.data(index.siblingAtColumn(i)) for i, k in enumerate(self.columns)}
        tm_dict[self.columns[index.column()]] = value
        tm = TeamMemberDbSchema.model_validate(tm_dict)
        upsert_team_members([tm])

        self.dataChanged.emit(index, index)
        return True

    def removeRow(self, row: int) -> bool:
        if self.unsaved_insert_row() and self.is_last_row(row):
            self.insert_row = None
        else:
            db_id = self.data(self.createIndex(row, 0))
            delete_team_member(db_id)

        self.layoutChanged.emit()
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


class TeamMemberTableGroup(QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Członkowie zespołu orzekającego", parent=parent)
        self.team_member_tab_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.table_model = TeamMemberTableModel()

        self.table = QTableView()
        self.table.clicked.connect(self.row_selected_event)
        self.table.setModel(self.table_model)
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.hideColumn(0)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        layout.addWidget(self.table)

    def row_selected_event(self, item, **kwargs):
        footer_container = (
            self.team_member_tab_container.settings_container.content_container.main_body_container.footer_container
        )
        footer_container.settings_footer_container.footer_team_members_container.remove_selected_member_btn.setEnabled(
            True
        )
