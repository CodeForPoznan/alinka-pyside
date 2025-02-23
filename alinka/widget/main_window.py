import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QHBoxLayout, QWidget

from alinka.widget.containers.central_widget import CentralWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        icon = QIcon()
        icon.addFile(os.path.join("statics", "alinka.svg"))
        self.setWindowTitle("Alinka")

        central_widget = CentralWidget(self)
        layout = QHBoxLayout(self)
        layout.addWidget(central_widget)
        self.setWindowIcon(icon)
        self.show()
