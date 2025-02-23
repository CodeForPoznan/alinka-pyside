from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QVBoxLayout

from alinka.constants.common import SchoolTypes
from alinka.db.queries import filter_schools_by_type
from alinka.widget.components import (
    LabeledCheckboxComponent,
    LabeledComboBoxComponent,
    LabeledInputComponent,
)


class SchoolDataGroupContainer(QGroupBox):
    def __init__(self, parent):
        super().__init__(title="Szkoła", parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.school_type = LabeledComboBoxComponent("Rodzaj Szkoły", self, 300)
        self.school_type.combobox.setPlaceholderText("Wybierz z listy...")
        self.school_type.combobox.addItems(SchoolTypes.values())
        self.school_type.combobox.currentTextChanged.connect(self.populate_school_cb)

        self.school = LabeledComboBoxComponent("Szkoła", self, 300)

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

    def populate_school_cb(self):
        """On change selected school type we should clean item of school dropdown"""
        selected_school_type = self.school_type.combobox.currentText()
        self.school.combobox.clear()
        schools = filter_schools_by_type(selected_school_type)
        self.school.combobox.addItems([school.name for school in schools])
