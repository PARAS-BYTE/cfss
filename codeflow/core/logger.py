"""
Safe Logging Subsystem for CodeFlow Studio.

Provides structured, safe application logging. To uphold privacy and safety
requirements, source code content is NEVER logged unless explicitly enabled
by the user via advanced debugging flags.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional


class CodeFlowLogger:
    """
    Application-wide logger configured with safety guards.
    """
    _logger: Optional[logging.Logger] = None
    _allow_source_logging: bool = False
    _log_file_path: Optional[str] = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls.setup_logging()
        return cls._logger

    @classmethod
    def setup_logging(
        cls,
        log_dir: Optional[str | Path] = None,
        level: int = logging.INFO,
        allow_source_logging: bool = False,
    ) -> logging.Logger:
        cls._allow_source_logging = allow_source_logging

        logger = logging.getLogger("CodeFlowStudio")
        logger.setLevel(level)
        logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler in user app data or local directory
        if log_dir is None:
            # Default to local logs directory
            log_dir = Path.cwd() / "logs"
        else:
            log_dir = Path(log_dir)

        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "codeflow.log"
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            cls._log_file_path = str(log_file)
        except Exception as e:
            logger.warning(f"Failed to create file logger at {log_dir}: {e}")

        cls._logger = logger
        return logger

    @classmethod
    def set_source_logging_allowed(cls, allowed: bool) -> None:
        cls._allow_source_logging = allowed
        cls.get_logger().info(f"Source code logging in traces set to: {allowed}")

    @classmethod
    def is_source_logging_allowed(cls) -> bool:
        return cls._allow_source_logging

    @classmethod
    def sanitize_code_preview(cls, code_snippet: str, max_len: int = 20) -> str:
        """
        Sanitize or redact code strings from logs unless explicitly enabled.
        """
        if cls._allow_source_logging:
            return repr(code_snippet[:max_len])
        return f"<REDACTED length={len(code_snippet)}>"

    @classmethod
    def get_log_file_path(cls) -> Optional[str]:
        return cls._log_file_path
