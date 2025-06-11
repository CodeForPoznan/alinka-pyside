from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.schemas.db_schema import DecisionDbSchema
from alinka.widget.actions import generate_and_save_decision


class ApplicationFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.footer_container = parent
        self.content_container = self.footer_container.main_body_container.content_container
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.print_btn = QPushButton("Drukuj dokumenty", self)
        self.print_btn.clicked.connect(self.print_documents)
        self.save_btn = QPushButton("Zapisz", self)
        self.save_btn.clicked.connect(self.on_save_btn_clicked)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.save_btn)

        self.setVisible(visible)

    @property
    def document_data(self):
        return self.content_container.application_container.document_data

    def on_save_btn_clicked(self) -> None:
        decision_db = self.save_document_data()
        self.content_container.application_container.set_document_data_id(decision_db.id)
        self.save_btn.setText("Zapisz zmiany")

    def validate_document_data(self) -> None:
        if not self.content_container.validate_basic_settings():
            error_message = self.content_container.settings_container.error_message
            self.content_container.main_body_container.header_container.set_error_message(error_message)
            return
        if not self.content_container.validate_application():
            error_message = self.content_container.application_container.error_message
            self.content_container.main_body_container.header_container.set_error_message(error_message)
            return

    def print_documents(self) -> None:
        self.validate_document_data()
        decision_db = generate_and_save_decision(form_data=self.document_data, generate=True)
        self.content_container.application_container.set_document_data_id(decision_db.id)

    def save_document_data(self) -> DecisionDbSchema:
        self.validate_document_data()
        return generate_and_save_decision(form_data=self.document_data, generate=False)
