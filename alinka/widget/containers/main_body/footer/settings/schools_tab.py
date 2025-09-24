from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget
from sqlalchemy.exc import IntegrityError

from alinka.db.queries import create_school


class SettingsSchoolsContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.settings_footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)

        add_remove_applicant_btn = QPushButton("Dodaj szkołę do listy")
        add_remove_applicant_btn.clicked.connect(self.add_school)
        layout.addWidget(add_remove_applicant_btn)

    def add_school(self) -> None:
        content_container = self.settings_footer_container.footer_container.main_body_container.content_container
        school_tab_container = content_container.settings_container.schools_tab_container

        try:
            create_school(
                school_tab_container.school_data_group.school_data.model_dump(exclude=("full_address", "description"))
            )
        except IntegrityError:
            header_container = self.settings_footer_container.footer_container.main_body_container.header_container
            header_container.set_error_message("Szkoła o podanym numerze RSPO już istnieje.")
            content_container = self.settings_footer_container.footer_container.main_body_container.content_container
            school_data_group = content_container.settings_container.schools_tab_container.school_data_group
            # we need to clear the form after showing the error message
            school_data_group.clear()
            return

        school_tab_container.school_list.refresh()
