"""
Text Fidelity Comparator Dialog for CodeFlow Studio.

Compares original source code against actual output text produced in target
editors (such as VS Code) to verify 100% byte and formatting fidelity.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from codeflow.core.comparator import DiffResult, DiscrepancyType, SourceComparator


class TextComparatorDialog(QDialog):
    """
    Verification tool comparing original source with target editor result.
    """

    def __init__(self, source_text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Fidelity Verification — Source vs Result Comparator")
        self.resize(950, 680)
        self._source_text = source_text
        self._init_ui()
        if source_text:
            self.source_editor.setPlainText(source_text)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Instructions Header
        instruction = QLabel(
            "📋 <b>VS Code Integration Verification</b>: Copy the text from VS Code (Ctrl+A, Ctrl+C), "
            "paste it into the 'Editor Result' pane below, and click <b>Verify Exact Match</b>."
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #cccccc; padding: 4px;")
        layout.addWidget(instruction)

        # Splitter: Source on Left, Result on Right
        splitter = QSplitter(Qt.Horizontal)

        # Left: Original Source
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_header = QLabel("Original Source Code")
        left_header.setStyleSheet("color: #569cd6; font-weight: bold;")
        left_layout.addWidget(left_header)

        self.source_editor = QPlainTextEdit()
        self.source_editor.setFont(QFont("Cascadia Code", 10))
        self.source_editor.setPlaceholderText("Original source code...")
        left_layout.addWidget(self.source_editor)
        splitter.addWidget(left_widget)

        # Right: Result from Target Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_header_layout = QHBoxLayout()
        right_header = QLabel("Target Editor Result (Pasted from VS Code)")
        right_header.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        right_header_layout.addWidget(right_header, stretch=1)

        self.paste_btn = QPushButton("Paste from Clipboard")
        self.paste_btn.clicked.connect(self._paste_clipboard)
        right_header_layout.addWidget(self.paste_btn)
        right_layout.addLayout(right_header_layout)

        self.result_editor = QPlainTextEdit()
        self.result_editor.setFont(QFont("Cascadia Code", 10))
        self.result_editor.setPlaceholderText("Paste output from VS Code here...")
        right_layout.addWidget(self.result_editor)
        splitter.addWidget(right_widget)

        splitter.setSizes([475, 475])
        layout.addWidget(splitter, stretch=2)

        # Verification Button
        btn_row = QHBoxLayout()
        self.compare_btn = QPushButton("🔍 Verify Exact Match")
        self.compare_btn.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold; padding: 8px 18px;")
        self.compare_btn.clicked.connect(self.run_comparison)
        btn_row.addWidget(self.compare_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.close_btn)
        layout.addLayout(btn_row)

        # Diagnostic Report Box
        self.report_frame = QFrame()
        self.report_frame.setStyleSheet("background-color: #252526; border: 1px solid #3c3c3c; border-radius: 6px;")
        report_layout = QVBoxLayout(self.report_frame)

        self.status_badge = QLabel("Status: Awaiting Verification")
        self.status_badge.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffe082;")
        report_layout.addWidget(self.status_badge)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Consolas", 10))
        self.report_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; border: none;")
        report_layout.addWidget(self.report_text)

        layout.addWidget(self.report_frame, stretch=1)

    def _paste_clipboard(self) -> None:
        try:
            import pyperclip
            text = pyperclip.paste()
            self.result_editor.setPlainText(text)
            self.run_comparison()
        except Exception:
            pass

    def run_comparison(self) -> None:
        """Execute text comparison and display diagnostic diagnosis."""
        source = self.source_editor.toPlainText()
        result = self.result_editor.toPlainText()

        diff_res: DiffResult = SourceComparator.compare(source, result)

        if diff_res.is_exact_match:
            self.status_badge.setText("✅ 100% EXACT MATCH: Full Source Fidelity Confirmed!")
            self.status_badge.setStyleSheet("font-size: 14px; font-weight: bold; color: #4caf50;")
            self.report_text.setHtml(
                f"<b style='color:#4caf50;'>All {diff_res.source_char_count} characters, indentation spaces, "
                f"tabs, and newlines match perfectly!</b><br>"
                f"No VS Code auto-indent doubling or bracket duplication occurred."
            )
        else:
            self.status_badge.setText("⚠️ DISCREPANCIES DETECTED")
            self.status_badge.setStyleSheet("font-size: 14px; font-weight: bold; color: #f44336;")
            md_html = (
                f"<b style='color:#f44336;'>Fidelity Mismatch:</b><br>"
                f"Source: {diff_res.source_char_count} chars ({diff_res.source_line_count} lines)<br>"
                f"Result: {diff_res.result_char_count} chars ({diff_res.result_line_count} lines)<br><br>"
                f"<b>First Discrepancy:</b> Line {diff_res.first_diff_line}, Col {diff_res.first_diff_col}<br>"
                f"Expected: <code>{repr(diff_res.first_diff_source_char)}</code>, "
                f"Found: <code>{repr(diff_res.first_diff_result_char)}</code><br><br>"
                f"<b>Diagnosis:</b><br>{diff_res.diagnostic_message.replace('\n', '<br>')}<br><br>"
                f"<b>Unified Diff:</b><br><pre>{diff_res.unified_diff[:1500]}</pre>"
            )
            self.report_text.setHtml(md_html)
