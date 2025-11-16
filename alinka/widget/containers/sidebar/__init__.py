from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SidebarMenuContainer(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.sidebar_menu = parent
        self.setObjectName("SidebarMenuContainer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Search button
        self.search_child_btn = QPushButton("Wyszukaj", self)
        self.search_child_btn.setObjectName("sidebar_button")
        self.search_child_btn.setCheckable(True)
        self.search_child_btn.setChecked(True)
        self.search_child_btn.setFixedWidth(180)
        self.search_child_btn.clicked.connect(self.show_browser)
        self.button_group.addButton(self.search_child_btn)
        layout.addWidget(self.search_child_btn, 0, Qt.AlignHCenter)

        # Create document button
        self.create_documents_btn = QPushButton("Utwórz dokument", self)
        self.create_documents_btn.setObjectName("sidebar_button")
        self.create_documents_btn.setCheckable(True)
        self.create_documents_btn.setEnabled(True)
        self.create_documents_btn.setFixedWidth(180)
        self.create_documents_btn.clicked.connect(self.show_application)
        self.button_group.addButton(self.create_documents_btn)
        layout.addWidget(self.create_documents_btn, 0, Qt.AlignHCenter)

        # Settings button
        self.settings_btn = QPushButton("Ustawienia", self)
        self.settings_btn.setObjectName("sidebar_button")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setFixedWidth(180)
        self.settings_btn.clicked.connect(self.show_settings)
        self.button_group.addButton(self.settings_btn)
        layout.addWidget(self.settings_btn, 0, Qt.AlignHCenter)

        layout.addStretch(1)

        logo_label = QLabel(self)
        logo_pixmap = QPixmap("./statics/alinka.svg")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label, 0, Qt.AlignHCenter)

    def show_browser(self):
        self.search_child_btn.setChecked(True)
        self.sidebar_menu.central_widget.main_body.content_container.show_browser_container()
        self.sidebar_menu.central_widget.main_body.footer_container.show_browser_footer_container()

    def showEvent(self, event):
        main_body = self.sidebar_menu.central_widget.main_body
        main_body.content_container.validate_basic_settings()
        return super().showEvent(event)

    def toggle_create_application_btn(self, enabled: bool):
        self.create_documents_btn.setEnabled(enabled)

    def show_application(self) -> None:
        self.create_documents_btn.setChecked(True)
        main_body = self.sidebar_menu.central_widget.main_body
        if not main_body.content_container.validate_basic_settings():
            return None
        main_body.content_container.show_application_container()
        main_body.footer_container.show_application_footer_container()

    def show_settings(self) -> None:
        self.settings_btn.setChecked(True)
        main_body = self.sidebar_menu.central_widget.main_body
        main_body.content_container.show_settings_container()
        main_body.footer_container.show_settings_footer_container()


class SidebarMenu(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.central_widget = parent
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("SidebarMenu")
        self.setFixedWidth(200)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_menu_container = SidebarMenuContainer(self)
        layout.addWidget(self.sidebar_menu_container)
