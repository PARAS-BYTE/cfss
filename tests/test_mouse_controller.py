"""
Tests for DemoMouseController - user intervention detection and lifecycle.
"""

import pytest
from codeflow.core.mouse_controller import DemoMouseController


class TestDemoMouseController:
    def test_initialization(self):
        controller = DemoMouseController(enabled=False, intensity="subtle", interval_seconds=3.0)
        assert controller.enabled is False
        assert controller.intensity == "subtle"
        assert controller.user_intervened is False

    def test_lifecycle_when_disabled(self):
        controller = DemoMouseController(enabled=False)
        # Should not start thread when disabled
        controller.start()
        assert controller._thread is None
        controller.stop()

    def test_user_interrupt_detection(self):
        overridden = []
        controller = DemoMouseController(
            enabled=True,
            on_user_override=lambda: overridden.append(True)
        )
        controller._expected_x = 100
        controller._expected_y = 100

        # Mock current position far away (user moved mouse)
        controller._get_current_pos = lambda: (500, 500)

        interrupted = controller._check_user_interrupt()
        assert interrupted is True
        assert controller.user_intervened is True
        assert len(overridden) == 1
