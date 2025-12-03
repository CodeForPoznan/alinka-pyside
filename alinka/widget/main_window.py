from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from alinka.statics import get_statics_resource_path
from alinka.widget.containers.central_widget import CentralWidget
from alinka.widget.styles import (
    get_custom_overrides_stylesheet,
    get_validation_stylesheet,
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        icon = QIcon()
        icon.addFile(get_statics_resource_path("alinka.svg"))
        self.setWindowTitle("Alinka")

        self.setMinimumSize(1000, 600)

        # Apply validation and custom overrides on top of qt-material
        # This ensures validation highlighting and custom styles override
        custom_styles = get_validation_stylesheet() + get_custom_overrides_stylesheet()
        self.setStyleSheet(custom_styles)

        central_widget = CentralWidget(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(central_widget)
        self.setWindowIcon(icon)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
