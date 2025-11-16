from PySide6.QtCore import Qt, Signal
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

from alinka import rspo_client
from alinka.constants.common import CHOOSE_FROM_LIST_MESSAGE


class NoScrollComboBox(QComboBox):
    """QComboBox that ignores mouse wheel events to prevent accidental changes."""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent scrolling through options."""
        event.ignore()


class ValidationMixin:
    """
    Mixin class to add validation functionality to components/containers
    Including this mixing ensures that all components/containers have a consistent
    interface for validation-related methods and properties.
    Method should be overridden in subclasses as needed.
    """

    @property
    def is_valid(self) -> bool:
        """Method to check if the component/container is valid."""
        return True

    @property
    def error_message(self) -> str | None:
        """
        Method to get the error message if the component is not valid.
        Return type should be string - if there's error message or None if there's no error.
        """
        return None

    def validate(self) -> bool:
        """
        Trigger validation of this component/containers and subclasses.
        This method should also update the visual state of the component/container
        to reflect whether it's valid or not (e.g., highlighting fields in red)
        by calling self.display_validation_result(validation_result)
        """
        is_valid = self.is_valid
        self.display_validation_result(is_valid)
        return is_valid

    def clear_validation_state(self) -> None:
        """Reset component and it's parent validation state"""
        pass

    def display_validation_result(self, validation_result: bool) -> None:
        """Display validation result by updating component's appearance"""
        pass


class LabeledInputComponent(ValidationMixin, QFrame):
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
        layout.setContentsMargins(12, 12, 12, 12)  # Bold margins for better spacing
        layout.setSpacing(8)  # More spacing between label and input
        label = QLabel(text=text, parent=self)
        # Make label bolder and darker
        label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")
        self.line_edit = QLineEdit(self)
        self.line_edit.setMinimumHeight(36)  # Taller input fields
        if min_length:
            self.line_edit.setMinimumWidth(min_length)

        self.line_edit.textChanged.connect(self.clear_validation_state)

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

    def display_validation_result(self, validation_result: bool) -> None:
        if validation_result:
            self.line_edit.setProperty("validationState", "valid")
        else:
            self.line_edit.setProperty("validationState", "invalid")
        self.line_edit.style().unpolish(self.line_edit)
        self.line_edit.style().polish(self.line_edit)

    def toggle_highlight(self, color: str | None) -> None:
        # Legacy method for backward compatibility
        if color:
            self.line_edit.setProperty("validationState", "valid" if "green" in color.lower() else "invalid")
        else:
            self.line_edit.setProperty("validationState", "")
        self.line_edit.style().unpolish(self.line_edit)
        self.line_edit.style().polish(self.line_edit)

    @property
    def is_valid(self) -> bool:
        if self.is_required:
            return bool(self.text.strip())
        return True

    @property
    def error_message(self) -> str | None:
        if self.is_required and not self.text:
            return f"Pole '{self.label}' jest wymagane."
        if self.used_validator and not self.is_valid:
            return self.used_validator.default_error_message

    def clear_validation_state(self) -> None:
        """Reset component validation state"""
        # Only clear field-level validation, not tab-level validation
        # Tab-level validation should only be cleared when the tab actually becomes valid
        self.toggle_highlight(None)


