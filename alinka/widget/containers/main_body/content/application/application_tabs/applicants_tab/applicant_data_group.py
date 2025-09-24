from PySide6.QtWidgets import QGridLayout, QGroupBox, QWidget

from alinka.schemas import PersonalData
from alinka.widget.components import LabeledCheckboxComponent, LabeledInputComponent


class ApplicantDataGroup(QGroupBox):
    def __init__(self, title: str, parent: QWidget, checkbox_description: str, initial_height: int):
        super().__init__(title=title, parent=parent)
        self.setFixedHeight(initial_height)
        layout = QGridLayout(self)
        self.full_name = LabeledInputComponent("Imię i nazwisko", self, 200)
        self.full_name_gen = LabeledInputComponent("Imię i nazwisko (dopełniacz)", self, 200)
        layout.addWidget(self.full_name, 0, 0)
        layout.addWidget(self.full_name_gen, 0, 1)

        self.address_checkbox = LabeledCheckboxComponent(checkbox_description, self, "right")
        layout.addWidget(self.address_checkbox, 1, 0)

        self.address = LabeledInputComponent("Adres", self)
        self.town = LabeledInputComponent("Miejscowość", self)
        layout.addWidget(self.address, 2, 0)
        layout.addWidget(self.town, 2, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self)
        self.post = LabeledInputComponent("Poczta", self)
        layout.addWidget(self.postal_code, 3, 0)
        layout.addWidget(self.post, 3, 1)

    def populate_applicant_data(self, applicant_data: PersonalData) -> None:
        self.full_name.text = applicant_data.full_name
        self.full_name_gen.text = applicant_data.full_name_gen
        self.address.text = applicant_data.address
        self.town.text = applicant_data.town
        self.postal_code.text = applicant_data.postal_code
        self.post.text = applicant_data.post

    def clear(self) -> None:
        self.full_name.clear()
        self.full_name_gen.clear()
        self.address_checkbox.checkbox.setChecked(False)
        self.address.clear()
        self.town.clear()
        self.postal_code.clear()
        self.post.clear()

    @property
    def applicant_data(self) -> PersonalData | None:
        if self.full_name.text:
            return PersonalData(
                full_name=self.full_name.text,
                full_name_gen=self.full_name_gen.text,
                address=self.address.text,
                town=self.town.text,
                postal_code=self.postal_code.text,
                post=self.post.text,
            )

    @property
    def is_valid(self) -> bool:
        # should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/91
        return True

    def error_message(self) -> str | None:
        # should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/91
        return None
