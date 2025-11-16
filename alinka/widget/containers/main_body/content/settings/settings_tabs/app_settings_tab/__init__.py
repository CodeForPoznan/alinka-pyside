from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QSizePolicy, QVBoxLayout, QWidget
from qt_material import list_themes, apply_stylesheet

from alinka.widget.components import LabeledComboBoxComponent, ValidationMixin


class AppSettingsTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings_container = parent
        # Set size policy to not expand vertically
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop)

        # Theme settings group
        theme_group = QGroupBox("Motyw aplikacji", self)
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(12)

        # Description label
        description = QLabel(
            "Wybierz motyw kolorystyczny aplikacji. Zmiany zostaną zastosowane natychmiast.",
            self
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #334155; font-size: 13px; font-weight: 500;")
        theme_layout.addWidget(description)

        # Theme selector dropdown
        self.theme_selector = LabeledComboBoxComponent(
            "Wybierz motyw",
            self,
            required=False,
            static=True
        )
        
        # Get all available qt-material themes
        available_themes = list_themes()
        
        # Create friendly names for themes
        theme_display_names = {
            'light_amber.xml': 'Jasny - Bursztynowy',
            'light_blue.xml': 'Jasny - Niebieski',
            'light_cyan.xml': 'Jasny - Cyjanowy',
            'light_lightgreen.xml': 'Jasny - Jasnozielony',
            'light_pink.xml': 'Jasny - Różowy',
            'light_purple.xml': 'Jasny - Fioletowy',
            'light_red.xml': 'Jasny - Czerwony',
            'light_teal.xml': 'Jasny - Morski',
            'light_teal_500.xml': 'Jasny - Morski 500',
            'light_yellow.xml': 'Jasny - Żółty',
            'dark_amber.xml': 'Ciemny - Bursztynowy',
            'dark_blue.xml': 'Ciemny - Niebieski',
            'dark_cyan.xml': 'Ciemny - Cyjanowy',
            'dark_lightgreen.xml': 'Ciemny - Jasnozielony',
            'dark_pink.xml': 'Ciemny - Różowy',
            'dark_purple.xml': 'Ciemny - Fioletowy',
            'dark_red.xml': 'Ciemny - Czerwony',
            'dark_teal.xml': 'Ciemny - Morski',
            'dark_yellow.xml': 'Ciemny - Żółty',
        }

        # Add themes to dropdown
        self.theme_map = {}  # Map display name to actual theme file
        for theme in sorted(available_themes):
            display_name = theme_display_names.get(theme, theme)
            self.theme_selector.addItem(display_name, theme)
            self.theme_map[display_name] = theme

        # Set current theme (light_teal_500 is default)
        current_index = self.theme_selector.combobox.findData('light_teal_500.xml')
        if current_index >= 0:
            self.theme_selector.combobox.setCurrentIndex(current_index)

        # Connect theme change event
        self.theme_selector.combobox.currentIndexChanged.connect(self.change_theme)

        theme_layout.addWidget(self.theme_selector)
        layout.addWidget(theme_group)

    def change_theme(self, index):
        """Apply the selected theme to the application."""
        if index < 0:
            return
        
        theme_file = self.theme_selector.combobox.itemData(index)
        if not theme_file:
            return

        # Get the main application instance
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            # Apply the new theme
            apply_stylesheet(app, theme=theme_file, invert_secondary=True)
            
            # Reapply custom styles to override qt-material where needed
            main_window = self.window()
            if main_window:
                from alinka.widget.styles import (
                    get_custom_overrides_stylesheet,
                    get_validation_stylesheet,
                )
                custom_styles = (
                    get_validation_stylesheet() +
                    get_custom_overrides_stylesheet()
                )
                main_window.setStyleSheet(custom_styles)

    @property
    def is_valid(self) -> bool:
        # This tab doesn't require validation
        return True

    @property
    def error_message(self) -> str | None:
        return None

