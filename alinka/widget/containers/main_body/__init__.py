from PySide2.QtWidgets import QFrame, QVBoxLayout, QWidget

from .content import ContentContainer
from .footer import FooterContainer
from .header import HeaderContainer


class MainBody(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        header_container = HeaderContainer(self)
        self.content_container = ContentContainer(self)
        self.footer_container = FooterContainer(self)
        layout.addWidget(header_container)
        layout.addWidget(self.content_container)
        layout.addWidget(self.footer_container)
