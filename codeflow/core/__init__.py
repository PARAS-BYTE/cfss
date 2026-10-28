"""Core module exports for CodeFlow Studio."""

from codeflow.core.source_model import SourceTextModel, SourceStats, LineEnding
from codeflow.core.session import SessionManager, SessionState, SessionStats, PauseReason
from codeflow.core.logger import CodeFlowLogger
from codeflow.core.comparator import SourceComparator, DiffResult, DiscrepancyType

__all__ = [
    "SourceTextModel",
    "SourceStats",
    "LineEnding",
    "SessionManager",
    "SessionState",
    "SessionStats",
    "PauseReason",
    "CodeFlowLogger",
    "SourceComparator",
    "DiffResult",
    "DiscrepancyType",
]
