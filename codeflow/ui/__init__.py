"""UI module exports for CodeFlow Studio."""

from codeflow.ui.main_window import CodeFlowMainWindow
from codeflow.ui.editor import CodeEditor
from codeflow.ui.highlighter import CodeHighlighter
from codeflow.ui.line_numbers import LineNumberArea
from codeflow.ui.settings_panel import SettingsPanel
from codeflow.ui.status_panel import StatusPanel
from codeflow.ui.session_dialog import SessionSummaryDialog
from codeflow.ui.comparator_dialog import TextComparatorDialog
from codeflow.ui.styles import DARK_THEME_QSS

__all__ = [
    "CodeFlowMainWindow",
    "CodeEditor",
    "CodeHighlighter",
    "LineNumberArea",
    "SettingsPanel",
    "StatusPanel",
    "SessionSummaryDialog",
    "TextComparatorDialog",
    "DARK_THEME_QSS",
]
