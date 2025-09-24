from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.db.queries import get_school_by_name
from alinka.schemas import ChildData, DocumentData, SchoolData, SchoolDbSchema
from alinka.widget.components import ValidationMixin

from .child_data_group import ChildDataGroupContainer
from .general_data_group import GeneralDataGroupContainer
from .school_data_group import SchoolDataGroupContainer


class ChildDataTabContainer(QWidget, ValidationMixin):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.general_data_group = GeneralDataGroupContainer(self)
        self.child_data_group = ChildDataGroupContainer(self)
        self.school_data_group = SchoolDataGroupContainer(self)

        layout.addWidget(self.general_data_group)
        layout.addWidget(self.child_data_group)
        layout.addWidget(self.school_data_group)

        self.validation_groups = [self.school_data_group, self.child_data_group]

    def validate_required_fields(self) -> bool:
        """Validate all validation groups and highlight missing fields"""
        is_valid = True

        for group in self.validation_groups:
            if not group.validate_required_fields():
                is_valid = False

        return is_valid

    def clear_highlights(self):
        """Clear highlighting from all validation groups"""
        for group in self.validation_groups:
            group.clear_highlights()

    @property
    def is_valid(self) -> bool:
        return all(
            container.is_valid for container in [self.general_data_group, self.child_data_group, self.school_data_group]
        )

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Uzupełnij formularz"
        return None

    @property
    def child_data(self) -> ChildData:
        return ChildData(
            pesel=self.child_data_group.pesel.text,
            address=self.child_data_group.address.text,
            town=self.child_data_group.town.text,
            post=self.child_data_group.post.text,
            postal_code=self.child_data_group.postal_code.text,
            full_name=self.child_data_group.child_name_nom.text,
            full_name_gen=self.child_data_group.child_name_gen.text,
            birth_place=self.child_data_group.birth_place.text,
            klass=self.school_data_group.school_klass.text,
            profession=self.school_data_group.school_profession.text,
            student=self.school_data_group.student_checkbox.checkbox.isChecked(),
        )

    @property
    def school_data(self) -> SchoolData:
        selected_school_name = self.school_data_group.school.combobox.currentText()

        if not selected_school_name or selected_school_name.strip() == "":
            raise ValueError("No school selected. Please select a school from the dropdown.")

        school: SchoolDbSchema = get_school_by_name(selected_school_name)

        if not school:
            raise ValueError(f"School '{selected_school_name}' not found in database.")

        return SchoolData(
            address=school.address,
            town=school.town,
            postal_code=school.postal_code,
            post=school.post,
            name=school.name,
            type=school.type,
            parent_organisation=school.parent_organisation_name,
        )

    def clear(self) -> None:
        self.general_data_group.clear()
        self.child_data_group.clear()
        self.school_data_group.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        self.general_data_group.populate_data(document_data)
        self.child_data_group.populate_data(document_data)
        self.school_data_group.populate_data(document_data)
