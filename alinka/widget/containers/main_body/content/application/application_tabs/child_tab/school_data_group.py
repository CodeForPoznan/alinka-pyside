from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QVBoxLayout

from alinka.constants.common import SchoolTypes
from alinka.db.queries import filter_schools_by_type
from alinka.schemas import DocumentData
from alinka.widget.components import (
    LabeledCheckboxComponent,
    LabeledComboBoxComponent,
    LabeledInputComponent,
    ValidationMixin,
)


class SchoolDataGroupContainer(QGroupBox, ValidationMixin):
    def __init__(self, parent):
        super().__init__(title="Szkoła", parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.school_type = LabeledComboBoxComponent("Rodzaj Szkoły", self, 300, required=True)
        self.school_type.combobox.setPlaceholderText("Wybierz z listy...")
        self.school_type.combobox.addItems(SchoolTypes.values())
        self.school_type.combobox.currentTextChanged.connect(self.populate_school_combobox)

        self.school = LabeledComboBoxComponent("Szkoła", self, 300, required=True)
        self.school.combobox.setPlaceholderText("Wybierz szkołę...")

        school_klass_profession_frame = QFrame(self)
        school_klass_profession_frame_layout = QHBoxLayout(school_klass_profession_frame)
        school_klass_profession_frame_layout.setContentsMargins(0, 0, 0, 0)

        self.student_checkbox = LabeledCheckboxComponent("Uczeń", school_klass_profession_frame)

        self.school_klass = LabeledInputComponent("Klasa", school_klass_profession_frame)
        self.school_profession = LabeledInputComponent("Zawód", school_klass_profession_frame)

        school_klass_profession_frame_layout.addWidget(self.student_checkbox)
        school_klass_profession_frame_layout.addWidget(self.school_klass)
        school_klass_profession_frame_layout.addWidget(self.school_profession)

        layout.addWidget(self.school_type)
        layout.addWidget(self.school)
        layout.addWidget(school_klass_profession_frame)

        self.required_fields = [self.school_type, self.school]
        self.connect_field_clear_handlers(self.required_fields)

    def populate_school_combobox(self):
        """On change selected school type we should clean item of school dropdown"""
        selected_school_type = self.school_type.combobox.currentText()
        self.school.combobox.clear()
        schools = filter_schools_by_type(selected_school_type)
        self.school.combobox.addItems([school.name for school in schools])

    def refresh_school_dropdown(self):
        """Refresh the school dropdown with latest schools from database"""
        current_school_type = self.school_type.combobox.currentText()
        if current_school_type:
            self.populate_school_combobox()

    def validate_required_fields(self) -> bool:
        """Validate required fields and highlight missing ones"""
        return super().validate_required_fields(self.required_fields)

    def clear_highlights(self):
        """Clear highlighting from all fields"""
        super().clear_highlights(self.required_fields)

    @property
    def is_valid(self) -> bool:
        if not self.school_type.combobox.currentText() or not self.school.combobox.currentText():
            return False

        return all(
            component.is_valid
            for component in [self.school_type, self.school, self.school_klass, self.school_profession]
        )

    @property
    def error_message(self) -> str | None:
        if not self.school_type.combobox.currentText():
            return "Wybierz rodzaj szkoły."

        if not self.school.combobox.currentText():
            return "Wybierz szkołę z listy."

        for component in [self.school_type, self.school, self.school_klass, self.school_profession]:
            if not component.is_valid:
                return component.error_message
        return None

    def clear(self) -> None:
        self.school_type.combobox.setCurrentIndex(-1)
        self.school.combobox.setCurrentIndex(-1)
        self.student_checkbox.checkbox.setChecked(False)
        self.school_klass.clear()
        self.school_profession.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        school_data = document_data.school
        child_data = document_data.child
        self.school_type.combobox.setCurrentText(school_data.type)
        self.school.combobox.setCurrentText(school_data.name)
        self.student_checkbox.checkbox.setChecked(child_data.student)
        self.school_klass.text = child_data.klass
        self.school_profession.text = child_data.profession
