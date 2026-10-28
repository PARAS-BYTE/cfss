"""
Source Text Model for CodeFlow Studio.

Responsible for preserving exact source-code representations, including
whitespace, indentation (spaces and tabs), blank lines, special characters,
and detected line endings. Never silently trims or reformats source code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple


class LineEnding(Enum):
    LF = "\n"
    CRLF = "\r\n"
    CR = "\r"
    MIXED = "MIXED"
    NONE = ""


@dataclass
class SourceStats:
    """Metadata and statistics describing the source text."""
    total_characters: int = 0
    total_lines: int = 0
    blank_lines: int = 0
    leading_space_lines: int = 0
    tab_indented_lines: int = 0
    detected_line_ending: LineEnding = LineEnding.NONE
    file_path: Optional[str] = None
    language: str = "plain_text"


class SourceTextModel:
    """
    Encapsulates source code text while guaranteeing exact preservation.
    
    Guarantees:
    - Never strips or normalizes leading or trailing whitespace.
    - Preserves exact tab characters ('\\t') and space characters (' ').
    - Preserves consecutive blank lines and end-of-file trailing newlines.
    - Accurately reports line counts, character indices, and line endings.
    """

    # Common language file extensions map
    EXT_MAP = {
        ".py": "python",
        ".pyw": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".cpp": "cpp",
        ".cxx": "cpp",
        ".cc": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "css",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sql": "sql",
        ".md": "markdown",
        ".markdown": "markdown",
        ".sh": "bash",
        ".bash": "bash",
        ".bat": "batch",
        ".cmd": "batch",
        ".ps1": "powershell",
        ".txt": "plain_text",
    }

    def __init__(self, text: str = "", language: str = "plain_text", file_path: Optional[str] = None):
        self._raw_text: str = text
        self._language: str = language
        self._file_path: Optional[str] = file_path
        self._stats: SourceStats = self._compute_stats()

    @property
    def raw_text(self) -> str:
        """Return the exact, unmodified source text."""
        return self._raw_text

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        self._language = value
        self._stats.language = value

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def stats(self) -> SourceStats:
        return self._stats

    def set_text(self, text: str, language: Optional[str] = None) -> None:
        """Update the stored source text and recompute statistics."""
        self._raw_text = text
        if language is not None:
            self._language = language
        self._stats = self._compute_stats()

    def get_lines(self, keep_ends: bool = False) -> List[str]:
        """
        Return the lines of the text.
        
        Args:
            keep_ends: If True, each line retains its terminating line break.
        """
        if not self._raw_text:
            return []
        return self._raw_text.splitlines(keepends=keep_ends)

    def get_line(self, line_index: int) -> str:
        """Retrieve a specific 0-indexed line."""
        lines = self.get_lines(keep_ends=False)
        if 0 <= line_index < len(lines):
            return lines[line_index]
        raise IndexError(f"Line index {line_index} out of range [0, {len(lines)})")

    def character_at(self, index: int) -> str:
        """Get character at index."""
        return self._raw_text[index]

    def __len__(self) -> int:
        return len(self._raw_text)

    def _detect_line_ending(self) -> LineEnding:
        """Detect whether CRLF, LF, CR, or MIXED line endings are used."""
        crlf_count = self._raw_text.count("\r\n")
        # Standalone LF: total LF minus CRLF
        lf_count = self._raw_text.count("\n") - crlf_count
        # Standalone CR: total CR minus CRLF
        cr_count = self._raw_text.count("\r") - crlf_count

        active_types = sum(1 for c in (crlf_count, lf_count, cr_count) if c > 0)
        if active_types == 0:
            return LineEnding.NONE
        if active_types > 1:
            return LineEnding.MIXED
        if crlf_count > 0:
            return LineEnding.CRLF
        if lf_count > 0:
            return LineEnding.LF
        return LineEnding.CR

    def _compute_stats(self) -> SourceStats:
        """Compute comprehensive metrics without altering source text."""
        raw = self._raw_text
        if not raw:
            return SourceStats(
                total_characters=0,
                total_lines=0,
                blank_lines=0,
                leading_space_lines=0,
                tab_indented_lines=0,
                detected_line_ending=LineEnding.NONE,
                file_path=self._file_path,
                language=self._language,
            )

        lines = raw.splitlines(keepends=False)
        # Note: if raw ends with newline, splitlines doesn't create extra empty line unless keepends or trailing logic
        # Standard line count:
        total_lines = len(lines)
        if raw.endswith("\n") or raw.endswith("\r"):
            total_lines += 1  # count trailing empty line

        blank_lines = sum(1 for l in lines if len(l.strip()) == 0)
        leading_space_lines = sum(1 for l in lines if l.startswith(" "))
        tab_indented_lines = sum(1 for l in lines if l.startswith("\t"))

        return SourceStats(
            total_characters=len(raw),
            total_lines=total_lines,
            blank_lines=blank_lines,
            leading_space_lines=leading_space_lines,
            tab_indented_lines=tab_indented_lines,
            detected_line_ending=self._detect_line_ending(),
            file_path=self._file_path,
            language=self._language,
        )

    @classmethod
    def from_file(cls, path: str | Path, encoding: Optional[str] = None) -> SourceTextModel:
        """
        Load a file with exact byte-to-text fidelity.
        
        Attempts UTF-8, UTF-8-sig, and fallback encodings to preserve all characters.
        """
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        raw_bytes = p.read_bytes()

        # Detect encoding if not explicitly passed
        text = None
        encodings_to_try = [encoding] if encoding else ["utf-8-sig", "utf-8", "utf-16", "cp1252", "latin-1"]
        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                # Using newline='' via io.StringIO or reading bytes and decoding
                text = raw_bytes.decode(enc)
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if text is None:
            # Fallback with replacement to avoid crash
            text = raw_bytes.decode("utf-8", errors="replace")

        # Auto-detect language by extension
        ext = p.suffix.lower()
        language = cls.EXT_MAP.get(ext, "plain_text")

        return cls(text=text, language=language, file_path=str(p.resolve()))

    def save_to_file(self, path: str | Path, encoding: str = "utf-8") -> None:
        """Save raw text to a destination path."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # Write binary bytes directly to preserve exact line endings without OS translation
        p.write_bytes(self._raw_text.encode(encoding))
        self._file_path = str(p.resolve())
        self._stats.file_path = self._file_path
