from PySide2.QtWidgets import QFrame, QHBoxLayout, QWidget

from .schools_tab import SettingsSchoolsContainer
from .support_center_tab import SettingsSupportCenterDataContainer
from .team_member_tab import SettingsTeamMembersContainer


class SettingsFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.footer_support_center_data_container = SettingsSupportCenterDataContainer(self, True)
        self.footer_schools_container = SettingsSchoolsContainer(self, False)
        self.footer_team_members_container = SettingsTeamMembersContainer(self, False)
        layout.addWidget(self.footer_support_center_data_container)
        layout.addWidget(self.footer_schools_container)
        layout.addWidget(self.footer_team_members_container)

    def show_footer_support_center_data_container(self):
        self.footer_support_center_data_container.setVisible(True)
        self.footer_schools_container.setVisible(False)
        self.footer_team_members_container.setVisible(False)

    def show_footer_schools_container(self):
        self.footer_support_center_data_container.setVisible(False)
        self.footer_schools_container.setVisible(True)
        self.footer_team_members_container.setVisible(False)

    def show_footer_team_members_container(self):
        self.footer_support_center_data_container.setVisible(False)
        self.footer_schools_container.setVisible(False)
        self.footer_team_members_container.setVisible(True)
