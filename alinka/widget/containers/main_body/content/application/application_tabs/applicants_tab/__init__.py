from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from alinka.schemas import DocumentData, PersonalData
from alinka.widget.components import ValidationMixin

from .applicant_data_group import ApplicantDataGroup


class ApplicantsTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.application_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.applicant_1_data_group = ApplicantDataGroup(
            title="Wnioskodawca 1 (otrzymuje gotowy dokument)",
            parent=self,
            checkbox_description="Adres inny niż dziecka",
            initial_visible=True,
        )
        self.applicant_2_data_group = ApplicantDataGroup(
            title="Wnioskodawca 2",
            parent=self,
            checkbox_description="Adres inny niż pierwszego rodzica",
            initial_visible=False,
        )
        add_remove_applicant_btn = QPushButton("Dodaj/usuń wnioskodawcę")
        add_remove_applicant_btn.clicked.connect(self.toggle_applicant_2_group)
        layout.addWidget(self.applicant_1_data_group)
        layout.addWidget(self.applicant_2_data_group)
        layout.addWidget(add_remove_applicant_btn)

        self.containers = [self.applicant_1_data_group, self.applicant_2_data_group]
        self._applicant_2_active = False

    def toggle_applicant_2_group(self):
        if self._applicant_2_active:
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.address_checkbox.checkbox.setChecked(False)
            self.applicant_2_data_group.setVisible(False)
            self._applicant_2_active = False
        else:
            self.applicant_2_data_group.setVisible(True)
            self._applicant_2_active = True

        self.layout().update()
        self.layout().activate()
        self.adjustSize()

    @property
    def applicants(self) -> list[PersonalData]:
        return [applicant.applicant_data for applicant in self.containers if applicant.applicant_data]

    @property
    def is_first_parent_address_different(self) -> bool:
        return self.applicant_1_data_group.address_checkbox.is_checked

    @property
    def is_second_parent_address_different(self) -> bool:
        return self.applicant_2_data_group.address_checkbox.is_checked

    @property
    def is_second_applicant_active(self) -> bool:
        return self._applicant_2_active

    def clear(self) -> None:
        self.applicant_1_data_group.clear()
        self.applicant_2_data_group.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        applicants = document_data.applicants
        checkbox1 = document_data.is_first_parent_address_different
        checkbox2 = document_data.is_second_parent_address_different

        if len(applicants) == 1:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            checkbox = self.applicant_1_data_group.address_checkbox.checkbox
            checkbox.setChecked(checkbox1)
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.setVisible(False)
            self._applicant_2_active = False
        elif len(applicants) == 2:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            self.applicant_2_data_group.populate_applicant_data(applicants[1])
            checkbox1_widget = self.applicant_1_data_group.address_checkbox.checkbox
            checkbox1_widget.setChecked(checkbox1)
            checkbox2_widget = self.applicant_2_data_group.address_checkbox.checkbox
            checkbox2_widget.setChecked(checkbox2)
            self.applicant_2_data_group.setVisible(True)
            self._applicant_2_active = True

    @property
    def is_valid(self) -> bool:
        if self._applicant_2_active:
            return self.applicant_1_data_group.is_valid and self.applicant_2_data_group.is_valid
        return self.applicant_1_data_group.is_valid

    def error_messages(self) -> str | None:
        if not self.applicant_1_data_group.is_valid:
            return self.applicant_1_data_group.error_message

        if self._applicant_2_active and not self.applicant_2_data_group.is_valid:
            return self.applicant_2_data_group.error_message

        return None

    def validate(self) -> bool:
        applicant_1_valid = self.applicant_1_data_group.validate()

        if self._applicant_2_active:
            applicant_2_valid = self.applicant_2_data_group.validate()
            return applicant_1_valid and applicant_2_valid

        return applicant_1_valid

    def clear_validation_state(self) -> None:
        self.applicant_1_data_group.clear_validation_state()
        if self._applicant_2_active:
            self.applicant_2_data_group.clear_validation_state()
