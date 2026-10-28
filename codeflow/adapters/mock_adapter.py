"""
Mock Keyboard Adapter for Testing and Verification.

Captures all sent characters, newlines, tabs, and pastes in memory without
invoking actual OS SendInput or keyboard events.
"""

from __future__ import annotations

from typing import List
from codeflow.adapters.base import BaseKeyboardAdapter


class MockKeyboardAdapter(BaseKeyboardAdapter):
    """
    In-memory recorder for verifying keyboard typing streams.
    """

    def __init__(self):
        self.recorded_events: List[str] = []
        self.typed_buffer: List[str] = []

    def is_available(self) -> bool:
        return True

    def type_char(self, char: str) -> None:
        self.recorded_events.append(f"CHAR:{char}")
        self.typed_buffer.append(char)

    def type_newline(self) -> None:
        self.recorded_events.append("KEY:NEWLINE")
        self.typed_buffer.append("\n")

    def type_tab(self) -> None:
        self.recorded_events.append("KEY:TAB")
        self.typed_buffer.append("\t")

    def type_backspace(self) -> None:
        self.recorded_events.append("KEY:BACKSPACE")
        if self.typed_buffer:
            self.typed_buffer.pop()

    def paste_text(self, text: str) -> None:
        self.recorded_events.append(f"PASTE:{text}")
        self.typed_buffer.append(text)

    def get_typed_text(self) -> str:
        """Return the accumulated string that was typed."""
        return "".join(self.typed_buffer)

    def clear(self) -> None:
        self.recorded_events.clear()
        self.typed_buffer.clear()