class LabeledComboBoxComponent(ValidationMixin, QFrame):
    def __init__(
        self,
        text: str,
        parent: QWidget,
        min_length: int | None = None,
        required: bool = False,
        static: bool = False,
        unselectable: bool = False,
    ):
        self.label = text
        self.is_required = required
        # If static, options won't change dynamically, e.g. school types
        # clear means in this case remove selection only
        self.is_static = static
        # If unselectable, user is able to remove selection (set to no selection)
        self.is_unselectable = unselectable
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # Bold margins to match input
        layout.setSpacing(8)  # More spacing between label and combobox
        layout.setAlignment(Qt.AlignTop)  # Align to top to reduce empty space
        label = QLabel(text=text, parent=self)
        # Make label bolder and darker
        label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")
        self.combobox = NoScrollComboBox(self)
        self.combobox.setMinimumHeight(28)  # Reduced height
        if min_length:
            self.combobox.setMinimumWidth(min_length)
        if self.is_unselectable:
            self.combobox.insertItem(0, CHOOSE_FROM_LIST_MESSAGE)
            self.combobox.currentIndexChanged.connect(self._clear_if_unselected)
        self.combobox.currentIndexChanged.connect(self.clear_validation_state)
        self.combobox.currentTextChanged.connect(self.clear_validation_state)
        layout.addWidget(label)
        layout.addWidget(self.combobox)
        
        # Initialize combobox state
        self._update_combobox_state()

    @property
    def text(self) -> str:
        return self.combobox.currentText()

    @text.setter
    def text(self, text):
        index = self.combobox.findText(text)
        if index >= 0:
            self.combobox.setCurrentIndex(index)

    def _clear_if_unselected(self) -> None:
        if self.is_unselectable and self.combobox.currentIndex() == 0:
            self.remove_selection()

    def remove_selection(self) -> None:
        self.combobox.setCurrentIndex(-1)
        self._update_combobox_state()

    def _insert_invitation_item(self) -> None:
        self.combobox.insertItem(0, CHOOSE_FROM_LIST_MESSAGE)

    def clear_options(self) -> None:
        self.combobox.clear()
        if self.is_unselectable:
            self._insert_invitation_item()
        self.combobox.setEnabled(True)

    def clear(self) -> None:
        self.remove_selection()
        if not self.is_static:
            self.clear_options()

    def addItems(self, items: list[str]) -> None:
        self.combobox.addItems(items)
        self._update_combobox_state()
    
    def addItem(self, text: str, userData=None) -> None:
        """Wrapper for combobox.addItem that also updates state."""
        self.combobox.addItem(text, userData)
        self._update_combobox_state()
    
    def _update_combobox_state(self) -> None:
        """Enable/disable combobox based on whether it has selectable items."""
        # If combobox is editable, always keep it enabled (user can type)
        if self.combobox.isEditable():
            self.combobox.setEnabled(True)
            return
        
        # Count items excluding the invitation item if present
        item_count = self.combobox.count()
        if self.is_unselectable and item_count > 0:
            # Has at least the invitation item, check if there are more
            has_selectable_items = item_count > 1
        else:
            has_selectable_items = item_count > 0
        
        # Disable if no selectable items, enable otherwise
        self.combobox.setEnabled(has_selectable_items)
        
        # If disabled and empty, set placeholder-like text
        if not has_selectable_items and not self.is_unselectable:
            # This will be handled by the stylesheet or we could add a
            # placeholder
            pass

    def display_validation_result(self, validation_result: bool) -> None:
        if validation_result:
            self.combobox.setProperty("validationState", "valid")
        else:
            self.combobox.setProperty("validationState", "invalid")
        self.combobox.style().unpolish(self.combobox)
        self.combobox.style().polish(self.combobox)

    def toggle_highlight(self, color: str | None) -> None:
        # Legacy method for backward compatibility
        if color:
            self.combobox.setProperty("validationState", "valid" if "green" in color.lower() else "invalid")
        else:
            self.combobox.setProperty("validationState", "")
        self.combobox.style().unpolish(self.combobox)
        self.combobox.style().polish(self.combobox)

    def clear_validation_state(self) -> None:
        """Reset component validation state"""
        # Only clear field-level validation, not tab-level validation
        self.toggle_highlight(None)

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


class LabeledCheckboxComponent(ValidationMixin, QFrame):
    def __init__(self, text, parent, label_position: str = "above"):
        super().__init__(parent)
        label = QLabel(text=text, parent=self)
        # Make label bolder and darker
        label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")
        self.checkbox = QCheckBox(self)

        layout_class = QVBoxLayout if label_position == "above" else QHBoxLayout
        layout = layout_class(self)
        # Match margins and spacing with LabeledInputComponent for alignment
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(label)
        if label_position == "above":
            layout.insertWidget(1, self.checkbox)
        else:
            layout.addWidget(self.checkbox)

    def clear(self) -> None:
        self.checkbox.setChecked(False)

    @property
    def is_checked(self) -> bool:
        return self.checkbox.isChecked()


