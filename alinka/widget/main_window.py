from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QHBoxLayout, QWidget

from alinka.statics import get_statics_resource_path
from alinka.widget.containers.central_widget import CentralWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        icon = QIcon()
        icon.addFile(get_statics_resource_path("alinka.svg"))
        self.setWindowTitle("Alinka")

        central_widget = CentralWidget(self)
        layout = QHBoxLayout(self)
        layout.addWidget(central_widget)
        self.setWindowIcon(icon)
        self.show()
