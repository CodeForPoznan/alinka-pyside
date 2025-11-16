from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.db.queries import upsert_support_center
from alinka.schemas import SupportCenterData, SupportCenterDbSchema
from alinka.widget.toast import show_success


class SettingsSupportCenterDataContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.setting_footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)

        # Add stretch to push button to the right
        layout.addStretch()

        self.save_btn = QPushButton("Zapisz dane poradni", self)
        self.save_btn.clicked.connect(self.save_support_center_data)
        self.save_btn.setFixedWidth(200)
        layout.addWidget(self.save_btn)

    @property
    def support_center_data(self) -> SupportCenterData:
        main_body_container = self.setting_footer_container.footer_container.main_body_container
        return main_body_container.content_container.settings_container.support_center_data

    def save_support_center_data(self) -> None:
        support_center_data = SupportCenterDbSchema(**self.support_center_data.model_dump())
        upsert_support_center(support_center_data.model_dump())
        self.setting_footer_container.footer_container.main_body_container.content_container.validate_basic_settings()
        show_success(self.window(), "Dane poradni zostały zapisane")
