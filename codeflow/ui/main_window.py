"""
Main Window for CodeFlow Studio Desktop Application.

Integrates the Code Editor, Settings Sidebar, Execution Controls, Target Focus
Monitoring, Emergency Stop, and Fidelity Verification into a cohesive,
modern dark-themed desktop interface.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QKeyCombination, QSize, Qt
from PySide6.QtGui import QAction, QCloseEvent, QFont, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from codeflow.adapters.base import BaseKeyboardAdapter, TextEntryMode
from codeflow.adapters.clipboard_adapter import ClipboardStreamAdapter
from codeflow.adapters.pyautogui_adapter import PyAutoGUIAdapter
from codeflow.adapters.win32_adapter import Win32SendInputAdapter
from codeflow.config import TypingSettings
from codeflow.core.emergency_stop import EmergencyStopManager
from codeflow.core.engine import TypingEngine
from codeflow.core.logger import CodeFlowLogger
from codeflow.core.mouse_controller import DemoMouseController
from codeflow.core.session import PauseReason, SessionManager, SessionState
from codeflow.core.source_model import SourceTextModel
from codeflow.core.worker import TypingWorker
from codeflow.ui.comparator_dialog import TextComparatorDialog
from codeflow.ui.editor import CodeEditor
from codeflow.ui.session_dialog import SessionSummaryDialog
from codeflow.ui.settings_panel import SettingsPanel
from codeflow.ui.status_panel import StatusPanel
from codeflow.ui.styles import DARK_THEME_QSS
from codeflow.windows.window_detector import WindowDetector


class CodeFlowMainWindow(QMainWindow):
    """
    Primary desktop window for CodeFlow Studio.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeFlow Studio — Precision Code-Typing Simulator")
        self.resize(1180, 780)
        self.setMinimumSize(850, 600)

        # Apply dark theme
        self.setStyleSheet(DARK_THEME_QSS)

        # Core subsystems
        self.logger = CodeFlowLogger.get_logger()
        self.session_manager = SessionManager()
        self.window_detector = WindowDetector()
        self.emergency_stop = EmergencyStopManager()
        self.mouse_controller = DemoMouseController()

        self.engine = TypingEngine(
            session_manager=self.session_manager,
            window_detector=self.window_detector,
            mouse_controller=self.mouse_controller,
        )
        self.worker = TypingWorker(self.engine)

        self._init_ui()
        self._setup_shortcuts()
        self._bind_signals()

        # Load default starter code
        starter_code = (
            "# Welcome to CodeFlow Studio — Precision Code-Typing Simulator\n"
            "# Configured for realistic coding demos and authorized VS Code entry.\n"
            "\n"
            "def fibonacci_stream(n: int):\n"
            '    """Generate Fibonacci sequence with exact code preservation."""\n'
            "    a, b = 0, 1\n"
            "    for _ in range(n):\n"
            "        yield a\n"
            "        a, b = b, a + b\n"
            "\n"
            "if __name__ == '__main__':\n"
            '    results = list(fibonacci_stream(10))\n'
            '    print(f"Fibonacci sequence: {results}")\n'
        )
        self.editor.load_code(starter_code, language="python")

    def _init_ui(self) -> None:
        # Central Splitter (Editor on left, Settings on right)
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        splitter = QSplitter(Qt.Horizontal)

        # Code Editor
        self.editor = CodeEditor(self)
        splitter.addWidget(self.editor)

        # Settings Sidebar
        self.settings_panel = SettingsPanel(self.window_detector, self)
        self.settings_panel.setFixedWidth(360)
        splitter.addWidget(self.settings_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        main_layout.addWidget(splitter, stretch=1)

        # Bottom Status Panel
        self.status_panel = StatusPanel(self)
        main_layout.addWidget(self.status_panel)

        self.setCentralWidget(central_widget)

        # Menu bar & Toolbars
        self._create_menus()
        self._create_toolbar()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.cursor_stat_label = QLabel("Ln 1, Col 1")
        self.metrics_stat_label = QLabel("0 chars | 0 lines")
        self.lang_stat_label = QLabel("Language: Python")
        self.failsafe_stat_label = QLabel("Failsafe: Esc / F8 to abort")

        self.status_bar.addWidget(self.cursor_stat_label)
        self.status_bar.addWidget(QLabel(" | "))
        self.status_bar.addWidget(self.metrics_stat_label)
        self.status_bar.addWidget(QLabel(" | "))
        self.status_bar.addWidget(self.lang_stat_label)
        self.status_bar.addPermanentWidget(self.failsafe_stat_label)

    def _create_menus(self) -> None:
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_act = QAction("&Open Source File...", self)
        open_act.setShortcut(QKeySequence.Open)
        open_act.triggered.connect(self.editor.open_file_dialog)
        file_menu.addAction(open_act)

        save_act = QAction("&Save File...", self)
        save_act.setShortcut(QKeySequence.Save)
        save_act.triggered.connect(self.editor.save_file_dialog)
        file_menu.addAction(save_act)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        undo_act = QAction("&Undo", self)
        undo_act.setShortcut(QKeySequence.Undo)
        undo_act.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_act)

        redo_act = QAction("&Redo", self)
        redo_act.setShortcut(QKeySequence.Redo)
        redo_act.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_act)

        edit_menu.addSeparator()

        cut_act = QAction("Cu&t", self)
        cut_act.setShortcut(QKeySequence.Cut)
        cut_act.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_act)

        copy_act = QAction("&Copy", self)
        copy_act.setShortcut(QKeySequence.Copy)
        copy_act.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_act)

        paste_act = QAction("&Paste", self)
        paste_act.setShortcut(QKeySequence.Paste)
        paste_act.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_act)

        select_all_act = QAction("Select &All", self)
        select_all_act.setShortcut(QKeySequence.SelectAll)
        select_all_act.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_act)

        edit_menu.addSeparator()

        clear_act = QAction("&Clear Editor", self)
        clear_act.triggered.connect(self.editor.clear_code)
        edit_menu.addAction(clear_act)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        verify_act = QAction("🔍 &Verify Result in Comparator...", self)
        verify_act.setShortcut("Ctrl+T")
        verify_act.triggered.connect(self._open_comparator)
        tools_menu.addAction(verify_act)

        refresh_win_act = QAction("↻ &Refresh Window List", self)
        refresh_win_act.triggered.connect(self.settings_panel.refresh_windows)
        tools_menu.addAction(refresh_win_act)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        guide_act = QAction("&VS Code Setup Guide", self)
        guide_act.triggered.connect(self._show_vscode_guide)
        help_menu.addAction(guide_act)

        about_act = QAction("&About CodeFlow Studio", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main Operations", self)
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        open_btn = toolbar.addAction("OPEN FILE")
        open_btn.triggered.connect(self.editor.open_file_dialog)

        save_btn = toolbar.addAction("SAVE")
        save_btn.triggered.connect(self.editor.save_file_dialog)

        copy_btn = toolbar.addAction("COPY ALL")
        copy_btn.triggered.connect(self.editor.copy_all_code)

        clear_btn = toolbar.addAction("CLEAR")
        clear_btn.triggered.connect(self.editor.clear_code)

        toolbar.addSeparator()

        verify_btn = toolbar.addAction("VERIFY FIDELITY")
        verify_btn.triggered.connect(self._open_comparator)

        toolbar.addSeparator()

        # Quick Samples
        toolbar.addWidget(QLabel(" SAMPLES: "))

        py_btn = QPushButton("PYTHON")
        py_btn.setFixedHeight(24)
        py_btn.clicked.connect(lambda: self._load_example("sample_python.py", "python"))
        toolbar.addWidget(py_btn)

        js_btn = QPushButton("JAVASCRIPT")
        js_btn.setFixedHeight(24)
        js_btn.clicked.connect(lambda: self._load_example("sample_javascript.js", "javascript"))
        toolbar.addWidget(js_btn)

        cpp_btn = QPushButton("C++")
        cpp_btn.setFixedHeight(24)
        cpp_btn.clicked.connect(lambda: self._load_example("sample_cpp.cpp", "cpp"))
        toolbar.addWidget(cpp_btn)

        uni_btn = QPushButton("UNICODE")
        uni_btn.setFixedHeight(24)
        uni_btn.clicked.connect(lambda: self._load_example("sample_unicode.py", "python"))
        toolbar.addWidget(uni_btn)

        toolbar.addSeparator()

        # Language dropdown
        toolbar.addWidget(QLabel(" Language: "))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Python", "JavaScript", "TypeScript", "CPP", "Rust", "Go",
            "HTML", "CSS", "SQL", "JSON", "Plain Text",
        ])
        self.lang_combo.currentTextChanged.connect(self._on_language_changed)
        toolbar.addWidget(self.lang_combo)

    def _setup_shortcuts(self) -> None:
        # F5: Start
        self.start_action = QAction(self)
        self.start_action.setShortcut(QKeySequence("F5"))
        self.start_action.triggered.connect(self._on_start_requested)
        self.addAction(self.start_action)

        # F6: Pause / Resume
        self.pause_resume_action = QAction(self)
        self.pause_resume_action.setShortcut(QKeySequence("F6"))
        self.pause_resume_action.triggered.connect(self._on_pause_resume_toggle)
        self.addAction(self.pause_resume_action)

        # Escape / F7 / F8: Stop
        self.stop_action = QAction(self)
        self.stop_action.setShortcuts([QKeySequence("Escape"), QKeySequence("F7")])
        self.stop_action.triggered.connect(self._on_stop_requested)
        self.addAction(self.stop_action)

    def _bind_signals(self) -> None:
        # Editor signals
        self.editor.cursor_moved.connect(self._on_cursor_moved)
        self.editor.metrics_updated.connect(self._on_metrics_updated)

        # Settings panel
        self.settings_panel.settings_changed.connect(self._on_settings_updated)

        # Status panel button clicks
        self.status_panel.start_clicked.connect(self._on_start_requested)
        self.status_panel.pause_clicked.connect(self._on_pause_requested)
        self.status_panel.resume_clicked.connect(self._on_resume_requested)
        self.status_panel.stop_clicked.connect(self._on_stop_requested)

        # Worker signals (Safe cross-thread execution)
        self.worker.countdown_tick.connect(self._on_countdown_tick)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.focus_warning.connect(self._on_focus_lost)
        self.worker.session_paused.connect(self._on_session_paused)
        self.worker.session_resumed.connect(self._on_session_resumed)
        self.worker.session_stopped.connect(self._on_session_stopped)
        self.worker.session_completed.connect(self._on_session_completed)
        self.worker.error_occurred.connect(self._on_error_occurred)
        self.worker.typo_occurred.connect(self._on_typo_occurred)
        self.worker.inspection_scrolling.connect(self._on_inspection_scrolling)
        self.worker.mouse_action.connect(self._on_mouse_action)

        # Emergency stop global listener hook
        self.emergency_stop.add_stop_callback(self._on_emergency_stop_triggered)

    def _on_cursor_moved(self, line: int, col: int) -> None:
        self.cursor_stat_label.setText(f"Ln {line}, Col {col}")

    def _on_metrics_updated(self, chars: int, lines: int) -> None:
        self.metrics_stat_label.setText(f"{chars} chars | {lines} lines")
        self.settings_panel.update_duration_estimate(chars, lines)

    def _on_language_changed(self, lang_name: str) -> None:
        clean = lang_name.lower().replace(" ", "_")
        self.editor.set_language(clean)
        self.lang_stat_label.setText(f"Language: {lang_name}")

    def _on_settings_updated(self, settings: TypingSettings) -> None:
        # Sync target display in status panel
        self.status_panel.set_target_info(
            settings.target_title,
            is_vscode="visual studio code" in settings.target_title.lower(),
        )
        self.emergency_stop.set_key(settings.emergency_stop_key)
        self.failsafe_stat_label.setText(f"Failsafe: {settings.emergency_stop_key} to abort")

    def _get_active_adapter(self, settings: TypingSettings) -> BaseKeyboardAdapter:
        """Instantiate configured keyboard adapter."""
        if settings.entry_mode == TextEntryMode.WIN32_PHYSICAL:
            win32 = Win32SendInputAdapter(simulate_physical_keys=True, key_hold_time_ms=settings.key_hold_time_ms)
            if win32.is_available():
                return win32
            return PyAutoGUIAdapter()
        elif settings.entry_mode == TextEntryMode.WIN32_UNICODE:
            win32 = Win32SendInputAdapter(simulate_physical_keys=False)
            if win32.is_available():
                return win32
            return PyAutoGUIAdapter()
        elif settings.entry_mode == TextEntryMode.CLIPBOARD_LINE:
            win32 = Win32SendInputAdapter(simulate_physical_keys=settings.simulate_physical_keys, key_hold_time_ms=settings.key_hold_time_ms)
            return ClipboardStreamAdapter(fallback_adapter=win32 if win32.is_available() else PyAutoGUIAdapter())
        elif settings.entry_mode == TextEntryMode.MOCK:
            from codeflow.adapters.mock_adapter import MockKeyboardAdapter
            return MockKeyboardAdapter()
        else:
            return PyAutoGUIAdapter()

    def _on_start_requested(self) -> None:
        """Validate input and initiate typing run."""
        source_model = self.editor.source_model
        if not source_model.raw_text:
            QMessageBox.warning(
                self,
                "No Source Code",
                "Please enter or load some source code in the editor before starting.",
            )
            return

        settings = self.settings_panel.settings

        # Check target window safety
        if not settings.allow_any_target and not settings.target_hwnd:
            ret = QMessageBox.question(
                self,
                "Confirm Target Window",
                "No specific window is selected. CodeFlow will type into whatever window is in focus after countdown.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret != QMessageBox.Yes:
                return

        # Configure mouse motion & inspection scrolls
        self.mouse_controller.enabled = settings.enable_mouse_motion or settings.enable_inspection_scroll
        self.mouse_controller.intensity = settings.mouse_intensity
        self.mouse_controller.interval_seconds = settings.mouse_interval_seconds
        self.mouse_controller.enable_inspection_scroll = settings.enable_inspection_scroll
        self.mouse_controller.enable_random_hovering = settings.enable_random_hovering
        self.mouse_controller.inspection_scroll_distance = settings.inspection_scroll_distance
        self.mouse_controller.inspection_pause_seconds = settings.inspection_pause_seconds

        # Configure and start emergency hotkey monitoring
        self.emergency_stop.start_monitoring()

        # Update status panel
        next_state = SessionState.COUNTDOWN if settings.initial_delay_seconds > 0 else SessionState.RUNNING
        self.status_panel.update_state(next_state)

        adapter = self._get_active_adapter(settings)
        started = self.worker.start_typing(source_model, settings, adapter)
        if not started:
            self.emergency_stop.stop_monitoring()
            self.status_panel.update_state(SessionState.IDLE)
            QMessageBox.critical(self, "Error", "Failed to start typing engine worker.")

    def _on_pause_requested(self) -> None:
        self.worker.pause_typing(PauseReason.USER_MANUAL)

    def _on_resume_requested(self) -> None:
        self.worker.resume_typing()

    def _on_pause_resume_toggle(self) -> None:
        state = self.session_manager.state
        if state == SessionState.RUNNING:
            self._on_pause_requested()
        elif state == SessionState.PAUSED:
            self._on_resume_requested()

    def _on_stop_requested(self) -> None:
        self.worker.stop_typing()
        self.emergency_stop.stop_monitoring()

    def _on_emergency_stop_triggered(self) -> None:
        # Emergency stop thread callback -> invoke worker stop
        self.worker.stop_typing()

    def _on_countdown_tick(self, seconds_left: int) -> None:
        self.status_panel.set_countdown(seconds_left)

    def _on_progress_updated(self, typed: int, total: int, current_line: int, total_lines: int) -> None:
        stats = self.session_manager.stats
        settings = self.settings_panel.settings
        elapsed = stats.elapsed_active_seconds
        eta = stats.estimate_remaining_seconds(settings.typing_rate_cpm)
        cpm = stats.effective_cpm
        self.status_panel.update_progress(typed, total, current_line, total_lines, elapsed, eta, cpm)

    def _on_focus_lost(self, fg_title: str) -> None:
        self.status_panel.show_focus_warning(fg_title)

    def _on_typo_occurred(self, intended: str, typo: str) -> None:
        self.status_panel.flash_typo_notification(intended, typo)

    def _on_inspection_scrolling(self, active: bool) -> None:
        self.status_panel.set_inspection_scrolling(active)

    def _on_mouse_action(self, msg: str) -> None:
        self.status_panel.set_mouse_action(msg)

    def _load_example(self, filename: str, lang: str) -> None:
        """Quickly load one of the built-in sample scripts."""
        example_path = Path.cwd() / "examples" / filename
        if example_path.is_file():
            try:
                model = SourceTextModel.from_file(example_path)
                self.editor.load_code(model.raw_text, language=lang, file_path=str(example_path))
                self.editor.set_language(lang)
            except Exception as e:
                self.logger.warning(f"Failed to load example {filename}: {e}")

    def _on_session_paused(self, reason: str) -> None:
        self.status_panel.update_state(SessionState.PAUSED)

    def _on_session_resumed(self) -> None:
        self.status_panel.update_state(SessionState.RUNNING)

    def _on_session_stopped(self) -> None:
        self.emergency_stop.stop_monitoring()
        self.status_panel.update_state(SessionState.STOPPED)
        self._show_session_summary()

    def _on_session_completed(self) -> None:
        self.emergency_stop.stop_monitoring()
        self.status_panel.update_state(SessionState.COMPLETED)
        self._show_session_summary()

    def _on_error_occurred(self, err_msg: str) -> None:
        self.emergency_stop.stop_monitoring()
        self.status_panel.update_state(SessionState.ERROR)
        QMessageBox.critical(
            self,
            "Automation Error",
            f"An error occurred during automation:\n\n{err_msg}\n\n"
            "Recovery: Verify that the target application is accessible and not running in elevated administrator mode.",
        )

    def _show_session_summary(self) -> None:
        summary = self.session_manager.generate_summary()
        dialog = SessionSummaryDialog(summary, self)
        dialog.verify_requested.connect(self._open_comparator)
        dialog.exec()

    def _open_comparator(self) -> None:
        source_text = self.editor.source_model.raw_text
        dialog = TextComparatorDialog(source_text, self)
        dialog.exec()

    def _show_vscode_guide(self) -> None:
        QMessageBox.information(
            self,
            "VS Code Integration Guide",
            "<h3>VS Code Exact Fidelity Configuration</h3>"
            "<p>To achieve 100% byte-for-byte fidelity in VS Code character typing:</p>"
            "<ul>"
            "<li><b>Auto-Indent</b>: Set <code>\"editor.autoIndent\": \"none\"</code> to prevent double indentation.</li>"
            "<li><b>Auto-Closing Brackets</b>: Set <code>\"editor.autoClosingBrackets\": \"never\"</code>.</li>"
            "<li><b>Auto-Closing Quotes</b>: Set <code>\"editor.autoClosingQuotes\": \"never\"</code>.</li>"
            "<li><b>Alternatively</b>: Use CodeFlow's <b>Line-by-Line Streaming</b> entry mode, which is immune to IDE auto-completion!</li>"
            "</ul>",
        )

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About CodeFlow Studio",
            "<b>CodeFlow Studio v1.0.0</b><br>"
            "Windows Desktop Code-Typing Simulator for coding demonstrations, tutorials, "
            "and authorized UI automation in VS Code.<br><br>"
            "Built with PySide6, Win32 SendInput Unicode, and Python 3.12+."
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Safely stop any ongoing typing before exiting."""
        if self.session_manager.state.is_active():
            ret = QMessageBox.question(
                self,
                "Exit CodeFlow Studio",
                "A typing session is currently active. Stop session and exit?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret == QMessageBox.Yes:
                self.worker.stop_typing()
                self.emergency_stop.stop_monitoring()
                event.accept()
            else:
                event.ignore()
        else:
            self.emergency_stop.stop_monitoring()
            event.accept()
