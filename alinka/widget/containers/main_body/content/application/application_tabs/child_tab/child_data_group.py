from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QGroupBox

from alinka.widget.components import LabeledInputComponent


class ChildDataGroupContainer(QGroupBox):
    def __init__(self, parent):
        super().__init__(title="Uczeń", parent=parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.child_name_nom = LabeledInputComponent("Imię i nazwisko", self, 200)
        self.child_name_gen = LabeledInputComponent("Imię i nazwisko (dopełniacz)", self, 200)
        layout.addWidget(self.child_name_nom, 0, 0)
        layout.addWidget(self.child_name_gen, 0, 1)

        self.birth_place = LabeledInputComponent("Miejsce urodzenia", self)
        self.pesel = LabeledInputComponent("PESEL", self)
        layout.addWidget(self.birth_place, 1, 0)
        layout.addWidget(self.pesel, 1, 1)

        self.address = LabeledInputComponent("Adres", self)
        self.town = LabeledInputComponent("Miejscowość", self)
        layout.addWidget(self.address, 2, 0)
        layout.addWidget(self.town, 2, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self)
        self.post = LabeledInputComponent("Poczta", self)
        layout.addWidget(self.postal_code, 3, 0)
        layout.addWidget(self.post, 3, 1)
