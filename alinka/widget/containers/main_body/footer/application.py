from PySide2.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.db.queries import get_support_center_data
from alinka.exceptions import ValidationError
from alinka.widget.actions import generate_and_save_decision


class ApplicationFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.parent = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.print_btn = QPushButton("Drukuj dokumenty", self)
        self.print_btn.clicked.connect(self.print_documents)
        self.save_btn = QPushButton("Zapisz", self)
        self.save_btn.clicked.connect(self.save_document_data)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.save_btn)

        if not visible:
            self.setVisible(visible)

    @property
    def document_data(self):
        return self.parent.parent.content_container.application_container.document_data

    def validate_document_data(self) -> None:
        if not get_support_center_data():
            raise ValidationError()

    def print_documents(self) -> None:
        try:
            self.validate_document_data()
            generate_and_save_decision(form_data=self.document_data, generate=True)
        except Exception:
            # to decide how we want handle this exception in separate ticket
            # on handling exceptions
            pass

    def save_document_data(self) -> None:
        try:
            self.validate_document_data()
            generate_and_save_decision(form_data=self.document_data, generate=False)
        except Exception:
            # to decide how we want handle this exception in separate ticket
            # on handling exceptions
            pass
