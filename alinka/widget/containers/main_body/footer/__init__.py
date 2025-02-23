from PySide2.QtWidgets import QFrame, QHBoxLayout, QWidget

from .application import ApplicationFooterContainer
from .settings import SettingsFooterContainer


class FooterContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.main_body_container = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.application_footer_container = ApplicationFooterContainer(self, visible=False)
        layout.addWidget(self.application_footer_container)

        self.settings_footer_container = SettingsFooterContainer(self, visible=True)
        layout.addWidget(self.settings_footer_container)

    def show_settings_footer_container(self):
        self.application_footer_container.setVisible(False)
        self.settings_footer_container.setVisible(True)

    def show_application_footer_container(self):
        self.settings_footer_container.setVisible(False)
        self.application_footer_container.setVisible(True)
