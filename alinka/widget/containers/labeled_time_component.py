from datetime import time as dt_time
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QTextEdit, QTimeEdit, QVBoxLayout

from alinka.widget.components import ValidationMixin


class LabeledTimeComponent(ValidationMixin, QWidget):
    def __init__(self, label: str, parent: QWidget, required = False):
        super().__init__(parent)
        self.required = required

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._label = QLabel(label)
        self._label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")

        self.time_input = QTimeEdit(self)
        self.time_input.setDisplayFormat("hh:mm:ss")
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setKeyboardTracking(False)

        layout.addWidget(self._label)
        layout.addWidget(self.time_input)

    @property
    def time(selfself) -> dt_time:
        q = self.time_input.time()
        return dt_time(q.hour(), q.minute(), q.second())

    @property
    def text(self) -> str:
        return self.time_input.time().toString("HH:mm")

    @text.setter
    def text(self, value: str) -> None:
        q = QTime.fromString(value, "HH:mm")
        if q.isValid():
            self.time_input.setTime(q)

    @property
    def is_valid(self) -> bool:
        if not self.required:
            return True
        return self.time_input.time().isValid()

    @property
    def error_message(self) -> str | None:
        if self.required and not self.time_input.time().isValid():
            return "Proszę wybrać prawidłową godzinę."
        return None

    def validate(self) -> bool:
        valid = self.is_valid
        self.display_validation_result(not valid)
        return valid

    def clear_validation_state(self) -> None:
        self.time_input.setProperty("validationState", "")
        self.time_input.style().unpolish(self.time_input)
        self.time_input.style().polish(self.time_input)

    def display_validation_result(self, invalid: bool) -> None:
        self.time_input.setProperty("validationState", "invalid" if invalid else "valid")
        self.time_input.style().unpolish(self.time_input)
        self.time_input.style().polish(self.time_input)

    def clear(self) -> None:
        self.time_input.setTime(QTime.currentTime())
        self.clear_validation_state()
