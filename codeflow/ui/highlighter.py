"""
Multi-Language Syntax Highlighter for CodeFlow Studio.

Supports Python, JavaScript, TypeScript, C/C++, Rust, Go, HTML, CSS, SQL,
JSON, and Markdown with dark-theme syntax coloring.
"""

from __future__ import annotations

import re
from typing import Dict, List, Pattern, Tuple

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument


class HighlightingRule:
    def __init__(self, pattern: QRegularExpression, format_rule: QTextCharFormat):
        self.pattern = pattern
        self.format = format_rule


class CodeHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter dynamically adaptable to different programming languages.
    """

    LANGUAGE_KEYWORDS: Dict[str, List[str]] = {
        "python": [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "finally", "for", "from",
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            "True", "False", "None",
        ],
        "javascript": [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "finally",
            "for", "function", "if", "import", "in", "instanceof", "new",
            "return", "super", "switch", "this", "throw", "try", "typeof",
            "var", "void", "while", "with", "yield", "let", "static", "await",
            "async", "true", "false", "null", "undefined",
        ],
        "typescript": [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "finally",
            "for", "function", "if", "import", "in", "instanceof", "new",
            "return", "super", "switch", "this", "throw", "try", "typeof",
            "var", "void", "while", "with", "yield", "let", "static", "await",
            "async", "true", "false", "null", "undefined", "interface", "type",
            "namespace", "declare", "abstract", "enum", "implements",
        ],
        "cpp": [
            "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor",
            "bool", "break", "case", "catch", "char", "char8_t", "char16_t",
            "char32_t", "class", "compl", "concept", "const", "consteval",
            "constexpr", "constinit", "const_cast", "continue", "co_await",
            "co_return", "co_yield", "decltype", "default", "delete", "do",
            "double", "dynamic_cast", "else", "enum", "explicit", "export",
            "extern", "false", "float", "for", "friend", "goto", "if", "inline",
            "int", "long", "mutable", "namespace", "new", "noexcept", "not",
            "not_eq", "nullptr", "operator", "or", "or_eq", "private", "protected",
            "public", "register", "reinterpret_cast", "requires", "return",
            "short", "signed", "sizeof", "static", "static_assert", "static_cast",
            "struct", "switch", "template", "this", "thread_local", "throw",
            "true", "try", "typedef", "typeid", "typename", "union", "unsigned",
            "using", "virtual", "void", "volatile", "wchar_t", "while", "xor", "xor_eq",
        ],
        "rust": [
            "as", "break", "const", "continue", "crate", "else", "enum", "extern",
            "false", "fn", "for", "if", "impl", "in", "let", "loop", "match",
            "mod", "move", "mut", "pub", "ref", "return", "self", "Self",
            "static", "struct", "super", "trait", "true", "type", "unsafe",
            "use", "where", "while", "async", "await", "dyn",
        ],
        "go": [
            "break", "default", "func", "interface", "select", "case", "defer",
            "go", "map", "struct", "chan", "else", "goto", "package", "switch",
            "const", "fallthrough", "if", "range", "type", "continue", "for",
            "import", "return", "var", "true", "false", "nil",
        ],
        "sql": [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "UPDATE", "DELETE",
            "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "GROUP", "BY", "ORDER",
            "HAVING", "LIMIT", "CREATE", "TABLE", "DROP", "ALTER", "ADD",
            "CONSTRAINT", "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "INDEX",
            "UNION", "ALL", "DISTINCT", "AS", "AND", "OR", "NOT", "IN", "IS",
            "NULL", "LIKE", "BETWEEN", "CASE", "WHEN", "THEN", "ELSE", "END",
        ],
    }

    def __init__(self, document: QTextDocument, language: str = "python"):
        super().__init__(document)
        self._language = language.lower()
        self._rules: List[HighlightingRule] = []
        self._init_formats()
        self._build_rules()

    def set_language(self, language: str) -> None:
        self._language = language.lower()
        self._build_rules()
        self.rehighlight()

    def _init_formats(self) -> None:
        # VS Code Dark+ Color Palette
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569cd6"))  # Blue
        self.keyword_format.setFontWeight(QFont.Bold)

        self.type_format = QTextCharFormat()
        self.type_format.setForeground(QColor("#4ec9b0"))  # Cyan/Teal

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#dcdcaa"))  # Yellow

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#ce9178"))  # Orange/Peach

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#b5cea8"))  # Light Green

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6a9955"))  # Green
        self.comment_format.setFontItalic(True)

        self.decorator_format = QTextCharFormat()
        self.decorator_format.setForeground(QColor("#c586c0"))  # Magenta

    def _build_rules(self) -> None:
        self._rules.clear()

        # Numbers (hex, float, int)
        number_rx = QRegularExpression(r"\b(0x[0-9a-fA-F]+|\d+(\.\d+)?([eE][+-]?\d+)?)\b")
        self._rules.append(HighlightingRule(number_rx, self.number_format))

        # Function definitions & calls
        func_rx = QRegularExpression(r"\b([A-Za-z_][A-Za-z0-9_]*)(?=\s*\()")
        self._rules.append(HighlightingRule(func_rx, self.function_format))

        # Decorators / Annotations
        if self._language == "python":
            dec_rx = QRegularExpression(r"@[A-Za-z_][A-Za-z0-9_\.]*")
            self._rules.append(HighlightingRule(dec_rx, self.decorator_format))

        # Strings
        # Double quoted strings
        self._rules.append(HighlightingRule(QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
        # Single quoted strings
        self._rules.append(HighlightingRule(QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))
        # Backtick strings (JS/TS/Go/Markdown)
        self._rules.append(HighlightingRule(QRegularExpression(r"`[^`\\]*(\\.[^`\\]*)*`"), self.string_format))

        # Keywords for current language
        keywords = self.LANGUAGE_KEYWORDS.get(self._language, self.LANGUAGE_KEYWORDS.get("python", []))
        for kw in keywords:
            kw_rx = QRegularExpression(rf"\b{re.escape(kw)}\b")
            self._rules.append(HighlightingRule(kw_rx, self.keyword_format))

        # Line comments based on language
        if self._language in ("python", "bash", "powershell", "yaml"):
            self._rules.append(HighlightingRule(QRegularExpression(r"#[^\n]*"), self.comment_format))
        elif self._language in ("javascript", "typescript", "cpp", "c", "rust", "go", "java", "csharp"):
            self._rules.append(HighlightingRule(QRegularExpression(r"//[^\n]*"), self.comment_format))
        elif self._language == "sql":
            self._rules.append(HighlightingRule(QRegularExpression(r"--[^\n]*"), self.comment_format))
        elif self._language in ("html", "xml", "markdown"):
            self._rules.append(HighlightingRule(QRegularExpression(r"<!--[^\n]*-->"), self.comment_format))

    def highlightBlock(self, text: str) -> None:
        """Apply rules to block of text."""
        for rule in self._rules:
            match_iterator = rule.pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)
