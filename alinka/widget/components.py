from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from alinka.widget.validators import RequiredValidator


class ValidationMixin:
    """Mixin providing reusable validation and highlighting functionality.

    It can be used by any component that needs field validation.
    """

    def highlight_field(self, field_component: any, highlight: bool) -> None:
        """Trigger highlighting of a field component with consistent styling.

        Args:
            field_component: The component to highlight (LabeledInputComponent or LabeledComboBoxComponent)
            highlight: Whether to highlight (True) or clear highlighting (False)
        """
        if not hasattr(field_component, "line_edit") and not hasattr(field_component, "combobox"):
            return

        widget = getattr(field_component, "line_edit", None) or getattr(field_component, "combobox", None)

        if highlight:
            widget.setStyleSheet("border: 2px solid #ff4444; background-color: #fff5f5; color: black;")
        else:
            widget.setStyleSheet("")

    def validate_required_fields(self, required_fields: list) -> bool:
        """Validate a list of required fields and highlight missing ones.

        Args:
            required_fields: List of field components to validate

        Returns:
            bool: True if all fields are valid, False otherwise
        """
        is_valid = True

        for field in required_fields:
            if not field.is_valid:
                self.highlight_field(field, True)
                is_valid = False
            else:
                self.highlight_field(field, False)

        return is_valid

    def clear_highlights(self, fields: list) -> None:
        """Clear highlighting from a list of fields.

        Args:
            fields: List of field components to clear highlighting from
        """
        for field in fields:
            self.highlight_field(field, False)

    def connect_field_clear_handlers(self, fields: list) -> None:
        """Connect text change handlers to clear highlights when users start typing.

        Args:
            fields: List of field components to connect handlers to
        """
        for field in fields:
            if hasattr(field, "line_edit"):
                # For input fields, clear highlight when text changes
                field.line_edit.textChanged.connect(lambda checked, f=field: self.highlight_field(f, False))
            elif hasattr(field, "combobox"):
                # For combobox fields, clear highlight when selection changes
                field.combobox.currentTextChanged.connect(lambda text, f=field: self.highlight_field(f, False))
                # Also connect to currentIndexChanged for more reliable triggering
                field.combobox.currentIndexChanged.connect(lambda index, f=field: self.highlight_field(f, False))


class BaseComponent(QFrame):
    @property
    def is_valid(self) -> bool:
        """
        Method to check if the component is valid.
        If this method is not overridden in the subclass, component is always valid.
        """
        return True

    @property
    def error_message(self) -> str | None:
        """
        Method to get the error message if the component is not valid.
        If this method is not overridden in the subclass, it returns None.
        Return type should be string - if there's error message or None if there's no error.
        """
        return None


class LabeledInputComponent(BaseComponent):
    def __init__(
        self,
        text: str,
        parent: QWidget,
        min_length: int | None = None,
        required: bool = False,
        validator: QValidator | None = None,
    ):
        self.used_validator = None
        self.label = text
        self.is_required = required
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        label = QLabel(text=text, parent=self)
        self.line_edit = QLineEdit(self)
        if min_length:
            self.line_edit.setMinimumWidth(min_length)

        if validator:
            self.used_validator = validator
        elif required:
            self.used_validator = RequiredValidator()
        if self.used_validator:
            self.line_edit.setValidator(self.used_validator)
            self.line_edit.editingFinished.connect(self.validate)

        layout.addWidget(label)
        layout.addWidget(self.line_edit)

    @property
    def text(self) -> str:
        return self.line_edit.text()

    @text.setter
    def text(self, text):
        self.line_edit.setText(text)

    def clear(self) -> None:
        self.line_edit.clear()

    def toggle_highlight(self, color: str | None) -> None:
        if color:
            self.line_edit.setStyleSheet(f"background-color: {color};")
        else:
            self.line_edit.setStyleSheet("")

    def validate(self) -> None:
        if self.used_validator:
            validation_state, _, _ = self.used_validator.validate(self.text, 0)
            if validation_state != QValidator.Acceptable:
                self.toggle_highlight("mistyrose")
            else:
                self.toggle_highlight(None)

    @property
    def is_valid(self) -> bool:
        # For required fields without a specific validator, check if they have content
        if self.is_required and not self.used_validator:
            return bool(self.text.strip())

        # For fields with validators, check the validation state
        if self.used_validator:
            validation_state, _, _ = self.used_validator.validate(self.text, 0)
            return validation_state == QValidator.Acceptable

        # For non-required fields without validators, always valid
        return True

    @property
    def error_message(self) -> str | None:
        if self.is_required and not self.text:
            return f"Pole '{self.label}' jest wymagane."
        if self.used_validator and not self.is_valid:
            return self.used_validator.default_error_message


class LabeledComboBoxComponent(BaseComponent):
    def __init__(
        self,
        text: str,
        parent: QWidget,
        min_length: int | None = None,
        required: bool = False,
    ):
        self.label = text
        self.is_required = required
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        label = QLabel(text=text, parent=self)
        self.combobox = QComboBox(self)
        if min_length:
            self.combobox.setMinimumWidth(min_length)

        layout.addWidget(label)
        layout.addWidget(self.combobox)

    @property
    def text(self) -> str:
        return self.combobox.currentText()

    @text.setter
    def text(self, text):
        index = self.combobox.findText(text)
        if index >= 0:
            self.combobox.setCurrentIndex(index)

    def clear(self) -> None:
        self.combobox.clear()

    def addItems(self, items: list[str]) -> None:
        self.combobox.addItems(items)

    @property
    def is_valid(self) -> bool:
        if not self.is_required:
            return True
        return bool(self.combobox.currentText())

    @property
    def error_message(self) -> str | None:
        if self.is_required and not self.text:
            return f"Pole '{self.label}' jest wymagane."
        return None


class LabeledCheckboxComponent(BaseComponent):
    def __init__(self, text, parent, label_position: str = "above"):
        super().__init__(parent)
        label = QLabel(text=text, parent=self)
        self.checkbox = QCheckBox(self)

        layout_class = QVBoxLayout if label_position == "above" else QHBoxLayout
        layout = layout_class(self)
        layout.addWidget(label)
        if label_position == "above":
            layout.insertWidget(1, self.checkbox)
        else:
            layout.addWidget(self.checkbox)


class LabeledDateComponent(BaseComponent):
    def __init__(self, text, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text=text, parent=self)
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.dateTime()
        layout.addWidget(label)
        layout.addWidget(self.date_input)
