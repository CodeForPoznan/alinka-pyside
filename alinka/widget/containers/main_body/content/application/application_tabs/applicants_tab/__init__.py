from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from alinka.schemas import DocumentData, PersonalData

from .applicant_data_group import ApplicantDataGroup


class ApplicantsTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.applicant_1_data_group = ApplicantDataGroup(
            title="Wnioskodawca 1", parent=self, checkbox_description="Adres taki sam jak dziecka", initial_height=200
        )
        self.applicant_2_data_group = ApplicantDataGroup(
            title="Wnioskodawca 2",
            parent=self,
            checkbox_description="Adres taki sam jak pierwszego rodzica",
            initial_height=0,
        )
        add_remove_applicant_btn = QPushButton("Dodaj/usuń wnioskodawcę")
        add_remove_applicant_btn.clicked.connect(self.toggle_applicant_2_group)
        layout.addWidget(self.applicant_1_data_group)
        layout.addWidget(self.applicant_2_data_group)
        layout.addWidget(add_remove_applicant_btn)

    def toggle_applicant_2_group(self):
        if self.applicant_2_data_group.height():
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.checkable = False
            self.applicant_2_data_group.setFixedHeight(0)
        else:
            self.applicant_2_data_group.checkable = True
            self.applicant_2_data_group.setFixedHeight(200)

    @property
    def applicants(self) -> list[PersonalData]:
        return [
            applicant.applicant_data
            for applicant in [self.applicant_1_data_group, self.applicant_2_data_group]
            if applicant.applicant_data
        ]

    @property
    def address_child_checkbox(self) -> bool:
        return self.applicant_1_data_group.address_checkbox.checkbox.isChecked()

    @property
    def address_first_parent_checkbox(self) -> bool:
        return self.applicant_2_data_group.address_checkbox.checkbox.isChecked()

    @property
    def is_valid(self) -> bool:
        # Should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/91
        return True

    def error_message(self) -> str | None:
        # Should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/91
        return None

    def clear(self) -> None:
        self.applicant_1_data_group.clear()
        self.applicant_2_data_group.clear()
        self.applicant_1_data_group.address_checkbox.checkbox.setChecked(False)
        self.applicant_2_data_group.address_checkbox.checkbox.setChecked(False)

    def populate_data(self, document_data: DocumentData) -> None:
        applicants = document_data.applicants
        checkbox1 = document_data.address_child_checkbox
        checkbox2 = document_data.address_first_parent_checkbox

        if len(applicants) == 1:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            self.applicant_1_data_group.address_checkbox.checkbox.setChecked(checkbox1)
            self.applicant_2_data_group.clear()
            self.applicant_2_data_group.checkable = False
            self.applicant_2_data_group.setFixedHeight(0)
        elif len(applicants) == 2:
            self.applicant_1_data_group.populate_applicant_data(applicants[0])
            self.applicant_2_data_group.populate_applicant_data(applicants[1])
            self.applicant_1_data_group.address_checkbox.checkbox.setChecked(checkbox1)
            self.applicant_2_data_group.address_checkbox.checkbox.setChecked(checkbox2)
            self.applicant_2_data_group.setFixedHeight(200)
