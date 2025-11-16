"""
Design system for Alinka application.
Provides stylesheets for validation states and custom overrides.
"""

COLORS = {
    "success": "#10b981",
    "error": "#ef4444",
    "background": "#ffffff",
    "border": "#cbd5e1",  # More visible border
    "text_primary": "#000000",
    "validation_success": "#d1fae5",  # Light green
    "validation_error": "#fee2e2",  # Light red
    # Additional colors extracted from stylesheets
    "tab_background": "#f1f5f9",  # Tab background
    "tab_text": "#64748b",  # Tab text color
    "tab_selected_border": "#14b8a6",  # Active tab bottom border (teal)
    "tab_hover": "#e2e8f0",  # Tab hover background
    "focus_background": "#e0f2fe",  # Focus state background
    "disabled_border": "#94a3b8",  # Disabled button border
    "calendar_hover": "#e0f2f1",  # Calendar hover background
    "invalid_selected": "#fecaca",  # Invalid selected tab background
}


# Custom overrides are applied in main_window.py and individual components
def get_validation_stylesheet() -> str:
    """
    Returns stylesheet for validation states only.
    This is applied on top of qt-material to ensure validation highlighting
    works.
    """
    return f"""
    /* Validation States - Applied on top of qt-material */
    QLineEdit[validationState="valid"] {{
        background-color: {COLORS["validation_success"]};
        border: 1px solid {COLORS["success"]};
    }}

    QLineEdit[validationState="invalid"] {{
        background-color: {COLORS["validation_error"]};
        border: 1px solid {COLORS["error"]};
    }}

    QComboBox[validationState="valid"] {{
        background-color: {COLORS["validation_success"]};
        border: 1px solid {COLORS["success"]};
    }}

    QComboBox[validationState="invalid"] {{
        background-color: {COLORS["validation_error"]};
        border: 1px solid {COLORS["error"]};
    }}

    QDateEdit[validationState="valid"] {{
        background-color: {COLORS["validation_success"]};
        border: 1px solid {COLORS["success"]};
    }}

    QDateEdit[validationState="invalid"] {{
        background-color: {COLORS["validation_error"]};
        border: 1px solid {COLORS["error"]};
    }}
    """


