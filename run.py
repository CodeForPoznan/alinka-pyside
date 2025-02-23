import sys

from PySide2.QtWidgets import QApplication

from alinka.widget.main_window import MainWindow

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
