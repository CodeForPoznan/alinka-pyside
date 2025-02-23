from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class SidebarMenuContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setAlignment(Qt.AlignTop)
        search_child_btn = QPushButton("Wyszukaj dziecko", self)
        search_child_btn.clicked.connect(self.show_query_child)
        layout.addWidget(search_child_btn)
        create_documents_btn = QPushButton("Utwórz dokument", self)
        create_documents_btn.clicked.connect(self.show_application)
        layout.addWidget(create_documents_btn)
        settings_btn = QPushButton("Ustawienia", self)
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)

    def show_query_child(self):
        pass

    def show_application(self):
        self.parent.parent.main_body.content_container.show_application_container()
        self.parent.parent.main_body.footer_container.show_application_footer_container()

    def show_settings(self):
        self.parent.parent.main_body.content_container.show_settings_container()
        self.parent.parent.main_body.footer_container.show_settings_footer_container()


class SidebarMenu(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.main_container = SidebarMenuContainer(self)
        layout.addWidget(self.main_container)
