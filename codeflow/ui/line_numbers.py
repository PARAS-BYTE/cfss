"""
Line Number Area Widget for CodeFlow Studio Code Editor.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberArea(QWidget):
    """
    Vertical gutter painted adjacent to the code editor displaying line numbers.
    """

    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self.code_editor.line_number_area_paint_event(event)
