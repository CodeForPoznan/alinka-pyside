from PySide2.QtWidgets import QFrame, QHBoxLayout, QWidget


class SettingsSchoolsContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
