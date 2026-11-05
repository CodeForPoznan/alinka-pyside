from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Signal


class CacheStatusWidget(QWidget):
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Prawa strona wyrównana
        layout.addStretch()

        # Teksty
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        self.label_title = QLabel("Dane pobrane:")
        self.label_date = QLabel("Brak pobranych danych")

        # Stylizacja do prawej
        self.label_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_date.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_date)
        layout.addLayout(text_layout)

        # Pionowy separator i przycisk (zgodnie z instrukcją)
        self.separator = QLabel("│")
        layout.addWidget(self.separator)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(24, 24)
        self.refresh_btn.setToolTip("Odśwież dane RSPO")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_btn)

    def set_loading(self):
        self.label_title.setText("Stan:")
        self.label_date.setText("Odświeżanie...")
        self.refresh_btn.setEnabled(False)

    def set_data(self, date_str: str | None, error: bool = False):
        self.refresh_btn.setEnabled(True)
        if error:
            self.label_title.setText("RSPO niedostępne.")
            self.label_date.setText(f"Ostatnie: {date_str}" if date_str else "Brak danych")
        else:
            self.label_title.setText("Dane pobrane:")
            self.label_date.setText(date_str if date_str else "Brak pobranych danych")