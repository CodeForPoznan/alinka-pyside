from PySide2.QtWidgets import QVBoxLayout, QWidget

from .select_support_center_group import SelectSupportCenterGroup
from .support_center_data_group import SupportCenterDataGroup


class SupportCenterTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.select_support_center_group = SelectSupportCenterGroup(self)
        self.support_center_data_group = SupportCenterDataGroup(self)
        layout.addWidget(self.select_support_center_group)
        layout.addWidget(self.support_center_data_group)

    @property
    def support_center_data(self):
        return self.support_center_data_group.support_center_data
