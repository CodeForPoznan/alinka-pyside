from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.config import settings
from alinka.widget.actions import generate_and_save_decision
from alinka.widget.components import ConfirmationModal
from alinka.widget.toast import show_success, show_validation_error


class ApplicationFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.user_settings = QSettings(settings.APP_AUTHOR, settings.APP_NAME)
        self.footer_container = parent
        self.content_container = self.footer_container.main_body_container.content_container
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.cancel_btn = QPushButton("Anuluj", self)
        self.cancel_btn.clicked.connect(self.cancel_application)

        layout.addStretch()

        self.save_and_export_btn = QPushButton("Zapisz i eksportuj", self)
        self.save_and_export_btn.clicked.connect(self.print_documents)
        self.save_and_export_btn.setFixedWidth(200)

        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_and_export_btn)

        self.setVisible(visible)

    @property
    def document_data(self):
        return self.content_container.application_container.document_data

    def enable_sidebar_buttons(self) -> None:
        sidebar_menu = self.content_container.sidebar_menu_container
        sidebar_menu.search_child_btn.setEnabled(True)
        sidebar_menu.settings_btn.setEnabled(True)
        if self.content_container.validate_basic_settings():
            sidebar_menu.create_documents_btn.setEnabled(True)

    def redirect_to_browser(self) -> None:
        self.enable_sidebar_buttons()
        self.content_container.application_container.finish_application_flow()
        self.content_container.show_browser_container()
        self.footer_container.show_browser_footer_container()

    def validate_document_data(self) -> bool:
        if not self.content_container.validate_basic_settings():
            error_message = self.content_container.settings_container.error_message
            show_validation_error(self, error_message)
            return False
        if not self.content_container.validate_application():
            error_message = self.content_container.application_container.error_message
            show_validation_error(self, error_message)
            return False

        return True

    def print_documents(self) -> None:
        application_container = self.content_container.application_container
        # Call validate_required_fields on the child tab
        if not application_container.validate():
            return
        self.validate_document_data()

        dialogTitle = "Wybierz katalog zapisu dokumentu"

        destination_path = QFileDialog.getExistingDirectory(
            self, dialogTitle, self.user_settings.value("last_dir", settings.DOCUMENTS_PATH)
        )
        if not destination_path:
            return

        self.user_settings.setValue("last_dir", destination_path)

        generate_and_save_decision(form_data=self.document_data, generate=True, destination_path=destination_path)
        show_success(self, "Dokumenty zostały wygenerowane pomyślnie")
        self.redirect_to_browser()

    def cancel_application(self) -> None:
        if not ConfirmationModal(
            self,
            "Potwierdzenie anulowania",
            "Czy na pewno chcesz anulować tworzenie dokumentu?\n\nWszystkie wprowadzone dane zostaną utracone.",
        ).confirm():
            return

        self.content_container.main_body_container.header_container.set_info_message("Tworzenie dokumentu anulowane")
        self.redirect_to_browser()
