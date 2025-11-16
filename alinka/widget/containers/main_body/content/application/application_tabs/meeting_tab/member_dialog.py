from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout

from alinka.db.queries import insert_team_member, update_team_member
from alinka.schemas import (
    MeetingMemberData,
    TeamMemberDbCreateSchema,
    TeamMemberDbSchema,
)
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class MemberDialog(ValidationMixin, QDialog):
    def __init__(self, parent, title, _id: int | None = None, name: str | None = None, function: str | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(700, 200)
        self.resize(700, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Input fields
        inputs_frame = QHBoxLayout()
        inputs_frame.setSpacing(20)
        self.id = _id
        self.member_name = LabeledInputComponent("Imię i nazwisko", self, required=True)
        self.member_name.text = name
        self.member_function = LabeledInputComponent("Funkcja", self, required=True)
        self.member_function.text = function
        inputs_frame.addWidget(self.member_name)
        inputs_frame.addWidget(self.member_function)

        # Buttons
        buttons_frame = QHBoxLayout()
        buttons_frame.setSpacing(12)
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
                padding: 8px 16px;
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
                padding: 8px 16px;
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

        layout.addLayout(inputs_frame)
        layout.addLayout(buttons_frame)

    def get_member_data(self) -> MeetingMemberData:
        return MeetingMemberData(id=self.id, name=self.member_name.text, function=self.member_function.text)

    def save_member_data(self) -> None:
        if self.id:
            member_data = TeamMemberDbSchema(id=self.id, name=self.member_name.text, function=self.member_function.text)
            update_team_member(member_data)
        else:
            member_data = TeamMemberDbCreateSchema(name=self.member_name.text, function=self.member_function.text)
            # check if given team member already exists - next iteration when we have toasts
            insert_team_member(member_data)

    def validate(self) -> bool:
        name_valid = self.member_name.validate()
        function_valid = self.member_function.validate()
        return name_valid and function_valid

    def accept(self):
        """Override accept to validate before closing"""
        if self.validate():
            self.save_member_data()
            super().accept()
