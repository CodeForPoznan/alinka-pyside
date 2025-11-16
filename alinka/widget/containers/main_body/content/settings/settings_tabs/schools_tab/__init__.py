from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.db.queries import check_if_any_school_exists
from alinka.widget.components import ValidationMixin

from .school_list_group import SchoolListGroup
from .select_school_group import SelectSchoolGroup


class SchoolTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        self.setting_container = parent
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        self.select_schools_region_group = SelectSchoolGroup(self)
        layout.addWidget(self.select_schools_region_group, 0)

        self.school_list = SchoolListGroup(self)
        layout.addWidget(self.school_list, 1)

    @property
    def is_valid(self) -> bool:
        return check_if_any_school_exists()

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Brak dodanej szkoły w ustawieniach. Dodaj szkołę, aby utworzyć nowy wniosek."
        return None

    def validate(self) -> bool:
        return True  # No validation needed without school data group
