from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from .application import ApplicationFooterContainer
from .browser import BrowserFooterContainer


class FooterContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.main_body_container = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        self.application_footer_container = ApplicationFooterContainer(self, visible=False)
        layout.addWidget(self.application_footer_container)
        self.browser_footer_container = BrowserFooterContainer(self, visible=True)
        layout.addWidget(self.browser_footer_container)

    def show_settings_footer_container(self):
        self.application_footer_container.setVisible(False)
        self.browser_footer_container.setVisible(False)

    def show_application_footer_container(self):
        self.application_footer_container.setVisible(True)
        self.browser_footer_container.setVisible(False)

    def show_browser_footer_container(self):
        self.application_footer_container.setVisible(False)
        self.browser_footer_container.setVisible(True)