def get_custom_overrides_stylesheet() -> str:
    """
    Returns custom stylesheet overrides for qt-material themes.
    These styles ensure consistent branding and accessibility.
    """
    return f"""
    /* Global minimum font size */
    * {{
        font-size: 14px;
    }}
    
    /* Override qt-material for active tabs */
    QTabBar::tab {{
        padding: 10px 20px !important;
        margin: 2px 2px 0px 2px !important;
        border-top-left-radius: 6px !important;
        border-top-right-radius: 6px !important;
        border: 2px solid transparent !important;
        border-bottom: none !important;
        background-color: {COLORS["tab_background"]} !important;
        color: {COLORS["tab_text"]} !important;
        font-weight: 500 !important;
    }}
    
    QTabBar::tab:selected {{
        color: {COLORS["text_primary"]} !important;  /* Black text for active tabs */
        font-weight: bold !important;  /* Bold text for active tabs */
        background-color: {COLORS["background"]} !important;  /* White background for active tab */
        border-bottom: 3px solid {COLORS["tab_selected_border"]} !important;  /* Teal bottom border for active tab */
    }}
    
    QTabBar::tab:hover {{
        background-color: {COLORS["tab_hover"]} !important;  /* Slightly darker on hover */
    }}
    
    /* Note: Invalid tab styles are applied dynamically */
    
    /* Override qt-material for breadcrumb/title - same style as LabeledInputComponent labels */
    QLabel[breadcrumb="true"] {{
        color: {COLORS["tab_text"]} !important;  /* Light gray text like LabeledInputComponent */
        font-size: 13px !important;  /* Same size as LabeledInputComponent */
        font-weight: 600 !important;  /* Same weight as LabeledInputComponent */
    }}
    
    /* Override qt-material for GroupBox titles */
    QGroupBox {{
        color: {COLORS["text_primary"]} !important;
        font-weight: bold !important;
        border: none !important;
        padding-top: 15px !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
    }}
    
    QGroupBox::title {{
        color: {COLORS["text_primary"]} !important;
        font-weight: bold !important;
    }}
    
    /* Remove borders from all frames and containers */
    QFrame {{
        border: none !important;
    }}
    
    /* Sidebar gray background */
    QFrame#SidebarMenu, QFrame#SidebarMenuContainer {{
        background-color: {COLORS["tab_background"]} !important;
    }}
    
    /* Keep borders only for input widgets */
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
        border: 1px solid {COLORS["border"]} !important;
    }}
    
    /* Fix QComboBox styling - prevent green colors */
    QComboBox {{
        color: {COLORS["tab_text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    
    QComboBox:focus {{
        background-color: {COLORS["focus_background"]} !important;
        color: {COLORS["text_primary"]} !important;
        border: 1px solid {COLORS["border"]} !important;
    }}
    
    QComboBox:on {{
        background-color: {COLORS["focus_background"]} !important;
        color: {COLORS["text_primary"]} !important;
        border-radius: 4px;
        padding: 4px 8px;
    }}
    
    QComboBox:hover {{
        background-color: {COLORS["tab_background"]};
    }}
    
    QComboBox::drop-down:on {{
        background-color: transparent !important;
    }}
    
    /* Fix disabled button text color for readability */
    QPushButton:disabled {{
        background-color: {COLORS["border"]} !important;  /* Light gray background */
        color: {COLORS["text_primary"]} !important;  /* Black text for readability */
        border: 1px solid {COLORS["disabled_border"]} !important;
    }}
    
    /* Fix editable QComboBox text color */
    QComboBox[editable="true"] QLineEdit {{
        color: {COLORS["text_primary"]} !important;
    }}
    
    QComboBox:editable QLineEdit {{
        color: {COLORS["text_primary"]} !important;
    }}
    
    QComboBox QLineEdit {{
        color: {COLORS["text_primary"]} !important;
    }}
    
    QComboBox::drop-down {{
    }}
    
    QComboBox::down-arrow {{
        border: none;
        width: 20px;
        height: 20px;
    }}
    
    QComboBox:on::down-arrow {{
        border: none;
        width: 20px;
        height: 20px;
    }}
    
    /* Reduce dropdown item height */
    QComboBox QAbstractItemView::item {{
        padding: 4px 8px;
        color: {COLORS["text_primary"]};
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        color: {COLORS["text_primary"]} !important;
        background-color: {COLORS["tab_hover"]} !important;
    }}
    
    /* Table header styling - darker, more visible */
    QHeaderView::section {{
        color: {COLORS["text_primary"]} !important;
        font-weight: bold !important;
        background-color: {COLORS["tab_hover"]} !important;
    }}
    
    /* Table selected row - white text on selection */
    QTableView::item:selected {{
        color: white !important;
        background-color: {COLORS["success"]} !important;
    }}
    
    QTableView::item:selected:focus {{
        color: white !important;
    }}
    
    /* Input text should be black, not green */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        color: {COLORS["text_primary"]} !important;
    }}
    
    QComboBox QAbstractItemView {{
        color: {COLORS["text_primary"]} !important;
        background-color: {COLORS["background"]};
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        color: {COLORS["text_primary"]} !important;
        background-color: {COLORS["tab_hover"]} !important;
    }}
    
    /* Calendar text color fixes */
    QCalendarWidget QWidget {{
        color: {COLORS["text_primary"]};
    }}
    
    QCalendarWidget QTableView {{
        color: {COLORS["text_primary"]};
        selection-background-color: {COLORS["tab_selected_border"]};
        selection-color: white;
    }}
    
    QCalendarWidget QAbstractItemView {{
        color: {COLORS["text_primary"]} !important;
        selection-background-color: {COLORS["tab_selected_border"]} !important;
        selection-color: white !important;
    }}
    
    QCalendarWidget QAbstractItemView::item {{
        color: {COLORS["text_primary"]};
    }}
    
    QCalendarWidget QAbstractItemView::item:hover {{
        background-color: {COLORS["calendar_hover"]};
    }}
    
    QCalendarWidget QAbstractItemView::item:selected {{
        color: white !important;
        background-color: {COLORS["tab_selected_border"]} !important;
        font-weight: bold;
    }}
    
    QCalendarWidget QAbstractItemView::item:selected:focus {{
        color: white !important;
        background-color: {COLORS["tab_selected_border"]} !important;
    }}
    
    /* Calendar selected date - bold white text */
    QCalendarWidget QAbstractItemView:enabled {{
        selection-background-color: {COLORS["tab_selected_border"]};
        selection-color: white;
        font-weight: bold;
    }}
    
    QCalendarWidget QMenu {{
        color: {COLORS["text_primary"]};
    }}
    
    QCalendarWidget QToolButton {{
        color: {COLORS["text_primary"]};
    }}
    
    QCalendarWidget QSpinBox {{
        color: {COLORS["text_primary"]};
    }}
    
    /* Extra spacing after GroupBox title */
    QGroupBox {{
        margin-top: 10px;
    }}
    """

