"""Custom QTabBar that supports validation highlighting."""

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QFont
from PySide6.QtWidgets import QTabBar, QStyleOptionTab, QStyle


class ValidationTabBar(QTabBar):
    """Custom QTabBar with validation highlighting for invalid tabs."""    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._invalid_tabs = []
    
    def set_invalid_tabs(self, invalid_indices: list[int]) -> None:
        """Set which tab indices should be painted as invalid."""
        self._invalid_tabs = invalid_indices
        self.update()
    
    def paintEvent(self, event):
        """Override paint to draw validation indicators for invalid tabs."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for index in range(self.count()):
            tab_rect = self.tabRect(index)
            
            if not tab_rect.intersects(event.rect()):
                continue
            
            opt = QStyleOptionTab()
            self.initStyleOption(opt, index)
            
            if index in self._invalid_tabs:
                self.style().drawControl(
                    QStyle.CE_TabBarTab,
                    opt,
                    painter,
                    self
                )
                
                painter.save()
                
                if opt.state & QStyle.State_Selected:
                    indicator_color = QColor("#d32f2f")
                    icon_color = QColor("#d32f2f")
                    indicator_width = 4
                else:
                    indicator_color = QColor("#e57373")
                    icon_color = QColor("#d32f2f")
                    indicator_width = 3
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(indicator_color))
                indicator_rect = QRect(
                    tab_rect.left(),
                    tab_rect.top() + 4,
                    indicator_width,
                    tab_rect.height() - 8
                )
                painter.drawRoundedRect(indicator_rect, 2, 2)
                
                icon_font = QFont()
                icon_font.setPointSize(11)
                icon_font.setBold(True)
                painter.setFont(icon_font)
                painter.setPen(icon_color)
                
                font_metrics = painter.fontMetrics()
                icon_x = tab_rect.right() - 20
                icon_y = tab_rect.center().y() + (font_metrics.ascent() // 2)
                painter.drawText(QPoint(icon_x, icon_y), "⚠")
                
                painter.restore()
            else:

                self.style().drawControl(
                    QStyle.CE_TabBarTab,
                    opt,
                    painter,
                    self
                )
