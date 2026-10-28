"""
Tests for SourceComparator - fidelity analysis, auto-indent/bracket diagnostics, and diff generation.
"""

import pytest
from codeflow.core.comparator import SourceComparator, DiscrepancyType


class TestSourceComparator:
    def test_exact_match(self):
        code = (
            "def calculate(x, y):\n"
            "    # Comment with spaces and tabs\n"
            "\tresult = (x + y) * 2\n"
            "    return result\n"
        )
        res = SourceComparator.compare(code, code)
        assert res.is_exact_match is True
        assert res.source_char_count == len(code)
        assert res.result_char_count == len(code)
        assert DiscrepancyType.EXACT_MATCH in res.discrepancy_types
        assert "100% Fidelity" in res.summary_markdown()

    def test_line_ending_difference(self):
        code_lf = "def foo():\n    return 42\n"
        code_crlf = "def foo():\r\n    return 42\r\n"
        res = SourceComparator.compare(code_lf, code_crlf)
        assert res.is_exact_match is False
        assert DiscrepancyType.LINE_ENDING_MISMATCH in res.discrepancy_types

    def test_auto_indent_divergence(self):
        source = (
            "def foo():\n"
            "    val = 1\n"
        )
        # IDE automatically added 4 extra spaces to line 2
        result = (
            "def foo():\n"
            "        val = 1\n"
        )
        res = SourceComparator.compare(source, result)
        assert res.is_exact_match is False
        assert DiscrepancyType.AUTO_INDENT_DIVERGENCE in res.discrepancy_types
        assert "autoIndent" in res.diagnostic_message

    def test_auto_bracket_duplication(self):
        source = 'print("hello")\n'
        # IDE auto-closing quotes/brackets duplicated the closing symbol
        result = 'print("hello"")\n'
        res = SourceComparator.compare(source, result)
        assert res.is_exact_match is False
        assert DiscrepancyType.AUTO_BRACKET_DUPLICATION in res.discrepancy_types
        assert "autoClosingBrackets" in res.diagnostic_message

    def test_truncation(self):
        source = "def long_function():\n    step1()\n    step2()\n    step3()\n"
        result = "def long_function():\n    step1()\n"
        res = SourceComparator.compare(source, result)
        assert res.is_exact_match is False
        assert DiscrepancyType.TRUNCATION in res.discrepancy_types
        assert "truncated" in res.diagnostic_message.lower()

    def test_first_diff_location(self):
        source = "line1\nline2 ABC\nline3\n"
        result = "line1\nline2 XYZ\nline3\n"
        res = SourceComparator.compare(source, result)
        assert res.is_exact_match is False
        assert res.first_diff_line == 2
        assert res.first_diff_col == 7
        assert res.first_diff_source_char == "A"
        assert res.first_diff_result_char == "X"
