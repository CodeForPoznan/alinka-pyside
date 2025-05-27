from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.db.queries import get_support_center_data

from .select_support_center_group import SelectSupportCenterGroup
from .support_center_data_group import SupportCenterDataGroup


class SupportCenterTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        layout = QVBoxLayout(self)

        self.select_support_center_group = SelectSupportCenterGroup(self)
        self.support_center_data_group = SupportCenterDataGroup(self)
        layout.addWidget(self.select_support_center_group)
        layout.addWidget(self.support_center_data_group)

    @property
    def support_center_data(self):
        return self.support_center_data_group.support_center_data

    @property
    def is_valid(self) -> bool:
        return bool(get_support_center_data())

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Nie została wybrana żadna poradnia. Proszę wybrać właściwą poradnię."

        return None
