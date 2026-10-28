"""
Tests for SourceTextModel - fidelity, whitespace preservation, newlines, and unicode.
"""

import tempfile
from pathlib import Path
import pytest
from codeflow.core.source_model import SourceTextModel, LineEnding


class TestSourceTextModel:
    def test_empty_text(self):
        model = SourceTextModel("")
        assert model.raw_text == ""
        assert len(model) == 0
        assert model.stats.total_characters == 0
        assert model.stats.total_lines == 0
        assert model.stats.blank_lines == 0
        assert model.stats.detected_line_ending == LineEnding.NONE

    def test_exact_whitespace_preservation(self):
        text_with_spaces_and_tabs = (
            "def example():\n"
            "    # 4 spaces leading\n"
            "\t# 1 tab leading\n"
            "        # 8 spaces leading\n"
            "\t\t# 2 tabs leading\n"
            "    trailing space preserved   \n"
            "    tabs at end\t\t\n"
        )
        model = SourceTextModel(text_with_spaces_and_tabs)
        # Verify exact raw string match
        assert model.raw_text == text_with_spaces_and_tabs
        # Verify lines
        lines = model.get_lines(keep_ends=False)
        assert lines[0] == "def example():"
        assert lines[1] == "    # 4 spaces leading"
        assert lines[2] == "\t# 1 tab leading"
        assert lines[3] == "        # 8 spaces leading"
        assert lines[4] == "\t\t# 2 tabs leading"
        assert lines[5] == "    trailing space preserved   "
        assert lines[6] == "    tabs at end\t\t"

    def test_newlines_and_blank_lines(self):
        text_with_blanks = "line1\n\n\nline2\n   \n\t\nline3\n"
        model = SourceTextModel(text_with_blanks)
        assert model.raw_text == text_with_blanks
        assert model.stats.blank_lines >= 4
        # Check that consecutive blank lines are preserved
        lines = model.get_lines(keep_ends=False)
        assert lines[1] == ""
        assert lines[2] == ""
        assert lines[4] == "   "
        assert lines[5] == "\t"

    def test_crlf_vs_lf_line_endings(self):
        crlf_text = "line1\r\nline2\r\nline3\r\n"
        lf_text = "line1\nline2\nline3\n"
        cr_text = "line1\rline2\rline3\r"
        mixed_text = "line1\r\nline2\nline3\r"

        assert SourceTextModel(crlf_text).stats.detected_line_ending == LineEnding.CRLF
        assert SourceTextModel(lf_text).stats.detected_line_ending == LineEnding.LF
        assert SourceTextModel(cr_text).stats.detected_line_ending == LineEnding.CR
        assert SourceTextModel(mixed_text).stats.detected_line_ending == LineEnding.MIXED

    def test_unicode_and_special_characters(self):
        special_code = (
            '# Unicode and symbols test:\n'
            'message = "Hello, 世界 🌍! 🚀"\n'
            'math = "∑(x_i) ≥ 0 and α != β"\n'
            'escapes = `template \\n \\t \\" \\\'`\n'
            'brackets = { [ ( "key": 42 ) ] }\n'
        )
        model = SourceTextModel(special_code, language="python")
        assert model.raw_text == special_code
        assert model.stats.total_characters == len(special_code)
        assert model.character_at(special_code.index("世")) == "世"
        assert model.character_at(special_code.index("🚀")) == "🚀"

    def test_file_load_and_save_exact_fidelity(self):
        content = (
            "// C++ File with exact formatting\r\n"
            "#include <iostream>\r\n"
            "\r\n"
            "int main() {\r\n"
            "\tstd::cout << \"Test: 100% Exact\" << std::endl;\r\n"
            "\treturn 0;\r\n"
            "}\r\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.cpp"
            file_path.write_bytes(content.encode("utf-8"))

            loaded = SourceTextModel.from_file(file_path)
            assert loaded.raw_text == content
            assert loaded.language == "cpp"
            assert loaded.stats.detected_line_ending == LineEnding.CRLF

            out_path = Path(tmpdir) / "saved.cpp"
            loaded.save_to_file(out_path)
            assert out_path.read_bytes() == content.encode("utf-8")
