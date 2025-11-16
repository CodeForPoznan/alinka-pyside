from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class CreatorsTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        # Set size policy to not expand vertically
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("O aplikacji", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-bottom: 8px;")
        layout.addWidget(title_label)

        # App name - use teal color
        app_name_label = QLabel("Alinka", self)
        app_name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #14b8a6; margin-top: 8px;")
        layout.addWidget(app_name_label)

        # Description
        description_label = QLabel(
            "Aplikacja do wspomagania pracy poradni psychologiczno-pedagogicznej.\n"
            "Umożliwia tworzenie i zarządzanie dokumentami orzeczeń oraz opinii.",
            self,
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #334155; font-size: 13px; line-height: 1.6; margin-top: 8px;")
        layout.addWidget(description_label)

        # Creators section
        creators_title = QLabel("Twórcy", self)
        creators_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; margin-top: 24px;")
        layout.addWidget(creators_title)

        creators_label = QLabel(
            "Aplikacja została stworzona przez Code for Poznań.\n\n"
            "Code for Poznań to społeczność programistów, designerów i innych specjalistów, "
            "którzy wspólnie pracują nad projektami technologicznymi dla dobra społecznego.",
            self,
        )
        creators_label.setWordWrap(True)
        creators_label.setStyleSheet("color: #334155; font-size: 13px; line-height: 1.6; margin-top: 8px;")
        layout.addWidget(creators_label)

        # Contact
        contact_title = QLabel("Kontakt", self)
        contact_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; margin-top: 24px;")
        layout.addWidget(contact_title)

        contact_label = QLabel("Email: hello@codeforpoznan.pl", self)
        contact_label.setStyleSheet("color: #14b8a6; font-weight: 500; font-size: 14px; margin-top: 8px;")
        layout.addWidget(contact_label)

    @property
    def is_valid(self) -> bool:
        # This tab doesn't require validation
        return True

    @property
    def error_message(self) -> str | None:
        return None
