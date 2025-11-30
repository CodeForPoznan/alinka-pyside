"""Custom QTabBar that supports validation highlighting."""

from PySide6.QtCore import QPoint, QRect, Qt, QSize
from PySide6.QtGui import QBrush, QColor, QFont, QPainter
from PySide6.QtWidgets import QTabBar


class ValidationTabBar(QTabBar):
    """Custom QTabBar with validation highlighting for invalid tabs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._invalid_tabs = []
        self.icon_margin = 10  # margines od prawej krawędzi tab'a
        self.warning_icon = "⚠"


    def set_invalid_tabs(self, invalid_indices: list[int]) -> None:
        """Set which tab indices should be painted as invalid."""
        self._invalid_tabs = invalid_indices
        self.update()

    def tabSizeHint(self, index: int) -> QSize:
        """Increase the width of the tab to accommodate the warning icon."""
        size = super().tabSizeHint(index)
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.tabText(index))
        icon_width = font_metrics.horizontalAdvance(self.warning_icon)
        extra_width = icon_width + 40 + self.icon_margin
        size.setWidth(max(size.width(), text_width + extra_width))
        return size

    def paintEvent(self, event):
        """Override paint to draw validation indicators for invalid tabs."""
        super().paintEvent(event)

        if not self._invalid_tabs:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for index in self._invalid_tabs:
            tab_rect = self.tabRect(index)

            painter.save()

            indicator_color = QColor("#d32f2f")
            icon_color = QColor("#d32f2f")
            indicator_width = 4

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(indicator_color))
            indicator_rect = QRect(tab_rect.left() + 2, tab_rect.top() + 4, indicator_width, tab_rect.height() - 8)
            painter.drawRoundedRect(indicator_rect, 2, 2)

            icon_font = QFont()
            icon_font.setPointSize(11)
            icon_font.setBold(True)
            painter.setFont(icon_font)
            painter.setPen(icon_color)

            font_metrics = painter.fontMetrics()

            icon_x = tab_rect.right() - self.icon_margin - font_metrics.horizontalAdvance(self.warning_icon)
            icon_y = tab_rect.center().y() + (font_metrics.ascent() // 2)
            painter.drawText(QPoint(icon_x, icon_y), self.warning_icon)

            painter.restore()
