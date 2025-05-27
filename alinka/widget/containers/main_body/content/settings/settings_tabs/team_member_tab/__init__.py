from PySide6.QtWidgets import QVBoxLayout, QWidget

from .team_member_table_group import TeamMemberTableGroup


class TeamMemberTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        layout = QVBoxLayout(self)
        self.team_members_table_group = TeamMemberTableGroup(self)
        layout.addWidget(self.team_members_table_group)

    @property
    def is_valid(self) -> bool:
        # this method should be implemented in next iteration
        # ticket https://github.com/CodeForPoznan/alinka-pyside/issues/90
        return True

    @property
    def error_message(self) -> str | None:
        # this method should be implemented in next iteration
        # ticket https://github.com/CodeForPoznan/alinka-pyside/issues/90
        return None
