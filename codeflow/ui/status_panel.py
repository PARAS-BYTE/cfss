"""
Execution Control and Status Panel for CodeFlow Studio.

Houses Start/Pause/Resume/Stop buttons, real-time progress bars, target focus status,
live WPM speedometer pill, and inspection scroll status banners.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from codeflow.core.session import SessionState


class StatusPanel(QWidget):
    """
    Bottom control and status reporting panel.
    """
    start_clicked = Signal()
    pause_clicked = Signal()
    resume_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
        self.update_state(SessionState.IDLE)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # 1. Focus Warning Banner (Hidden by default)
        self.warning_banner = QFrame()
        self.warning_banner.setObjectName("focusWarningBanner")
        self.warning_banner.setVisible(False)
        banner_layout = QHBoxLayout(self.warning_banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)

        self.warning_text = QLabel("[FOCUS LOST] Automation paused to prevent typing in unintended applications. Refocus target or click Resume.")
        self.warning_text.setObjectName("focusWarningText")
        self.warning_text.setWordWrap(True)
        banner_layout.addWidget(self.warning_text, stretch=1)

        self.banner_resume_btn = QPushButton("RESUME")
        self.banner_resume_btn.clicked.connect(self.resume_clicked.emit)
        banner_layout.addWidget(self.banner_resume_btn)

        self.banner_stop_btn = QPushButton("STOP")
        self.banner_stop_btn.clicked.connect(self.stop_clicked.emit)
        banner_layout.addWidget(self.banner_stop_btn)

        layout.addWidget(self.warning_banner)

        # 2. Inspection Scroll Active Banner (Shown while mouse is scrolling/hovering and typing is halted)
        self.inspection_banner = QFrame()
        self.inspection_banner.setObjectName("inspectionBanner")
        self.inspection_banner.setVisible(False)
        insp_layout = QHBoxLayout(self.inspection_banner)
        insp_layout.setContentsMargins(10, 6, 10, 6)

        self.inspection_text = QLabel("[MOUSE INSPECTION ACTIVE] Mouse is scrolling and hovering over code. Keyboard input is strictly locked.")
        self.inspection_text.setObjectName("inspectionText")
        insp_layout.addWidget(self.inspection_text, stretch=1)
        layout.addWidget(self.inspection_banner)

        # 2.5 Live HUD Action Feed (Displays exact current microsecond state)
        self.live_hud_frame = QFrame()
        self.live_hud_frame.setObjectName("liveHudCard")
        self.live_hud_frame.setStyleSheet(
            "background: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 4px 10px;"
        )
        hud_layout = QHBoxLayout(self.live_hud_frame)
        hud_layout.setContentsMargins(6, 4, 6, 4)

        self.live_hud_icon = QLabel("[STATUS]")
        self.live_hud_icon.setObjectName("liveHudStatusTag")
        hud_layout.addWidget(self.live_hud_icon)

        self.live_action_label = QLabel("System Ready: Click START AUTOMATION [F5] to begin.")
        self.live_action_label.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 12px;")
        hud_layout.addWidget(self.live_action_label, stretch=1)

        self.input_method_pill = QLabel("INPUT: SHIFT+KEY PHYSICAL")
        self.input_method_pill.setStyleSheet(
            "color: #79c0ff; font-size: 11px; font-weight: 600; padding: 3px 8px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;"
        )
        hud_layout.addWidget(self.input_method_pill)

        layout.addWidget(self.live_hud_frame)

        # 3. Status & Metric Row
        metrics_row = QHBoxLayout()

        # Target Window status badge
        self.target_badge = QLabel("TARGET: READY")
        self.target_badge.setObjectName("statusBadgeGreen")
        metrics_row.addWidget(self.target_badge)

        self.target_title_label = QLabel("TARGET: ANY WINDOW")
        self.target_title_label.setStyleSheet("color: #58a6ff; font-weight: 600;")
        metrics_row.addWidget(self.target_title_label, stretch=1)

        # Live WPM Speedometer Pill
        self.wpm_pill = QLabel("SPEED: 40 WPM (200 CPM)")
        self.wpm_pill.setStyleSheet(
            "color: #79c0ff; font-weight: 600; font-size: 11px; padding: 3px 8px; background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px;"
        )
        metrics_row.addWidget(self.wpm_pill)

        # Cadence / Typo pill badge
        self.cadence_pill = QLabel("CADENCE: 30-45 WPM WAVY")
        self.cadence_pill.setStyleSheet(
            "color: #d2a8ff; font-weight: 600; font-size: 11px; padding: 3px 8px; background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px;"
        )
        metrics_row.addWidget(self.cadence_pill)

        # Countdown display
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #e3b341; font-weight: bold; font-size: 13px;")
        metrics_row.addWidget(self.countdown_label)

        # Time labels
        self.time_label = QLabel("Elapsed: 00:00 | ETA: --:--")
        self.time_label.setStyleSheet("color: #8b949e; font-weight: 500;")
        metrics_row.addWidget(self.time_label)

        layout.addLayout(metrics_row)

        # 4. Progress Bar & Detail Label
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.progress_detail_label = QLabel("Ready to start (0 / 0 characters)")
        self.progress_detail_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(self.progress_detail_label)

        # 5. Action Button Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.start_btn = QPushButton("▶ START AUTOMATION [F5]")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_clicked.emit)
        btn_row.addWidget(self.start_btn, stretch=2)

        self.stop_btn = QPushButton("■ STOP AUTOMATION [ESC]")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        btn_row.addWidget(self.stop_btn, stretch=2)

        self.pause_btn = QPushButton("❚❚ PAUSE [F6]")
        self.pause_btn.setObjectName("pauseButton")
        self.pause_btn.setMinimumHeight(44)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        btn_row.addWidget(self.pause_btn, stretch=1)

        self.resume_btn = QPushButton("▶ RESUME [F6]")
        self.resume_btn.setObjectName("resumeButton")
        self.resume_btn.setMinimumHeight(44)
        self.resume_btn.setCursor(Qt.PointingHandCursor)
        self.resume_btn.clicked.connect(self.resume_clicked.emit)
        btn_row.addWidget(self.resume_btn, stretch=1)

        layout.addLayout(btn_row)

    def set_target_info(self, title: str, is_vscode: bool = False) -> None:
        name = title if title else "ANY ACTIVE WINDOW"
        if len(name) > 55:
            name = name[:52] + "..."
        prefix = "VS CODE: " if is_vscode else "WINDOW: "
        self.target_title_label.setText(f"{prefix}{name.upper()}")

    def show_focus_warning(self, fg_title: str) -> None:
        self.warning_banner.setVisible(True)
        self.target_badge.setText("FOCUS LOST")
        self.target_badge.setObjectName("statusBadgeRed")
        self.target_badge.style().unpolish(self.target_badge)
        self.target_badge.style().polish(self.target_badge)
        self.warning_text.setText(
            f"[FOCUS LOST] Target window lost focus! Active window: '{fg_title}'. Automation paused for safety. "
            "Refocus target window or click RESUME."
        )

    def hide_focus_warning(self) -> None:
        self.warning_banner.setVisible(False)
        self.target_badge.setText("TARGET FOCUSED")
        self.target_badge.setObjectName("statusBadgeGreen")
        self.target_badge.style().unpolish(self.target_badge)
        self.target_badge.style().polish(self.target_badge)

    def set_inspection_scrolling(self, active: bool) -> None:
        """Show/hide inspection scrolling banner and update live HUD."""
        self.inspection_banner.setVisible(active)
        if active:
            self.live_hud_icon.setText("[HALTED]")
            self.live_action_label.setText("HALTED: Mouse scrolling & reviewing code. Keyboard input strictly locked.")
            self.live_action_label.setStyleSheet("color: #79c0ff; font-weight: bold; font-size: 12px;")
            self.cadence_pill.setText("MOUSE INSPECTION: TYPING HALTED")
            self.cadence_pill.setStyleSheet("color: #79c0ff; font-weight: 600; font-size: 11px; padding: 3px 8px; background-color: #0d1117; border: 1px solid #1f6feb; border-radius: 4px;")
        else:
            self.live_hud_icon.setText("[RUNNING]")
            self.live_action_label.setText("Active: Typing code with natural wavy cadence (30-45 WPM)...")
            self.live_action_label.setStyleSheet("color: #7ee787; font-weight: 600; font-size: 12px;")
            self.cadence_pill.setText("CADENCE: 30-45 WPM WAVY")
            self.cadence_pill.setStyleSheet("color: #d2a8ff; font-weight: 600; font-size: 11px; padding: 3px 8px; background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px;")

    def set_mouse_action(self, msg: str) -> None:
        """Receive detailed mouse inspection progress."""
        self.live_hud_icon.setText("[MOUSE]")
        self.live_action_label.setText(f"Mouse Action: {msg} [Typing Locked]")
        self.live_action_label.setStyleSheet("color: #79c0ff; font-weight: bold; font-size: 12px;")

    def flash_typo_notification(self, intended: str, typo: str) -> None:
        """Indicate an auto-corrected typo or word slip in live HUD."""
        self.live_hud_icon.setText("[TYPO]")
        self.live_action_label.setText(f"Typo self-correction: Mistake '{typo}' -> Backspaced -> Corrected to '{intended}'")
        self.live_action_label.setStyleSheet("color: #ffa657; font-weight: bold; font-size: 12px;")
        self.cadence_pill.setText(f"CORRECTION: '{typo}' -> '{intended}'")
        self.cadence_pill.setStyleSheet("color: #ffa657; font-weight: 600; font-size: 11px; padding: 3px 8px; background-color: #0d1117; border: 1px solid #bd561d; border-radius: 4px;")

    def set_countdown(self, seconds_left: int) -> None:
        self.live_hud_icon.setText("[COUNTDOWN]")
        self.live_action_label.setText(f"Countdown: {seconds_left}s remaining. Switch to target application window now.")
        self.live_action_label.setStyleSheet("color: #e3b341; font-weight: bold; font-size: 12px;")
        self.countdown_label.setText(f"STARTING IN {seconds_left}S")
        self.target_badge.setText("COUNTDOWN")
        self.target_badge.setObjectName("statusBadgeAmber")
        self.target_badge.style().unpolish(self.target_badge)
        self.target_badge.style().polish(self.target_badge)

    def clear_countdown(self) -> None:
        self.countdown_label.setText("")

    def update_progress(self, typed: int, total: int, current_line: int, total_lines: int, elapsed_s: float, eta_s: float, cpm: float = 0.0) -> None:
        pct = 0
        if total > 0:
            pct = int((typed / total) * 100)
        self.progress_bar.setValue(min(100, pct))

        el_min = int(elapsed_s // 60)
        el_sec = int(elapsed_s % 60)
        eta_min = int(eta_s // 60)
        eta_sec = int(eta_s % 60)

        wpm = cpm / 5.0
        if wpm > 0:
            self.wpm_pill.setText(f"SPEED: {int(wpm)} WPM ({int(cpm)} CPM)")

        self.time_label.setText(f"Elapsed: {el_min:02d}:{el_sec:02d} | ETA: {eta_min:02d}:{eta_sec:02d}")

        line_str = f"Line {current_line}" + (f" of {total_lines}" if total_lines > 0 else "")
        self.progress_detail_label.setText(f"Progress: {typed} / {total} characters ({pct}%) — {line_str}")

    def update_state(self, state: SessionState) -> None:
        if state == SessionState.IDLE:
            self.start_btn.setVisible(True)
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(False)
            self.stop_btn.setEnabled(False)
            self.stop_btn.setVisible(False)
            self.hide_focus_warning()
            self.set_inspection_scrolling(False)
            self.clear_countdown()
            self.target_badge.setText("IDLE")
            self.target_badge.setObjectName("statusBadgeGreen")
            self.live_hud_icon.setText("[READY]")
            self.live_action_label.setText("System Ready: Click START AUTOMATION [F5] to begin.")
            self.live_action_label.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 12px;")

        elif state == SessionState.COUNTDOWN:
            self.start_btn.setVisible(False)
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            self.stop_btn.setEnabled(True)

        elif state == SessionState.RUNNING:
            self.start_btn.setVisible(False)
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.pause_btn.setVisible(True)
            self.resume_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            self.stop_btn.setEnabled(True)
            self.hide_focus_warning()
            self.clear_countdown()
            self.target_badge.setText("RUNNING")
            self.target_badge.setObjectName("statusBadgeGreen")
            self.live_hud_icon.setText("[ACTIVE]")
            self.live_action_label.setText("Typing code with natural wavy cadence (30-45 WPM)...")
            self.live_action_label.setStyleSheet("color: #7ee787; font-weight: 600; font-size: 12px;")

        elif state == SessionState.PAUSED:
            self.start_btn.setVisible(False)
            self.start_btn.setEnabled(False)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(True)
            self.resume_btn.setEnabled(True)
            self.stop_btn.setVisible(True)
            self.stop_btn.setEnabled(True)
            self.target_badge.setText("PAUSED")
            self.target_badge.setObjectName("statusBadgeAmber")
            self.live_hud_icon.setText("[PAUSED]")
            self.live_action_label.setText("PAUSED: Typing suspended. Click RESUME [F6] or refocus target window.")
            self.live_action_label.setStyleSheet("color: #e3b341; font-weight: bold; font-size: 12px;")

        elif state in (SessionState.STOPPED, SessionState.COMPLETED, SessionState.ERROR):
            self.start_btn.setVisible(True)
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(False)
            self.stop_btn.setEnabled(False)
            self.stop_btn.setVisible(False)
            self.clear_countdown()
            self.set_inspection_scrolling(False)
            if state == SessionState.COMPLETED:
                self.target_badge.setText("COMPLETED")
                self.target_badge.setObjectName("statusBadgeGreen")
                self.live_hud_icon.setText("[DONE]")
                self.live_action_label.setText("Completed! Source text typed exactly with 100% fidelity.")
                self.live_action_label.setStyleSheet("color: #7ee787; font-weight: bold; font-size: 12px;")
            elif state == SessionState.STOPPED:
                self.target_badge.setText("STOPPED")
                self.target_badge.setObjectName("statusBadgeAmber")
                self.live_hud_icon.setText("[STOPPED]")
                self.live_action_label.setText("Stopped by user. Session terminated safely.")
                self.live_action_label.setStyleSheet("color: #f85149; font-weight: 600; font-size: 12px;")
            else:
                self.target_badge.setText("ERROR")
                self.target_badge.setObjectName("statusBadgeRed")
                self.live_hud_icon.setText("[ERROR]")
                self.live_action_label.setText("Error occurred during automation. Check error report.")
                self.live_action_label.setStyleSheet("color: #f85149; font-weight: bold; font-size: 12px;")

        self.target_badge.style().unpolish(self.target_badge)
        self.target_badge.style().polish(self.target_badge)

        self.target_badge.style().unpolish(self.target_badge)
        self.target_badge.style().polish(self.target_badge)
