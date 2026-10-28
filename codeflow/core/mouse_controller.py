"""
Demonstration Mouse Controller and Inspection Scroller for CodeFlow Studio.

Provides gentle, realistic mouse movement during coding presentations and tutorials.
Includes in-between inspection scrolling:
- Scrolls upward a little bit
- Hovers randomly across code lines as if reading/reviewing
- Scrolls back down to the cursor position
- STOPS TYPING COMPLETELY while mouse scrolling and hovering are active!
Immediately halts automated movement if physical user mouse activity is detected.
"""

from __future__ import annotations

import math
import random
import sys
import threading
import time
from typing import Callable, Optional

from codeflow.core.logger import CodeFlowLogger


class DemoMouseController:
    """
    Subtle demonstration cursor animator with inspection scrolling, random hovering,
    and immediate user-override cancellation.
    """

    USER_INTERRUPT_THRESHOLD = 15.0  # pixels

    def __init__(
        self,
        enabled: bool = True,
        intensity: str = "subtle",
        interval_seconds: float = 4.0,
        enable_inspection_scroll: bool = True,
        enable_random_hovering: bool = True,
        inspection_scroll_distance: int = 3,
        inspection_pause_seconds: float = 1.8,
        on_user_override: Optional[Callable[[], None]] = None,
        on_mouse_action: Optional[Callable[[str], None]] = None,
    ):
        self._logger = CodeFlowLogger.get_logger()
        self.enabled = enabled
        self.intensity = intensity
        self.interval_seconds = interval_seconds
        self.enable_inspection_scroll = enable_inspection_scroll
        self.enable_random_hovering = enable_random_hovering
        self.inspection_scroll_distance = inspection_scroll_distance
        self.inspection_pause_seconds = inspection_pause_seconds
        self.on_user_override = on_user_override
        self.on_mouse_action = on_mouse_action

        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._is_scrolling = False
        self._thread: Optional[threading.Thread] = None
        self._expected_x = 0
        self._expected_y = 0
        self._user_intervened = False

        try:
            import pyautogui
            pyautogui.FAILSAFE = False
        except Exception:
            pass

    def _notify_action(self, action_msg: str) -> None:
        if self.on_mouse_action:
            try:
                self.on_mouse_action(action_msg)
            except Exception:
                pass

    @property
    def user_intervened(self) -> bool:
        return self._user_intervened

    @property
    def is_scrolling(self) -> bool:
        return self._is_scrolling

    def start(self) -> None:
        """Start the background mouse motion loop."""
        if not self.enabled or (self._thread and self._thread.is_alive()):
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._user_intervened = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="DemoMouseController")
        self._thread.start()

    def stop(self) -> None:
        """Stop background mouse loop."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.4)
        self._thread = None

    def pause(self) -> None:
        self._pause_event.set()

    def resume(self) -> None:
        self._pause_event.clear()

    def _get_current_pos(self) -> tuple[int, int]:
        try:
            import pyautogui
            pos = pyautogui.position()
            return pos.x, pos.y
        except Exception:
            return 0, 0

    def _check_user_interrupt(self) -> bool:
        """Return True if user moved mouse manually beyond threshold."""
        cur_x, cur_y = self._get_current_pos()
        dist = math.hypot(cur_x - self._expected_x, cur_y - self._expected_y)
        if dist > self.USER_INTERRUPT_THRESHOLD:
            self._user_intervened = True
            self._logger.info(f"User manual mouse activity detected (drift={dist:.1f}px). Cancelling motion.")
            if self.on_user_override:
                try:
                    self.on_user_override()
                except Exception:
                    pass
            return True
        return False

    def _perform_smooth_move(self, start_x: int, start_y: int, target_x: int, target_y: int, duration: float) -> bool:
        """
        Interpolate cursor smoothly with easing while checking for user override.
        """
        steps = max(5, int(duration * 40))  # 40 Hz updates
        dt = duration / steps

        try:
            import pyautogui
        except ImportError:
            return False

        for i in range(1, steps + 1):
            if self._stop_event.is_set() or self._pause_event.is_set():
                return False

            if self._check_user_interrupt():
                return False

            t = i / steps
            ease_t = 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

            interp_x = int(start_x + (target_x - start_x) * ease_t)
            interp_y = int(start_y + (target_y - start_y) * ease_t)

            try:
                pyautogui.moveTo(interp_x, interp_y)
                self._expected_x = interp_x
                self._expected_y = interp_y
            except Exception:
                return False

            time.sleep(dt)

        return True

    def _wheel_scroll(self, clicks: int) -> None:
        """Perform mouse wheel scroll ticks (positive = scroll up, negative = scroll down)."""
        if self._user_intervened:
            return
        try:
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, clicks * 120, 0)
            else:
                import pyautogui
                pyautogui.scroll(clicks)
        except Exception as e:
            self._logger.debug(f"Wheel scroll error: {e}")

    def execute_inspection_scroll(
        self,
        distance_ticks: int = 3,
        pause_seconds: float = 1.8,
        enable_hovering: bool = True,
        on_start_scroll: Optional[Callable[[], None]] = None,
        on_finish_scroll: Optional[Callable[[], None]] = None,
    ) -> bool:
        """
        Executes in-between scroll inspection:
        1. Signals typing engine to PAUSE typing.
        2. Smoothly moves mouse upward towards previous code lines.
        3. Scrolls up a little bit.
        4. Randomly hovers cursor across lines (as if reading/checking).
        5. Scrolls back down to cursor point.
        6. Smoothly returns cursor and signals typing engine to RESUME.
        """
        if not self.enabled or self._user_intervened:
            return False

        self._is_scrolling = True
        try:
            # 1. Stop typing
            self._notify_action("Halting typing: Preparing mouse inspection...")
            if on_start_scroll:
                try:
                    on_start_scroll()
                except Exception:
                    pass

            cur_x, cur_y = self._get_current_pos()
            self._expected_x = cur_x
            self._expected_y = cur_y

            # 2. Move cursor upward into code inspection area
            self._notify_action("Moving mouse upward into code inspection area...")
            up_target_x = max(80, cur_x + random.randint(-50, 50))
            up_target_y = max(80, cur_y - random.randint(100, 220))
            self._perform_smooth_move(cur_x, cur_y, up_target_x, up_target_y, duration=0.5)

            if self._user_intervened or self._stop_event.is_set():
                return False

            # 3. Scroll upward a little bit
            self._notify_action(f"Scrolling up {distance_ticks} clicks to inspect previous code...")
            for _ in range(distance_ticks):
                if self._user_intervened or self._stop_event.is_set():
                    break
                self._wheel_scroll(1)
                time.sleep(0.07)

            # 4. Random Hovering across code lines (user requested: 'mouse hovering random hovering')
            if enable_hovering and not self._user_intervened and not self._stop_event.is_set():
                self._notify_action("Hovering cursor gently across code lines to review logic...")
                hover_hops = random.randint(2, 3)
                sub_pause = max(0.3, pause_seconds / hover_hops)
                for _ in range(hover_hops):
                    if self._user_intervened or self._stop_event.is_set():
                        break
                    hx, hy = self._get_current_pos()
                    # Hover over nearby code tokens (gentle 20-60px movements)
                    tx = max(80, hx + random.randint(-45, 45))
                    ty = max(80, hy + random.randint(-25, 25))
                    self._perform_smooth_move(hx, hy, tx, ty, duration=0.35)
                    time.sleep(sub_pause)
            else:
                time.sleep(pause_seconds)

            if self._user_intervened or self._stop_event.is_set():
                return False

            # 5. Scroll back down to return
            self._notify_action(f"Scrolling down {distance_ticks} clicks to return to editor line...")
            for _ in range(distance_ticks):
                if self._user_intervened or self._stop_event.is_set():
                    break
                self._wheel_scroll(-1)
                time.sleep(0.07)

            # 6. Smoothly return cursor to editing point
            self._notify_action("Returning cursor to editing cursor position...")
            final_x, final_y = self._get_current_pos()
            self._perform_smooth_move(final_x, final_y, cur_x, cur_y, duration=0.45)
            time.sleep(0.2)
            self._notify_action("Mouse inspection complete — Resuming typing...")
            return True

        finally:
            self._is_scrolling = False
            # Resume typing
            if on_finish_scroll:
                try:
                    on_finish_scroll()
                except Exception:
                    pass

    def _run_loop(self) -> None:
        """Periodic gentle cursor drift."""
        while not self._stop_event.is_set():
            wait_time = max(1.5, self.interval_seconds + random.uniform(-1.0, 1.0))
            if self._stop_event.wait(wait_time):
                break

            if self._pause_event.is_set() or self._is_scrolling:
                time.sleep(0.1)
                continue

            if self._user_intervened:
                time.sleep(1.0)
                continue

            try:
                cur_x, cur_y = self._get_current_pos()
                self._expected_x = cur_x
                self._expected_y = cur_y

                if self.intensity == "subtle":
                    radius = random.uniform(8, 25)
                    duration = random.uniform(0.6, 1.2)
                elif self.intensity == "moderate":
                    radius = random.uniform(25, 60)
                    duration = random.uniform(0.8, 1.5)
                else:  # active
                    radius = random.uniform(60, 120)
                    duration = random.uniform(1.0, 2.0)

                angle = random.uniform(0, 2 * math.pi)
                target_x = max(50, cur_x + int(radius * math.cos(angle)))
                target_y = max(50, cur_y + int(radius * math.sin(angle)))

                self._perform_smooth_move(cur_x, cur_y, target_x, target_y, duration)

            except Exception as e:
                self._logger.debug(f"Mouse movement loop error: {e}")
                time.sleep(1.0)
