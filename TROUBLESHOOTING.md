# CodeFlow Studio — Troubleshooting & Integration Guide

This guide covers common integration challenges, target-editor behaviors (such as VS Code auto-indentation), Windows permissions, and emergency cancellation mechanisms.

---

## 1. VS Code Auto-Indentation and Formatting Artifacts

### Symptoms
- When CodeFlow Studio types indented blocks (e.g. inside Python functions or JS blocks), the result in VS Code has double indentation (e.g., 8 spaces instead of 4).
- Blank lines contain unintended spaces.

### Root Cause
When simulated typing presses the `Enter` key after an indented line, VS Code's built-in language server automatically indents the new line to match the previous block level. If CodeFlow Studio then sends the 4 leading spaces of the next source line, the line ends up doubly indented.

### Solutions

#### Solution A: Use CodeFlow's Line-by-Line Streaming Mode (Recommended for Zero-Config)
In the **Text Entry Strategy** dropdown in CodeFlow Studio, select:
> **Line-by-Line Stream (Clipboard)**

This enters each line as an atomic, perfectly preserved chunk with simulated pacing. VS Code accepts the line as pre-formatted and does not inject redundant auto-indentation.

#### Solution B: Configure VS Code Editor Settings (For Character-by-Character Demos)
If you want character-by-character animation:
1. Open VS Code Settings (`Ctrl+,` or `.vscode/settings.json`).
2. Add or set the following options:
   ```json
   {
     "editor.autoIndent": "none",
     "editor.formatOnType": false,
     "editor.trimAutoWhitespace": false
   }
   ```
3. Re-run your typing run. The output will now match 100% byte-for-byte.

---

## 2. VS Code Auto-Closing Brackets & Quotes Duplication

### Symptoms
- Brackets or quotes appear doubled in the editor (e.g., `def foo())):`, `[""hello""]`).

### Root Cause
VS Code automatically inserts a closing bracket or quote whenever an opening one is typed (`(`, `[`, `{`, `'`, `"`). When CodeFlow subsequent types the source text's closing bracket, it appears twice.

### Solutions
1. In VS Code settings (`settings.json`):
   ```json
   {
     "editor.autoClosingBrackets": "never",
     "editor.autoClosingQuotes": "never",
     "editor.autoClosingDelete": "never"
   }
   ```
2. Or use CodeFlow's **Line-by-Line Streaming** strategy.

---

## 3. Target Application Focus Lost Warning

### Symptoms
- Automation pauses immediately after start or mid-way through typing.
- A red warning banner displays: `⚠️ Target lost focus! Automation paused...`.

### Recovery Steps
1. CodeFlow Studio intentionally pauses typing if focus departs the designated target window to prevent unintended keystrokes from entering active chats, browsers, or system dialogs.
2. Simply click back into the target editor (VS Code) to restore focus.
3. CodeFlow Studio will automatically detect window focus return and resume typing after a brief 300ms settling pause.
4. Alternatively, click the **Resume** button on the warning banner or press `F6`.
5. If you want CodeFlow to type into whichever window is active without strict HWND matching, enable:
   > `☑ Allow typing into any active window`

---

## 4. Keystrokes Not Appearing in Elevated Applications (UIPI)

### Symptoms
- The countdown completes, the progress bar advances, but no text appears in the target editor.

### Root Cause (Windows UIPI)
Windows User Interface Privilege Isolation (UIPI) forbids standard non-elevated user processes from sending synthetic `SendInput` events into processes running with higher privileges (Administrator / Elevated).

### Solution
- If your VS Code or terminal was launched as Administrator, launch CodeFlow Studio with Administrator privileges as well.

---

## 5. Emergency Stop / Cancellation Failsafe

### How to Stop Immediately
1. **Escape Key (`Esc`)**: The primary global emergency cancellation key.
2. **Function Key (`F8`)**: Alternative hotkey if `Esc` is mapped to an editor command.
3. **Screen Corner Failsafe**: Slam the physical mouse cursor into the top-left corner `(0, 0)` of your display.
4. **UI Button**: Click the red **⏹ Stop Run (Esc)** button on the status panel.

---

## 6. Demonstration Mouse Motion Interrupts

### Expected Behavior
- Demonstration mouse drift is gentle and purely aesthetic.
- The instant you physically nudge or move your mouse (drift > 15px), CodeFlow Studio detects your physical override and immediately suspends automated mouse movement so it never fights with your hand.
