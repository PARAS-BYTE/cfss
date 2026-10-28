"""
Configuration and Typing Settings for CodeFlow Studio.
Supports:
- Automated Mode with WPM fluctuation strictly between 30 and 45 WPM (Target 40 WPM).
- Multi-character word slip typos and backspace corrections.
- In-between mouse scroll-up, hover inspection, and scroll-down routines (typing pauses during mouse activity).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from codeflow.adapters.base import TextEntryMode


@dataclass
class TypingSettings:
    """Configurable parameters for typing cadence, wavy rhythm, human typos, and demo controls."""
    
    # 1. Autonomous Simulation Mode
    autonomous_mode_enabled: bool = True  # 1-Click Autonomous Human Simulation
    
    # 2. WPM Cadence & Fluctuation (Target 40 WPM, fluctuating 30 - 45 WPM)
    target_wpm: int = 40                  # Target 40 WPM
    wpm_fluctuation_enabled: bool = True  # Fluctuates naturally like a real human
    wpm_min: int = 30                     # Lower bound (30 WPM = 150 CPM)
    wpm_max: int = 45                     # Upper bound (45 WPM = 225 CPM)
    typing_rate_cpm: int = 200            # 40 WPM * 5 = 200 CPM base
    jitter_percent: int = 20              # Natural timing noise
    newline_pause_ms: int = 320           # Pause at line breaks
    initial_delay_seconds: float = 3.0    # Countdown before typing starts

    # 3. Wavy Speed Rhythm
    enable_wavy_cadence: bool = True      # Undulating speed wave
    wavy_amplitude_percent: int = 30      # Wave depth within WPM bounds
    wavy_cycle_length: int = 12           # Characters per wave period

    # 4. Human Mistakes (Word Slips & Multi-Backspace Corrections)
    enable_typos: bool = True             # Natural mistakes & auto-corrections
    typo_rate_percent: float = 4.0        # Mistake probability (noticeable human typos & fixes)
    enable_word_slip_typos: bool = True   # Sometimes types 2-4 wrong chars then backspaces all
    typo_max_slip_chars: int = 3          # Max characters slipped before noticing and backspacing
    key_hold_time_ms: int = 50            # Physical key press hold time (ms)
    cognitive_pause_ms: int = 350         # Pause on punctuation / syntax boundaries

    # 5. Automation Strategy & Entry Mode
    entry_mode: TextEntryMode = TextEntryMode.WIN32_PHYSICAL
    simulate_physical_keys: bool = True   # Emulates hardware Shift+Key for capitals and symbols

    # 6. Target Window & Safety
    target_hwnd: Optional[int] = None
    target_title: str = ""
    allow_any_target: bool = False
    pause_on_focus_loss: bool = True
    emergency_stop_key: str = "Escape"    # "Escape" or "F8"

    # 7. Mouse Motion, Random Inspection Scrolling & Hovering (Typing halts during mouse activity!)
    enable_mouse_motion: bool = True             # Gentle demonstration cursor drift
    mouse_intensity: str = "subtle"               # "subtle", "moderate", "active"
    mouse_interval_seconds: float = 4.0
    enable_inspection_scroll: bool = True         # Random scroll up little bit & come back
    enable_random_hovering: bool = True           # Hover cursor over code while inspecting
    inspection_scroll_interval_lines: int = 4     # Scroll inspection every 3-5 lines
    inspection_scroll_distance: int = 3           # Wheel scroll clicks upward then back
    inspection_pause_seconds: float = 1.8         # Pause & hover time while typing is stopped

    @property
    def base_char_delay(self) -> float:
        """Base delay in seconds per character based on CPM/WPM."""
        cpm = max(10, self.typing_rate_cpm)
        return 60.0 / cpm

    @property
    def newline_pause_seconds(self) -> float:
        return max(0.0, self.newline_pause_ms / 1000.0)

    @property
    def jitter_fraction(self) -> float:
        return max(0.0, min(0.8, self.jitter_percent / 100.0))

    @property
    def wavy_amplitude_fraction(self) -> float:
        return max(0.0, min(0.7, self.wavy_amplitude_percent / 100.0))

    def validate(self) -> None:
        """Clamp parameters to valid bounds."""
        if self.typing_rate_cpm > 250 and self.target_wpm == 40:
            self.typing_rate_cpm = max(10, self.typing_rate_cpm)
            self.target_wpm = max(10, int(self.typing_rate_cpm / 5))
            self.wpm_min = min(self.wpm_min, self.target_wpm)
            self.wpm_max = max(self.wpm_max, self.target_wpm)
        else:
            self.wpm_min = max(10, min(120, self.wpm_min))
            self.wpm_max = max(self.wpm_min + 5, min(200, self.wpm_max))
            self.target_wpm = max(self.wpm_min, min(self.wpm_max, self.target_wpm))
            self.typing_rate_cpm = self.target_wpm * 5

        self.jitter_percent = max(0, min(80, self.jitter_percent))
        self.newline_pause_ms = max(0, min(5000, self.newline_pause_ms))
        self.initial_delay_seconds = max(0.0, min(30.0, self.initial_delay_seconds))
        self.wavy_amplitude_percent = max(0, min(70, self.wavy_amplitude_percent))
        self.wavy_cycle_length = max(4, min(50, self.wavy_cycle_length))
        self.typo_rate_percent = max(0.0, min(100.0, self.typo_rate_percent))
        self.typo_max_slip_chars = max(1, min(6, self.typo_max_slip_chars))
        self.key_hold_time_ms = max(0, min(200, self.key_hold_time_ms))
        self.cognitive_pause_ms = max(0, min(2000, self.cognitive_pause_ms))
        self.inspection_scroll_interval_lines = max(2, min(50, self.inspection_scroll_interval_lines))
        self.inspection_scroll_distance = max(1, min(15, self.inspection_scroll_distance))
        self.inspection_pause_seconds = max(0.5, min(10.0, self.inspection_pause_seconds))
        if self.mouse_intensity not in ("subtle", "moderate", "active"):
            self.mouse_intensity = "subtle"

    def apply_autonomous_mode(self) -> None:
        """Configure exact 40 WPM (fluctuating 30 to 45 WPM), word typos, and scroll inspection."""
        self.autonomous_mode_enabled = True
        self.target_wpm = 40
        self.wpm_min = 30
        self.wpm_max = 45
        self.wpm_fluctuation_enabled = True
        self.typing_rate_cpm = 200
        self.jitter_percent = 22
        self.newline_pause_ms = 350
        self.enable_wavy_cadence = True
        self.wavy_amplitude_percent = 35
        self.wavy_cycle_length = 12
        self.enable_typos = True
        self.typo_rate_percent = 4.0
        self.enable_word_slip_typos = True
        self.typo_max_slip_chars = 3
        self.enable_mouse_motion = True
        self.enable_inspection_scroll = True
        self.enable_random_hovering = True
        self.inspection_scroll_interval_lines = 4
        self.inspection_scroll_distance = 3
        self.inspection_pause_seconds = 1.8
        self.mouse_intensity = "subtle"

    def apply_preset(self, preset_name: str) -> None:
        """Apply predefined typing persona presets."""
        name = preset_name.lower()
        if "autonomous" in name or "natural" in name or "human" in name:
            self.apply_autonomous_mode()
        elif "fast" in name or "pro" in name:
            self.autonomous_mode_enabled = False
            self.target_wpm = 110
            self.wpm_min = 90
            self.wpm_max = 130
            self.typing_rate_cpm = 550
            self.jitter_percent = 12
            self.newline_pause_ms = 120
            self.enable_wavy_cadence = True
            self.wavy_amplitude_percent = 20
            self.enable_typos = True
            self.typo_rate_percent = 0.8
            self.enable_word_slip_typos = False
            self.enable_mouse_motion = True
            self.enable_inspection_scroll = False
            self.mouse_intensity = "subtle"
        elif "casual" in name or "thinker" in name:
            self.autonomous_mode_enabled = True
            self.target_wpm = 35
            self.wpm_min = 25
            self.wpm_max = 42
            self.typing_rate_cpm = 175
            self.jitter_percent = 35
            self.newline_pause_ms = 480
            self.enable_wavy_cadence = True
            self.wavy_amplitude_percent = 45
            self.enable_typos = True
            self.typo_rate_percent = 3.5
            self.enable_word_slip_typos = True
            self.enable_mouse_motion = True
            self.enable_inspection_scroll = True
            self.enable_random_hovering = True
            self.mouse_intensity = "moderate"
        elif "verbatim" in name or "exact" in name:
            self.autonomous_mode_enabled = False
            self.target_wpm = 80
            self.wpm_min = 80
            self.wpm_max = 80
            self.wpm_fluctuation_enabled = False
            self.typing_rate_cpm = 400
            self.jitter_percent = 0
            self.newline_pause_ms = 0
            self.enable_wavy_cadence = False
            self.enable_typos = False
            self.typo_rate_percent = 0.0
            self.enable_mouse_motion = False
            self.enable_inspection_scroll = False

    def estimate_duration_seconds(self, char_count: int, line_count: int) -> float:
        if char_count == 0:
            return 0.0
        char_time = char_count * self.base_char_delay
        newline_time = max(0, line_count - 1) * self.newline_pause_seconds
        scroll_count = 0
        if self.enable_inspection_scroll and self.inspection_scroll_interval_lines > 0:
            scroll_count = max(0, line_count // self.inspection_scroll_interval_lines)
        scroll_time = scroll_count * (self.inspection_pause_seconds + 1.2)
        typo_time = 0.0
        if self.enable_typos and self.typo_rate_percent > 0:
            typo_count = int(char_count * (self.typo_rate_percent / 100.0))
            typo_time = typo_count * 0.55
        return self.initial_delay_seconds + char_time + newline_time + scroll_time + typo_time

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entry_mode"] = self.entry_mode.name
        return d

    @classmethod
    def from_dict(cls, data: dict) -> TypingSettings:
        copy = dict(data)
        if "entry_mode" in copy and isinstance(copy["entry_mode"], str):
            try:
                copy["entry_mode"] = TextEntryMode[copy["entry_mode"]]
            except KeyError:
                copy["entry_mode"] = TextEntryMode.WIN32_UNICODE
        settings = cls(**copy)
        settings.validate()
        return settings

    def save_to_file(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, path: Path | str) -> TypingSettings:
        p = Path(path)
        if not p.is_file():
            return cls()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except Exception:
            return cls()
