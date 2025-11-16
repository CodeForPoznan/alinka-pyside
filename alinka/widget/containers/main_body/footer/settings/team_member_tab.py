from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.widget.toast import show_success


class SettingsTeamMembersContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.settings_footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)

        layout.addStretch()

        self.add_new_member_btn = QPushButton("Dodaj", self)
        self.add_new_member_btn.clicked.connect(self.add_new_member)
        self.add_new_member_btn.setFixedWidth(120)

        self.remove_selected_member_btn = QPushButton("Usuń", self)
        self.remove_selected_member_btn.setEnabled(False)
        self.remove_selected_member_btn.clicked.connect(self.remove_selected_member)
        self.remove_selected_member_btn.setFixedWidth(120)

        layout.addWidget(self.add_new_member_btn)
        layout.addWidget(self.remove_selected_member_btn)

    def add_new_member(self):
        content_container = self.settings_footer_container.footer_container.main_body_container.content_container
        table_model = (
            content_container.settings_container.team_member_tab_container.team_members_table_group.table_model
        )
        row_count = table_model.rowCount()
        table_model.insertRow(row_count)

    def _on_member_added(self):
        """Show toast when a team member is successfully added."""
        show_success(self.window(), "Członek zespołu został dodany")

    def remove_selected_member(self):
        content_container = self.settings_footer_container.footer_container.main_body_container.content_container
        team_members_table_group = (
            content_container.settings_container.team_member_tab_container.team_members_table_group
        )
        table = team_members_table_group.table
        table_model = team_members_table_group.table_model

        selected_rows = sorted(
            (r.row() for r in table.selectionModel().selectedRows()),
            reverse=True,
        )
        if not selected_rows:
            return

        for selected_row in selected_rows:
            table_model.removeRow(selected_row)

        show_success(self.window(), "Członek zespołu został usunięty")

    @property
    def team_members(self):
        return self.parent.parent.content_container.settings_container.team_members
