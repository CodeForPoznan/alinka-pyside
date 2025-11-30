from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QGridLayout, QGroupBox

from alinka.schemas import DocumentData
from alinka.widget.components import (
    LabeledCheckboxComponent,
    LabeledInputComponent,
    ValidationMixin,
)
from alinka.widget.validators import PeselValidator


class PeselComponent(LabeledInputComponent):
    def __init__(self, parent):
        super().__init__("PESEL", parent)
        self.pesel_validator = PeselValidator()
        self.line_edit.setValidator(self.pesel_validator)
        self.line_edit.textChanged.connect(self.validate)

    @property
    def is_valid(self) -> bool:
        validation_state, _, _ = self.pesel_validator.validate(self.text, 0)
        return validation_state == QValidator.Acceptable

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Nieprawidłowy PESEL"
        return None


class ChildDataGroupContainer(ValidationMixin, QGroupBox):
    def __init__(self, parent):
        self.child_data_container = parent
        super().__init__(title="Uczeń", parent=parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 24, 10, 10)
        self.child_name_nom = LabeledInputComponent("Imię i nazwisko", self, 200, required=True)
        self.child_name_gen = LabeledInputComponent("Imię i nazwisko (dopełniacz)", self, 200, required=True)
        layout.addWidget(self.child_name_nom, 0, 0)
        layout.addWidget(self.child_name_gen, 0, 1)

        self.birth_place = LabeledInputComponent("Miejsce urodzenia", self, required=True)
        self.pesel = PeselComponent(self)
        layout.addWidget(self.birth_place, 1, 0)
        layout.addWidget(self.pesel, 1, 1)

        self.address = LabeledInputComponent("Adres", self, required=True)
        self.town = LabeledInputComponent("Miejscowość", self, required=True)
        layout.addWidget(self.address, 2, 0)
        layout.addWidget(self.town, 2, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self, required=True)
        self.post = LabeledInputComponent("Poczta", self, required=True)
        layout.addWidget(self.postal_code, 3, 0)
        layout.addWidget(self.post, 3, 1)

        self.student_checkbox = LabeledCheckboxComponent("Uczeń", self)
        layout.addWidget(self.student_checkbox, 4, 0)

        self.school_klass = LabeledInputComponent("Klasa", self)
        self.school_profession = LabeledInputComponent("Zawód", self)
        layout.addWidget(self.school_klass, 5, 0)
        layout.addWidget(self.school_profession, 5, 1)

        self.components = [
            self.child_name_nom,
            self.child_name_gen,
            self.birth_place,
            self.pesel,
            self.address,
            self.town,
            self.postal_code,
            self.post,
            self.student_checkbox,
            self.school_klass,
            self.school_profession,
        ]

    def clear(self) -> None:
        for c in self.components:
            c.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        child = document_data.child
        self.child_name_nom.text = child.full_name
        self.child_name_gen.text = child.full_name_gen
        self.birth_place.text = child.birth_place
        self.pesel.text = child.pesel
        self.address.text = child.address
        self.town.text = child.town
        self.postal_code.text = child.postal_code
        self.post.text = child.post
        self.student_checkbox.checkbox.setChecked(child.student)
        self.school_klass.text = child.klass
        self.school_profession.text = child.profession

    def child_data(self):
        pass

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message
        return None

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])

    def clear_validation_state(self) -> None:
        for c in self.components:
            c.clear_validation_state()
