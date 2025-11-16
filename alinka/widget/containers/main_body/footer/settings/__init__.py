from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from .support_center_tab import SettingsSupportCenterDataContainer


class SettingsFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        self.footer_support_center_data_container = \
            SettingsSupportCenterDataContainer(self, True)
        layout.addWidget(self.footer_support_center_data_container)

    def show_footer_support_center_data_container(self):
        self.footer_support_center_data_container.setVisible(True)
