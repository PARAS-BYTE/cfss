"""
Direct Win32 SendInput Unicode Keyboard Adapter for CodeFlow Studio.

Sends exact Unicode code points directly to the focused target window via
Windows user32 SendInput API using KEYEVENTF_UNICODE.

Advantages:
- Does not depend on active keyboard layout (QWERTY, AZERTY, QWERTZ, Dvorak).
- Does not manipulate Shift/Alt/Ctrl keys, preventing accidental editor shortcut triggers.
- Fully supports all Unicode characters, symbols, quotes, backticks, brackets, and emojis.
"""

from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes
from typing import List, Optional

from codeflow.adapters.base import BaseKeyboardAdapter
from codeflow.core.logger import CodeFlowLogger


# Win32 Constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_BACK = 0x08
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_V = 0x56

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_UNION),
    ]


LPINPUT = ctypes.POINTER(INPUT)


class Win32SendInputAdapter(BaseKeyboardAdapter):
    """
    Precision keyboard adapter using Win32 SendInput.
    Supports physical key simulation (Shift+Key emulation via VkKeyScanW)
    with seamless fallback to KEYEVENTF_UNICODE for non-keyboard glyphs.
    """

    def __init__(self, simulate_physical_keys: bool = True, key_hold_time_ms: int = 15):
        self._logger = CodeFlowLogger.get_logger()
        self.simulate_physical_keys = simulate_physical_keys
        self.key_hold_time_ms = key_hold_time_ms
        self._available = sys.platform == "win32"
        if self._available:
            try:
                self._user32 = ctypes.windll.user32
                self._send_input = self._user32.SendInput
                self._send_input.argtypes = [wintypes.UINT, LPINPUT, ctypes.c_int]
                self._send_input.restype = wintypes.UINT
                self._vk_key_scan = self._user32.VkKeyScanW
                self._vk_key_scan.argtypes = [wintypes.WCHAR]
                self._vk_key_scan.restype = ctypes.c_short
            except Exception as e:
                self._logger.warning(f"Failed to bind Win32 SendInput: {e}")
                self._available = False

    def is_available(self) -> bool:
        return self._available

    def _send_inputs(self, inputs: List[INPUT]) -> int:
        if not self._available:
            return 0
        n = len(inputs)
        array_type = INPUT * n
        input_array = array_type(*inputs)
        sent = self._send_input(n, input_array, ctypes.sizeof(INPUT))
        return sent

    def _make_vk_input(self, vk: int, keyup: bool = False) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        flags = KEYEVENTF_KEYUP if keyup else 0
        inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
        return inp

    def _make_unicode_input(self, char_code: int, keyup: bool = False) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        flags = KEYEVENTF_UNICODE
        if keyup:
            flags |= KEYEVENTF_KEYUP
        inp.u.ki = KEYBDINPUT(wVk=0, wScan=char_code, dwFlags=flags, time=0, dwExtraInfo=0)
        return inp

    def type_char(self, char: str) -> None:
        """
        Type a character using physical keystrokes (Shift+Key) if possible,
        falling back to Win32 SendInput Unicode for complex codepoints.
        """
        if not self._available or not char:
            return

        if char == "\n":
            self.type_newline()
            return
        if char == "\r":
            self.type_newline()
            return
        if char == "\t":
            self.type_tab()
            return

        # Physical Key Simulation: emulate hardware Shift+Keypress (e.g. Shift+a for 'A')
        if self.simulate_physical_keys and hasattr(self, "_vk_key_scan"):
            try:
                scan = self._vk_key_scan(char)
                if scan != -1 and scan != -32768:
                    vk = scan & 0xFF
                    shift_state = (scan >> 8) & 0xFF
                    use_shift = bool(shift_state & 0x01)
                    use_ctrl = bool(shift_state & 0x02)
                    use_alt = bool(shift_state & 0x04)

                    down_inputs: List[INPUT] = []
                    up_inputs: List[INPUT] = []

                    if use_shift:
                        down_inputs.append(self._make_vk_input(VK_SHIFT, keyup=False))
                        up_inputs.insert(0, self._make_vk_input(VK_SHIFT, keyup=True))
                    if use_ctrl:
                        down_inputs.append(self._make_vk_input(VK_CONTROL, keyup=False))
                        up_inputs.insert(0, self._make_vk_input(VK_CONTROL, keyup=True))
                    if use_alt:
                        down_inputs.append(self._make_vk_input(VK_MENU, keyup=False))
                        up_inputs.insert(0, self._make_vk_input(VK_MENU, keyup=True))

                    down_inputs.append(self._make_vk_input(vk, keyup=False))
                    up_inputs.insert(0, self._make_vk_input(vk, keyup=True))

                    if self.key_hold_time_ms > 0:
                        self._send_inputs(down_inputs)
                        time.sleep(self.key_hold_time_ms / 1000.0)
                        self._send_inputs(up_inputs)
                    else:
                        self._send_inputs(down_inputs + up_inputs)
                    return
            except Exception as e:
                self._logger.debug(f"VkKeyScan fallback to unicode: {e}")

        # Unicode codepoint fallback
        code_point = ord(char)
        inputs = []
        if code_point <= 0xFFFF:
            inputs.append(self._make_unicode_input(code_point, keyup=False))
            inputs.append(self._make_unicode_input(code_point, keyup=True))
        else:
            # UTF-16 surrogate pair for SMP characters (emojis, etc.)
            cp = code_point - 0x10000
            high_surrogate = 0xD800 + (cp >> 10)
            low_surrogate = 0xDC00 + (cp & 0x3FF)
            inputs.append(self._make_unicode_input(high_surrogate, keyup=False))
            inputs.append(self._make_unicode_input(high_surrogate, keyup=True))
            inputs.append(self._make_unicode_input(low_surrogate, keyup=False))
            inputs.append(self._make_unicode_input(low_surrogate, keyup=True))

        self._send_inputs(inputs)

    def type_newline(self) -> None:
        """Send VK_RETURN (Enter) key event."""
        if not self._available:
            return
        inputs = [
            self._make_vk_input(VK_RETURN, keyup=False),
            self._make_vk_input(VK_RETURN, keyup=True),
        ]
        self._send_inputs(inputs)

    def type_tab(self) -> None:
        """Send VK_TAB key event."""
        if not self._available:
            return
        inputs = [
            self._make_vk_input(VK_TAB, keyup=False),
            self._make_vk_input(VK_TAB, keyup=True),
        ]
        self._send_inputs(inputs)

    def type_backspace(self) -> None:
        """Send VK_BACK key event."""
        if not self._available:
            return
        inputs = [
            self._make_vk_input(VK_BACK, keyup=False),
            self._make_vk_input(VK_BACK, keyup=True),
        ]
        self._send_inputs(inputs)

    def paste_text(self, text: str) -> None:
        """Paste text via clipboard and Ctrl+V."""
        try:
            import pyperclip
            pyperclip.copy(text)
            time.sleep(0.01)
            # Send Ctrl+V
            inputs = [
                self._make_vk_input(VK_CONTROL, keyup=False),
                self._make_vk_input(VK_V, keyup=False),
                self._make_vk_input(VK_V, keyup=True),
                self._make_vk_input(VK_CONTROL, keyup=True),
            ]
            self._send_inputs(inputs)
        except Exception as e:
            self._logger.warning(f"Paste failed: {e}")
