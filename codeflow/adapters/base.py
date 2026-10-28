"""
Keyboard Adapter Interface and Text Entry Modes for CodeFlow Studio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class TextEntryMode(Enum):
    """Supported keyboard text-entry automation modes."""
    WIN32_PHYSICAL = "Physical Keystrokes (Shift+Key - Real Keyboard Emulation)"
    WIN32_UNICODE = "Direct Unicode (Win32 SendInput - Layout Independent)"
    PYAUTOGUI = "Standard Keystrokes (PyAutoGUI)"
    CLIPBOARD_LINE = "Line-by-Line Streaming (Clipboard Paced)"
    MOCK = "Simulated Mock (Testing & Offscreen)"


class BaseKeyboardAdapter(ABC):
    """
    Abstract interface decoupling source text and engine from OS-specific keyboard APIs.
    """

    @abstractmethod
    def type_char(self, char: str) -> None:
        """Type a single character."""
        pass

    @abstractmethod
    def type_newline(self) -> None:
        """Type a line break (Enter/Return)."""
        pass

    @abstractmethod
    def type_tab(self) -> None:
        """Type a horizontal tab character."""
        pass

    @abstractmethod
    def type_backspace(self) -> None:
        """Type backspace."""
        pass

    @abstractmethod
    def paste_text(self, text: str) -> None:
        """Paste text chunk directly."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this adapter is functional in current environment."""
        pass
