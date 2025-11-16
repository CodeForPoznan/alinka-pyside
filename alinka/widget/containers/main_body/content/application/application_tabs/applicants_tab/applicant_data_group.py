from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QGroupBox, QWidget

from alinka.schemas import PersonalData
from alinka.widget.components import (
    LabeledCheckboxComponent,
    LabeledInputComponent,
    ValidationMixin,
)


class ParentAddressFrame(ValidationMixin, QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.address = LabeledInputComponent("Adres", self, required=True)
        self.town = LabeledInputComponent("Miejscowość", self, required=True)
        layout.addWidget(self.address, 0, 0)
        layout.addWidget(self.town, 0, 1)

        self.postal_code = LabeledInputComponent("Kod pocztowy", self)
        self.post = LabeledInputComponent("Poczta", self, required=True)
        layout.addWidget(self.postal_code, 1, 0)
        layout.addWidget(self.post, 1, 1)

        self.setLayout(layout)
        self.setVisible(False)

        self.components = [self.address, self.town, self.postal_code, self.post]

    def clear(self) -> None:
        for component in self.components:
            component.clear()

    def populate_applicant_data(self, applicant_data: PersonalData) -> None:
        self.address.text = applicant_data.address
        self.town.text = applicant_data.town
        self.postal_code.text = applicant_data.postal_code
        self.post.text = applicant_data.post

    @property
    def is_valid(self) -> bool:
        """Check if all address components are filled when visible."""
        if not self.isVisible():
            return True
        return all(component.text for component in self.components)

    @property
    def error_message(self) -> str | None:
        """Get error message for address validation."""
        if not self.is_valid:
            for component in self.components:
                if not component.text:
                    return f"{component.label} jest wymagane"
        return None

    def validate(self) -> bool:
        """Validate address components."""
        for component in self.components:
            component.validate()
        
        is_valid = self.is_valid
        self.display_validation_result(is_valid)
        return is_valid

    def display_validation_result(self, validation_result: bool) -> None:
        """Update visual validation state."""
        pass

    def clear_validation_state(self) -> None:
        """Reset validation state for address components."""
        for component in self.components:
            component.clear_validation_state()


class ApplicantDataGroup(ValidationMixin, QGroupBox):
    def __init__(self, title: str, parent: QWidget, checkbox_description: str, initial_visible: bool = True):
        super().__init__(title=title, parent=parent)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        self.full_name = LabeledInputComponent(
            "Imię i nazwisko", self, 200, required=True
        )
        self.full_name_gen = LabeledInputComponent(
            "Imię i nazwisko (dopełniacz)", self, 200, required=True
        )
        layout.addWidget(self.full_name, 0, 0)
        layout.addWidget(self.full_name_gen, 0, 1)

        self.address_checkbox = LabeledCheckboxComponent(checkbox_description, self, "right")
        self.address_checkbox.checkbox.checkStateChanged.connect(self.show_hide_address_frame)
        # Make checkbox span both columns to prevent overlap
        layout.addWidget(self.address_checkbox, 1, 0, 1, 2)

        self.address_frame = ParentAddressFrame(self)
        layout.addWidget(self.address_frame, 2, 0, 1, 2)
        
        # Set initial visibility
        self.setVisible(initial_visible)

    def show_hide_address_frame(self) -> None:
        if self.address_checkbox.checkbox.isChecked():
            self.address_frame.setVisible(True)
        else:
            self.address_frame.setVisible(False)
            self.address_frame.clear()

    def populate_applicant_data(self, applicant_data: PersonalData) -> None:
        self.full_name.text = applicant_data.full_name
        self.full_name_gen.text = applicant_data.full_name_gen
        self.address_frame.populate_applicant_data(applicant_data)

    def clear(self) -> None:
        self.full_name.clear()
        self.full_name_gen.clear()
        self.address_checkbox.checkbox.setChecked(False)
        self.address_frame.clear()

    @property
    def applicant_data(self) -> PersonalData | None:
        if self.full_name.text:
            return PersonalData(
                full_name=self.full_name.text,
                full_name_gen=self.full_name_gen.text,
                address=self.address_frame.address.text,
                town=self.address_frame.town.text,
                postal_code=self.address_frame.postal_code.text,
                post=self.address_frame.post.text,
            )

    @property
    def is_valid(self) -> bool:
        """Check if the applicant data group is valid.
        
        Checks actual field values regardless of Qt visibility state.
        """
        if not self.full_name.is_valid or not self.full_name_gen.is_valid:
            return False
        
        if self.address_checkbox.is_checked:
            address_components = [
                self.address_frame.address,
                self.address_frame.town,
                self.address_frame.postal_code,
                self.address_frame.post
            ]
            return all(component.text for component in address_components)
        
        return True

    @property
    def error_message(self) -> str | None:
        """Get error message if validation fails."""
        if not self.is_valid:
            # Check name fields first
            if not self.full_name.is_valid:
                return self.full_name.error_message
            if not self.full_name_gen.is_valid:
                return self.full_name_gen.error_message
            
            # Check address fields if checkbox is checked
            if self.address_checkbox.is_checked:
                if not self.address_frame.address.text:
                    return "Adres jest wymagany"
                if not self.address_frame.town.text:
                    return "Miejscowość jest wymagana"
                if not self.address_frame.postal_code.text:
                    return "Kod pocztowy jest wymagany"
                if not self.address_frame.post.text:
                    return "Poczta jest wymagana"
        return None

    def validate(self) -> bool:
        """Validate the applicant data group and update visual state."""
        # Validate individual name components
        self.full_name.validate()
        self.full_name_gen.validate()
        
        # Validate address components if checkbox is checked
        if self.address_checkbox.is_checked:
            self.address_frame.validate()
        
        # Overall validation
        is_valid = self.is_valid
        self.display_validation_result(is_valid)
        return is_valid

    def display_validation_result(self, validation_result: bool) -> None:
        """Update visual validation state of the group."""
        # The group box styling will be handled by the parent ValidationMixin
        pass

    def clear_validation_state(self) -> None:
        """Reset validation state for this component and its children."""
        self.full_name.clear_validation_state()
        self.full_name_gen.clear_validation_state()
        if self.address_checkbox.is_checked:
            self.address_frame.clear_validation_state()
