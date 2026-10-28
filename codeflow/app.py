"""
Application Entry Point for CodeFlow Studio.
"""

from __future__ import annotations

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from codeflow.core.logger import CodeFlowLogger
from codeflow.ui.main_window import CodeFlowMainWindow


def main() -> int:
    """Launch CodeFlow Studio GUI Application."""
    # Initialize logger
    CodeFlowLogger.setup_logging()
    logger = CodeFlowLogger.get_logger()
    logger.info("Starting CodeFlow Studio...")

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("CodeFlow Studio")
    app.setOrganizationName("CodeFlow")

    window = CodeFlowMainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
