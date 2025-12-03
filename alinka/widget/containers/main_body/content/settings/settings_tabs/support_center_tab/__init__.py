from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from alinka.db.queries import get_support_center_data
from alinka.widget.components import ValidationMixin

from .support_center_dialog import SupportCenterDialog


class HandleSupportCenterFrame(ValidationMixin, QWidget):
    support_center_changed = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.add_support_center_btn = QPushButton("Dodaj", self)
        self.add_support_center_btn.setFixedSize(200, 30)
        self.add_support_center_btn.clicked.connect(self.add_support_center)
        layout.addWidget(self.add_support_center_btn)

        self.update_support_center_btn = QPushButton("Edytuj", self)
        self.update_support_center_btn.setFixedSize(200, 30)
        self.update_support_center_btn.clicked.connect(self.update_support_center)
        layout.addWidget(self.update_support_center_btn)

        self.setLayout(layout)

    def add_support_center(self):
        dialog = SupportCenterDialog(self, edit=False)
        if dialog.exec():
            self.support_center_changed.emit()

    def update_support_center(self):
        dialog = SupportCenterDialog(self)
        if dialog.exec():
            self.support_center_changed.emit()

    def toggle_buttons(self, support_center_exists: bool):
        self.add_support_center_btn.setVisible(not support_center_exists)
        self.update_support_center_btn.setVisible(support_center_exists)


class SupportCenterTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        self.support_center_description = QLabel(self)
        self.support_center_description.setWordWrap(True)
        self.support_center_description.setTextFormat(Qt.RichText)
        self.support_center_description.setAlignment(Qt.AlignCenter)
        self.support_center_description.setText(self.support_center_description_text)
        self.handle_support_center_frame = HandleSupportCenterFrame(self)
        self.handle_support_center_frame.support_center_changed.connect(self.support_center_description_updated)
        self.handle_support_center_frame.toggle_buttons(self.is_valid)

        layout.addWidget(self.support_center_description, 0)
        layout.addWidget(self.handle_support_center_frame, 0)
        layout.addStretch()

    def support_center_description_updated(self):
        support_center_exists = self.is_valid
        self.handle_support_center_frame.toggle_buttons(support_center_exists)

        self.support_center_description.setText(self.support_center_description_text)
        self.settings_container.content_container.validate_basic_settings()

    @property
    def support_center_description_text(self) -> str:
        support_center_data = get_support_center_data()
        if not support_center_data:
            return self.no_support_center_selected_message

        return f"""
        <div align="center">
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">NAZWA PORADNI</span><br/>
                <span style="font-size:14pt;">{support_center_data.name_nominative}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">NAZWA PORADNI (DOPEŁNIACZ)</span><br/>
                <span style="font-size:14pt;">{support_center_data.name_genitive}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">ZESPÓŁ ORZEKAJĄCY</span><br/>
                <span style="font-size:14pt;">{support_center_data.institute_name}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">KURATOR</span><br/>
                <span style="font-size:14pt;">{support_center_data.kurator}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">ADRES</span><br/>
                <span style="font-size:14pt;">{support_center_data.address}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">MIEJSCOWOŚĆ</span><br/>
                <span style="font-size:14pt;">{support_center_data.town}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">KOD POCZTOWY</span><br/>
                <span style="font-size:14pt;">{support_center_data.postal_code}</span></p>
            </div>
            <div>
                <p><span style="font-weight:bold; font-size:10pt;">POCZTA</span><br/>
                <span style="font-size:14pt;">{support_center_data.post}</span></p>
            </div>
        </div>
        """

    @property
    def no_support_center_selected_message(self) -> str:
        return """
        <div align="center">
            <p><span style="font-weight:bold; font-size:18pt; color:#856404;">⚠️ BRAK WYBRANEJ PORADNI</span></p>
            <p><span style="font-size:16pt; color:#856404;">Proszę wybrać właściwą poradnię.</span></p>
        </div>
        """

    @property
    def is_valid(self) -> bool:
        return bool(get_support_center_data())

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return "Nie została wybrana żadna poradnia. Proszę wybrać właściwą poradnię."

        return None
