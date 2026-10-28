"""
Tests for Keyboard Adapters (Mock, Win32, PyAutoGUI, Clipboard).
"""

import pytest
from codeflow.adapters.base import TextEntryMode
from codeflow.adapters.mock_adapter import MockKeyboardAdapter
from codeflow.adapters.win32_adapter import Win32SendInputAdapter
from codeflow.adapters.pyautogui_adapter import PyAutoGUIAdapter
from codeflow.adapters.clipboard_adapter import ClipboardStreamAdapter


class TestKeyboardAdapters:
    def test_mock_adapter_character_stream(self):
        adapter = MockKeyboardAdapter()
        assert adapter.is_available() is True

        adapter.type_char("d")
        adapter.type_char("e")
        adapter.type_char("f")
        adapter.type_char(" ")
        adapter.type_tab()
        adapter.type_newline()
        adapter.type_char("x")
        adapter.type_backspace()
        adapter.type_char("y")

        assert adapter.get_typed_text() == "def \t\ny"
        assert "KEY:NEWLINE" in adapter.recorded_events
        assert "KEY:TAB" in adapter.recorded_events
        assert "KEY:BACKSPACE" in adapter.recorded_events

    def test_mock_adapter_paste(self):
        adapter = MockKeyboardAdapter()
        chunk = "    total = sum(items)\n"
        adapter.paste_text(chunk)
        assert adapter.get_typed_text() == chunk
        assert f"PASTE:{chunk}" in adapter.recorded_events

    def test_win32_adapter_initialization(self):
        adapter = Win32SendInputAdapter()
        # In Windows environment, should be available
        assert isinstance(adapter.is_available(), bool)

    def test_win32_physical_key_simulation(self):
        adapter = Win32SendInputAdapter(simulate_physical_keys=True, key_hold_time_ms=0)
        if not adapter.is_available():
            pytest.skip("Win32 SendInput not available on this platform")

        captured_batches = []
        adapter._send_inputs = lambda inputs: captured_batches.append(inputs)

        # 1. Uppercase 'A' should emit Shift + A
        adapter.type_char("A")
        assert len(captured_batches) > 0
        all_inputs = [inp for batch in captured_batches for inp in batch]
        vks = [inp.u.ki.wVk for inp in all_inputs]
        # VK_SHIFT is 0x10, VK for 'A' is 0x41
        assert 0x10 in vks
        assert 0x41 in vks

        # 2. Lowercase 'a' should not emit Shift
        captured_batches.clear()
        adapter.type_char("a")
        all_inputs = [inp for batch in captured_batches for inp in batch]
        vks = [inp.u.ki.wVk for inp in all_inputs]
        assert 0x10 not in vks
        assert 0x41 in vks

        # 3. Unicode fallback for characters not in standard keyboard layout
        captured_batches.clear()
        adapter.type_char("中")
        all_inputs = [inp for batch in captured_batches for inp in batch]
        flags = [inp.u.ki.dwFlags for inp in all_inputs]
        assert any(f & 0x0004 for f in flags)

    def test_pyautogui_adapter_initialization(self):
        adapter = PyAutoGUIAdapter()
        assert isinstance(adapter.is_available(), bool)

    def test_clipboard_stream_adapter(self):
        mock = MockKeyboardAdapter()
        clip_adapter = ClipboardStreamAdapter(fallback_adapter=mock)
        assert clip_adapter.is_available() is True
        clip_adapter.type_char("a")
        assert mock.get_typed_text() == "a"
