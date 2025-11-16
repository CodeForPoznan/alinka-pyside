from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.widget.toast import show_success, show_validation_error


class SettingsSchoolsContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.settings_footer_container = parent
        self.setVisible(visible)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)

        layout.addStretch()

        add_remove_applicant_btn = QPushButton("Dodaj szkołę do listy")
        add_remove_applicant_btn.clicked.connect(self.add_school)
        add_remove_applicant_btn.setFixedWidth(200)
        layout.addWidget(add_remove_applicant_btn)

    def add_school(self) -> None:
        main_body_container = self.settings_footer_container.footer_container.main_body_container
        school_tab_container = main_body_container.content_container.settings_container.schools_tab_container
        if not school_tab_container.validate():
            show_validation_error(self.window(), school_tab_container.error_message)
            return

        # School data group removed - school creation no longer available from settings
        show_success(self.window(), "Ustawienia szkół zostały zaktualizowane")
