"""
Tests for TypingEngine - cadence, fidelity, pause/resume, and cancellation.
"""

import time
import pytest
from codeflow.adapters.base import TextEntryMode
from codeflow.adapters.mock_adapter import MockKeyboardAdapter
from codeflow.config import TypingSettings
from codeflow.core.engine import TypingEngine
from codeflow.core.session import SessionManager, SessionState
from codeflow.core.source_model import SourceTextModel
from codeflow.windows.window_detector import WindowDetector, WindowInfo


class TestTypingEngine:
    def test_exact_character_execution(self):
        source_code = (
            "def add(a, b):\n"
            "    # indent 4 spaces\n"
            "\treturn a + b\n"
        )
        model = SourceTextModel(source_code)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        # Mock window detector always returns valid target focused
        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe", is_vscode=True)
        detector.set_mock_mode([mock_win], foreground=mock_win)

        engine = TypingEngine(session_manager=mgr, window_detector=detector)

        settings = TypingSettings(
            typing_rate_cpm=3000,  # Fast for test
            jitter_percent=0,
            newline_pause_ms=0,
            initial_delay_seconds=0.0,
            enable_wavy_cadence=False,
            enable_typos=False,
            cognitive_pause_ms=0,
            entry_mode=TextEntryMode.MOCK,
            allow_any_target=True,
            pause_on_focus_loss=False,
        )

        completed = []
        engine.on_completed = lambda: completed.append(True)

        assert engine.start(model, settings, adapter) is True
        engine.wait(timeout=5.0)

        assert len(completed) == 1
        assert mgr.state == SessionState.COMPLETED
        assert adapter.get_typed_text() == source_code

    def test_line_streaming_execution(self):
        source_code = "line 1\nline 2\nline 3\n"
        model = SourceTextModel(source_code)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe", is_vscode=True)
        detector.set_mock_mode([mock_win], foreground=mock_win)

        engine = TypingEngine(session_manager=mgr, window_detector=detector)

        settings = TypingSettings(
            typing_rate_cpm=3000,
            newline_pause_ms=0,
            initial_delay_seconds=0.0,
            entry_mode=TextEntryMode.CLIPBOARD_LINE,
            allow_any_target=True,
            pause_on_focus_loss=False,
        )

        engine.start(model, settings, adapter)
        engine.wait(timeout=2.0)

        assert mgr.state == SessionState.COMPLETED
        assert adapter.get_typed_text() == source_code

    def test_cancellation_stop(self):
        # Long text
        long_code = "x = 1\n" * 100
        model = SourceTextModel(long_code)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe")
        detector.set_mock_mode([mock_win], foreground=mock_win)

        engine = TypingEngine(session_manager=mgr, window_detector=detector)
        settings = TypingSettings(
            typing_rate_cpm=300,  # Slow enough to stop mid-way
            initial_delay_seconds=0.0,
            allow_any_target=True,
            pause_on_focus_loss=False,
        )

        stopped_callbacks = []
        engine.on_stopped = lambda: stopped_callbacks.append(True)

        engine.start(model, settings, adapter)
        time.sleep(0.05)
        assert engine.stop() is True
        engine.wait(timeout=1.0)

        assert mgr.state == SessionState.STOPPED
        assert len(stopped_callbacks) == 1
        # Should have stopped before finishing all text
        assert len(adapter.get_typed_text()) < len(long_code)

    def test_pause_and_resume(self):
        text = "abcdefghij"  # 10 chars
        model = SourceTextModel(text)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe")
        detector.set_mock_mode([mock_win], foreground=mock_win)

        engine = TypingEngine(session_manager=mgr, window_detector=detector)
        settings = TypingSettings(
            typing_rate_cpm=1200,  # 50ms per char
            jitter_percent=0,
            newline_pause_ms=0,
            initial_delay_seconds=0.0,
            allow_any_target=True,
            pause_on_focus_loss=False,
        )

        engine.start(model, settings, adapter)
        time.sleep(0.06)
        assert engine.pause() is True
        assert mgr.state == SessionState.PAUSED
        time.sleep(0.04)
        paused_len = len(adapter.get_typed_text())

        # Wait a moment to ensure no new chars are typed while paused
        time.sleep(0.06)
        assert len(adapter.get_typed_text()) == paused_len

        # Resume
        assert engine.resume() is True
        engine.wait(timeout=2.0)
        assert mgr.state == SessionState.COMPLETED
        assert adapter.get_typed_text() == text

    def test_wavy_speed_cadence(self):
        engine = TypingEngine()
        settings = TypingSettings(
            typing_rate_cpm=600,  # base 100ms
            jitter_percent=0,
            wpm_fluctuation_enabled=False,
            enable_wavy_cadence=True,
            wavy_amplitude_percent=50,
            wavy_cycle_length=10,
        )
        delays = [engine._compute_wavy_char_delay(i, settings, 'a') for i in range(10)]
        # Delay should undulate: maximum should exceed base and minimum should be below base
        assert max(delays) > min(delays)
        # Verify sinusoid amplitude effect
        assert max(delays) > 0.10
        assert min(delays) < 0.10

    def test_wpm_30_to_45_fluctuation(self):
        engine = TypingEngine()
        settings = TypingSettings(
            target_wpm=40,
            wpm_fluctuation_enabled=True,
            wpm_min=30,
            wpm_max=45,
            jitter_percent=0,
            cognitive_pause_ms=0,
        )
        delays = [engine._compute_wavy_char_delay(i, settings, 'a') for i in range(24)]
        for d in delays:
            assert 0.25 <= d <= 0.42
        assert max(delays) > min(delays)

    def test_human_typo_and_self_correction(self):
        source = "hello"
        model = SourceTextModel(source)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe")
        detector.set_mock_mode([mock_win], foreground=mock_win)

        engine = TypingEngine(session_manager=mgr, window_detector=detector)
        typos_recorded = []
        engine.on_typo = lambda ind, typ: typos_recorded.append((ind, typ))

        # 100% typo rate to guarantee trigger
        settings = TypingSettings(
            typing_rate_cpm=2400,
            jitter_percent=0,
            enable_wavy_cadence=False,
            enable_typos=True,
            typo_rate_percent=100.0,
            allow_any_target=True,
            pause_on_focus_loss=False,
            initial_delay_seconds=0.0,
        )

        engine.start(model, settings, adapter)
        engine.wait(timeout=5.0)

        assert mgr.state == SessionState.COMPLETED
        # Typos must have been caught and recorded
        assert len(typos_recorded) > 0
        # Crucially: Backspace erased the typo, so final text is STILL 100% exact!
        assert adapter.get_typed_text() == source
        assert "KEY:BACKSPACE" in adapter.recorded_events

    def test_inspection_scroll_stops_typing(self):
        # 15 lines of text
        source = "x = 1\n" * 15
        model = SourceTextModel(source)
        adapter = MockKeyboardAdapter()
        mgr = SessionManager()

        detector = WindowDetector()
        mock_win = WindowInfo(1, "VS Code", 100, "code.exe")
        detector.set_mock_mode([mock_win], foreground=mock_win)

        from codeflow.core.mouse_controller import DemoMouseController
        mouse = DemoMouseController(enabled=True)
        # Mock scroll execution to avoid actual mouse moves in headless test
        scroll_events = []
        def mock_scroll(distance_ticks=4, pause_seconds=1.5, on_start_scroll=None, on_finish_scroll=None):
            scroll_events.append("SCROLLED")
            return True
        mouse.execute_inspection_scroll = mock_scroll

        engine = TypingEngine(session_manager=mgr, window_detector=detector, mouse_controller=mouse)
        scroll_signals = []
        engine.on_inspection_scroll = lambda active: scroll_signals.append(active)

        settings = TypingSettings(
            typing_rate_cpm=3000,
            jitter_percent=0,
            enable_wavy_cadence=False,
            enable_typos=False,
            cognitive_pause_ms=0,
            newline_pause_ms=0,
            enable_inspection_scroll=True,
            inspection_scroll_interval_lines=5,
            allow_any_target=True,
            pause_on_focus_loss=False,
            initial_delay_seconds=0.0,
        )

        engine.start(model, settings, adapter)
        engine.wait(timeout=5.0)

        assert mgr.state == SessionState.COMPLETED
        assert adapter.get_typed_text() == source
        assert len(scroll_events) >= 2
        # Emitted True (started) and False (finished)
        assert True in scroll_signals
        assert False in scroll_signals
