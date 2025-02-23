from PySide2.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget


class SettingsTeamMembersContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.settings_footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)

        self.add_new_member_btn = QPushButton("Dodaj", self)
        self.add_new_member_btn.clicked.connect(self.add_new_member)
        self.remove_selected_member_btn = QPushButton("Usuń", self)
        self.remove_selected_member_btn.setEnabled(False)
        self.remove_selected_member_btn.clicked.connect(self.remove_selected_member)

        layout.addWidget(self.add_new_member_btn)
        layout.addWidget(self.remove_selected_member_btn)

    def add_new_member(self):
        content_container = self.settings_footer_container.footer_container.main_body_container.content_container
        table_model = (
            content_container.settings_container.team_member_tab_container.team_members_table_group.table_model
        )
        row_count = table_model.rowCount()
        table_model.insertRow(row_count)

    def remove_selected_member(self):
        content_container = self.settings_footer_container.footer_container.main_body_container.content_container
        team_members_table_group = (
            content_container.settings_container.team_member_tab_container.team_members_table_group
        )
        table = team_members_table_group.table
        table_model = team_members_table_group.table_model

        selected_indexes = table.selectionModel().selectedRows()
        for selected_index in selected_indexes:
            table_model.removeRow(selected_index.row())
        table_model.select()

    @property
    def team_members(self):
        return self.parent.parent.content_container.settings_container.team_members
