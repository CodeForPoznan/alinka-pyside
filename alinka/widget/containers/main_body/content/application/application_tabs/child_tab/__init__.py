from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QWidget

from alinka.db.queries import get_school_by_name
from alinka.schemas import ChildData, SchoolData, SchoolDbSchema

from .child_data_group import ChildDataGroupContainer
from .general_data_group import GeneralDataGroupContainer
from .school_data_group import SchoolDataGroupContainer


class ChildDataTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.general_data_group = GeneralDataGroupContainer(self)
        self.child_data_group = ChildDataGroupContainer(self)
        self.school_data_group = SchoolDataGroupContainer(self)

        layout.addWidget(self.general_data_group)
        layout.addWidget(self.child_data_group)
        layout.addWidget(self.school_data_group)

    @property
    def child_data(self) -> ChildData:
        return ChildData(
            pesel=self.child_data_group.pesel.text,
            address=self.child_data_group.address.text,
            town=self.child_data_group.town.text,
            post=self.child_data_group.post.text,
            postal_code=self.child_data_group.postal_code.text,
            full_name=self.child_data_group.child_name_nom.text,
            full_name_gen=self.child_data_group.child_name_gen.text,
            birth_place=self.child_data_group.birth_place.text,
            klass=self.school_data_group.school_klass.text,
            profession=self.school_data_group.school_profession.text,
            student=self.school_data_group.student_checkbox.checkbox.isChecked(),
        )

    @property
    def school_data(self) -> SchoolData:
        selected_school_name = self.school_data_group.school.combobox.currentText()
        school: SchoolDbSchema = get_school_by_name(selected_school_name)
        return SchoolData(
            address=school.address,
            town=school.town,
            postal_code=school.postal_code,
            post=school.post,
            name=school.name,
            type=school.type,
            parent_organisation=school.parent_organisation_name,
        )
