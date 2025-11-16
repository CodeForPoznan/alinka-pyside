from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QWidget

from alinka.schemas import SchoolDbCreateSchema, SchoolDbSchema
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class SchoolDataGroup(ValidationMixin, QGroupBox):
    id: int | None
    rspo_id: int | None = None
    rspo_type_id: int | None = None

    def __init__(self, parent: QWidget, school_data: SchoolDbSchema | None = None):
        super().__init__(title="Dane szkoły", parent=parent)
        self.parent = parent
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.name = LabeledInputComponent("Nazwa", self, required=True)
        layout.addWidget(self.name, 0, 0, 1, 2)

        self.type = LabeledInputComponent("Typ", self)
        layout.addWidget(self.type, 1, 0)

        self.parent_organisation_name = LabeledInputComponent("Nazwa jednostki prowadzącej", self)
        layout.addWidget(self.parent_organisation_name, 2, 0, 1, 2)

        self.address = LabeledInputComponent("Adres", self, required=True)
        self.town = LabeledInputComponent("Miejscowość", self, required=True)
        layout.addWidget(self.address, 3, 0)
        layout.addWidget(self.town, 3, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self, required=True)
        self.post = LabeledInputComponent("Poczta", self, required=True)
        layout.addWidget(self.postal_code, 4, 0)
        layout.addWidget(self.post, 4, 1)

        if school_data:
            self.school_data = school_data

        self.components = [
            self.name,
            self.type,
            self.parent_organisation_name,
            self.address,
            self.town,
            self.postal_code,
            self.post,
        ]

    @property
    def school_data(self) -> SchoolDbCreateSchema | SchoolDbSchema | None:
        if not self.is_valid:
            return None
        school_data = {
            "rspo_id": self.rspo_id,
            "rspo_type": self.rspo_type_id,
            "name": self.name.text,
            "type": self.type.text,
            "parent_organisation_name": self.parent_organisation_name.text,
            "address": self.address.text,
            "town": self.town.text,
            "postal_code": self.postal_code.text,
            "post": self.post.text,
        }
        if self.id:
            school_data["id"] = self.id
            return SchoolDbSchema.model_validate(school_data)
        else:
            return SchoolDbCreateSchema.model_validate(school_data)

    @school_data.setter
    def school_data(self, school_data: SchoolDbCreateSchema | SchoolDbSchema | None) -> None:
        self.clear()
        if not school_data:
            return None

        if isinstance(school_data, SchoolDbSchema):
            self.id = school_data.id

        self.rspo_id = school_data.rspo_id
        self.rspo_type_id = school_data.rspo_type_id
        self.name.text = school_data.name
        self.type.text = school_data.type
        self.parent_organisation_name.text = school_data.parent_organisation_name
        self.address.text = school_data.address
        self.town.text = school_data.town
        self.postal_code.text = school_data.postal_code
        self.post.text = school_data.post

    def clear(self):
        self.id = None
        self.rspo_id = None
        self.rspo_type = None
        self.name.clear()
        self.type.clear()
        self.parent_organisation_name.clear()
        self.address.clear()
        self.town.clear()
        self.postal_code.clear()
        self.post.clear()

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])
