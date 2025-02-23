from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class LabeledInputComponent(QFrame):
    def __init__(self, text, parent, min_lenght: int | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        label = QLabel(text=text, parent=self)
        self.line_edit = QLineEdit(self)
        if min_lenght:
            self.line_edit.setMinimumWidth(min_lenght)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)

    @property
    def text(self) -> str:
        return self.line_edit.text()

    @text.setter
    def text(self, text):
        self.line_edit.setText(text)

    def clear(self) -> None:
        self.line_edit.clear()


class LabeledComboBoxComponent(QFrame):
    def __init__(self, text, parent, min_lenght: int | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text=text, parent=self)
        self.combobox = QComboBox(self)
        if min_lenght:
            self.combobox.setMinimumWidth(min_lenght)
        layout.addWidget(label)
        layout.addWidget(self.combobox)


class LabeledCheckboxComponent(QFrame):
    def __init__(self, text, parent, label_position: str = "above"):
        super().__init__(parent)
        label = QLabel(text=text, parent=self)
        self.checkbox = QCheckBox(self)

        layout_class = QVBoxLayout if label_position == "above" else QHBoxLayout
        layout = layout_class(self)
        layout.addWidget(label)
        if label_position == "above":
            layout.insertWidget(1, self.checkbox)
        else:
            layout.addWidget(self.checkbox)


class LabeledDateComponent(QFrame):
    def __init__(self, text, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text=text, parent=self)
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.dateTime()
        layout.addWidget(label)
        layout.addWidget(self.date_input)
