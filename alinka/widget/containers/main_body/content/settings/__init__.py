from PySide2.QtWidgets import QTabWidget, QWidget

from .settings_tabs import (
    SchoolTabContainer,
    SupportCenterTabContainer,
    TeamMemberTabContainer,
)


class SettingsContainer(QTabWidget):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.content_container = parent
        self.setVisible(visible)
        self.support_center_tab_container = SupportCenterTabContainer(self)
        self.schools_tab_container = SchoolTabContainer(self)
        self.team_member_tab_container = TeamMemberTabContainer(self)
        self.addTab(self.support_center_tab_container, "Dane poradni")
        self.addTab(self.schools_tab_container, "Szkoły")
        self.addTab(self.team_member_tab_container, "Zespół orzekający")
        self.currentChanged.connect(self.handle_footer_visibility)

    @property
    def support_center_data(self):
        return self.support_center_tab_container.support_center_data

    def handle_footer_visibility(self, index):
        setting_footer_container = self.content_container.main_body_container.footer_container.settings_footer_container
        match index:
            case 0:
                setting_footer_container.show_footer_support_center_data_container()
            case 1:
                setting_footer_container.show_footer_schools_container()
            case 2:
                setting_footer_container.show_footer_team_members_container()
