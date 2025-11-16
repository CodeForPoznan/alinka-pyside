from PySide6.QtCore import Qt
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
        
        # Enable maximize button and make dialog resizable
        self.setWindowFlags(
            Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        if not school_data:
            self.setMinimumSize(1000, 750)
            self.resize(1000, 950)
            self.select_school_group = SelectSchoolGroup(self)
            self.select_school_group.school_selected.connect(self.populate_school_data)
            layout.addWidget(self.select_school_group)
        else:
            self.setMinimumSize(1000, 500)
            self.resize(1000, 600)

        self.school_data_group = SchoolDataGroup(self, school_data)

        # buttons
        buttons_frame = QHBoxLayout()
        buttons_frame.setSpacing(10)
        buttons_frame.addStretch()

        self.save_btn = QPushButton("Zapisz", self)
        self.save_btn.setMinimumWidth(120)
        self.save_btn.setMinimumHeight(35)
        self.cancel_btn = QPushButton("Anuluj", self)
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.setMinimumHeight(35)

        # Apply green theme styling
        self.save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0px 0px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """
        )

        self.cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e5e7eb;
                color: #374151;
                border: none;
                border-radius: 4px;
                padding: 0px 0px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
            QPushButton:pressed {
                background-color: #9ca3af;
            }
        """
        )

        self.save_btn.clicked.connect(self.accept)
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
