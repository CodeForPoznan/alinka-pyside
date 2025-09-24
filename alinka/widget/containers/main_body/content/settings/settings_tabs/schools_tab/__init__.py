from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.db.queries import check_if_any_school_exists

from .school_data_group import SchoolDataGroup
from .school_list_group import SchoolListGroup
from .select_school_group import SelectSchoolGroup


class SchoolTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.select_schools_region_group = SelectSchoolGroup(self)
        layout.addWidget(self.select_schools_region_group)

        self.school_data_group = SchoolDataGroup(self)
        layout.addWidget(self.school_data_group)

        self.school_list = SchoolListGroup(self)
        layout.addWidget(self.school_list)

    @property
    def is_valid(self) -> bool:
        return check_if_any_school_exists()

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Brak dodanej szkoły w ustawieniach. Dodaj szkołę, aby utworzyć nowy wniosek."
        return None