class LabeledDateComponent(ValidationMixin, QFrame):
    def __init__(self, text, parent, required: bool = False):
        super().__init__(parent)
        self.required = required
        self.label = text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # Match LabeledInputComponent margins
        layout.setSpacing(8)  # Match LabeledInputComponent spacing
        label = QLabel(text=text, parent=self)
        # Make label bolder and darker to match LabeledInputComponent
        label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")
        self.date_input = QDateEdit(self)
        self.date_input.setMinimumHeight(36)
        self.date_input.setCalendarPopup(True)
        
        # Disable mouse wheel scrolling
        self.date_input.setFocusPolicy(Qt.StrongFocus)
        self.date_input.installEventFilter(self)
        
        # Set Polish locale for calendar
        from PySide6.QtCore import QLocale
        polish_locale = QLocale(QLocale.Polish, QLocale.Poland)
        self.date_input.setLocale(polish_locale)
        
        # Style the calendar widget immediately after creation
        calendar = self.date_input.calendarWidget()
        if calendar:
            self._style_calendar(calendar)
        
        layout.addWidget(label)
        layout.addWidget(self.date_input)
    
    def _style_calendar(self, calendar):
        """Apply aggressive styling to calendar widget."""
        # Set stylesheet on the calendar widget
        calendar.setStyleSheet("""
            QCalendarWidget QTableView {
                selection-background-color: #14b8a6 !important;
                selection-color: white !important;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #14b8a6 !important;
                selection-color: white !important;
                color: #000000;
            }
            QCalendarWidget QAbstractItemView::item:selected {
                background-color: #14b8a6 !important;
                color: white !important;
            }
        """)
        
        # Find the table view in the calendar and style it directly
        from PySide6.QtWidgets import QTableView
        table_view = calendar.findChild(QTableView)
        if table_view:
            # Use QPalette for more reliable color setting
            from PySide6.QtGui import QPalette, QColor
            palette = table_view.palette()
            palette.setColor(QPalette.Highlight, QColor("#14b8a6"))
            palette.setColor(QPalette.HighlightedText, QColor("white"))
            table_view.setPalette(palette)
    
    def showEvent(self, event):
        """Apply calendar styling when widget is shown."""
        super().showEvent(event)
        calendar = self.date_input.calendarWidget()
        if calendar:
            self._style_calendar(calendar)
    
    def eventFilter(self, obj, event):
        """Filter wheel events to prevent scrolling."""
        if event.type() == event.Type.Wheel and obj == self.date_input:
            event.ignore()
            return True
        return super().eventFilter(obj, event)

    def clear(self) -> None:
        self.date_input.clear()

    def display_validation_result(self, validation_result: bool) -> None:
        if validation_result:
            self.date_input.setProperty("validationState", "valid")
        else:
            self.date_input.setProperty("validationState", "invalid")
        self.date_input.style().unpolish(self.date_input)
        self.date_input.style().polish(self.date_input)

    def toggle_highlight(self, color: str | None) -> None:
        # Legacy method for backward compatibility
        if color:
            self.date_input.setProperty("validationState", "valid" if "green" in color.lower() else "invalid")
        else:
            self.date_input.setProperty("validationState", "")
        self.date_input.style().unpolish(self.date_input)
        self.date_input.style().polish(self.date_input)

    @property
    def is_valid(self) -> bool:
        if self.required and not self.date_input.date():
            return False
        return True

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return f"Pole '{self.label}' jest wymagane."

    def clear_validation_state(self) -> None:
        """Reset component validation state"""
        # Only clear field-level validation, not tab-level validation
        self.toggle_highlight(None)


class SelectProvinceDistrictGroup(ValidationMixin, QFrame):
    """Generic component to select provinece and district from RPSO"""

    selection_changed = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.select_school_group = parent

        location_frame_layout = QHBoxLayout(self)
        location_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.province_combobox = LabeledComboBoxComponent("Województwo", self, required=True)
        self.province_combobox.combobox.setPlaceholderText("Wybierz z listy...")
        self.province_combobox.combobox.currentTextChanged.connect(self.on_province_changed)

        try:
            provinces = rspo_client.list_provinces()
            for province in provinces:
                self.province_combobox.addItem(province.name, province.id)
        except Exception as e:
            error_msg = "Błąd ładowania danych - sprawdź połączenie z internetem"
            self.province_combobox.combobox.setPlaceholderText(error_msg)
            self.province_combobox.combobox.setEditable(True)
            self.province_combobox.combobox.setEnabled(True)
            print(f"Error loading provinces: {e}")

        self.district_combobox = LabeledComboBoxComponent(
            "Powiat", self, required=True
        )
        self.district_combobox.combobox.setPlaceholderText(
            "Wybierz z listy..."
        )
        self.district_combobox.combobox.currentTextChanged.connect(
            self.on_district_changed
        )
        location_frame_layout.addWidget(self.province_combobox)
        location_frame_layout.addWidget(self.district_combobox)

    @property
    def province_id(self) -> int | None:
        return self.province_combobox.combobox.currentData()

    @property
    def district_id(self) -> int | None:
        return self.district_combobox.combobox.currentData()

    def populate_districts_combobox(self) -> None:
        self.district_combobox.clear()
        if not self.province_id:
            return
        try:
            districts = rspo_client.list_districts(
                province_id=self.province_id
            )
            for district in districts:
                self.district_combobox.addItem(district.name, district.id)
        except Exception as e:
            error_msg = "Błąd ładowania powiatów - sprawdź połączenie"
            self.district_combobox.combobox.setPlaceholderText(error_msg)
            self.district_combobox.combobox.setEditable(True)
            self.district_combobox.combobox.setEnabled(True)
            print(f"Error loading districts: {e}")

    def on_province_changed(self):
        """
        In case of province change we should clear all other selections and
        repopulate districts combobox
        """
        self.selection_changed.emit()
        self.district_combobox.clear()
        self.populate_districts_combobox()

    def on_district_changed(self):
        """In case of district change we should only trigger selection
        changed signal"""
        self.selection_changed.emit()
