from PySide2.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from alinka.widget.containers.main_body import MainBody
from alinka.widget.containers.sidebar import SidebarMenu


class CentralWidget(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.side_bar = SidebarMenu(self)
        self.main_body = MainBody(self)
        layout.addWidget(self.side_bar)
        layout.addWidget(self.main_body)
