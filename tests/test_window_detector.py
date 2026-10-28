"""
Tests for WindowDetector and WindowInfo.
"""

import pytest
from codeflow.windows.window_detector import WindowDetector, WindowInfo


class TestWindowDetector:
    def test_window_info_properties(self):
        w = WindowInfo(
            hwnd=12345,
            title="app.py - Visual Studio Code",
            process_id=5678,
            process_name="Code.exe",
            is_vscode=True,
            is_foreground=True,
        )
        assert w.is_vscode is True
        assert w.is_foreground is True
        assert "Code.exe" in w.display_name()

    def test_mock_detection(self):
        detector = WindowDetector()

        vsc_win = WindowInfo(101, "main.py - Visual Studio Code", 1001, "Code.exe", is_vscode=True)
        notepad_win = WindowInfo(102, "Untitled - Notepad", 1002, "notepad.exe", is_vscode=False)
        codeflow_win = WindowInfo(103, "CodeFlow Studio", 1003, "python.exe", is_vscode=False)

        detector.set_mock_mode(
            windows=[vsc_win, notepad_win, codeflow_win],
            foreground=vsc_win,
        )

        # Check foreground
        fg = detector.get_foreground_window()
        assert fg is not None
        assert fg.hwnd == 101

        # Check list windows
        wins = detector.list_windows()
        assert len(wins) == 3

        # Check VS Code finder
        vsc_list = detector.find_vscode_windows()
        assert len(vsc_list) == 1
        assert vsc_list[0].hwnd == 101

        # Check target focused: matches
        focused, current = detector.is_target_focused(target_hwnd=101)
        assert focused is True
        assert current.hwnd == 101

        # Check target focused: mismatch (expecting 102, but 101 is foreground)
        focused, current = detector.is_target_focused(target_hwnd=102)
        assert focused is False

        # Check title matching
        focused, _ = detector.is_target_focused(target_title="Visual Studio Code")
        assert focused is True

        focused, _ = detector.is_target_focused(target_title="Notepad")
        assert focused is False

        # Check allow_any
        focused, _ = detector.is_target_focused(allow_any=True)
        assert focused is True

        # Switch foreground to CodeFlow itself
        detector.set_mock_mode([vsc_win, notepad_win, codeflow_win], foreground=codeflow_win)
        focused, _ = detector.is_target_focused(allow_any=True)
        assert focused is False  # CodeFlow itself should not be considered valid target
