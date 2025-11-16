from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from alinka import rspo_client
from alinka.constants.common import RSPOSchoolTypes, SchoolTypes
from alinka.schemas.rspo_schema import BaseEntity, InstitutionRequestBody
from alinka.widget.components import (
    LabeledComboBoxComponent,
    SelectProvinceDistrictGroup,
    ValidationMixin,
)


class SelectSchoolGroup(ValidationMixin, QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Wybierz szkołę", parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        self.province_district_group = SelectProvinceDistrictGroup(self)
        self.province_district_group.selection_changed.connect(self.province_district_changed)

        self.commune_combobox = LabeledComboBoxComponent("Gmina", self, required=True)
        self.commune_combobox.combobox.setPlaceholderText("Wybierz z listy...")
        self.commune_combobox.combobox.currentTextChanged.connect(
            self.clear_schools
        )
        layout.addWidget(self.province_district_group)
        layout.addWidget(self.commune_combobox)

        self.school_type_combobox = LabeledComboBoxComponent("Rodzaj szkoły", self, required=True, static=True)
        self.school_type_combobox.combobox.setPlaceholderText("Wybierz rodzaj szkoły...")
        self.school_type_combobox.combobox.addItems(SchoolTypes.values())
        self.school_type_combobox.combobox.currentTextChanged.connect(self.populate_schools_combobox)
        layout.addWidget(self.school_type_combobox)

        self.schools_combobox = LabeledComboBoxComponent("Szkoła", self, required=True)
        self.schools_combobox.combobox.setPlaceholderText("Wybierz szkołę...")
        self.schools_combobox.combobox.currentTextChanged.connect(self.populate_school_data)
        layout.addWidget(self.schools_combobox)

        self.components = [
            self.province_district_group,
            self.commune_combobox,
            self.school_type_combobox,
            self.schools_combobox,
        ]

    def province_district_changed(self):
        self.populate_commune_combobox()
        self.school_type_combobox.remove_selection()
        self.schools_combobox.clear()
        self.clear_school_data()

    @staticmethod
    def get_institution_type_ids(school_type: SchoolTypes | None) -> list[int]:
        institution_types = rspo_client.list_institution_types()
        match school_type:
            case SchoolTypes.PRZEDSZKOLE.value:
                return [it.id for it in institution_types if it.name == RSPOSchoolTypes.PRZEDSZKOLE.value]
            case SchoolTypes.SZKOLA_PODSTAWOWA.value:
                return [it.id for it in institution_types if it.is_primary_school]
            case SchoolTypes.SZKOLA_PONADPODSTAWOWA.value:
                return [it.id for it in institution_types if it.is_secondary_school]
            case _:
                return [
                    it.id
                    for it in institution_types
                    if it.name == RSPOSchoolTypes.PRZEDSZKOLE.value or it.is_primary_school or it.is_secondary_school
                ]

    @staticmethod
    def get_school_type_from_school_data(school_type: BaseEntity) -> SchoolTypes | None:
        institution_types = rspo_client.list_institution_types()
        if school_type.name == RSPOSchoolTypes.PRZEDSZKOLE:
            return SchoolTypes.PRZEDSZKOLE.value
        elif school_type.id in [it.id for it in institution_types if it.is_primary_school]:
            return SchoolTypes.SZKOLA_PODSTAWOWA.value
        elif school_type.id in [it.id for it in institution_types if it.is_secondary_school]:
            return SchoolTypes.SZKOLA_PONADPODSTAWOWA.value
        else:
            return None

    def populate_commune_combobox(self) -> None:
        self.commune_combobox.clear()
        selected_province_id = self.province_district_group.province_id
        selected_district_id = self.province_district_group.district_id
        if not (selected_province_id and selected_district_id):
            return

        try:
            communes = rspo_client.list_communes(
                province_id=selected_province_id,
                district_id=selected_district_id
            )
            for commune in communes:
                self.commune_combobox.combobox.addItem(
                    commune.name, commune.id
                )
        except Exception as e:
            # If we can't load communes, show error and enable manual entry
            error_msg = "Błąd ładowania gmin - sprawdź połączenie"
            self.commune_combobox.combobox.setPlaceholderText(error_msg)
            self.commune_combobox.combobox.setEditable(True)
            self.commune_combobox.combobox.setEnabled(True)
            print(f"Error loading communes: {e}")

    def populate_schools_combobox(self):
        self.schools_combobox.clear()

        selected_province_id = self.province_district_group.province_id
        selected_district_id = self.province_district_group.district_id
        selected_commune_id = self.commune_combobox.combobox.currentData()
        selected_school_type = self.school_type_combobox.combobox.currentText()
        institution_type_ids = self.get_institution_type_ids(
            selected_school_type
        )
        if not all([
            selected_province_id,
            selected_district_id,
            selected_commune_id,
            institution_type_ids
        ]):
            return

        self.schools = rspo_client.list_institutions(
            body=InstitutionRequestBody(
                province_id=selected_province_id,
                district_id=selected_district_id,
                commune_id=selected_commune_id,
                institution_type_ids=institution_type_ids,
            )
        )
        for school in self.schools.items:
            self.schools_combobox.combobox.addItem(school.name, school.id)

    def populate_school_data(self):
        # School data group removed - no longer needed for settings
        pass

    def clear_school_types(self) -> None:
        self.school_type_combobox.remove_selection()
        self.clear_school_data()

    def clear_school_data(self):
        # School data group removed - no longer needed for settings
        pass

    def clear_schools(self):
        self.schools_combobox.clear()
        self.clear_school_data()

    @property
    def is_valid(self) -> bool:
        return all(component.is_valid for component in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message

        return None

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])

    def clear_validation_state(self) -> None:
        # Clear validation for child components only
        for c in self.components:
            c.clear_validation_state()
