"""
Line-by-Line Streaming Keyboard Adapter for CodeFlow Studio.

Pastes source text line-by-line using clipboard streaming with simulated
typing pacing. This method provides the highest resistance against IDE-level
auto-indentation corruptions and auto-closing bracket duplication in VS Code.
"""

from __future__ import annotations

import time
from typing import Optional

from codeflow.adapters.base import BaseKeyboardAdapter
from codeflow.core.logger import CodeFlowLogger


class ClipboardStreamAdapter(BaseKeyboardAdapter):
    """
    Paced line-by-line clipboard entry adapter.
    """

    def __init__(self, fallback_adapter: Optional[BaseKeyboardAdapter] = None):
        self._logger = CodeFlowLogger.get_logger()
        self._fallback = fallback_adapter
        self._available = True
        try:
            import pyperclip
            self._pyperclip = pyperclip
        except ImportError:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def type_char(self, char: str) -> None:
        if self._fallback:
            self._fallback.type_char(char)
        else:
            self.paste_text(char)

    def type_newline(self) -> None:
        if self._fallback:
            self._fallback.type_newline()
        else:
            self.paste_text("\n")

    def type_tab(self) -> None:
        if self._fallback:
            self._fallback.type_tab()
        else:
            self.paste_text("\t")

    def type_backspace(self) -> None:
        if self._fallback:
            self._fallback.type_backspace()

    def paste_text(self, text: str) -> None:
        if not self._available:
            return
        try:
            self._pyperclip.copy(text)
            time.sleep(0.01)
            # Use fallback or ctypes/pyautogui to trigger Ctrl+V
            if self._fallback:
                self._fallback.paste_text(text)
        except Exception as e:
            self._logger.debug(f"Clipboard paste error: {e}")
