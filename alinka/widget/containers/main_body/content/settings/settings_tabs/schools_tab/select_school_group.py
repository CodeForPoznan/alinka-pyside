from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from alinka import rspo_client
from alinka.constants.common import RSPOSchoolTypes, SchoolTypes
from alinka.schemas.rspo_schema import BaseEntity, InstitutionRequestBody
from alinka.widget.components import LabeledComboBoxComponent, ValidationMixin


class SelectSchoolGroup(QGroupBox, ValidationMixin):
    def __init__(self, parent: QWidget):
        super().__init__(title="Wybierz szkołę", parent=parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        location_frame = QFrame(self)

        location_frame_layout = QHBoxLayout(location_frame)
        location_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.province_combobox = LabeledComboBoxComponent("Województwo", location_frame, required=True)
        self.province_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.province_combobox.combobox.currentTextChanged.connect(self.populate_districts_combobox)

        provinces = rspo_client.list_provinces()
        for province in provinces:
            self.province_combobox.combobox.addItem(province.name, province.id)

        self.district_combobox = LabeledComboBoxComponent("Powiat", location_frame, required=True)
        self.district_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.district_combobox.combobox.currentTextChanged.connect(self.populate_commune_combobox)
        location_frame_layout.addWidget(self.province_combobox)
        location_frame_layout.addWidget(self.district_combobox)

        self.commune_combobox = LabeledComboBoxComponent("Gmina", self, required=True)
        self.commune_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.commune_combobox.combobox.currentTextChanged.connect(self.clear_school_types)
        layout.addWidget(location_frame)
        layout.addWidget(self.commune_combobox)

        self.school_type_combobox = LabeledComboBoxComponent("Rodzaj szkoły", self, required=True)
        self.school_type_combobox.combobox.setPlaceholderText("Wybierz rodzaj szkoły...")
        self.school_type_combobox.combobox.addItems(SchoolTypes.values())
        self.school_type_combobox.combobox.currentTextChanged.connect(self.populate_schools_combobox)
        layout.addWidget(self.school_type_combobox)

        self.schools_combobox = LabeledComboBoxComponent("Szkoła", self, required=True)
        self.schools_combobox.combobox.setPlaceholderText("Wybierz szkołę...")
        self.schools_combobox.combobox.currentTextChanged.connect(self.populate_school_data)
        layout.addWidget(self.schools_combobox)

        self.required_fields = [
            self.province_combobox,
            self.district_combobox,
            self.commune_combobox,
            self.school_type_combobox,
            self.schools_combobox,
        ]

        self.connect_field_clear_handlers(self.required_fields)

    def validate_required_fields(self) -> bool:
        """Validate required fields and highlight missing ones"""
        return super().validate_required_fields(self.required_fields)

    def clear_highlights(self):
        """Clear highlighting from all fields"""
        super().clear_highlights(self.required_fields)

    def populate_districts_combobox(self):
        selected_province_id = self.province_combobox.combobox.currentData()
        self.district_combobox.combobox.clear()
        self.commune_combobox.combobox.clear()
        self.school_type_combobox.combobox.setCurrentIndex(-1)
        self.schools_combobox.combobox.clear()
        self.clear_school_data()
        districts = rspo_client.list_districts(province_id=selected_province_id)
        for district in districts:
            self.district_combobox.combobox.addItem(district.name, district.id)

    def populate_commune_combobox(self):
        selected_province_id = self.province_combobox.combobox.currentData()
        selected_district_id = self.district_combobox.combobox.currentData()
        self.commune_combobox.combobox.clear()
        self.school_type_combobox.combobox.setCurrentIndex(-1)
        self.schools_combobox.combobox.clear()
        self.clear_school_data()
        if not all([selected_district_id, selected_province_id]):
            return
        communes = rspo_client.list_communes(province_id=selected_province_id, district_id=selected_district_id)
        for commune in communes:
            self.commune_combobox.combobox.addItem(commune.name, commune.id)

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

    def clear_school_types(self):
        self.school_type_combobox.combobox.setCurrentIndex(-1)

    def populate_schools_combobox(self):
        self.schools_combobox.combobox.clear()
        selected_province_id = self.province_combobox.combobox.currentData()
        selected_district_id = self.district_combobox.combobox.currentData()
        selected_commune_id = self.commune_combobox.combobox.currentData()
        selected_school_type = self.school_type_combobox.combobox.currentText()
        institution_type_ids = self.get_institution_type_ids(selected_school_type)
        if not all([selected_province_id, selected_district_id, selected_commune_id]):
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
        selected_school_rspo = self.schools_combobox.combobox.currentData()
        school = rspo_client.get_institution(rspo_id=selected_school_rspo)
        self.parent.school_data_group.populate_fields(
            province_id=self.province_combobox.combobox.currentData(),
            district_id=self.district_combobox.combobox.currentData(),
            rspo_id=school.rspo_id,
            rspo_type_id=school.type.id,
            name=school.name,
            type=self.get_school_type_from_school_data(school.type),
            parent_organisation_name=school.parent_organisation_name,
            address=school.address,
            town=school.town,
            postal_code=school.postal_code,
            post=school.post,
        )

    def clear_school_data(self):
        self.parent.school_data_group.clear()
