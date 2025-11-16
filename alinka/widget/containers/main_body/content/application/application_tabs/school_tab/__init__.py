from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from alinka.constants.common import SchoolTypes
from alinka.db.queries import (
    delete_school,
    filter_schools_by_type,
    get_school_by_id,
    get_schools,
)
from alinka.schemas import SchoolData, SchoolDbSchema
from alinka.widget.components import LabeledComboBoxComponent, ValidationMixin

from .school_dialog import SchoolDialog


class HandleSchoolFrame(ValidationMixin, QFrame):
    # signal emitted when the school list is changed
    # it should refresh school list in SchoolListGroup
    school_list_changed = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self.add_school_btn = QPushButton("Dodaj", self)
        self.add_school_btn.clicked.connect(self.add_new_school)
        self.edit_school_btn = QPushButton("Edytuj", self, enabled=False)
        self.edit_school_btn.clicked.connect(self.edit_school)
        self.remove_school_btn = QPushButton("Usuń", self, enabled=False)
        self.remove_school_btn.clicked.connect(self.remove_school)

        # Apply green styling to match the app theme
        button_style = """
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """
        self.add_school_btn.setStyleSheet(button_style)
        self.edit_school_btn.setStyleSheet(button_style)
        self.remove_school_btn.setStyleSheet(button_style)

        layout.addWidget(self.add_school_btn)
        layout.addWidget(self.edit_school_btn)
        layout.addWidget(self.remove_school_btn)

    def add_new_school(self):
        dialog = SchoolDialog(self, "Dodaj nową szkołę")
        if dialog.exec():
            self.school_list_changed.emit()

    def edit_school(self):
        selected_school = self.get_selected_school()
        if not selected_school:
            return
        dialog = SchoolDialog(self, "Edytuj szkołę", school_data=selected_school)
        if dialog.exec():
            self.school_list_changed.emit()

    def remove_school(self):
        selected_school = self.get_selected_school()
        if not selected_school:
            return
        delete_school(selected_school.id)
        self.school_list_changed.emit()

    def get_selected_school(self) -> SchoolDbSchema | None:
        return self.parent().get_selected_school()


class SchoolTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.application_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)

        self.school_type = LabeledComboBoxComponent("Rodzaj Szkoły", self, 300, required=True, static=True)
        self.school_type.combobox.setPlaceholderText("Wybierz z listy...")
        # Empty option for "no selection"
        self.school_type.addItem("")
        self.school_type.addItems(SchoolTypes.values())
        # Explicitly enable after adding items
        self.school_type.combobox.setEnabled(True)
        self.school_type.combobox.currentTextChanged.connect(self.populate_school_list)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nazwa Szkoły", "Typ Szkoły", "Adres", "Miejscowość"])

        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.resizeColumnsToContents()
        self.table_view.selectionModel().selectionChanged.connect(self.selection_changed)

        # Add modern styling to match the meeting tab
        self.table_view.setStyleSheet(
            """
            QTableView {
                outline: none;
                background-color: white;
                gridline-color: #e2e8f0;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
            }
            QTableView[validationState="invalid"] {
                border: 2px solid #ef4444;
                background-color: #fef2f2;
            }
            QTableView[validationState="valid"] {
                border: 2px solid #10b981;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
                min-height: 28px;
            }
            QTableView::item:selected {
                background-color: #dcfce7;
                color: black;
            }
            QTableView::item:hover {
                background-color: #f3f4f6;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                font-weight: 600;
                color: #374151;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """
        )

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.populate_school_list()

        self.handle_school_frame = HandleSchoolFrame(self)
        self.handle_school_frame.school_list_changed.connect(self.populate_school_list)

        layout.addWidget(self.school_type)
        layout.addWidget(self.table_view)
        layout.addWidget(self.handle_school_frame)

        # Add stretch to push all content to the top
        layout.addStretch()

    def selection_changed(self):
        is_selected = bool(self.get_selected_school())
        self.handle_school_frame.edit_school_btn.setEnabled(is_selected)
        self.handle_school_frame.remove_school_btn.setEnabled(is_selected)

    @property
    def is_selected(self) -> bool:
        selected_indexes = self.table_view.selectionModel().selectedRows()
        return selected_indexes and len(selected_indexes) == 1

    def get_selected_school(self) -> SchoolDbSchema | None:
        if not self.is_selected:
            return None

        selected_row = self.table_view.selectionModel().selectedRows()[0].row()
        school_id = self.model.item(selected_row, 0).data()
        return get_school_by_id(school_id)

    def populate_school_list(self):
        self.model.setRowCount(0)
        school_type = self.school_type.combobox.currentText()
        schools = get_schools() if not school_type else filter_schools_by_type(school_type)
        for school in schools:
            row = [
                QStandardItem(school.name),
                QStandardItem(school.type),
                QStandardItem(school.address),
                QStandardItem(school.town),
            ]
            for item in row:
                item.setData(school.id)
            self.model.appendRow(row)

    def clear(self):
        self.table_view.clearSelection()

    @property
    def school_data(self) -> SchoolData | None:
        selected_school = self.get_selected_school()
        if not selected_school:
            return None

        return SchoolData(
            rspo_id=selected_school.rspo_id,
            rspo_type=selected_school.rspo_type,
            parent_organisation_name=selected_school.parent_organisation_name,
            type=selected_school.type,
            name=selected_school.name,
            address=selected_school.address,
            town=selected_school.town,
            postal_code=selected_school.postal_code,
            post=selected_school.post,
        )

    @property
    def is_valid(self) -> bool:
        return self.is_selected

    @property
    def errror_message(self) -> str | None:
        if not self.is_selected:
            return "Nie wybrano szkoły z listy."
        return None

    def validate(self):
        is_valid = self.is_valid
        self.display_validation_result(is_valid)
        return is_valid

    def display_validation_result(self, validation_result: bool) -> None:
        if validation_result:
            self.table_view.setProperty("validationState", "valid")
        else:
            self.table_view.setProperty("validationState", "invalid")
        self.table_view.style().unpolish(self.table_view)
        self.table_view.style().polish(self.table_view)

    def toggle_highlight(self, color: str | None) -> None:
        # Keep this method for compatibility but it's no longer used
        # Validation now uses the property-based approach
        pass

    def clear_validation_state(self):
        self.table_view.setProperty("validationState", "")
        self.table_view.style().unpolish(self.table_view)
        self.table_view.style().polish(self.table_view)
