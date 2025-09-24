from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox

from alinka.schemas import DocumentData
from alinka.widget.components import LabeledInputComponent, ValidationMixin
from alinka.widget.validators import PeselValidator


class ChildDataGroupContainer(QGroupBox, ValidationMixin):
    def __init__(self, parent):
        super().__init__(title="Uczeń", parent=parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.child_name_nom = LabeledInputComponent("Imię i nazwisko", self, 200, required=True)
        self.child_name_gen = LabeledInputComponent("Imię i nazwisko (dopełniacz)", self, 200, required=True)
        layout.addWidget(self.child_name_nom, 0, 0)
        layout.addWidget(self.child_name_gen, 0, 1)

        self.birth_place = LabeledInputComponent("Miejsce urodzenia", self, required=True)
        self.pesel_validator = PeselValidator()
        self.pesel = LabeledInputComponent("PESEL", self, validator=self.pesel_validator, required=True)
        self.pesel.line_edit.textChanged.connect(self.check_and_update_pesel_input)
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

        self.required_fields = [
            self.child_name_nom,
            self.child_name_gen,
            self.birth_place,
            self.pesel,
            self.address,
            self.town,
            self.postal_code,
            self.post,
        ]

        self.auto_clear_fields = [
            self.child_name_nom,
            self.child_name_gen,
            self.birth_place,
            self.address,
            self.town,
            self.postal_code,
            self.post,
        ]

        self.connect_field_clear_handlers(self.auto_clear_fields)

    def check_and_update_pesel_input(self, pesel: str) -> None:
        state, _, _ = self.pesel_validator.validate(pesel, 0)
        if state == PeselValidator.Intermediate and len(pesel) >= 11:
            self.pesel.toggle_highlight("mistyrose")
        elif state == PeselValidator.Acceptable:
            self.pesel.toggle_highlight("lightgreen")
        else:
            self.pesel.toggle_highlight("")

    def validate_required_fields(self) -> bool:
        """Validate required fields and highlight missing ones"""
        return super().validate_required_fields(self.required_fields)

    def clear_highlights(self):
        """Clear highlighting from all fields"""
        super().clear_highlights(self.auto_clear_fields)
        self.pesel.toggle_highlight("")

    @property
    def is_valid(self) -> bool:
        return all(component.is_valid for component in self.required_fields)

    @property
    def error_message(self) -> str | None:
        for component in self.required_fields:
            if not component.is_valid:
                return component.error_message
        return None

    def clear(self) -> None:
        self.child_name_nom.clear()
        self.child_name_gen.clear()
        self.birth_place.clear()
        self.pesel.clear()
        self.address.clear()
        self.town.clear()
        self.postal_code.clear()
        self.post.clear()

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
