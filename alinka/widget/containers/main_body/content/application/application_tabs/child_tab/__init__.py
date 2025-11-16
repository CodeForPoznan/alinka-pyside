from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from alinka.schemas import ChildData, DocumentData
from alinka.widget.components import ValidationMixin

from .child_data_group import ChildDataGroupContainer
from .general_data_group import GeneralDataGroupContainer


class ChildDataTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        self.application_container = parent
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.general_data_group = GeneralDataGroupContainer(self)
        self.child_data_group = ChildDataGroupContainer(self)

        layout.addWidget(self.general_data_group)
        layout.addWidget(self.child_data_group)

        self.containers = [self.general_data_group, self.child_data_group]

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
            klass=self.child_data_group.school_klass.text,
            profession=self.child_data_group.school_profession.text,
            student=self.child_data_group.student_checkbox.checkbox.isChecked(),
        )

    def clear(self) -> None:
        for c in self.containers:
            c.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        for c in self.containers:
            c.populate_data(document_data)

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.containers)

    @property
    def error_message(self) -> str | None:
        for c in self.containers:
            if not c.is_valid:
                return c.error_message

        return None

    def validate(self) -> bool:
        return all([c.validate() for c in self.containers])

    def clear_validation_state(self) -> None:
        for container in self.containers:
            container.clear_validation_state()
