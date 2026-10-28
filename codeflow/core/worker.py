"""
Qt Worker Adapter for TypingEngine.

Provides thread-safe signal bridges between the background typing engine
and PySide6 UI widgets.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from codeflow.adapters.base import BaseKeyboardAdapter
from codeflow.config import TypingSettings
from codeflow.core.engine import TypingEngine
from codeflow.core.session import PauseReason, SessionState
from codeflow.core.source_model import SourceTextModel


class TypingWorker(QObject):
    """
    QObject signal wrapper for TypingEngine.
    """
    countdown_tick = Signal(int)
    progress_updated = Signal(int, int, int, int)  # chars_typed, total_chars, current_line, total_lines
    focus_warning = Signal(str)  # foreground window title
    session_paused = Signal(str)  # pause reason
    session_resumed = Signal()
    session_stopped = Signal()
    session_completed = Signal()
    error_occurred = Signal(str)
    typo_occurred = Signal(str, str)  # intended_char, typo_char
    inspection_scrolling = Signal(bool)  # True = scrolling active, False = finished
    mouse_action = Signal(str)  # Live mouse event message

    def __init__(self, engine: TypingEngine):
        super().__init__()
        self.engine = engine
        self._bind_callbacks()

    def _bind_callbacks(self) -> None:
        self.engine.on_countdown = lambda s: self.countdown_tick.emit(s)
        self.engine.on_progress = lambda c, tc, l, tl: self.progress_updated.emit(c, tc, l, tl)
        self.engine.on_focus_lost = lambda t: self.focus_warning.emit(t)
        self.engine.on_paused = lambda r: self.session_paused.emit(r)
        self.engine.on_resumed = lambda: self.session_resumed.emit()
        self.engine.on_stopped = lambda: self.session_stopped.emit()
        self.engine.on_completed = lambda: self.session_completed.emit()
        self.engine.on_error = lambda e: self.error_occurred.emit(e)
        self.engine.on_typo = lambda ind, typ: self.typo_occurred.emit(ind, typ)
        self.engine.on_inspection_scroll = lambda act: self.inspection_scrolling.emit(act)
        self.engine.on_mouse_action = lambda msg: self.mouse_action.emit(msg)

    def start_typing(
        self,
        source_model: SourceTextModel,
        settings: TypingSettings,
        adapter: BaseKeyboardAdapter,
    ) -> bool:
        return self.engine.start(source_model, settings, adapter)

    def pause_typing(self, reason: PauseReason = PauseReason.USER_MANUAL) -> bool:
        return self.engine.pause(reason)

    def resume_typing(self) -> bool:
        return self.engine.resume()

    def stop_typing(self) -> bool:
        return self.engine.stop()
