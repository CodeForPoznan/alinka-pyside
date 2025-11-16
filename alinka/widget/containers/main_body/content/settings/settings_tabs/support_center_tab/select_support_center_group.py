from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QSizePolicy, QVBoxLayout, QWidget

from alinka import rspo_client
from alinka.constants.common import RPSO_SUPPORT_CENTER_TYPE_ID
from alinka.schemas.rspo_schema import InstitutionRequestBody
from alinka.widget.components import (
    LabeledComboBoxComponent,
    SelectProvinceDistrictGroup,
    ValidationMixin,
)


class SelectSupportCenterGroup(ValidationMixin, QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Wybierz poradnię z RPSO", parent=parent)
        self.support_center_tab = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 10, 10, 0)

        self.province_district_group = SelectProvinceDistrictGroup(self)
        self.province_district_group.selection_changed.connect(self.populate_support_centers_combobox)

        self.support_center_combobox = LabeledComboBoxComponent("Poradnia", self)
        self.support_center_combobox.combobox.setPlaceholderText("Wybierz z listy...")
        self.support_center_combobox.combobox.currentTextChanged.connect(self.populate_support_center_data)
        layout.addWidget(self.province_district_group)
        layout.addWidget(self.support_center_combobox)
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    def populate_support_centers_combobox(self):
        self.clear_support_center_data()
        selected_province_id = self.province_district_group.province_id
        selected_district_id = self.province_district_group.district_id
        if not all([selected_province_id, selected_district_id]):
            return
        self.support_center_combobox.clear()
        try:
            self.support_centers = rspo_client.list_institutions(
                body=InstitutionRequestBody(
                    province_id=selected_province_id,
                    district_id=selected_district_id,
                    institution_type_ids=[RPSO_SUPPORT_CENTER_TYPE_ID],
                )
            )
            for support_center in self.support_centers.items:
                self.support_center_combobox.combobox.addItem(
                    support_center.name, support_center.rspo_id
                )
        except Exception as e:
            error_msg = "Błąd ładowania poradni - sprawdź połączenie"
            self.support_center_combobox.combobox.setPlaceholderText(error_msg)
            self.support_center_combobox.combobox.setEditable(True)
            self.support_center_combobox.combobox.setEnabled(True)
            print(f"Error loading support centers: {e}")

    def populate_support_center_data(self):
        selected_support_center_rspo = (
            self.support_center_combobox.combobox.currentData()
        )
        if not selected_support_center_rspo:
            return
        support_center = [
            sc for sc in self.support_centers.items
            if sc.rspo_id == selected_support_center_rspo
        ][0]
        self.support_center_tab.support_center_data_group.populate_fields(
            province_id=self.province_district_group.province_id,
            district_id=self.province_district_group.district_id,
            rspo=support_center.rspo_id,
            name_nominative=support_center.name,
            address=support_center.address,
            town=support_center.town,
            postal_code=support_center.postal_code,
            post=support_center.post,
        )

    def clear_support_center_data(self):
        self.support_center_tab.support_center_data_group.clear()
