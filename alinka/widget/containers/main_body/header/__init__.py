from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class HeaderContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        header_content = QLabel("Exemplary header content", self)
        layout.addWidget(header_content)
