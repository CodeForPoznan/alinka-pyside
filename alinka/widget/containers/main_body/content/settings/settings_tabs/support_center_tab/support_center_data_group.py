from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QSizePolicy, QWidget

from alinka.db.queries import get_support_center_data
from alinka.schemas.document_schema import SupportCenterData
from alinka.widget.components import LabeledInputComponent, ValidationMixin


class SupportCenterDataGroup(ValidationMixin, QGroupBox):
    province_id: int | None = None
    district_id: int | None = None
    rspo: int | None = None

    def __init__(self, parent: QWidget):
        super().__init__(title="Dane poradni", parent=parent)
        # Set size policy to minimize vertical space
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(4)  # Minimal spacing
        layout.setContentsMargins(10, 10, 10, 10)  # Compact margins

        self.name_nominative = LabeledInputComponent("Nazwa poradnii (mianownik)", self, min_length=100)
        layout.addWidget(self.name_nominative, 0, 0, 1, 2)

        self.name_genitive = LabeledInputComponent("Nazwa poradnii (dopełniacz)", self, min_length=100)
        layout.addWidget(self.name_genitive, 1, 0, 1, 2)

        self.institute_name = LabeledInputComponent("Zespół orzekający", self, min_length=100)
        layout.addWidget(self.institute_name, 2, 0, 1, 2)

        self.kurator = LabeledInputComponent("Kurator", self)
        layout.addWidget(self.kurator, 3, 0, 1, 2)

        self.address = LabeledInputComponent("Adres", self)
        self.town = LabeledInputComponent("Miejscowość", self)
        layout.addWidget(self.address, 4, 0)
        layout.addWidget(self.town, 4, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self)
        self.post = LabeledInputComponent("Poczta", self)
        layout.addWidget(self.postal_code, 5, 0)
        layout.addWidget(self.post, 5, 1)

        self.components = [
            self.name_nominative,
            self.name_genitive,
            self.institute_name,
            self.kurator,
            self.address,
            self.town,
            self.postal_code,
            self.post,
        ]
        self.populate_fields_on_init()

    def populate_fields(self, **kwargs):
        self.clear()
        self.province_id = kwargs.get("province_id")
        self.district_id = kwargs.get("district_id")
        self.rspo = kwargs.get("rspo")
        self.name_nominative.text = kwargs.get("name_nominative")
        self.name_genitive.text = kwargs.get("name_genitive")
        self.institute_name.text = kwargs.get("institute_name")
        self.kurator.text = kwargs.get("kurator")
        self.address.text = kwargs.get("address")
        self.town.text = kwargs.get("town")
        self.postal_code.text = kwargs.get("postal_code")
        self.post.text = kwargs.get("post")

    def populate_fields_on_init(self):
        support_center_data = get_support_center_data()
        if support_center_data:
            self.populate_fields(**support_center_data.model_dump())

    def clear(self):
        for c in self.components:
            c.clear()
        self.province_id = None
        self.district_id = None
        self.rspo = None

    @property
    def support_center_data(self):
        return SupportCenterData(
            province_id=self.province_id,
            district_id=self.district_id,
            rspo=self.rspo,
            address=self.address.text,
            town=self.town.text,
            postal_code=self.postal_code.text,
            post=self.post.text,
            name_nominative=self.name_nominative.text,
            name_genitive=self.name_genitive.text,
            institute_name=self.institute_name.text,
            kurator=self.kurator.text,
        )

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message

        return None

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])

    def clear_validation_state(self) -> None:
        for c in self.components:
            c.clear_validation_state()
