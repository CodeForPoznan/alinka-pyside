from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from alinka.db.queries import get_decision_data_by_id
from alinka.docx.utils import convert_raw_documents_data


class BrowserFooterContainer(QFrame):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.footer_container = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        layout.addStretch()

        self.create_new_btn = QPushButton("Utwórz nowy", self)
        self.create_new_btn.clicked.connect(self.create_new_decision)
        self.create_new_btn.setEnabled(False)
        self.create_new_btn.setFixedWidth(200)
        layout.addWidget(self.create_new_btn)

        self.setVisible(visible)

    def create_new_decision(self):
        content_container = self.footer_container.main_body_container.content_container
        selected_decision_id = content_container.browser_container.browse_decision_container.selected_decision_id
        if not selected_decision_id:
            self.create_new_btn.setEnabled(False)
            return
        decision_raw_data = get_decision_data_by_id(selected_decision_id)
        decision_data = convert_raw_documents_data(decision_raw_data)
        content_container.application_container.clear()
        content_container.application_container.populate_application_form(document_data=decision_data)
        content_container.show_application_container()
        self.footer_container.show_application_footer_container()
