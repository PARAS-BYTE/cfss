"""
PyAutoGUI Keyboard Adapter for CodeFlow Studio.

Fallback and secondary keyboard automation adapter utilizing PyAutoGUI.
"""

from __future__ import annotations

import time
from typing import Optional

from codeflow.adapters.base import BaseKeyboardAdapter
from codeflow.core.logger import CodeFlowLogger


class PyAutoGUIAdapter(BaseKeyboardAdapter):
    """
    Keyboard automation via PyAutoGUI.
    """

    def __init__(self):
        self._logger = CodeFlowLogger.get_logger()
        self._available = False
        try:
            import pyautogui
            # Disable pyautogui pause to control pacing manually
            pyautogui.PAUSE = 0.001
            self._pyautogui = pyautogui
            self._available = True
        except ImportError:
            self._logger.warning("PyAutoGUI not installed or not available.")

    def is_available(self) -> bool:
        return self._available

    def type_char(self, char: str) -> None:
        if not self._available or not char:
            return
        try:
            if char == "\n" or char == "\r":
                self.type_newline()
            elif char == "\t":
                self.type_tab()
            else:
                self._pyautogui.write(char)
        except Exception as e:
            self._logger.debug(f"PyAutoGUI write error for char {repr(char)}: {e}")

    def type_newline(self) -> None:
        if not self._available:
            return
        try:
            self._pyautogui.press("enter")
        except Exception as e:
            self._logger.debug(f"PyAutoGUI press enter error: {e}")

    def type_tab(self) -> None:
        if not self._available:
            return
        try:
            self._pyautogui.press("tab")
        except Exception as e:
            self._logger.debug(f"PyAutoGUI press tab error: {e}")

    def type_backspace(self) -> None:
        if not self._available:
            return
        try:
            self._pyautogui.press("backspace")
        except Exception as e:
            self._logger.debug(f"PyAutoGUI press backspace error: {e}")

    def paste_text(self, text: str) -> None:
        if not self._available:
            return
        try:
            import pyperclip
            pyperclip.copy(text)
            time.sleep(0.01)
            self._pyautogui.hotkey("ctrl", "v")
        except Exception as e:
            self._logger.debug(f"PyAutoGUI paste error: {e}")
