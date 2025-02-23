from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from alinka import rspo_client
from alinka.constants.common import RPSO_SUPPORT_CENTER_TYPE_ID
from alinka.schemas.rspo_schema import InstitutionRequestBody
from alinka.widget.components import LabeledComboBoxComponent


class SelectSupportCenterGroup(QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Wybierz poradnię z RPSO", parent=parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        location_frame = QFrame(self)

        location_frame_layout = QHBoxLayout(location_frame)
        location_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.province_combobox = LabeledComboBoxComponent("Województwo", location_frame)
        self.province_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.province_combobox.combobox.currentTextChanged.connect(self.populate_districts_cb)
        provinces = rspo_client.list_provinces()
        for province in provinces:
            self.province_combobox.combobox.addItem(province.name, province.id)

        self.district_combobox = LabeledComboBoxComponent("Powiat", location_frame)
        self.district_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.district_combobox.combobox.currentTextChanged.connect(self.populate_support_centers_cb)
        location_frame_layout.addWidget(self.province_combobox)
        location_frame_layout.addWidget(self.district_combobox)

        self.support_center_combobox = LabeledComboBoxComponent("Poradnia", self)
        self.support_center_combobox.combobox.setPlaceholderText("Wybierz z listy....")
        self.support_center_combobox.combobox.currentTextChanged.connect(self.populate_support_center_data)
        layout.addWidget(location_frame)
        layout.addWidget(self.support_center_combobox)

    def populate_districts_cb(self):
        selected_province_id = self.province_combobox.combobox.currentData()
        self.district_combobox.combobox.clear()
        self.support_center_combobox.combobox.clear()
        districts = rspo_client.list_districts(province_id=selected_province_id)
        for district in districts:
            self.district_combobox.combobox.addItem(district.name, district.id)

    def populate_support_centers_cb(self):
        selected_province_id = self.province_combobox.combobox.currentData()
        selected_district_id = self.district_combobox.combobox.currentData()
        self.support_center_combobox.combobox.clear()
        self.support_centers = rspo_client.list_institutions(
            body=InstitutionRequestBody(
                province_id=selected_province_id,
                district_id=selected_district_id,
                institution_type_ids=[RPSO_SUPPORT_CENTER_TYPE_ID],
            )
        )
        for support_center in self.support_centers.items:
            self.support_center_combobox.combobox.addItem(support_center.name, support_center.rspo_id)

    def populate_support_center_data(self):
        selected_support_center_rspo = self.support_center_combobox.combobox.currentData()
        support_center = [sc for sc in self.support_centers.items if sc.rspo_id == selected_support_center_rspo][0]
        self.parent.support_center_data_group.populate_fields(
            province_id=self.province_combobox.combobox.currentData(),
            district_id=self.district_combobox.combobox.currentData(),
            rspo=support_center.rspo_id,
            name_nominative=support_center.name,
            address=support_center.address,
            town=support_center.town,
            postal_code=support_center.postal_code,
            post=support_center.post,
        )
