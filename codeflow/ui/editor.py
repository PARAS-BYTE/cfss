"""
Code Editor Component for CodeFlow Studio.

Multiline code editor with line number gutter, syntax highlighting, exact
whitespace/indentation preservation, and status metrics reporting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QTextCursor, QTextFormat
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPlainTextEdit, QTextEdit, QWidget

from codeflow.core.source_model import SourceTextModel
from codeflow.ui.highlighter import CodeHighlighter
from codeflow.ui.line_numbers import LineNumberArea


class CodeEditor(QPlainTextEdit):
    """
    Precision code editor widget with syntax highlighting and line numbers.
    """
    cursor_moved = Signal(int, int)  # line, col (1-indexed)
    metrics_updated = Signal(int, int)  # char_count, line_count

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._source_model = SourceTextModel()
        self._current_file_path: Optional[str] = None

        # Setup monospace editor font
        editor_font = QFont("Cascadia Code", 11)
        editor_font.setStyleHint(QFont.Monospace)
        self.setFont(editor_font)

        # Tab width = 4 spaces
        font_metrics = QFontMetrics(editor_font)
        self.setTabStopDistance(font_metrics.horizontalAdvance(" ") * 4)

        # Editor visual settings
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #2d2d30;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        # Line number area
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._on_cursor_moved)
        self.textChanged.connect(self._on_text_changed)

        self._update_line_number_area_width(0)
        self._highlight_current_line()

        # Syntax highlighter
        self.highlighter = CodeHighlighter(self.document(), language="python")

    @property
    def source_model(self) -> SourceTextModel:
        return self._source_model

    @property
    def current_file_path(self) -> Optional[str]:
        return self._current_file_path

    def set_language(self, language: str) -> None:
        """Update syntax highlighting language."""
        self.highlighter.set_language(language)
        self._source_model.language = language

    def load_code(self, text: str, language: Optional[str] = None, file_path: Optional[str] = None) -> None:
        """Load text into editor while synchronizing source model."""
        self._current_file_path = file_path
        lang = language or self._source_model.language
        self._source_model = SourceTextModel(text, language=lang, file_path=file_path)
        self.setPlainText(text)
        if language:
            self.set_language(language)
        self._emit_metrics()

    def open_file_dialog(self) -> bool:
        """Open local file via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Source Code File",
            "",
            "All Source Files (*.py *.js *.ts *.cpp *.c *.rs *.go *.html *.css *.sql *.json *.md *.txt);;All Files (*.*)",
        )
        if not file_path:
            return False

        try:
            model = SourceTextModel.from_file(file_path)
            self._source_model = model
            self._current_file_path = file_path
            self.setPlainText(model.raw_text)
            self.set_language(model.language)
            self._emit_metrics()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error Opening File", f"Could not open file:\n{e}")
            return False

    def save_file_dialog(self) -> bool:
        """Save code to current file or prompt save as."""
        target_path = self._current_file_path
        if not target_path:
            target_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Source File",
                "",
                "All Files (*.*)",
            )
            if not target_path:
                return False

        try:
            self._source_model.set_text(self.toPlainText())
            self._source_model.save_to_file(target_path)
            self._current_file_path = target_path
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error Saving File", f"Could not save file:\n{e}")
            return False

    def clear_code(self) -> None:
        self.clear()
        self._source_model.set_text("")
        self._emit_metrics()

    def copy_all_code(self) -> None:
        try:
            import pyperclip
            pyperclip.copy(self.toPlainText())
        except Exception:
            pass

    def _on_text_changed(self) -> None:
        """Synchronize text to source model without trimming."""
        text = self.toPlainText()
        self._source_model.set_text(text)
        self._emit_metrics()

    def _emit_metrics(self) -> None:
        chars = len(self._source_model.raw_text)
        lines = self._source_model.stats.total_lines
        self.metrics_updated.emit(chars, lines)

    def _on_cursor_moved(self) -> None:
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_moved.emit(line, col)

    def line_number_area_width(self) -> int:
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 14 + self.fontMetrics().horizontalAdvance("9") * digits
        return max(space, 36)

    def _update_line_number_area_width(self, _) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def _highlight_current_line(self) -> None:
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        painter.setFont(self.font())
        painter.setPen(QColor("#858585"))

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
