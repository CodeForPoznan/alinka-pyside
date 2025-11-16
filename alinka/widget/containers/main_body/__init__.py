from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QWidget

from alinka.widget.components import ValidationMixin

from .content import ContentContainer
from .footer import FooterContainer
from .header import HeaderContainer


class MainBody(ValidationMixin, QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.central_widget = parent
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.header_container = HeaderContainer(self)
        self.content_container = ContentContainer(self)
        self.footer_container = FooterContainer(self)
        
        # Set size policies for proper resizing
        self.header_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.footer_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout.addWidget(self.header_container)
        layout.addWidget(self.content_container)
        layout.addWidget(self.footer_container)
        
