from PySide2.QtCore import Qt
from PySide2.QtSql import QSqlTableModel
from PySide2.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHeaderView,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class TeamMemberTableGroup(QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Członkowie zespołu orzekającego", parent=parent)
        self.team_member_tab_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.table_model = QSqlTableModel()
        self.table_model.setTable("team_member")
        self.table_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.table_model.select()

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
