import os
import sys
from datetime import datetime

import platformdirs

from alinka.config import settings

# see: https://pyinstaller.org/en/stable/runtime-information.html#using-sys-executable-and-sys-argv-0
# we're assuming, that as it's run from PyInstaller,
# then console is not attached - let's write logs to a file
if getattr(sys, "frozen", False):
    logs_file = os.path.join(
        platformdirs.user_data_dir(appname=settings.APP_NAME, appauthor=settings.APP_AUTHOR),
        "logs",
        datetime.now().strftime("alinka_%Y-%m-%d_%H-%M-%S.log"),
    )
    os.makedirs(os.path.dirname(logs_file), exist_ok=True)
    sys.stdout = sys.stderr = open(logs_file, "w", encoding="utf-8")

# We're pushing these import below, just to redirect
# stdout and stderr as soon as possible
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from alinka.widget.main_window import MainWindow

app = QApplication(sys.argv)

# Apply qt-material light teal theme as default
apply_stylesheet(app, theme='light_teal_500.xml', invert_secondary=True)

window = MainWindow()
window.showMaximized()

app.exec()
