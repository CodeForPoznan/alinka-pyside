from PySide2.QtWidgets import QFrame, QVBoxLayout, QWidget

from .application import ApplicationContainer
from .settings import SettingsContainer


class ContentContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.main_body_container = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.application_container = ApplicationContainer(self, visible=False)
        layout.addWidget(self.application_container)

        self.settings_container = SettingsContainer(self, visible=True)
        layout.addWidget(self.settings_container)

    def show_settings_container(self):
        self.application_container.setVisible(False)
        self.settings_container.setVisible(True)

    def show_application_container(self):
        self.settings_container.setVisible(False)
        self.application_container.setVisible(True)
