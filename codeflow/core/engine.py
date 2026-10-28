"""
Core Typing Engine for CodeFlow Studio.

Features:
- Precise 30-45 WPM speed fluctuation (Target 40 WPM).
- Multi-character word slips and multi-backspace auto-corrections.
- Random in-between mouse inspection scrolling and random line hovering (typing pauses during mouse activity).
- Window focus tracking and emergency cancellation.
"""

from __future__ import annotations

import math
import random
import sys
import threading
import time
from typing import Callable, Dict, List, Optional

from codeflow.adapters.base import BaseKeyboardAdapter, TextEntryMode
from codeflow.config import TypingSettings
from codeflow.core.logger import CodeFlowLogger
from codeflow.core.mouse_controller import DemoMouseController
from codeflow.core.session import PauseReason, SessionManager, SessionState
from codeflow.core.source_model import SourceTextModel
from codeflow.windows.window_detector import WindowDetector, WindowInfo


QWERTY_ADJACENT: Dict[str, List[str]] = {
    'a': ['s', 'q', 'z', 'w'],
    'b': ['v', 'g', 'h', 'n'],
    'c': ['x', 'd', 'v', 'f'],
    'd': ['s', 'e', 'r', 'f', 'c', 'x'],
    'e': ['w', 'r', 's', 'd'],
    'f': ['d', 'r', 't', 'g', 'v', 'c'],
    'g': ['f', 't', 'y', 'h', 'b', 'v'],
    'h': ['g', 'y', 'u', 'j', 'n', 'b'],
    'i': ['u', 'o', 'k', 'j'],
    'j': ['h', 'u', 'i', 'k', 'm', 'n'],
    'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p'],
    'm': ['n', 'j', 'k'],
    'n': ['b', 'h', 'j', 'm'],
    'o': ['i', 'p', 'k', 'l'],
    'p': ['o', 'l'],
    'q': ['w', 'a'],
    'r': ['e', 't', 'd', 'f'],
    's': ['a', 'w', 'e', 'd', 'x', 'z'],
    't': ['r', 'y', 'f', 'g'],
    'u': ['y', 'i', 'h', 'j'],
    'v': ['c', 'f', 'g', 'b'],
    'w': ['q', 'e', 'a', 's'],
    'x': ['z', 's', 'd', 'c'],
    'y': ['t', 'u', 'g', 'h'],
    'z': ['a', 's', 'x'],
}


