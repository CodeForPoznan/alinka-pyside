from PySide6.QtWidgets import QTabWidget, QWidget

from alinka.constants.common import INVALID_TAB_TOOLTIP_MESSAGE
from alinka.widget.components import ValidationMixin
from alinka.widget.custom_tabbar import ValidationTabBar

from .settings_tabs import (
    AppSettingsTabContainer,
    CreatorsTabContainer,
    SupportCenterTabContainer,
)


class SettingsContainer(ValidationMixin, QTabWidget):
    def __init__(self, parent: QWidget, content_container, visible: bool = False):
        super().__init__(parent)
        self.content_container = content_container
        self.setVisible(visible)

        # Install custom tab bar for validation highlighting
        custom_tab_bar = ValidationTabBar(self)
        self.setTabBar(custom_tab_bar)

        # track invalid tabs
        self._invalid_tabs = set()

        self.support_center_tab_container = SupportCenterTabContainer(self)
        self.app_settings_tab_container = AppSettingsTabContainer(self)
        self.creators_tab_container = CreatorsTabContainer(self)
        self.addTab(self.support_center_tab_container, "Dane poradni")
        self.addTab(self.app_settings_tab_container, "Ustawienia aplikacji")
        self.addTab(self.creators_tab_container, "O aplikacji")
        self.currentChanged.connect(self.update_breadcrumb)

    @property
    def is_valid(self) -> bool:
        return self.support_center_tab_container.is_valid

    @property
    def error_message(self) -> str | None:
        if not self.support_center_tab_container.is_valid:
            return self.support_center_tab_container.error_message

        return None

    @property
    def support_center_data(self):
        return self.support_center_tab_container.support_center_data

    def update_breadcrumb(self, index: int):
        """Update breadcrumb when tab changes"""
        header_container = self.content_container.main_body_container.header_container
        tab_name = self.tabText(index)
        header_container.set_breadcrumb(f"Ustawienia > {tab_name}")

    def _update_invalid_tabs_display(self) -> None:
        """Update the visual display of invalid tabs"""
        invalid_list = sorted(list(self._invalid_tabs))

        custom_tab_bar = self.tabBar()
        if isinstance(custom_tab_bar, ValidationTabBar):
            custom_tab_bar.set_invalid_tabs(invalid_list)

        # Update tooltips
        for index in range(self.count()):
            if index in self._invalid_tabs:
                tooltip = INVALID_TAB_TOOLTIP_MESSAGE
                custom_tab_bar.setTabToolTip(index, tooltip)
            else:
                custom_tab_bar.setTabToolTip(index, "")

    def mark_invalid_tabs(self, invalid_indices: list[int]) -> None:
        """Mark tabs as invalid using custom tab bar painting"""
        self._invalid_tabs = set(invalid_indices)
        self._update_invalid_tabs_display()

    def clear_invalid_tabs(self) -> None:
        """Clear invalid state from all tabs"""
        self._invalid_tabs.clear()
        self._update_invalid_tabs_display()
