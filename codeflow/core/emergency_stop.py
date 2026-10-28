"""
Emergency Stop and Global Cancellation Subsystem for CodeFlow Studio.

Monitors global failsafe keys (e.g., ESC, F8) and mouse screen-corner movements
to immediately abort any running automation run.
"""

from __future__ import annotations

import sys
import threading
import time
from typing import Callable, List, Optional

from codeflow.core.logger import CodeFlowLogger

# Win32 Virtual Key Codes
VK_ESCAPE = 0x1B
VK_F8 = 0x77
VK_PAUSE = 0x13


class EmergencyStopManager:
    """
    Background safety listener detecting emergency cancellation signals.
    """

    def __init__(self, key_name: str = "Escape"):
        self._logger = CodeFlowLogger.get_logger()
        self._key_name = key_name
        self._vk_code = VK_F8 if key_name.lower() == "f8" else VK_ESCAPE
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._callbacks: List[Callable[[], None]] = []
        self._win32_available = sys.platform == "win32"

    @property
    def stop_event(self) -> threading.Event:
        return self._stop_event

    def is_stop_requested(self) -> bool:
        return self._stop_event.is_set()

    def set_key(self, key_name: str) -> None:
        self._key_name = key_name
        self._vk_code = VK_F8 if key_name.lower() == "f8" else VK_ESCAPE

    def add_stop_callback(self, callback: Callable[[], None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def trigger_stop(self) -> None:
        """Manually trigger emergency cancellation."""
        if not self._stop_event.is_set():
            self._logger.info("Emergency stop triggered.")
            self._stop_event.set()
            for cb in list(self._callbacks):
                try:
                    cb()
                except Exception as e:
                    self._logger.debug(f"Error in emergency stop callback: {e}")

    def reset(self) -> None:
        self._stop_event.clear()

    def start_monitoring(self) -> None:
        """Begin listening for global emergency hotkey."""
        self.reset()
        if self._running or not self._win32_available:
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True, name="EmergencyStopMonitor")
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop background hotkey polling."""
        self._running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=0.3)
        self._monitor_thread = None

    def _monitor_loop(self) -> None:
        import ctypes
        user32 = ctypes.windll.user32
        get_async_key_state = user32.GetAsyncKeyState

        while self._running:
            try:
                # Check emergency stop key
                # High bit set means key is currently down (0x8000)
                if get_async_key_state(self._vk_code) & 0x8000:
                    self.trigger_stop()
                    break

                # Also monitor corner failsafe if pyautogui is present
                try:
                    import pyautogui
                    pos = pyautogui.position()
                    if pos.x == 0 and pos.y == 0:
                        self._logger.info("Mouse corner failsafe triggered.")
                        self.trigger_stop()
                        break
                except Exception:
                    pass

                time.sleep(0.04)  # 25 Hz poll rate
            except Exception:
                time.sleep(0.1)
