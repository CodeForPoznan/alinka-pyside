from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QGroupBox, QWidget

from alinka.schemas.document_schema import SupportCenterData
from alinka.widget.components import LabeledInputComponent


class SupportCenterDataGroup(QGroupBox):
    province_id: int | None = None
    district_id: int | None = None
    rspo: int | None = None

    def __init__(self, parent: QWidget):
        super().__init__(title="Dane poradnii", parent=parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.name_nominative = LabeledInputComponent("Nazwa poradnii (mianownik)", self, min_lenght=100)
        layout.addWidget(self.name_nominative, 0, 0, 1, 2)

        self.name_genitive = LabeledInputComponent("Nazwa poradni (dopełniacz)", self, min_lenght=100)
        layout.addWidget(self.name_genitive, 1, 0, 1, 2)

        self.institute_name = LabeledInputComponent("Zespół orzekający", self, min_lenght=100)
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

    def clear(self):
        self.name_nominative.clear()
        self.name_genitive.clear()
        self.institute_name.clear()
        self.kurator.clear()
        self.address.clear()
        self.town.clear()
        self.postal_code.clear()
        self.post.clear()

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
