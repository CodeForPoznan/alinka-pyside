from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSizePolicy, QWidget

from alinka.widget.containers.main_body import MainBody
from alinka.widget.containers.sidebar import SidebarMenu


class CentralWidget(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.side_bar = SidebarMenu(self)
        self.main_body = MainBody(self)
        
        # Set size policies for proper resizing
        self.side_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.main_body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(self.side_bar)
        layout.addWidget(self.main_body)
