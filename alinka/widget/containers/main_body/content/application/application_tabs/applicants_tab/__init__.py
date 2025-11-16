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
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.applicant_1_data_group = ApplicantDataGroup(
            title="Wnioskodawca 1", parent=self, checkbox_description="Adres inny niż dziecka", initial_visible=True
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

    def toggle_applicant_2_group(self):
        if self.applicant_2_data_group.isVisible():
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.address_checkbox.checkbox.setChecked(False)
            self.applicant_2_data_group.setVisible(False)
        else:
            self.applicant_2_data_group.setVisible(True)

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
        return self.applicant_2_data_group.is_visible

    def clear(self) -> None:
        self.applicant_1_data_group.clear()
        self.applicant_2_data_group.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        applicants = document_data.applicants
        checkbox1 = document_data.is_first_parent_address_different
        checkbox2 = document_data.is_second_parent_address_different

        if len(applicants) == 1:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            self.applicant_1_data_group.address_checkbox.checkbox.setChecked(checkbox1)
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.setVisible(False)
        elif len(applicants) == 2:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            self.applicant_2_data_group.populate_applicant_data(applicants[1])
            self.applicant_1_data_group.address_checkbox.checkbox.setChecked(checkbox1)
            self.applicant_2_data_group.address_checkbox.checkbox.setChecked(checkbox2)
            self.applicant_2_data_group.setVisible(True)

    @property
    def is_valid(self) -> bool:
        return all(applicant.is_valid for applicant in self.containers if applicant.isVisible())

    def error_messages(self) -> str | None:
        for applicant in self.containers:
            if applicant.isVisible() and not applicant.is_valid:
                return applicant.error_message

        return None

    def validate(self) -> bool:
        return all([a.validate() for a in self.containers if a.isVisible()])

    def clear_validation_state(self) -> None:
        self.application_container.clear_validation_state()
