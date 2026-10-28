# CodeFlow Studio — Windows Desktop Code-Typing Simulator

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-PySide6%20(Qt%206)-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Tests](https://img.shields.io/badge/tests-pytest%2041%2F41%20passed-success.svg)](https://docs.pytest.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)](https://microsoft.com)

CodeFlow Studio is a precision desktop application for Windows built to simulate realistic, controlled code-typing behavior for software demonstrations, tutorial recordings, presentations, and authorized UI automation in Visual Studio Code and other editors.

---

## Key Highlights

- **100% Exact Source Preservation**: Never trims, normalizes, or alters tabs, leading spaces, blank lines, trailing newlines, or Unicode characters.
- **Undulating "Wavy" Typing Cadence**: Dynamically modulates typing speed in natural sinusoidal bursts and deceleration cycles, replicating how human programmers accelerate through familiar syntax and pause on complex constructs.
- **Realistic Human Typos & Self-Correction**: Simulates authentic mistakes by typing adjacent QWERTY keys, momentarily pausing to notice the error, pressing Backspace, and re-typing the correct letter (ensuring source code remains 100% exact).
- **In-Between Inspection Scrolling**: Smoothly moves the cursor and scrolls upward to "inspect/review" earlier code blocks. **Typing halts completely while scrolling is active**, and resumes seamlessly once the cursor returns.
- **1-Click Persona Presets**: Instantly switch between "🧑‍💻 Natural Human", "🏎️ Fast Coder", "☕ Casual Thinker", and "🎯 Precision Exact".
- **Precision Keyboard Automation**:
  - **Win32 SendInput Direct Unicode**: Emits raw Unicode code points directly without shifting keys, immune to keyboard layout mismatches and shortcut accidental triggering.
  - **Line-by-Line Streaming (Clipboard Paced)**: Zero-configuration solution for VS Code that prevents auto-indent doubling and auto-bracket duplicates.
  - **PyAutoGUI Keystrokes**: Standard virtual key dispatch.
- **Target-Window Safety & Focus Tracking**: Monitors the active foreground window in real-time. Immediately pauses automation if focus leaves the target window, presenting a clear warning banner and recovery steps.
- **Demonstration Mouse Motion**: Optional subtle cursor drift with instant user-override cancellation (disengages automatically if physical mouse movement is detected).
- **Responsive Threaded UI**: Modern tabbed interface with real-time progress bars, live CPM indicators, and quick-load sample buttons for Python, JS, C++, and Unicode.
- **Built-in Text Fidelity Comparator**: Character-by-character and line-by-line verification dialog that diagnoses common IDE artifacts (auto-indent, duplicate brackets, line ending conversions).

---

## Project Structure

```
Killer (Bot)/
├── codeflow/
│   ├── __init__.py
│   ├── app.py                     # Main application entry point
│   ├── config.py                  # TypingSettings dataclass & serialization
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py                # BaseKeyboardAdapter interface & TextEntryMode enum
│   │   ├── win32_adapter.py       # Win32 SendInput Unicode adapter (64-bit ctypes)
│   │   ├── pyautogui_adapter.py   # PyAutoGUI keystroke adapter
│   │   ├── clipboard_adapter.py   # Paced line-by-line clipboard stream adapter
│   │   └── mock_adapter.py        # In-memory recorder adapter for testing
│   ├── core/
│   │   ├── __init__.py
│   │   ├── source_model.py        # Exact source text fidelity model & metrics
│   │   ├── session.py             # SessionState machine & real-time metric tracking
│   │   ├── engine.py              # Typing cadence engine with jitter and pauses
│   │   ├── worker.py              # Qt signal bridge between engine and GUI
│   │   ├── emergency_stop.py      # Global Esc/F8 hotkey & corner failsafe monitor
│   │   ├── mouse_controller.py    # Gentle demonstration mouse motion controller
│   │   ├── comparator.py          # Diff engine & VS Code diagnostic analyzer
│   │   └── logger.py              # Safe logger (redacts code strings unless enabled)
│   ├── windows/
│   │   ├── __init__.py
│   │   └── window_detector.py     # Win32 HWND enumeration and focus tracking
│   └── ui/
│       ├── __init__.py
│       ├── styles.py              # VS Code-inspired dark theme stylesheet (QSS)
│       ├── line_numbers.py        # Gutter widget painting line numbers
│       ├── highlighter.py         # Multi-language QSyntaxHighlighter
│       ├── editor.py              # Monospace multiline CodeEditor
│       ├── settings_panel.py      # Cadence, target, and safety sidebar
│       ├── status_panel.py        # Controls, progress bar, and focus warning banner
│       ├── session_dialog.py      # Post-run metrics summary dialog
│       └── main_window.py         # Main desktop window with menus and toolbars
├── examples/
│   ├── sample_python.py           # Sample with tabs, spaces, and docstrings
│   ├── sample_javascript.js       # Sample with async/await and template literals
│   ├── sample_cpp.cpp             # Sample with tabs, templates, and pointers
│   ├── sample_unicode.py          # Sample with math symbols, emojis, and Asian scripts
│   └── sample_markdown.md         # Sample markdown table and code block
├── tests/
│   ├── __init__.py
│   ├── test_source_model.py       # Exact whitespace & newline preservation tests
│   ├── test_session.py            # State transitions & metrics tests
│   ├── test_engine.py             # Cadence, jitter, pause, resume & cancellation tests
│   ├── test_keyboard_adapters.py  # Win32, PyAutoGUI, Clipboard & Mock adapter tests
│   ├── test_window_detector.py    # Window enumeration & focus tracking tests
│   ├── test_mouse_controller.py   # Mouse motion & user override detection tests
│   ├── test_comparator.py         # Diff & IDE artifact diagnostic tests
│   └── test_ui.py                 # PySide6 offscreen GUI integration tests
├── codeflow.spec                  # PyInstaller executable build specification
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Pinned dependencies
├── TROUBLESHOOTING.md             # Integration guide, VS Code settings & troubleshooting
├── run.py                         # Application launcher
└── README.md                      # Documentation
```

---

## Installation

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Python 3.12 or newer

### Setup
1. Clone or extract the repository to your local directory:
   ```powershell
   cd "c:\Users\paras\OneDrive\Desktop\Killer (Bot)"
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

---

## Quick Start

Launch the CodeFlow Studio application:
```powershell
python run.py
```

### Basic Workflow
1. **Paste or Open Code**: Paste your snippet directly into the code editor or click **📂 Open File** to load a local file (`.py`, `.js`, `.cpp`, `.md`, etc.).
2. **Configure Cadence**:
   - Set **Typing Rate** (e.g. 360 CPM ≈ 72 WPM).
   - Set **Cadence Jitter** (e.g. 25%) for realistic human-like pacing.
   - Adjust **Line Break Pause** (e.g. 250 ms) for pauses between statements.
3. **Select Target Application**:
   - Click **🎯 Target Active VS Code** or pick your editor window from the dropdown.
   - If targeting another editor or plain text area, choose `[Any Active Window]`.
4. **Start Automation**:
   - Press **`F5`** or click **▶ Start Automation**.
   - An initial countdown (e.g. 3 seconds) gives you ample time to activate the target editor.
   - During typing, you can press **`F6`** to Pause/Resume, or hit **`Esc`** for immediate emergency stop.
5. **View Session Report**:
   - Upon completion, a comprehensive session summary reports total characters, active typing duration, effective CPM/WPM, and pause events.
   - Click **🔍 Compare & Verify in VS Code...** to open the built-in fidelity verifier.

---

## Manual VS Code Integration Test Procedure

To verify 100% source fidelity against Visual Studio Code:

1. **Configure VS Code** (or use Line-by-Line Streaming mode):
   In VS Code (`Ctrl+,` -> Open Settings JSON), add:
   ```json
   {
     "editor.autoIndent": "none",
     "editor.autoClosingBrackets": "never",
     "editor.autoClosingQuotes": "never"
   }
   ```
2. **Open a New Blank Document in VS Code**:
   - Open VS Code, press `Ctrl+N` to open a blank editor tab, and set language mode to match your code.
3. **Open Sample in CodeFlow Studio**:
   - In CodeFlow Studio, load `examples/sample_python.py` or `examples/sample_unicode.py`.
   - In the target dropdown, click **🎯 Target Active VS Code**.
4. **Run Automation**:
   - Click **▶ Start Automation (F5)**.
   - During the 3-second countdown, switch focus to your blank VS Code tab.
   - Watch the code type with natural humanized cadence.
5. **Verify Result**:
   - In VS Code, press `Ctrl+A` then `Ctrl+C` to copy the typed result to the clipboard.
   - In CodeFlow Studio, press `Ctrl+T` or click **Tools -> Verify Result in Comparator**.
   - Click **Paste from Clipboard** and then **Verify Exact Match**.
   - CodeFlow Studio computes character-level diffs and confirms **✅ 100% EXACT MATCH (Full Source Fidelity Confirmed)**.

---

## Emergency Stops and Safety Features

- **Global Hotkey (`Esc` or `F8`)**: A background listener actively monitors for the cancellation key regardless of which window is in focus.
- **Mouse Corner Failsafe**: Moving the physical mouse cursor into the top-left screen corner `(0, 0)` immediately aborts typing.
- **Automatic Pause on Focus Depart**: If you switch to another window, CodeFlow instantly pauses typing and displays a visible alert banner.
- **Physical Mouse Override**: Demonstration mouse movement continuously samples mouse position; any manual nudge immediately cancels automated cursor drift.
- **Safe Logging**: Source code is never recorded in log files unless explicitly enabled via developer flags.

---

## Automated Test Suite

Run all automated unit and integration tests using pytest:

```powershell
python -m pytest -v tests/
```

### Coverage
- `test_source_model.py`: Exact whitespace preservation (tabs, 4-space, 8-space, trailing), newlines (CRLF, LF, CR, mixed, consecutive blanks), Unicode symbols, file I/O byte fidelity.
- `test_session.py`: State machine transitions, pause/resume lifecycle, focus loss handling, effective CPM/WPM math.
- `test_engine.py`: Execution pacing, character delays, cadence jitter, line-break pauses, thread cancellation, and line streaming.
- `test_keyboard_adapters.py`: Win32 SendInput Unicode struct packing, PyAutoGUI adapter, clipboard stream adapter, and mock in-memory recorder.
- `test_window_detector.py`: Win32 HWND enumeration, foreground window detection, and target focus checks.
- `test_mouse_controller.py`: Demonstration drift lifecycle and immediate physical mouse override detection.
- `test_comparator.py`: Character-by-character diffs, auto-indent doubling diagnosis, duplicate closing brackets diagnosis, and unified diff output.
- `test_ui.py`: PySide6 CodeEditor, LineNumberArea, Highlighting, SettingsPanel, StatusPanel, MainWindow, and TextComparatorDialog in offscreen mode.

---

## Windows Executable Packaging (PyInstaller)

To build a standalone Windows executable (`.exe`):

1. Ensure `pyinstaller` is installed:
   ```powershell
   python -m pip install pyinstaller
   ```
2. Build using the provided specification file:
   ```powershell
   pyinstaller codeflow.spec
   ```
3. The compiled executable will be located at:
   `dist/CodeFlowStudio/CodeFlowStudio.exe`

---

## License

This software is provided for authorized coding demonstrations, educational presentations, and software development workflows.
