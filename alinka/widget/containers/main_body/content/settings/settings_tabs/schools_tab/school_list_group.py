from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QGroupBox, QHeaderView, QTableView, QVBoxLayout, QWidget

from alinka.db.queries import get_schools


class SchoolListGroup(QGroupBox):
    def __init__(self, parent: QWidget):
        super().__init__(title="Lista szkół", parent=parent)
        self.school_tab = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nazwa Szkoły", "Typ Szkoły", "Adres", "Miejscowość"])

        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.resizeColumnsToContents()
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

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
