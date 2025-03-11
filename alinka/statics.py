import os
import sys


def get_statics_resource_path(resource):
    # see: https://pyinstaller.org/en/stable/runtime-information.html#using-sys-executable-and-sys-argv-0
    if getattr(sys, "frozen", False):
        dirname = sys._MEIPASS
    else:
        dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(dirname, "statics", resource)
