from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class SidebarMenuContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.sidebar_menu = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setAlignment(Qt.AlignTop)
        search_child_btn = QPushButton("Wyszukaj dziecko", self)
        search_child_btn.clicked.connect(self.show_query_child)
        layout.addWidget(search_child_btn)
        self.create_documents_btn = QPushButton("Utwórz dokument", self)
        self.create_documents_btn.clicked.connect(self.show_application)
        layout.addWidget(self.create_documents_btn)
        settings_btn = QPushButton("Ustawienia", self)
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)

    def show_query_child(self):
        pass

    def showEvent(self, event):
        main_body = self.sidebar_menu.central_widget.main_body
        main_body.content_container.validate_basic_settings()
        return super().showEvent(event)

    def toggle_create_application_btn(self, enabled: bool):
        self.create_documents_btn.setEnabled(enabled)

    def show_application(self) -> None:
        main_body = self.sidebar_menu.central_widget.main_body
        if not main_body.content_container.validate_basic_settings():
            return None
        main_body.content_container.show_application_container()
        main_body.footer_container.show_application_footer_container()

    def show_settings(self) -> None:
        main_body = self.sidebar_menu.central_widget.main_body
        main_body.content_container.show_settings_container()
        main_body.footer_container.show_settings_footer_container()


class SidebarMenu(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.central_widget = parent
        self.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        self.sidebar_menu_container = SidebarMenuContainer(self)
        layout.addWidget(self.sidebar_menu_container)
