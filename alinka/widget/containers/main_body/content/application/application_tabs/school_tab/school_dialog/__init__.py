from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout

from alinka.db.queries import create_school, update_school
from alinka.schemas import SchoolDbCreateSchema, SchoolDbSchema
from alinka.widget.components import ValidationMixin

from .school_data_group import SchoolDataGroup
from .select_school_group import SelectSchoolGroup


class SchoolDialog(ValidationMixin, QDialog):
    def __init__(self, parent, title, school_data: SchoolDbSchema | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(800, 330)

        layout = QVBoxLayout(self)
        if not school_data:
            self.setFixedSize(800, 550)
            self.select_school_group = SelectSchoolGroup(self)
            self.select_school_group.school_selected.connect(self.populate_school_data)
            layout.addWidget(self.select_school_group)
        self.school_data_group = SchoolDataGroup(self, school_data)

        # buttons
        buttons_frame = QHBoxLayout()
        self.save_btn = QPushButton("Zapisz", self)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Anuluj", self)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_frame.addWidget(self.save_btn)
        buttons_frame.addWidget(self.cancel_btn)

        layout.addWidget(self.school_data_group)
        layout.addLayout(buttons_frame)

    def validate(self) -> bool:
        return self.school_data_group.validate()

    def populate_school_data(self) -> None:
        school_data = self.select_school_group.selected_school
        self.school_data_group.school_data = school_data

    def get_school_data(self) -> SchoolDbCreateSchema | SchoolDbCreateSchema | None:
        return self.school_data_group.school_data

    def save_school_data(self) -> None:
        school_data = self.get_school_data()
        if not school_data:
            return None
        if isinstance(school_data, SchoolDbSchema):
            update_school(school_data)
        else:
            create_school(school_data)

    def accept(self):
        if self.validate():
            self.save_school_data()
            super().accept()
