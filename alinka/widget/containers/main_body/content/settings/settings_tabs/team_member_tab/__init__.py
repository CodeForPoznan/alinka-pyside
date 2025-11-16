from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from .team_member_table_group import TeamMemberTableGroup


class TeamMemberTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)
        
        self.team_members_table_group = TeamMemberTableGroup(self)
        layout.addWidget(self.team_members_table_group, 0)
        
        # Connect signal to refresh meeting tab when team members change
        self.team_members_table_group.table_model.memberChanged.connect(
            self._refresh_meeting_tab
        )
        
        # Add przewodniczący section below table
        self.przewodniczacy_group = QGroupBox("Przewodniczący zespołu", self)
        przewodniczacy_layout = QVBoxLayout(self.przewodniczacy_group)
        layout.addWidget(self.przewodniczacy_group, 0)
        
        layout.addStretch()  # Push content to top
    
    def _refresh_meeting_tab(self):
        """Refresh the meeting tab when team members change."""
        try:
            # Navigate to the meeting tab through the component hierarchy
            content_container = self.settings_container.content_container
            meeting_tab = content_container.application_container.meeting_tab_container
            meeting_tab.refresh_team_members()
        except (AttributeError, RuntimeError):
            # If containers don't exist or are deleted, silently ignore
            pass

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
