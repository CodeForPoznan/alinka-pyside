from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from alinka.widget.components import ValidationMixin
from alinka.widget.toast import show_validation_error

from .application import ApplicationContainer
from .browser import BrowserContainer
from .settings import SettingsContainer


class ContentContainer(ValidationMixin, QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.main_body_container = parent
        self.sidebar_menu_container = self.main_body_container.central_widget.side_bar.sidebar_menu_container
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area for content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)

        self.application_container = ApplicationContainer(self.content_widget, self, visible=False)
        self.settings_container = SettingsContainer(self.content_widget, self, visible=False)
        self.browser_container = BrowserContainer(self.content_widget, self, visible=True)

        self.content_layout.addWidget(self.application_container)
        self.content_layout.addWidget(self.settings_container)
        self.content_layout.addWidget(self.browser_container)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Initialize breadcrumb for default view (browser)
        self.main_body_container.header_container.set_breadcrumb("Wyszukaj dokument")

    def validate_basic_settings(self) -> bool:
        # Reset validation state for all tabs
        self.settings_container.clear_invalid_tabs()

        if not self.settings_container.is_valid:
            error_message = self.settings_container.error_message
            # TODO: check if we want to validate settings
            invalid_tab_names = []
            invalid_indices = []
            for index in range(self.settings_container.count()):
                tab_widget = self.settings_container.widget(index)
                tab_name = self.settings_container.tabText(index)
                # Skip app settings tab (index 1) and creators tab (index 2)
                # as they don't need validation
                if index in [1, 2]:
                    continue
                if hasattr(tab_widget, "is_valid") and not tab_widget.is_valid:
                    invalid_tab_names.append(tab_name)
                    invalid_indices.append(index)

            self.settings_container.mark_invalid_tabs(invalid_indices)

            show_validation_error(
                self.window(), error_message, tab_names=invalid_tab_names if invalid_tab_names else None
            )
            self.sidebar_menu_container.create_documents_btn.setEnabled(False)
            self.show_settings_container()
            return False
        else:
            self.sidebar_menu_container.create_documents_btn.setEnabled(True)
            return True

    def showEvent(self, event):
        self.validate_basic_settings()
        self.validate_application()
        return super().showEvent(event)

    def validate_application(self):
        if self.application_container.isVisible():
            # This will trigger validation and red tab highlighting if invalid
            return self.application_container.validate()
        return True

    def show_settings_container(self):
        header_container = self.main_body_container.header_container
        self.application_container.setVisible(False)
        self.settings_container.setVisible(True)
        self.browser_container.setVisible(False)
        # Set breadcrumb with current tab name
        current_tab_index = self.settings_container.currentIndex()
        tab_name = self.settings_container.tabText(current_tab_index)
        header_container.set_breadcrumb(f"Ustawienia > {tab_name}")

    def show_application_container(self):
        # before showing the application container, we need to validate the settings container
        if not self.validate_basic_settings():
            return
        # when we start create application, all action sidebar buttons should be disabled
        self.sidebar_menu_container.search_child_btn.setEnabled(False)
        self.sidebar_menu_container.settings_btn.setEnabled(False)
        self.sidebar_menu_container.create_documents_btn.setEnabled(False)

        header_container = self.main_body_container.header_container
        self.settings_container.setVisible(False)
        self.application_container.setVisible(True)
        self.browser_container.setVisible(False)
        # Set breadcrumb with current tab name
        current_tab_index = self.application_container.currentIndex()
        tab_name = self.application_container.tabText(current_tab_index)
        header_container.set_breadcrumb(f"Utwórz dokument > {tab_name}")

    def show_browser_container(self):
        header_container = self.main_body_container.header_container
        self.settings_container.setVisible(False)
        self.application_container.setVisible(False)
        self.browser_container.setVisible(True)
        header_container.set_breadcrumb("Wyszukaj dokument")
