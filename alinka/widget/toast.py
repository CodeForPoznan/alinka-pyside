from pyqttoast import Toast, ToastPosition, ToastPreset
from PySide6.QtWidgets import QApplication

DEFAULT_TOAST_DURATION = 4000


def show_toast(
    parent, message: str, toast_type: str = "info", duration: int = DEFAULT_TOAST_DURATION, title: str | None = None
):
    """
    Show a toast notification.

    Args:
        parent: Parent widget (should be the central widget or a child of it)
        message: Message text to display
        toast_type: Type of toast - "success", "error", "info", "warning"
        duration: Duration in milliseconds (default: 4000ms)
        title: Optional title for the toast (default: None)
    """
    # Find the central widget to ensure toasts appear within the app
    # content area
    toast_parent = parent
    if parent:
        # Try to find CentralWidget in the widget hierarchy
        current = parent
        while current:
            if current.__class__.__name__ == "CentralWidget":
                toast_parent = current
                break
            current = current.parent() if hasattr(current, "parent") else None

        # If CentralWidget not found, use the parent as-is
        if not toast_parent or toast_parent == parent:
            toast_parent = parent

    if not toast_parent:
        # Fallback: try to get from QApplication
        app = QApplication.instance()
        if app:
            toast_parent = app.activeWindow()

    if not toast_parent:
        return None

    toast = Toast(toast_parent)
    toast.setAlwaysOnMainScreen(False)
    toast.setDuration(duration)

    # Set position to TOP_RIGHT using the library's built-in positioning
    toast.setPosition(ToastPosition.TOP_RIGHT)

    toast.setMinimumWidth(400)
    toast.setMaximumWidth(600)

    # Apply minimal stylesheet - let pyqt-toast handle most styling
    toast.setStyleSheet(
        """
        QLabel {
            color: white;
        }
        QLabel#text {
            qproperty-wordWrap: true;
        }
        QLabel#title {
            font-weight: bold;
        }
        QLabel#icon {
            qproperty-alignment: AlignVCenter;
            margin-right: 8px;
        }
        QPushButton {
            color: white;
            background: transparent;
            border: none;
            padding: 4px;
            min-width: 24px;
            min-height: 24px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
    """
    )

    # Set title only if provided
    if title:
        toast.setTitle(title)
    else:
        # Hide title if not provided
        toast.setShowDuration(False)

    # Set message
    toast.setText(message)

    # Apply preset based on type
    preset_map = {
        "success": ToastPreset.SUCCESS,
        "error": ToastPreset.ERROR,
        "warning": ToastPreset.WARNING,
        "info": ToastPreset.INFORMATION,
    }
    preset = preset_map.get(toast_type.lower(), ToastPreset.INFORMATION)
    toast.applyPreset(preset)

    # Show the toast
    toast.show()

    return toast


def show_success(parent, message: str, title: str | None = None):
    """Convenience function for success messages."""
    return show_toast(parent, message, "success", title=title)


def show_error(parent, message: str, title: str | None = None):
    """Convenience function for error messages."""
    return show_toast(parent, message, "error", title=title)


def show_warning(parent, message: str, title: str | None = None):
    """Convenience function for warning messages."""
    return show_toast(parent, message, "warning", title=title)


def show_info(parent, message: str, title: str | None = None):
    """Convenience function for info messages."""
    return show_toast(parent, message, "info", title=title)


def show_validation_error(parent, message: str, tab_names: list[str] | None = None):
    """
    Show a validation error toast.
    This is a convenience function specifically for validation errors.

    Args:
        parent: Parent widget
        message: Error message to display
        tab_names: Optional list of tab names that have errors
    """
    title = "Błąd walidacji"
    if tab_names:
        tabs_text = ", ".join(tab_names)
        title = f"Błąd walidacji ({tabs_text})"

    return show_error(parent, message, title=title)
