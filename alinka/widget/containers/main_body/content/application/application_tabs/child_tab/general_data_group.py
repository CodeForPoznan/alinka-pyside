from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGroupBox, QHBoxLayout

from alinka.widget.components import LabeledInputComponent


class GeneralDataGroupContainer(QGroupBox):
    def __init__(self, parent):
        super().__init__(title="Dane ogólne", parent=parent)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.decision_no = LabeledInputComponent("Numer orzeczenia", self)
        self.file_no = LabeledInputComponent("Numer teczki", self)
        layout.addWidget(self.decision_no)
        layout.addWidget(self.file_no)
