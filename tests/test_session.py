"""
Tests for SessionManager and SessionState lifecycle and statistics.
"""

import time
import pytest
from codeflow.core.session import SessionManager, SessionState, PauseReason


class TestSessionManager:
    def test_initial_state(self):
        mgr = SessionManager()
        assert mgr.state == SessionState.IDLE
        assert mgr.stats.total_characters == 0
        assert mgr.stats.completion_percentage == 0.0

    def test_start_session_countdown_and_running(self):
        mgr = SessionManager()
        assert mgr.start_new_session(total_characters=100, total_lines=5, initial_delay_seconds=3.0)
        assert mgr.state == SessionState.COUNTDOWN
        assert mgr.stats.total_characters == 100
        assert mgr.stats.total_lines == 5

        # Transition to running
        assert mgr.transition_to(SessionState.RUNNING)
        assert mgr.state == SessionState.RUNNING

    def test_pause_and_resume_lifecycle(self):
        mgr = SessionManager()
        mgr.start_new_session(total_characters=100, total_lines=5, initial_delay_seconds=0.0)
        assert mgr.state == SessionState.RUNNING

        # Pause
        assert mgr.pause_session(PauseReason.USER_MANUAL)
        assert mgr.state == SessionState.PAUSED
        assert mgr.stats.pause_count == 1
        assert mgr.stats.pause_reason == PauseReason.USER_MANUAL

        # Resume
        assert mgr.resume_session()
        assert mgr.state == SessionState.RUNNING
        assert mgr.stats.pause_reason is None

    def test_focus_loss_pause(self):
        mgr = SessionManager()
        mgr.start_new_session(total_characters=100, total_lines=5)
        mgr.record_focus_loss()
        assert mgr.state == SessionState.PAUSED
        assert mgr.stats.focus_loss_count == 1
        assert mgr.stats.pause_reason == PauseReason.FOCUS_LOST

    def test_stop_session(self):
        mgr = SessionManager()
        mgr.start_new_session(total_characters=100, total_lines=5)
        assert mgr.stop_session()
        assert mgr.state == SessionState.STOPPED
        # Stopping again or pausing when stopped should be rejected
        assert not mgr.pause_session()
        assert not mgr.resume_session()

    def test_completion_and_metrics(self):
        mgr = SessionManager()
        mgr.start_new_session(total_characters=200, total_lines=10)
        mgr.record_progress(chars_typed=100, current_line=5)
        assert mgr.stats.completion_percentage == 50.0

        mgr.record_progress(chars_typed=200, current_line=10)
        assert mgr.stats.completion_percentage == 100.0
        assert mgr.complete_session()
        assert mgr.state == SessionState.COMPLETED

        summary = mgr.generate_summary()
        assert summary["state"] == "COMPLETED"
        assert summary["total_characters"] == 200
        assert summary["characters_typed"] == 200
        assert summary["completion_percentage"] == 100.0

    def test_listener_notification(self):
        mgr = SessionManager()
        events = []

        def on_update(state, stats):
            events.append((state, stats.characters_typed))

        mgr.add_listener(on_update)
        mgr.start_new_session(total_characters=50, total_lines=2)
        mgr.record_progress(chars_typed=10, current_line=1)
        mgr.stop_session()

        assert len(events) >= 3
        assert events[0][0] in (SessionState.RUNNING, SessionState.COUNTDOWN)
        assert events[-1][0] == SessionState.STOPPED
