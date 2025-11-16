from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QWidget,
)

from alinka.config import settings
from alinka.widget.actions import generate_and_save_decision
from alinka.widget.toast import show_success, show_validation_error


class ApplicationFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.footer_container = parent
        self.content_container = self.footer_container.main_body_container.content_container
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Business logic: add cancel button (from origin/develop)
        self.cancel_btn = QPushButton("Anuluj", self)
        self.cancel_btn.clicked.connect(self.cancel_application)
        layout.addWidget(self.cancel_btn)

        layout.addStretch()

        # UI: better styling for print button (from current branch)
        self.print_btn = QPushButton("Drukuj dokumenty", self)
        self.print_btn.clicked.connect(self.print_documents)
        self.print_btn.setFixedWidth(200)
        layout.addWidget(self.print_btn)

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

    def validate_document_data(self) -> None:
        if not self.content_container.validate_basic_settings():
            error_message = self.content_container.settings_container.error_message
            # UI: Use modern toast validation (from current branch)
            show_validation_error(self.window(), error_message)
            return
        if not self.content_container.validate_application():
            error_message = self.content_container.application_container.error_message
            # UI: Use modern toast validation (from current branch)
            show_validation_error(self.window(), error_message)
            return

    def print_documents(self) -> None:
        application_container = self.content_container.application_container
        # Call validate_required_fields on the child tab
        if not application_container.validate():
            return
        self.validate_document_data()

        dialogTitle = "Wybierz katalog zapisu dokumentu"

        destination_path = QFileDialog.getExistingDirectory(self, dialogTitle, settings.DOCUMENTS_PATH)
        if not destination_path:
            return

        generate_and_save_decision(form_data=self.document_data, generate=True, destination_path=destination_path)
        # UI: Use modern toast for success message (from current branch)
        show_success(self.window(), "Dokumenty zostały wygenerowane pomyślnie")
        # Business logic: Proper cleanup and navigation (from origin/develop)
        self.redirect_to_browser()

    def cancel_application(self) -> None:
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle("Potwierdzenie anulowania")
        msgbox.setText(
            "Czy na pewno chcesz anulować tworzenie dokumentu?\n\nWszystkie wprowadzone dane zostaną utracone."
        )
        msgbox.setIcon(QMessageBox.Icon.Question)

        yes_button = msgbox.addButton("Tak", QMessageBox.ButtonRole.YesRole)
        no_button = msgbox.addButton("Nie", QMessageBox.ButtonRole.NoRole)

        msgbox.setDefaultButton(no_button)
        msgbox.exec()

        if msgbox.clickedButton() != yes_button:
            return

        self.content_container.main_body_container.header_container.set_info_message("Tworzenie dokumentu anulowane")
        self.redirect_to_browser()
