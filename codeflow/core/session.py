"""
Session State Management for CodeFlow Studio.

Tracks execution lifecycles, timing, progress metrics, and state transitions
across IDLE, COUNTDOWN, RUNNING, PAUSED, STOPPED, COMPLETED, and ERROR states.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional


class SessionState(Enum):
    IDLE = auto()
    COUNTDOWN = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    COMPLETED = auto()
    ERROR = auto()

    def is_active(self) -> bool:
        """Return True if session is ongoing (COUNTDOWN, RUNNING, or PAUSED)."""
        return self in (SessionState.COUNTDOWN, SessionState.RUNNING, SessionState.PAUSED)

    def can_pause(self) -> bool:
        return self == SessionState.RUNNING

    def can_resume(self) -> bool:
        return self == SessionState.PAUSED

    def can_stop(self) -> bool:
        return self in (SessionState.COUNTDOWN, SessionState.RUNNING, SessionState.PAUSED)


class PauseReason(Enum):
    USER_MANUAL = "User requested pause"
    FOCUS_LOST = "Target window lost focus"
    USER_INTERACTION = "User mouse/keyboard activity detected"
    SYSTEM = "System pause"


@dataclass
class SessionStats:
    """Real-time metrics for an ongoing or completed typing session."""
    total_characters: int = 0
    characters_typed: int = 0
    total_lines: int = 0
    current_line: int = 0
    start_time: float = 0.0
    end_time: Optional[float] = None
    accumulated_active_time: float = 0.0
    accumulated_pause_time: float = 0.0
    last_resume_time: float = 0.0
    pause_start_time: float = 0.0
    pause_count: int = 0
    focus_loss_count: int = 0
    target_window_title: str = ""
    target_process_name: str = ""
    error_message: Optional[str] = None
    pause_reason: Optional[PauseReason] = None

    @property
    def completion_percentage(self) -> float:
        if self.total_characters == 0:
            return 0.0
        return min(100.0, (self.characters_typed / self.total_characters) * 100.0)

    @property
    def elapsed_active_seconds(self) -> float:
        """Active typing duration excluding pauses."""
        total = self.accumulated_active_time
        if self.last_resume_time > 0 and self.pause_start_time == 0:
            total += max(0.0, time.time() - self.last_resume_time)
        return total

    @property
    def effective_cpm(self) -> float:
        """Actual Characters-Per-Minute achieved during active typing."""
        active_secs = self.elapsed_active_seconds
        if active_secs <= 0.5 or self.characters_typed == 0:
            return 0.0
        return (self.characters_typed / active_secs) * 60.0

    @property
    def effective_wpm(self) -> float:
        """Standardized Words-Per-Minute (5 characters = 1 word)."""
        return self.effective_cpm / 5.0

    def estimate_remaining_seconds(self, configured_cpm: float) -> float:
        """Calculate estimated remaining seconds based on configured or actual CPM."""
        remaining_chars = max(0, self.total_characters - self.characters_typed)
        if remaining_chars == 0:
            return 0.0
        cpm = self.effective_cpm if self.effective_cpm > 50 else max(10.0, configured_cpm)
        chars_per_sec = cpm / 60.0
        return remaining_chars / chars_per_sec


class SessionManager:
    """
    Thread-safe orchestrator for session lifecycle and metric aggregation.
    """

    # Valid state transition graph
    VALID_TRANSITIONS = {
        SessionState.IDLE: {SessionState.COUNTDOWN, SessionState.RUNNING},
        SessionState.COUNTDOWN: {SessionState.RUNNING, SessionState.STOPPED, SessionState.ERROR},
        SessionState.RUNNING: {SessionState.PAUSED, SessionState.COMPLETED, SessionState.STOPPED, SessionState.ERROR},
        SessionState.PAUSED: {SessionState.RUNNING, SessionState.STOPPED, SessionState.ERROR},
        SessionState.STOPPED: {SessionState.IDLE, SessionState.COUNTDOWN, SessionState.RUNNING},
        SessionState.COMPLETED: {SessionState.IDLE, SessionState.COUNTDOWN, SessionState.RUNNING},
        SessionState.ERROR: {SessionState.IDLE, SessionState.COUNTDOWN, SessionState.RUNNING},
    }

    def __init__(self):
        self._lock = threading.RLock()
        self._state: SessionState = SessionState.IDLE
        self._stats: SessionStats = SessionStats()
        self._listeners: List[Callable[[SessionState, SessionStats], None]] = []

    @property
    def state(self) -> SessionState:
        with self._lock:
            return self._state

    @property
    def stats(self) -> SessionStats:
        with self._lock:
            return self._stats

    def add_listener(self, callback: Callable[[SessionState, SessionStats], None]) -> None:
        """Subscribe to state and metric changes."""
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[SessionState, SessionStats], None]) -> None:
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def _notify(self) -> None:
        """Invoke all listeners under safe copy."""
        with self._lock:
            curr_state = self._state
            curr_stats = self._stats
            listeners = list(self._listeners)

        for listener in listeners:
            try:
                listener(curr_state, curr_stats)
            except Exception:
                pass

    def transition_to(self, new_state: SessionState, error_message: Optional[str] = None) -> bool:
        """
        Safely transition to a new session state.
        
        Returns True if transition succeeded, False if invalid.
        """
        with self._lock:
            allowed = self.VALID_TRANSITIONS.get(self._state, set())
            if new_state not in allowed:
                return False

            now = time.time()
            old_state = self._state

            # Handle timers on state transition
            if new_state == SessionState.RUNNING:
                if old_state == SessionState.PAUSED:
                    if self._stats.pause_start_time > 0:
                        self._stats.accumulated_pause_time += now - self._stats.pause_start_time
                        self._stats.pause_start_time = 0.0
                    self._stats.last_resume_time = now
                elif old_state in (SessionState.IDLE, SessionState.COUNTDOWN):
                    self._stats.last_resume_time = now

            elif new_state == SessionState.PAUSED:
                if self._stats.last_resume_time > 0:
                    self._stats.accumulated_active_time += now - self._stats.last_resume_time
                self._stats.pause_start_time = now
                self._stats.pause_count += 1

            elif new_state in (SessionState.COMPLETED, SessionState.STOPPED, SessionState.ERROR):
                if old_state == SessionState.RUNNING and self._stats.last_resume_time > 0:
                    self._stats.accumulated_active_time += now - self._stats.last_resume_time
                elif old_state == SessionState.PAUSED and self._stats.pause_start_time > 0:
                    self._stats.accumulated_pause_time += now - self._stats.pause_start_time
                self._stats.end_time = now

            if error_message:
                self._stats.error_message = error_message

            self._state = new_state

        self._notify()
        return True

    def start_new_session(
        self,
        total_characters: int,
        total_lines: int,
        target_title: str = "",
        target_process: str = "",
        initial_delay_seconds: float = 0.0,
    ) -> bool:
        """Initialize session stats and begin COUNTDOWN or RUNNING."""
        with self._lock:
            self._stats = SessionStats(
                total_characters=total_characters,
                characters_typed=0,
                total_lines=total_lines,
                current_line=1 if total_lines > 0 else 0,
                start_time=time.time(),
                target_window_title=target_title,
                target_process_name=target_process,
            )
            next_state = SessionState.COUNTDOWN if initial_delay_seconds > 0 else SessionState.RUNNING
            self._state = next_state
            if next_state == SessionState.RUNNING:
                self._stats.last_resume_time = time.time()

        self._notify()
        return True

    def record_progress(self, chars_typed: int, current_line: int) -> None:
        """Update progress counts."""
        with self._lock:
            self._stats.characters_typed = chars_typed
            self._stats.current_line = current_line
        self._notify()

    def record_focus_loss(self) -> None:
        """Track focus lost event and pause session."""
        with self._lock:
            self._stats.focus_loss_count += 1
            self._stats.pause_reason = PauseReason.FOCUS_LOST
        self.transition_to(SessionState.PAUSED)

    def pause_session(self, reason: PauseReason = PauseReason.USER_MANUAL) -> bool:
        """Pause the active run."""
        with self._lock:
            if not self._state.can_pause():
                return False
            self._stats.pause_reason = reason
        return self.transition_to(SessionState.PAUSED)

    def resume_session(self) -> bool:
        """Resume typing from paused state."""
        with self._lock:
            if not self._state.can_resume():
                return False
            self._stats.pause_reason = None
        return self.transition_to(SessionState.RUNNING)

    def stop_session(self) -> bool:
        """Cancel the active run immediately."""
        with self._lock:
            if not self._state.can_stop():
                return False
        return self.transition_to(SessionState.STOPPED)

    def complete_session(self) -> bool:
        """Mark session as successfully completed."""
        return self.transition_to(SessionState.COMPLETED)

    def fail_session(self, error_message: str) -> bool:
        """Mark session as terminated with error."""
        return self.transition_to(SessionState.ERROR, error_message=error_message)

    def generate_summary(self) -> Dict[str, any]:
        """Produce a comprehensive summary dict for the session report."""
        with self._lock:
            s = self._stats
            state_name = self._state.name
            active_duration = s.elapsed_active_seconds
            total_duration = 0.0
            if s.start_time > 0:
                end = s.end_time if s.end_time else time.time()
                total_duration = max(0.0, end - s.start_time)

            return {
                "state": state_name,
                "total_characters": s.total_characters,
                "characters_typed": s.characters_typed,
                "total_lines": s.total_lines,
                "lines_completed": s.current_line,
                "completion_percentage": round(s.completion_percentage, 1),
                "total_duration_seconds": round(total_duration, 2),
                "active_duration_seconds": round(active_duration, 2),
                "pause_duration_seconds": round(s.accumulated_pause_time, 2),
                "pause_count": s.pause_count,
                "focus_loss_count": s.focus_loss_count,
                "effective_cpm": round(s.effective_cpm, 1),
                "effective_wpm": round(s.effective_wpm, 1),
                "target_window": s.target_window_title,
                "error_message": s.error_message,
            }
