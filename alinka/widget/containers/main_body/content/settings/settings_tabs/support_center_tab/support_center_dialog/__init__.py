from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from alinka.db.queries import get_support_center_data, upsert_support_center
from alinka.widget.components import ValidationMixin

from .select_support_center_group import SelectSupportCenterGroup
from .support_center_data_group import SupportCenterDataGroup


class SupportCenterDialog(ValidationMixin, QDialog):
    def __init__(self, parent: QWidget, edit: bool = True):
        super().__init__(parent)
        self.setWindowTitle("Edytuj poradnię" if edit else "Dodaj poradnię")
        self.resize(600, 300)

        layout = QVBoxLayout(self)

        if not edit:
            self.select_support_center_group = SelectSupportCenterGroup(self)
            self.select_support_center_group.support_center_selected.connect(self.populate_support_center_data)
            layout.addWidget(self.select_support_center_group)

        self.support_center_data_group = SupportCenterDataGroup(self)
        layout.addWidget(self.support_center_data_group)
        if edit:
            support_center_data = get_support_center_data()
            if support_center_data:
                self.support_center_data_group.populate_fields(support_center_data.model_dump())

                # Buttons
        buttons_frame = QHBoxLayout()
        self.save_btn = QPushButton("Zapisz", self)
        self.cancel_btn = QPushButton("Anuluj", self)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        buttons_frame.addWidget(self.save_btn)
        buttons_frame.addWidget(self.cancel_btn)

        layout.addSpacing(20)
        layout.addLayout(buttons_frame)

    def populate_support_center_data(self):
        selected_support_center = self.select_support_center_group.selected_support_center_data()
        if not selected_support_center:
            return
        self.support_center_data_group.populate_fields(selected_support_center)

    def save_support_center_data(self):
        support_center_data = self.support_center_data_group.support_center_data
        if not support_center_data:
            return
        upsert_support_center(support_center_data)

    def validate(self) -> bool:
        return self.support_center_data_group.validate()

    def accept(self) -> None:
        if not self.validate():
            return
        self.save_support_center_data()
        super().accept()
