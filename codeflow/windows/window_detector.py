"""
Target Window Detection and Focus Monitoring for CodeFlow Studio.

Tracks active Windows desktop applications, identifies VS Code windows,
and detects focus transitions to pause/abort automation if focus departs the target.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from codeflow.core.logger import CodeFlowLogger


@dataclass
class WindowInfo:
    """Information regarding a desktop window."""
    hwnd: int
    title: str
    process_id: int
    process_name: str
    is_vscode: bool = False
    is_foreground: bool = False

    def display_name(self) -> str:
        """Formatted string for UI dropdowns and labels."""
        proc = f" [{self.process_name}]" if self.process_name else ""
        return f"{self.title}{proc}"


class WindowDetector:
    """
    Win32 Window enumeration and focus state interrogator.
    """

    def __init__(self):
        self._logger = CodeFlowLogger.get_logger()
        self._win32_available = sys.platform == "win32"
        self._mock_foreground: Optional[WindowInfo] = None
        self._mock_windows: List[WindowInfo] = []

    def set_mock_mode(self, windows: List[WindowInfo], foreground: Optional[WindowInfo]) -> None:
        """Enable simulated windows for offline/testing environments."""
        self._mock_windows = list(windows)
        self._mock_foreground = foreground

    def _get_process_name(self, pid: int) -> str:
        """Retrieve executable name from process ID."""
        if pid <= 0:
            return ""
        try:
            import psutil
            return psutil.Process(pid).name()
        except Exception:
            return ""

    def get_foreground_window(self) -> Optional[WindowInfo]:
        """Fetch current foreground window."""
        if self._mock_foreground is not None:
            return self._mock_foreground

        if not self._win32_available:
            return None

        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            if not hwnd or hwnd == 0:
                return None

            title = win32gui.GetWindowText(hwnd).strip()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc_name = self._get_process_name(pid)
            is_vsc = "visual studio code" in title.lower() or "code.exe" in proc_name.lower()

            return WindowInfo(
                hwnd=hwnd,
                title=title,
                process_id=pid,
                process_name=proc_name,
                is_vscode=is_vsc,
                is_foreground=True,
            )
        except Exception as e:
            self._logger.debug(f"Error fetching foreground window: {e}")
            return None

    def list_windows(self, filter_empty: bool = True) -> List[WindowInfo]:
        """Enumerate top-level desktop windows."""
        if self._mock_windows:
            return list(self._mock_windows)

        if not self._win32_available:
            return []

        results: List[WindowInfo] = []
        try:
            import win32gui
            import win32process

            fg_hwnd = win32gui.GetForegroundWindow()

            def enum_proc(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).strip()
                    if filter_empty and not title:
                        return True
                    # Filter out tooltips / system invisible popups
                    if title in ("Program Manager", "Settings", "Windows Input Experience"):
                        return True

                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc_name = self._get_process_name(pid)
                    is_vsc = "visual studio code" in title.lower() or "code.exe" in proc_name.lower()

                    results.append(WindowInfo(
                        hwnd=hwnd,
                        title=title,
                        process_id=pid,
                        process_name=proc_name,
                        is_vscode=is_vsc,
                        is_foreground=(hwnd == fg_hwnd),
                    ))
                return True

            win32gui.EnumWindows(enum_proc, None)
        except Exception as e:
            self._logger.debug(f"Error enumerating windows: {e}")

        return results

    def find_vscode_windows(self) -> List[WindowInfo]:
        """Filter active windows for Visual Studio Code instances."""
        windows = self.list_windows(filter_empty=True)
        return [w for w in windows if w.is_vscode]

    def is_target_focused(
        self,
        target_hwnd: Optional[int] = None,
        target_title: Optional[str] = None,
        allow_any: bool = False,
    ) -> Tuple[bool, Optional[WindowInfo]]:
        """
        Verify whether the desired target application holds the active keyboard focus.
        
        Args:
            target_hwnd: Specific HWND handle of the expected window.
            target_title: Substring of title to match if HWND is omitted.
            allow_any: If True, any non-CodeFlow window is considered valid.
            
        Returns:
            Tuple of (is_focused: bool, current_foreground: Optional[WindowInfo])
        """
        fg = self.get_foreground_window()
        if fg is None:
            return False, None

        if allow_any:
            # Valid as long as it's not CodeFlow itself
            is_valid = "codeflow" not in fg.title.lower()
            return is_valid, fg

        if target_hwnd is not None and target_hwnd > 0:
            return (fg.hwnd == target_hwnd), fg

        if target_title:
            return (target_title.lower() in fg.title.lower()), fg

        return True, fg

    def bring_to_foreground(self, hwnd: int) -> bool:
        """Attempt to activate and bring window to front."""
        if not self._win32_available or hwnd <= 0:
            return False
        try:
            import win32gui
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            self._logger.debug(f"Failed to bring hwnd {hwnd} to foreground: {e}")
            return False
