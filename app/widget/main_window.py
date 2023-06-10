import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QLineEdit, QMainWindow, QPushButton
from schemas import DecisionDbSchema
from tests.fixtures import decision_data as decission_fixture
from widget.actions import generate_and_save_decision


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon = QIcon()
        icon.addFile(os.path.join("statics", "alinka.svg"))
        self.setWindowTitle("My App")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(icon)
        self.ui_components()
        self.show()

    def ui_components(self):
        self.button = QPushButton("Utwórz dokumenty", self)
        self.button.setGeometry(200, 150, 150, 40)
        self.button.clicked.connect(self.click_me)
        self.input_line = QLineEdit("Mock first name", self)
        self.input_line.setGeometry(200, 100, 150, 40)
        self.result = QLabel("Wait for result...", self)
        self.result.setGeometry(200, 200, 150, 40)

    def click_me(self):
        decission_data = DecisionDbSchema(**decission_fixture)
        decission_data.child_first_name = self.input_line.text()
        decission_data.id = None
        generate_and_save_decision(decission_data, generate=True)
        self.result.setText("SUCCESS")