class TypingEngine:
    """
    Cadence engine supporting 30-45 WPM wavy speed, multi-character word typos,
    and inspection scroll & hovering.
    """

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        window_detector: Optional[WindowDetector] = None,
        mouse_controller: Optional[DemoMouseController] = None,
    ):
        self._logger = CodeFlowLogger.get_logger()
        self.session_manager = session_manager or SessionManager()
        self.window_detector = window_detector or WindowDetector()
        self.mouse_controller = mouse_controller

        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._is_running = False

        # Event hooks
        self.on_countdown: Optional[Callable[[int], None]] = None
        self.on_progress: Optional[Callable[[int, int, int, int], None]] = None
        self.on_focus_lost: Optional[Callable[[str], None]] = None
        self.on_paused: Optional[Callable[[str], None]] = None
        self.on_resumed: Optional[Callable[[], None]] = None
        self.on_completed: Optional[Callable[[], None]] = None
        self.on_stopped: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_typo: Optional[Callable[[str, str], None]] = None
        self.on_inspection_scroll: Optional[Callable[[bool], None]] = None
        self.on_mouse_action: Optional[Callable[[str], None]] = None

    def _notify_mouse_action(self, msg: str) -> None:
        if self.on_mouse_action:
            try:
                self.on_mouse_action(msg)
            except Exception:
                pass

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(
        self,
        source_model: SourceTextModel,
        settings: TypingSettings,
        adapter: BaseKeyboardAdapter,
    ) -> bool:
        if self._is_running:
            return False

        settings.validate()
        self._stop_event.clear()
        self._pause_event.clear()
        self._is_running = True

        if self.mouse_controller:
            self.mouse_controller.on_mouse_action = self._notify_mouse_action

        self._worker_thread = threading.Thread(
            target=self._run_execution,
            args=(source_model, settings, adapter),
            daemon=True,
            name="TypingEngineWorker",
        )
        self._worker_thread.start()
        return True

    def pause(self, reason: PauseReason = PauseReason.USER_MANUAL) -> bool:
        if not self._is_running:
            return False
        self._pause_event.set()
        if self.mouse_controller:
            self.mouse_controller.pause()
        res = self.session_manager.pause_session(reason)
        if self.on_paused:
            self.on_paused(reason.value)
        return res

    def resume(self) -> bool:
        if not self._is_running:
            return False
        self._pause_event.clear()
        if self.mouse_controller:
            self.mouse_controller.resume()
        res = self.session_manager.resume_session()
        if self.on_resumed:
            self.on_resumed()
        return res

    def stop(self) -> bool:
        if not self._is_running:
            return False
        self._stop_event.set()
        self._pause_event.clear()
        if self.mouse_controller:
            self.mouse_controller.stop()
        return True

    def wait(self, timeout: Optional[float] = None) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=timeout)

    def _sleep_with_cancel_check(self, duration: float) -> bool:
        if duration <= 0:
            return self._stop_event.is_set()

        start = time.time()
        while time.time() - start < duration:
            if self._stop_event.is_set():
                return True
            time.sleep(min(0.015, duration))
        return False

    def _check_focus(self, settings: TypingSettings) -> bool:
        is_focused, _ = self.window_detector.is_target_focused(
            target_hwnd=settings.target_hwnd,
            target_title=settings.target_title,
            allow_any=settings.allow_any_target,
        )
        return is_focused

    def _handle_focus_loss(self, settings: TypingSettings) -> bool:
        self._logger.warning("Target window lost focus during automation.")
        self.session_manager.record_focus_loss()

        fg = self.window_detector.get_foreground_window()
        fg_title = fg.title if fg else "Unknown"

        if self.on_focus_lost:
            try:
                self.on_focus_lost(fg_title)
            except Exception:
                pass

        if self.mouse_controller:
            self.mouse_controller.pause()

        self._pause_event.set()

        while self._pause_event.is_set():
            if self._stop_event.is_set():
                return False

            time.sleep(0.1)

            if self._check_focus(settings):
                time.sleep(0.3)
                self._pause_event.clear()
                self.session_manager.resume_session()
                if self.mouse_controller:
                    self.mouse_controller.resume()
                if self.on_resumed:
                    try:
                        self.on_resumed()
                    except Exception:
                        pass
                return True

        return not self._stop_event.is_set()

    def _compute_wavy_char_delay(self, char_index: int, settings: TypingSettings, char: str) -> float:
        """
        Computes dynamic character delay.
        When WPM fluctuation is active, fluctuates naturally between wpm_min and wpm_max (e.g. 30 to 45 WPM).
        """
        # 1. Calculate WPM with smooth fluctuation between min and max bounds
        if settings.wpm_fluctuation_enabled and settings.wpm_max > settings.wpm_min and settings.typing_rate_cpm <= 500:
            mid_wpm = (settings.wpm_min + settings.wpm_max) / 2.0
            amp_wpm = (settings.wpm_max - settings.wpm_min) / 2.0
            cycle = max(4, settings.wavy_cycle_length)
            angle = (char_index % cycle) / cycle * 2.0 * math.pi
            
            # Sinusoidal speed wave
            fluct_wpm = mid_wpm + (amp_wpm * math.sin(angle))
            # Natural micro-jitter within bounds
            fluct_wpm += random.uniform(-2.0, 2.0)
            target_wpm = max(float(settings.wpm_min), min(float(settings.wpm_max), fluct_wpm))
            cpm = target_wpm * 5.0
            delay = 60.0 / cpm
        else:
            delay = settings.base_char_delay
            if settings.enable_wavy_cadence and settings.wavy_cycle_length > 0:
                cycle = settings.wavy_cycle_length
                angle = (char_index % cycle) / cycle * 2.0 * math.pi
                wave_multiplier = 1.0 - (settings.wavy_amplitude_fraction * math.sin(angle))
                delay *= max(0.4, wave_multiplier)

        # 2. Timing Jitter
        jitter = settings.jitter_fraction
        if jitter > 0:
            delay *= random.uniform(1.0 - jitter, 1.0 + jitter)

        # 3. Cognitive pause on punctuation / syntax boundaries
        if settings.cognitive_pause_ms > 0:
            if char in (':', ';', '{', '}', '\n'):
                delay += (settings.cognitive_pause_ms / 1000.0) * random.uniform(0.6, 1.2)
            elif char == ' ':
                delay *= 1.25

        return max(0.002, delay)

    def _simulate_typo_correction(
        self,
        char: str,
        adapter: BaseKeyboardAdapter,
        settings: TypingSettings,
    ) -> bool:
        """
        Simulate an authentic mistake: single-letter slip or multi-character word slip,
        followed by reaction pause, Backspace(s), and typing the correct character.
        Returns True if cancelled/stopped during typo routine, False otherwise.
        """
        lower = char.lower()
        if lower not in QWERTY_ADJACENT:
            return False

        scale = min(1.0, 360.0 / max(10, settings.typing_rate_cpm))

        # Decide whether to do a multi-character slip (e.g. typing 2-3 wrong letters)
        is_multi_slip = settings.enable_word_slip_typos and random.random() < 0.45
        slip_count = random.randint(2, settings.typo_max_slip_chars) if is_multi_slip else 1

        slipped_chars = []
        curr_key = lower
        for _ in range(slip_count):
            neighbors = QWERTY_ADJACENT.get(curr_key, ['e', 'r'])
            slip_char = random.choice(neighbors)
            if char.isupper():
                slip_char = slip_char.upper()
            slipped_chars.append(slip_char)
            curr_key = slip_char.lower()

        slipped_str = "".join(slipped_chars)

        if self.on_typo:
            try:
                self.on_typo(char, slipped_str)
            except Exception:
                pass

        # 1. Mistakenly type slip character(s)
        for sc in slipped_chars:
            adapter.type_char(sc)
            if self._sleep_with_cancel_check(random.uniform(0.05, 0.12) * scale):
                return True

        # 2. Human reaction delay (looking at screen and noticing mistake)
        reaction_time = random.uniform(0.18, 0.32) * scale
        if self._sleep_with_cancel_check(reaction_time):
            return True

        # 3. Hit Backspace for each mistaken letter
        for _ in range(len(slipped_chars)):
            adapter.type_backspace()
            if self._sleep_with_cancel_check(random.uniform(0.05, 0.09) * scale):
                return True

        # 4. Correction delay before hitting right key
        correction_time = random.uniform(0.08, 0.16) * scale
        if self._sleep_with_cancel_check(correction_time):
            return True

        return False

    def _run_execution(
        self,
        source_model: SourceTextModel,
        settings: TypingSettings,
        adapter: BaseKeyboardAdapter,
    ) -> None:
        try:
            raw_text = source_model.raw_text
            total_chars = len(raw_text)
            total_lines = source_model.stats.total_lines

            self.session_manager.start_new_session(
                total_characters=total_chars,
                total_lines=total_lines,
                target_title=settings.target_title,
                initial_delay_seconds=settings.initial_delay_seconds,
            )

            # Countdown Phase
            initial_delay = settings.initial_delay_seconds
            if initial_delay > 0:
                self._logger.info(f"Beginning countdown: {initial_delay}s")
                countdown_remaining = int(initial_delay)
                fractional = initial_delay - countdown_remaining

                if fractional > 0:
                    if self._sleep_with_cancel_check(fractional):
                        self._finish_stop()
                        return

                while countdown_remaining > 0:
                    if self._stop_event.is_set():
                        self._finish_stop()
                        return

                    if self.on_countdown:
                        try:
                            self.on_countdown(countdown_remaining)
                        except Exception:
                            pass

                    if self._sleep_with_cancel_check(1.0):
                        self._finish_stop()
                        return

                    countdown_remaining -= 1

            self.session_manager.transition_to(SessionState.RUNNING)
            if self.mouse_controller and settings.enable_mouse_motion:
                self.mouse_controller.start()

            # Automation Phase
            if settings.entry_mode == TextEntryMode.CLIPBOARD_LINE:
                self._execute_line_stream(source_model, settings, adapter)
            else:
                self._execute_char_by_char(raw_text, settings, adapter)

        except Exception as e:
            self._logger.exception(f"Unhandled error in typing engine: {e}")
            self.session_manager.fail_session(str(e))
            if self.on_error:
                try:
                    self.on_error(str(e))
                except Exception:
                    pass
        finally:
            self._is_running = False
            if self.mouse_controller:
                self.mouse_controller.stop()

    def _execute_char_by_char(
        self,
        raw_text: str,
        settings: TypingSettings,
        adapter: BaseKeyboardAdapter,
    ) -> None:
        total_chars = len(raw_text)
        current_line = 1
        chars_typed = 0
        newline_pause = settings.newline_pause_seconds
        lines_since_scroll = 0
        next_scroll_trigger = settings.inspection_scroll_interval_lines + random.randint(-1, 2)

        for i, char in enumerate(raw_text):
            if self._stop_event.is_set():
                self._finish_stop()
                return

            while self._pause_event.is_set():
                if self._stop_event.is_set():
                    self._finish_stop()
                    return
                time.sleep(0.05)

            if settings.pause_on_focus_loss and not self._check_focus(settings):
                resumed = self._handle_focus_loss(settings)
                if not resumed:
                    self._finish_stop()
                    return

            # Check for simulated human typo on alphabetic characters
            if settings.enable_typos and char.isalpha() and random.random() < (settings.typo_rate_percent / 100.0):
                cancelled = self._simulate_typo_correction(char, adapter, settings)
                if cancelled:
                    self._finish_stop()
                    return

            # Type the intended character
            adapter.type_char(char)
            chars_typed += 1

            if char == "\n":
                current_line += 1
                lines_since_scroll += 1

                # Check if in-between inspection scrolling should trigger!
                # Requirement: "at when mouse scrolls then typing should stop"
                if (
                    settings.enable_inspection_scroll
                    and self.mouse_controller
                    and lines_since_scroll >= next_scroll_trigger
                ):
                    lines_since_scroll = 0
                    next_scroll_trigger = settings.inspection_scroll_interval_lines + random.randint(-1, 2)
                    if self.on_inspection_scroll:
                        try:
                            self.on_inspection_scroll(True)
                        except Exception:
                            pass

                    # Execute scroll + hover while typing is completely stopped
                    try:
                        self.mouse_controller.execute_inspection_scroll(
                            distance_ticks=settings.inspection_scroll_distance,
                            pause_seconds=settings.inspection_pause_seconds,
                            enable_hovering=settings.enable_random_hovering,
                        )
                    except TypeError:
                        self.mouse_controller.execute_inspection_scroll(
                            distance_ticks=settings.inspection_scroll_distance,
                            pause_seconds=settings.inspection_pause_seconds,
                        )

                    if self.on_inspection_scroll:
                        try:
                            self.on_inspection_scroll(False)
                        except Exception:
                            pass

                elif newline_pause > 0:
                    if self._sleep_with_cancel_check(newline_pause):
                        self._finish_stop()
                        return

            # Dynamic wavy cadence delay calculation (30-45 WPM)
            char_delay = self._compute_wavy_char_delay(i, settings, char)

            if self._sleep_with_cancel_check(char_delay):
                self._finish_stop()
                return

            self.session_manager.record_progress(chars_typed, current_line)
            if self.on_progress:
                try:
                    self.on_progress(chars_typed, total_chars, current_line, 0)
                except Exception:
                    pass

        self.session_manager.complete_session()
        self._logger.info(f"Typing session completed: {chars_typed} characters typed.")
        if self.on_completed:
            try:
                self.on_completed()
            except Exception:
                pass

    def _execute_line_stream(
        self,
        source_model: SourceTextModel,
        settings: TypingSettings,
        adapter: BaseKeyboardAdapter,
    ) -> None:
        lines = source_model.get_lines(keep_ends=True)
        total_chars = len(source_model.raw_text)
        total_lines = len(lines)
        chars_typed = 0
        current_line = 1
        newline_pause = settings.newline_pause_seconds
        lines_since_scroll = 0

        for line in lines:
            if self._stop_event.is_set():
                self._finish_stop()
                return

            while self._pause_event.is_set():
                if self._stop_event.is_set():
                    self._finish_stop()
                    return
                time.sleep(0.05)

            if settings.pause_on_focus_loss and not self._check_focus(settings):
                resumed = self._handle_focus_loss(settings)
                if not resumed:
                    self._finish_stop()
                    return

            adapter.paste_text(line)
            chars_typed += len(line)
            current_line += 1
            lines_since_scroll += 1

            if (
                settings.enable_inspection_scroll
                and self.mouse_controller
                and lines_since_scroll >= settings.inspection_scroll_interval_lines
            ):
                lines_since_scroll = 0
                if self.on_inspection_scroll:
                    try:
                        self.on_inspection_scroll(True)
                    except Exception:
                        pass

                self.mouse_controller.execute_inspection_scroll(
                    distance_ticks=settings.inspection_scroll_distance,
                    pause_seconds=settings.inspection_pause_seconds,
                    enable_hovering=settings.enable_random_hovering,
                )

                if self.on_inspection_scroll:
                    try:
                        self.on_inspection_scroll(False)
                    except Exception:
                        pass

            line_delay = max(0.05, len(line) * settings.base_char_delay * 0.4) + newline_pause
            if self._sleep_with_cancel_check(line_delay):
                self._finish_stop()
                return

            self.session_manager.record_progress(chars_typed, current_line)
            if self.on_progress:
                try:
                    self.on_progress(chars_typed, total_chars, current_line, total_lines)
                except Exception:
                    pass

        self.session_manager.complete_session()
        if self.on_completed:
            try:
                self.on_completed()
            except Exception:
                pass

    def _finish_stop(self) -> None:
        self._logger.info("Typing engine cancelled by stop signal.")
        self.session_manager.stop_session()
        if self.on_stopped:
            try:
                self.on_stopped()
            except Exception:
                pass
