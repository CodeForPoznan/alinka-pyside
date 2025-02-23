from PySide2.QtWidgets import QVBoxLayout, QWidget

from .team_member_table_group import TeamMemberTableGroup


class TeamMemberTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        layout = QVBoxLayout(self)
        self.team_members_table_group = TeamMemberTableGroup(self)
        layout.addWidget(self.team_members_table_group)
