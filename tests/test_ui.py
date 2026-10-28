"""
Tests for UI components (Editor, SettingsPanel, StatusPanel, MainWindow, ComparatorDialog).
Runs headlessly via QT_QPA_PLATFORM=offscreen.
"""

import os
import pytest

# Ensure offscreen platform before importing QApplication
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from codeflow.core.session import SessionState
from codeflow.ui.editor import CodeEditor
from codeflow.ui.highlighter import CodeHighlighter
from codeflow.ui.line_numbers import LineNumberArea
from codeflow.ui.settings_panel import SettingsPanel
from codeflow.ui.status_panel import StatusPanel
from codeflow.ui.comparator_dialog import TextComparatorDialog
from codeflow.ui.main_window import CodeFlowMainWindow
from codeflow.windows.window_detector import WindowDetector, WindowInfo


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestUIComponents:
    def test_code_editor_loading_and_preservation(self, qapp):
        editor = CodeEditor()
        code = "def test_fn():\n\t# Tab line\n    # 4 spaces line\n\n\treturn True\n"
        editor.load_code(code, language="python")

        assert editor.toPlainText() == code
        assert editor.source_model.raw_text == code
        assert editor.source_model.language == "python"
        assert editor.line_number_area_width() > 0

        # Change language
        editor.set_language("javascript")
        assert editor.source_model.language == "javascript"

    def test_settings_panel_controls(self, qapp):
        detector = WindowDetector()
        mock_win = WindowInfo(10, "Test Editor", 200, "editor.exe")
        detector.set_mock_mode([mock_win], foreground=mock_win)

        panel = SettingsPanel(detector)
        # Test slider update
        panel.target_wpm_slider.setValue(45)
        assert panel.settings.target_wpm == 45
        assert panel.settings.typing_rate_cpm == 225

        panel.pause_slider.setValue(350)
        assert panel.settings.newline_pause_ms == 350

        panel.min_wpm_slider.setValue(30)
        assert panel.settings.wpm_min == 30

    def test_status_panel_states(self, qapp):
        status = StatusPanel()

        # IDLE
        status.update_state(SessionState.IDLE)
        assert status.start_btn.isEnabled() is True
        assert status.pause_btn.isEnabled() is False
        assert status.stop_btn.isEnabled() is False

        # RUNNING
        status.update_state(SessionState.RUNNING)
        assert status.start_btn.isEnabled() is False
        assert status.pause_btn.isEnabled() is True
        assert status.stop_btn.isEnabled() is True

        # PAUSED
        status.update_state(SessionState.PAUSED)
        assert status.resume_btn.isHidden() is False
        assert status.resume_btn.isEnabled() is True
        assert status.pause_btn.isHidden() is True

        # Progress
        status.update_progress(50, 100, 3, 6, 5.0, 5.0, 300.0)
        assert status.progress_bar.value() == 50

        # Focus warning
        status.show_focus_warning("Unintended Window")
        assert status.warning_banner.isHidden() is False
        status.hide_focus_warning()
        assert status.warning_banner.isHidden() is True

        # Mouse action & inspection
        status.set_mouse_action("Scrolling up 3 ticks")
        assert "Scrolling up 3 ticks" in status.live_action_label.text()
        status.set_inspection_scrolling(True)
        assert status.inspection_banner.isHidden() is False
        status.set_inspection_scrolling(False)
        assert status.inspection_banner.isHidden() is True

    def test_comparator_dialog_run(self, qapp):
        source = "const x = 42;\n"
        dlg = TextComparatorDialog(source_text=source)
        dlg.result_editor.setPlainText(source)
        dlg.run_comparison()
        assert "100% EXACT MATCH" in dlg.status_badge.text()

        # With discrepancy
        dlg.result_editor.setPlainText("const x = 99;\n")
        dlg.run_comparison()
        assert "DISCREPANCIES DETECTED" in dlg.status_badge.text()

    def test_main_window_instantiation(self, qapp):
        win = CodeFlowMainWindow()
        assert win.editor is not None
        assert win.settings_panel is not None
        assert win.status_panel is not None
        assert "CodeFlow Studio" in win.windowTitle()
