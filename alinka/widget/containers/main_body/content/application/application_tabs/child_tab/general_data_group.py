from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout

from alinka.schemas import DocumentData
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class GeneralDataGroupContainer(ValidationMixin, QGroupBox):
    def __init__(self, parent):
        self.child_tab_container = parent
        super().__init__(title="Dane ogólne", parent=parent)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.decision_no = LabeledInputComponent("Numer orzeczenia", self, required=True)
        self.file_no = LabeledInputComponent("Numer teczki", self, required=True)
        layout.addWidget(self.decision_no)
        layout.addWidget(self.file_no)

        self.components = [self.decision_no, self.file_no]

    def clear(self) -> None:
        for c in self.components:
            c.clear()

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message

        return None

    def populate_data(self, document_data: DocumentData) -> None:
        self.decision_no.text = document_data.decision_no
        self.file_no.text = document_data.file_no

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])

    def clear_validation_state(self) -> None:
        # Clear validation for child components only
        for c in self.components:
            c.clear_validation_state()
