"""
Session Summary Dialog for CodeFlow Studio.

Displays comprehensive post-run metrics and offers a direct pathway to verify
typed results against the original source code.
"""

from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SessionSummaryDialog(QDialog):
    """
    Modal dialog presenting transparent metrics upon run completion or cancellation.
    """
    verify_requested = Signal()

    def __init__(self, summary: Dict[str, any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.summary = summary
        self.setWindowTitle("Session Summary Report — CodeFlow Studio")
        self.resize(480, 420)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Header with State Badge
        state = self.summary.get("state", "UNKNOWN")
        badge_color = "#4caf50" if state == "COMPLETED" else ("#ff9800" if state == "STOPPED" else "#f44336")

        header = QLabel(f"Run Status: {state}")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {badge_color};")
        layout.addWidget(header)

        # Metrics Group
        group = QGroupBox("Execution Metrics")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        chars = f"{self.summary.get('characters_typed', 0)} / {self.summary.get('total_characters', 0)}"
        pct = f"{self.summary.get('completion_percentage', 0)}%"
        form.addRow("Characters Typed:", QLabel(f"{chars} ({pct})"))

        lines = f"{self.summary.get('lines_completed', 0)} / {self.summary.get('total_lines', 0)}"
        form.addRow("Lines Processed:", QLabel(lines))

        active_dur = f"{self.summary.get('active_duration_seconds', 0.0):.2f} s"
        form.addRow("Active Typing Time:", QLabel(active_dur))

        pause_dur = f"{self.summary.get('pause_duration_seconds', 0.0):.2f} s ({self.summary.get('pause_count', 0)} pauses)"
        form.addRow("Pause Duration:", QLabel(pause_dur))

        focus_losses = str(self.summary.get("focus_loss_count", 0))
        form.addRow("Focus Loss Events:", QLabel(focus_losses))

        cpm = f"{self.summary.get('effective_cpm', 0.0):.1f} CPM (~{self.summary.get('effective_wpm', 0.0):.1f} WPM)"
        form.addRow("Effective Typing Speed:", QLabel(cpm))

        target = self.summary.get("target_window", "Any Window") or "Any Window"
        form.addRow("Target Window:", QLabel(target[:40]))

        if self.summary.get("error_message"):
            err_label = QLabel(self.summary["error_message"])
            err_label.setStyleSheet("color: #f44336; font-weight: bold;")
            form.addRow("Error Details:", err_label)

        layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.verify_btn = QPushButton("🔍 Compare & Verify in VS Code...")
        self.verify_btn.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold; padding: 8px 14px;")
        self.verify_btn.clicked.connect(self._on_verify_clicked)
        btn_layout.addWidget(self.verify_btn)

        self.copy_btn = QPushButton("Copy Report")
        self.copy_btn.clicked.connect(self._copy_summary)
        btn_layout.addWidget(self.copy_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def _on_verify_clicked(self) -> None:
        self.accept()
        self.verify_requested.emit()

    def _copy_summary(self) -> None:
        try:
            import pyperclip
            lines = [f"{k}: {v}" for k, v in self.summary.items()]
            pyperclip.copy("\n".join(lines))
            self.copy_btn.setText("Copied!")
        except Exception:
            pass
