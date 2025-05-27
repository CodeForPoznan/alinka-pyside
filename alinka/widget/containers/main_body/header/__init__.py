from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class HeaderContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.header_content = QLabel("", self)
        layout.addWidget(self.header_content)

    def set_error_message(self, message: str):
        self.header_content.setText(message)
        self.header_content.setStyleSheet("color: red;")

    def clear_error_message(self):
        self.header_content.setText("")
        self.header_content.setStyleSheet("")
