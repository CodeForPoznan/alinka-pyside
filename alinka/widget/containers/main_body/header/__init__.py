from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class HeaderContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self.breadcrumb_label = QLabel("", self)
        self.breadcrumb_label.setProperty("breadcrumb", "true")

        self.header_content = QLabel("", self)

        layout.addWidget(self.breadcrumb_label)
        layout.addStretch()
        layout.addWidget(self.header_content)

    def set_error_message(self, message: str):
        self.header_content.setText(message)
        self.header_content.setProperty("error", "true")
        self.header_content.style().unpolish(self.header_content)
        self.header_content.style().polish(self.header_content)

    def set_success_message(self, message: str):
        self.header_content.setText(message)
        self.header_content.setProperty("success", "true")
        self.header_content.style().unpolish(self.header_content)
        self.header_content.style().polish(self.header_content)

    def clear_message(self):
        self.header_content.setText("")
        self.header_content.setProperty("error", "")
        self.header_content.setProperty("success", "")
        self.header_content.style().unpolish(self.header_content)
        self.header_content.style().polish(self.header_content)

    def set_info_message(self, message: str):
        self.header_content.setText(message)
        self.header_content.setStyleSheet("color: black;")

    def set_breadcrumb(self, text: str):
        self.breadcrumb_label.setText(text)
        self.breadcrumb_label.style().unpolish(self.breadcrumb_label)
        self.breadcrumb_label.style().polish(self.breadcrumb_label)

    def clear_breadcrumb(self):
        self.breadcrumb_label.setText("")
