from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QWidget

from alinka.schemas import SchoolData
from alinka.widget.components import LabeledInputComponent


class SchoolDataGroup(QGroupBox):
    rspo_id: int | None = None
    rspo_type_id: int | None = None

    def __init__(self, parent: QWidget):
        super().__init__(title="Dane szkoły", parent=parent)
        self.parent = parent
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.name = LabeledInputComponent("Nazwa", self)
        layout.addWidget(self.name, 0, 0, 1, 2)

        self.type = LabeledInputComponent("Typ", self)
        layout.addWidget(self.type, 1, 0)

        self.parent_organisation_name = LabeledInputComponent("Nazwa jednostki prowadzącej", self)
        layout.addWidget(self.parent_organisation_name, 2, 0, 1, 2)

        self.address = LabeledInputComponent("Adres", self)
        self.town = LabeledInputComponent("Miejscowość", self)
        layout.addWidget(self.address, 3, 0)
        layout.addWidget(self.town, 3, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self)
        self.post = LabeledInputComponent("Poczta", self)
        layout.addWidget(self.postal_code, 4, 0)
        layout.addWidget(self.post, 4, 1)

    @property
    def school_data(self) -> SchoolData:
        return SchoolData(
            rspo_id=self.rspo_id,
            rspo_type_id=self.rspo_type_id,
            address=self.address.text,
            town=self.town.text,
            postal_code=self.postal_code.text,
            post=self.post.text,
            type=self.type.text,
            name=self.name.text,
            parent_organisation_name=self.parent_organisation_name.text,
        )

    def populate_fields(self, **kwargs):
        self.clear()
        self.rspo_id = kwargs.get("rspo_id")
        self.rspo_type_id = kwargs.get("rspo_type_id")
        self.name.text = kwargs.get("name")
        self.type.text = kwargs.get("type")
        self.parent_organisation_name.text = kwargs.get("parent_organisation_name")
        self.address.text = kwargs.get("address")
        self.town.text = kwargs.get("town")
        self.postal_code.text = kwargs.get("postal_code")
        self.post.text = kwargs.get("post")

    def clear(self):
        self.rspo_id = None
        self.rspo_type = None
        self.name.clear()
        self.type.clear()
        self.parent_organisation_name.clear()
        self.address.clear()
        self.town.clear()
        self.postal_code.clear()
        self.post.clear()
