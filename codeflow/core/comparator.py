"""
Text Comparison and Fidelity Verification for CodeFlow Studio.

Performs character-by-character and line-by-line comparison between original
source text and output text captured from target editors (e.g., VS Code).
Diagnoses common IDE artifacts such as auto-indent doubling, auto-closing brackets,
and line ending mismatches.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class DiscrepancyType(Enum):
    NONE = "None"
    EXACT_MATCH = "Exact Match"
    AUTO_INDENT_DIVERGENCE = "Indentation mismatch (Likely IDE auto-indent)"
    AUTO_BRACKET_DUPLICATION = "Bracket/Quote duplication (Likely IDE auto-closing brackets)"
    LINE_ENDING_MISMATCH = "Line ending mismatch (CRLF vs LF)"
    TRAILING_WHITESPACE = "Trailing whitespace difference"
    TRUNCATION = "Result text truncated or incomplete"
    GENERAL_MISMATCH = "Character mismatch"


@dataclass
class DiffResult:
    """Detailed comparison report between source text and result text."""
    is_exact_match: bool
    source_char_count: int
    result_char_count: int
    source_line_count: int
    result_line_count: int
    first_diff_line: Optional[int] = None
    first_diff_col: Optional[int] = None
    first_diff_source_char: Optional[str] = None
    first_diff_result_char: Optional[str] = None
    discrepancy_types: List[DiscrepancyType] = field(default_factory=list)
    unified_diff: str = ""
    diagnostic_message: str = ""

    def summary_markdown(self) -> str:
        """Format the comparison result into a clean markdown report."""
        if self.is_exact_match:
            return (
                f"### Verification Result: EXACT MATCH (100% Fidelity)\n\n"
                f"- **Total Characters**: {self.source_char_count}\n"
                f"- **Total Lines**: {self.source_line_count}\n"
                f"- **Indentation & Whitespace**: Identical\n"
                f"- **Line Endings & Symbols**: Identical\n"
            )

        types_str = ", ".join(d.value for d in self.discrepancy_types)
        report = [
            f"### Verification Result: DISCREPANCIES DETECTED\n",
            f"- **Exact Match**: False",
            f"- **Source Length**: {self.source_char_count} chars ({self.source_line_count} lines)",
            f"- **Result Length**: {self.result_char_count} chars ({self.result_line_count} lines)",
            f"- **First Discrepancy**: Line {self.first_diff_line}, Column {self.first_diff_col}",
            f"- **Issue Classification**: {types_str}",
            f"\n**Diagnostic Diagnosis**:\n{self.diagnostic_message}\n",
        ]

        if self.unified_diff:
            report.append("```diff\n" + self.unified_diff[:2000] + "\n```")
        return "\n".join(report)


class SourceComparator:
    """
    Compares original source code with actual editor result.
    """

    BRACKET_PAIRS = {
        "(": ")",
        "[": "]",
        "{": "}",
        "'": "'",
        '"': '"',
        "`": "`",
    }

    @classmethod
    def compare(cls, source_text: str, result_text: str) -> DiffResult:
        """
        Perform rigorous verification between source and output text.
        """
        source_chars = len(source_text)
        result_chars = len(result_text)

        source_lines = source_text.splitlines(keepends=True)
        result_lines = result_text.splitlines(keepends=True)

        if source_text == result_text:
            return DiffResult(
                is_exact_match=True,
                source_char_count=source_chars,
                result_char_count=result_chars,
                source_line_count=len(source_lines),
                result_line_count=len(result_lines),
                discrepancy_types=[DiscrepancyType.EXACT_MATCH],
                diagnostic_message="All characters, indentation, whitespace, and line breaks are 100% identical.",
            )

        discrepancies: List[DiscrepancyType] = []
        diagnostics: List[str] = []

        # Check line endings mismatch if normalized text matches
        norm_source = source_text.replace("\r\n", "\n").replace("\r", "\n")
        norm_result = result_text.replace("\r\n", "\n").replace("\r", "\n")
        if norm_source == norm_result:
            discrepancies.append(DiscrepancyType.LINE_ENDING_MISMATCH)
            diagnostics.append(
                "Source text and result text are identical in content, but differ in line ending style (CRLF vs LF). "
                "VS Code or your editor converted newlines upon paste/entry."
            )

        # Check truncation
        if source_text.startswith(result_text) and len(result_text) < len(source_text):
            discrepancies.append(DiscrepancyType.TRUNCATION)
            diagnostics.append(
                f"Result text was truncated at character {len(result_text)} / {len(source_text)}. "
                "The automation session may have been stopped early or interrupted by focus loss."
            )

        # Locate first mismatch position
        min_len = min(source_chars, result_chars)
        first_diff_idx = None
        for i in range(min_len):
            if source_text[i] != result_text[i]:
                first_diff_idx = i
                break

        if first_diff_idx is None and source_chars != result_chars:
            first_diff_idx = min_len

        # Calculate line and column of first mismatch
        first_line = 1
        first_col = 1
        source_char = None
        result_char = None

        if first_diff_idx is not None:
            preceding = source_text[:first_diff_idx]
            first_line = preceding.count("\n") + 1
            last_nl = preceding.rfind("\n")
            first_col = first_diff_idx + 1 if last_nl == -1 else first_diff_idx - last_nl
            source_char = source_text[first_diff_idx] if first_diff_idx < source_chars else "<EOF>"
            result_char = result_text[first_diff_idx] if first_diff_idx < result_chars else "<EOF>"

        # Check for auto-indent divergence
        # Typically seen as excess leading whitespace on lines after newlines
        auto_indent_found = False
        bracket_duplication_found = False

        diff_gen = list(difflib.ndiff(
            source_text.splitlines(keepends=False),
            result_text.splitlines(keepends=False)
        ))

        for diff_line in diff_gen:
            if diff_line.startswith("+ "):
                added = diff_line[2:]
                # If the line only added leading spaces/tabs
                if added.startswith("    ") or added.startswith("\t"):
                    auto_indent_found = True
                # Check for double closing brackets
                if any(p in added for p in ("))", "]]", "}}", "''", '""')):
                    bracket_duplication_found = True

        if auto_indent_found and DiscrepancyType.AUTO_INDENT_DIVERGENCE not in discrepancies:
            discrepancies.append(DiscrepancyType.AUTO_INDENT_DIVERGENCE)
            diagnostics.append(
                "Excess leading indentation detected. In VS Code, auto-indentation was likely triggered when Enter was pressed. "
                "Remedy: Set \"editor.autoIndent\": \"none\" in VS Code settings, or use Line/Clipboard Streaming mode."
            )

        if bracket_duplication_found and DiscrepancyType.AUTO_BRACKET_DUPLICATION not in discrepancies:
            discrepancies.append(DiscrepancyType.AUTO_BRACKET_DUPLICATION)
            diagnostics.append(
                "Duplicate brackets/quotes detected. VS Code's auto-closing brackets inserted a closing pair automatically. "
                "Remedy: Set \"editor.autoClosingBrackets\": \"never\" and \"editor.autoClosingQuotes\": \"never\" in VS Code."
            )

        if not discrepancies:
            discrepancies.append(DiscrepancyType.GENERAL_MISMATCH)
            diagnostics.append(
                f"Character difference at line {first_line}, column {first_col}: "
                f"expected {repr(source_char)}, found {repr(result_char)}."
            )

        # Generate unified diff string
        unified = "".join(difflib.unified_diff(
            source_text.splitlines(keepends=True),
            result_text.splitlines(keepends=True),
            fromfile="original_source",
            tofile="editor_result",
            n=3,
        ))

        return DiffResult(
            is_exact_match=False,
            source_char_count=source_chars,
            result_char_count=result_chars,
            source_line_count=len(source_lines),
            result_line_count=len(result_lines),
            first_diff_line=first_line,
            first_diff_col=first_col,
            first_diff_source_char=source_char,
            first_diff_result_char=result_char,
            discrepancy_types=discrepancies,
            unified_diff=unified,
            diagnostic_message="\n\n".join(diagnostics),
        )
