from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QGroupBox, QHeaderView, QSizePolicy, QTableView, QVBoxLayout, QWidget

from alinka.db.queries import get_schools
from alinka.widget.components import ValidationMixin


class SchoolListGroup(ValidationMixin, QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Lista szkół", parent=parent)
        self.school_tab = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nazwa Szkoły", "Typ Szkoły", "Adres", "Miejscowość"])

        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setMinimumHeight(200)  # Ensure minimum height for multiple rows
        
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(True)
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Auto-stretch to fill available width
        header.setStretchLastSection(True)
        
        self.table_view.verticalHeader().setDefaultSectionSize(32)

        layout.addWidget(self.table_view)

    def populate_school_list(self):
        self.model.setRowCount(0)
        for school in get_schools():
            row = [
                QStandardItem(school.name),
                QStandardItem(school.type),
                QStandardItem(school.address),
                QStandardItem(school.town),
            ]
            for item in row:
                item.setData(school.id)
            self.model.appendRow(row)

    def refresh(self):
        self.model.setRowCount(0)
        self.populate_school_list()

    def showEvent(self, event):
        self.populate_school_list()
        return super().showEvent(event)
