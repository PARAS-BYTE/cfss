"""
Settings Sidebar Panel for CodeFlow Studio.

Features:
- Prominent 1-Click Autonomous Human Simulation Mode (40 WPM, fluctuating 30-45 WPM, word typos, scroll & hover).
- Dynamic Duration Estimation card with character, line, and overhead calculations.
- Clean Preset Profiles (Natural, Fast, Casual, Verbatim).
- Categorized Settings Tabs (Speed, Typos, Mouse, Target) housed inside a smooth QScrollArea.
- Target window selection with 1-click VS Code detection.
"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from codeflow.adapters.base import TextEntryMode
from codeflow.config import TypingSettings
from codeflow.windows.window_detector import WindowDetector, WindowInfo


class SettingsPanel(QWidget):
    """
    Modern settings sidebar with Autonomous Mode hero card, dynamic duration,
    and categorized tabs in a smooth dark-themed scroll area.
    """
    settings_changed = Signal(TypingSettings)
    request_vscode_detect = Signal()

    def __init__(self, window_detector: WindowDetector, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.window_detector = window_detector
        self._settings = TypingSettings()
        self._detected_windows: List[WindowInfo] = []
        self._last_chars: int = 0
        self._last_lines: int = 0

        self._init_ui()
        self.refresh_windows()

    @property
    def settings(self) -> TypingSettings:
        return self._settings

    def _init_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll Area to prevent any vertical squishing on any display
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("settingsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(12, 12, 14, 14)
        layout.setSpacing(12)

        # 1. Autonomous Simulation Hero Card
        self.hero_card = QFrame()
        self.hero_card.setObjectName("autonomousHeroCard")
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(12, 12, 12, 12)
        hero_layout.setSpacing(8)

        hero_top_row = QHBoxLayout()
        hero_title_box = QVBoxLayout()
        hero_title_box.setSpacing(4)

        hero_title = QLabel("AUTONOMOUS HUMAN SIMULATION")
        hero_title.setObjectName("heroTitle")
        hero_title_box.addWidget(hero_title)

        hero_sub = QLabel(
            "40 WPM wavy cadence (30-45 WPM) • Word-slip typos & corrections • Mouse inspection scrolling & hovering"
        )
        hero_sub.setObjectName("heroSubtitle")
        hero_sub.setWordWrap(True)
        hero_title_box.addWidget(hero_sub)
        hero_top_row.addLayout(hero_title_box, stretch=1)

        self.autonomous_toggle_btn = QPushButton("ACTIVE")
        self.autonomous_toggle_btn.setObjectName("autonomousToggleBtn")
        self.autonomous_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.autonomous_toggle_btn.clicked.connect(self._toggle_autonomous_mode)
        hero_top_row.addWidget(self.autonomous_toggle_btn, alignment=Qt.AlignTop)
        hero_layout.addLayout(hero_top_row)

        layout.addWidget(self.hero_card)

        # 1.5 Real-Time Estimated Duration Card
        self.est_card = QFrame()
        self.est_card.setObjectName("estCard")
        est_layout = QVBoxLayout(self.est_card)
        est_layout.setContentsMargins(12, 10, 12, 10)
        est_layout.setSpacing(4)

        est_header_row = QHBoxLayout()
        est_title = QLabel("ESTIMATED RUNTIME")
        est_title.setObjectName("estTitle")
        est_header_row.addWidget(est_title)

        self.duration_badge = QLabel("~00:00")
        self.duration_badge.setObjectName("estDurationBadge")
        est_header_row.addWidget(self.duration_badge, alignment=Qt.AlignRight)
        est_layout.addLayout(est_header_row)

        self.est_details_label = QLabel("0 characters • 0 lines • Calculated at 40 WPM")
        self.est_details_label.setObjectName("estDetailsLabel")
        self.est_details_label.setWordWrap(True)
        est_layout.addWidget(self.est_details_label)

        layout.addWidget(self.est_card)

        # 2. Quick Persona Presets
        preset_group = QGroupBox("PRESET TYPING PROFILES")
        preset_group.setObjectName("presetGroup")
        preset_layout = QGridLayout(preset_group)
        preset_layout.setContentsMargins(10, 16, 10, 10)
        preset_layout.setHorizontalSpacing(8)
        preset_layout.setVerticalSpacing(8)

        self.btn_preset_human = QPushButton("NATURAL 40 WPM")
        self.btn_preset_human.setProperty("class", "presetBtn")
        self.btn_preset_human.setMinimumHeight(34)
        self.btn_preset_human.setToolTip("Target 40 WPM (fluctuates 30-45 WPM), word slips & backspaces, inspection scroll & hover.")
        self.btn_preset_human.clicked.connect(lambda: self._apply_preset("natural"))
        preset_layout.addWidget(self.btn_preset_human, 0, 0)

        self.btn_preset_fast = QPushButton("FAST 110 WPM")
        self.btn_preset_fast.setProperty("class", "presetBtn")
        self.btn_preset_fast.setMinimumHeight(34)
        self.btn_preset_fast.setToolTip("Fast typing (90-130 WPM), minimal typos, subtle drift.")
        self.btn_preset_fast.clicked.connect(lambda: self._apply_preset("fast"))
        preset_layout.addWidget(self.btn_preset_fast, 0, 1)

        self.btn_preset_casual = QPushButton("CASUAL 35 WPM")
        self.btn_preset_casual.setProperty("class", "presetBtn")
        self.btn_preset_casual.setMinimumHeight(34)
        self.btn_preset_casual.setToolTip("Relaxed 35 WPM (25-42 WPM), frequent thinking pauses, word typos & inspection scrolls.")
        self.btn_preset_casual.clicked.connect(lambda: self._apply_preset("casual"))
        preset_layout.addWidget(self.btn_preset_casual, 1, 0)

        self.btn_preset_verbatim = QPushButton("EXACT VERBATIM")
        self.btn_preset_verbatim.setProperty("class", "presetBtn")
        self.btn_preset_verbatim.setMinimumHeight(34)
        self.btn_preset_verbatim.setToolTip("Pure linear typing with 0% typos and exact linear pacing.")
        self.btn_preset_verbatim.clicked.connect(lambda: self._apply_preset("verbatim"))
        preset_layout.addWidget(self.btn_preset_verbatim, 1, 1)

        layout.addWidget(preset_group)

        # 3. Categorized Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        self.tabs.setMinimumHeight(440)

        # TAB 1: Speed & Fluctuations (30 - 45 WPM)
        tab_speed = QWidget()
        tab_speed_layout = QVBoxLayout(tab_speed)
        tab_speed_layout.setContentsMargins(12, 14, 12, 14)
        tab_speed_layout.setSpacing(14)

        # Target WPM Header & Slider Card
        speed_card = QFrame()
        speed_card.setObjectName("innerControlCard")
        speed_layout = QVBoxLayout(speed_card)
        speed_layout.setSpacing(8)

        self.target_wpm_label = QLabel("TARGET SPEED: 40 WPM (200 CPM)")
        self.target_wpm_label.setObjectName("paramHeaderLabel")
        speed_layout.addWidget(self.target_wpm_label)

        self.target_wpm_slider = QSlider(Qt.Horizontal)
        self.target_wpm_slider.setRange(20, 100)
        self.target_wpm_slider.setValue(self._settings.target_wpm)
        self.target_wpm_slider.valueChanged.connect(self._on_target_wpm_changed)
        speed_layout.addWidget(self.target_wpm_slider)
        tab_speed_layout.addWidget(speed_card)

        # Fluctuation Range (30 to 45 WPM) Card
        fluct_card = QFrame()
        fluct_card.setObjectName("innerControlCard")
        fluct_layout = QVBoxLayout(fluct_card)
        fluct_layout.setSpacing(8)

        self.fluct_check = QCheckBox("ENABLE SPEED FLUCTUATION (30 - 45 WPM)")
        self.fluct_check.setChecked(self._settings.wpm_fluctuation_enabled)
        self.fluct_check.stateChanged.connect(self._on_fluct_enabled_changed)
        fluct_layout.addWidget(self.fluct_check)

        self.fluct_bounds_label = QLabel("FLUCTUATION BOUNDS: 30 WPM (MIN) — 45 WPM (MAX)")
        self.fluct_bounds_label.setObjectName("paramSubLabel")
        fluct_layout.addWidget(self.fluct_bounds_label)

        min_row = QHBoxLayout()
        min_lbl = QLabel("MIN WPM:")
        min_lbl.setFixedWidth(70)
        min_row.addWidget(min_lbl)
        self.min_wpm_slider = QSlider(Qt.Horizontal)
        self.min_wpm_slider.setRange(15, 60)
        self.min_wpm_slider.setValue(self._settings.wpm_min)
        self.min_wpm_slider.valueChanged.connect(self._on_min_wpm_changed)
        min_row.addWidget(self.min_wpm_slider)
        fluct_layout.addLayout(min_row)

        max_row = QHBoxLayout()
        max_lbl = QLabel("MAX WPM:")
        max_lbl.setFixedWidth(70)
        max_row.addWidget(max_lbl)
        self.max_wpm_slider = QSlider(Qt.Horizontal)
        self.max_wpm_slider.setRange(25, 90)
        self.max_wpm_slider.setValue(self._settings.wpm_max)
        self.max_wpm_slider.valueChanged.connect(self._on_max_wpm_changed)
        max_row.addWidget(self.max_wpm_slider)
        fluct_layout.addLayout(max_row)

        tab_speed_layout.addWidget(fluct_card)

        # Delays Card
        delays_card = QFrame()
        delays_card.setObjectName("innerControlCard")
        delays_layout = QVBoxLayout(delays_card)
        delays_layout.setSpacing(8)

        self.pause_label = QLabel("LINE BREAK PAUSE: 320 MS")
        self.pause_label.setObjectName("paramHeaderLabel")
        delays_layout.addWidget(self.pause_label)
        self.pause_slider = QSlider(Qt.Horizontal)
        self.pause_slider.setRange(0, 1500)
        self.pause_slider.setSingleStep(50)
        self.pause_slider.setValue(self._settings.newline_pause_ms)
        self.pause_slider.valueChanged.connect(self._on_pause_changed)
        delays_layout.addWidget(self.pause_slider)

        self.delay_label = QLabel("INITIAL COUNTDOWN DELAY: 3.0 SECONDS")
        self.delay_label.setObjectName("paramHeaderLabel")
        delays_layout.addWidget(self.delay_label)
        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setRange(0, 10)
        self.delay_slider.setValue(int(self._settings.initial_delay_seconds))
        self.delay_slider.valueChanged.connect(self._on_delay_changed)
        delays_layout.addWidget(self.delay_slider)

        tab_speed_layout.addWidget(delays_card)
        tab_speed_layout.addStretch()
        self.tabs.addTab(tab_speed, "SPEED")

        # TAB 2: Word Mistakes & Typos
        tab_typos = QWidget()
        tab_typos_layout = QVBoxLayout(tab_typos)
        tab_typos_layout.setContentsMargins(12, 14, 12, 14)
        tab_typos_layout.setSpacing(14)

        typo_card = QFrame()
        typo_card.setObjectName("innerControlCard")
        typo_card_layout = QVBoxLayout(typo_card)
        typo_card_layout.setSpacing(10)

        self.typos_check = QCheckBox("SIMULATE HUMAN MISTAKES & AUTO-CORRECTIONS")
        self.typos_check.setChecked(self._settings.enable_typos)
        self.typos_check.stateChanged.connect(self._on_typos_enabled_changed)
        typo_card_layout.addWidget(self.typos_check)

        self.word_slip_check = QCheckBox("MULTI-LETTER WORD SLIPS (TYPO THEN RAPID BACKSPACE)")
        self.word_slip_check.setChecked(self._settings.enable_word_slip_typos)
        self.word_slip_check.setToolTip("Types 2-3 mistaken adjacent letters, pauses in realization, then rapidly hits Backspace and types the right letters.")
        self.word_slip_check.stateChanged.connect(self._on_word_slip_changed)
        typo_card_layout.addWidget(self.word_slip_check)

        self.typo_rate_label = QLabel("MISTAKE FREQUENCY: 4.0%")
        self.typo_rate_label.setObjectName("paramHeaderLabel")
        typo_card_layout.addWidget(self.typo_rate_label)

        self.typo_rate_slider = QSlider(Qt.Horizontal)
        self.typo_rate_slider.setRange(0, 80)
        self.typo_rate_slider.setValue(int(self._settings.typo_rate_percent * 10))
        self.typo_rate_slider.valueChanged.connect(self._on_typo_rate_changed)
        typo_card_layout.addWidget(self.typo_rate_slider)

        tab_typos_layout.addWidget(typo_card)

        # Keystroke dynamics card
        dynamics_card = QFrame()
        dynamics_card.setObjectName("innerControlCard")
        dynamics_layout = QVBoxLayout(dynamics_card)
        dynamics_layout.setSpacing(8)

        self.hold_label = QLabel("KEY PRESS HOLD DURATION: 50 MS")
        self.hold_label.setObjectName("paramHeaderLabel")
        dynamics_layout.addWidget(self.hold_label)
        self.hold_slider = QSlider(Qt.Horizontal)
        self.hold_slider.setRange(10, 120)
        self.hold_slider.setValue(self._settings.key_hold_time_ms)
        self.hold_slider.valueChanged.connect(self._on_hold_changed)
        dynamics_layout.addWidget(self.hold_slider)

        self.cog_label = QLabel("PUNCTUATION COGNITIVE PAUSE: 350 MS")
        self.cog_label.setObjectName("paramHeaderLabel")
        dynamics_layout.addWidget(self.cog_label)
        self.cog_slider = QSlider(Qt.Horizontal)
        self.cog_slider.setRange(50, 1000)
        self.cog_slider.setValue(self._settings.cognitive_pause_ms)
        self.cog_slider.valueChanged.connect(self._on_cog_changed)
        dynamics_layout.addWidget(self.cog_slider)

        tab_typos_layout.addWidget(dynamics_card)

        typo_info = QLabel("NOTE: When a mistake happens, CodeFlow taps Backspace multiple times to fix the slip. Final source code remains 100% exact.")
        typo_info.setWordWrap(True)
        typo_info.setObjectName("infoCalloutLabel")
        tab_typos_layout.addWidget(typo_info)

        tab_typos_layout.addStretch()
        self.tabs.addTab(tab_typos, "TYPOS")

        # TAB 3: Mouse, Scroll Up/Down & Hovering
        tab_mouse = QWidget()
        tab_mouse_layout = QVBoxLayout(tab_mouse)
        tab_mouse_layout.setContentsMargins(12, 14, 12, 14)
        tab_mouse_layout.setSpacing(14)

        mouse_feat_card = QFrame()
        mouse_feat_card.setObjectName("innerControlCard")
        mouse_feat_layout = QVBoxLayout(mouse_feat_card)
        mouse_feat_layout.setSpacing(10)

        self.scroll_check = QCheckBox("INSPECTION SCROLL UP & RETURN (TYPING HALTS)")
        self.scroll_check.setChecked(self._settings.enable_inspection_scroll)
        self.scroll_check.setToolTip("At intervals, scrolls up to inspect earlier code, then returns down. Typing stops completely while mouse moves!")
        self.scroll_check.stateChanged.connect(self._on_scroll_enabled_changed)
        mouse_feat_layout.addWidget(self.scroll_check)

        self.hover_check = QCheckBox("RANDOM MOUSE HOVERING ACROSS CODE LINES")
        self.hover_check.setChecked(self._settings.enable_random_hovering)
        self.hover_check.setToolTip("Gently hovers cursor over functions, lines, and tokens as if reading.")
        self.hover_check.stateChanged.connect(self._on_hover_enabled_changed)
        mouse_feat_layout.addWidget(self.hover_check)

        self.scroll_int_label = QLabel("SCROLL INSPECTION INTERVAL: EVERY 4 LINES")
        self.scroll_int_label.setObjectName("paramHeaderLabel")
        mouse_feat_layout.addWidget(self.scroll_int_label)

        self.scroll_int_slider = QSlider(Qt.Horizontal)
        self.scroll_int_slider.setRange(2, 20)
        self.scroll_int_slider.setValue(self._settings.inspection_scroll_interval_lines)
        self.scroll_int_slider.valueChanged.connect(self._on_scroll_interval_changed)
        mouse_feat_layout.addWidget(self.scroll_int_slider)

        self.scroll_pause_label = QLabel("INSPECTION / HOVER PAUSE: 1.8 SECONDS")
        self.scroll_pause_label.setObjectName("paramHeaderLabel")
        mouse_feat_layout.addWidget(self.scroll_pause_label)

        self.scroll_pause_slider = QSlider(Qt.Horizontal)
        self.scroll_pause_slider.setRange(5, 50)
        self.scroll_pause_slider.setValue(int(self._settings.inspection_pause_seconds * 10))
        self.scroll_pause_slider.valueChanged.connect(self._on_scroll_pause_changed)
        mouse_feat_layout.addWidget(self.scroll_pause_slider)

        tab_mouse_layout.addWidget(mouse_feat_card)

        # Drift Card
        drift_card = QFrame()
        drift_card.setObjectName("innerControlCard")
        drift_layout = QVBoxLayout(drift_card)
        drift_layout.setSpacing(8)

        self.mouse_drift_check = QCheckBox("GENTLE BACKGROUND CURSOR DRIFT")
        self.mouse_drift_check.setChecked(self._settings.enable_mouse_motion)
        self.mouse_drift_check.stateChanged.connect(self._on_mouse_drift_changed)
        drift_layout.addWidget(self.mouse_drift_check)

        intensity_row = QHBoxLayout()
        intensity_lbl = QLabel("MOTION INTENSITY:")
        intensity_lbl.setFixedWidth(120)
        intensity_row.addWidget(intensity_lbl)
        self.mouse_intensity_combo = QComboBox()
        self.mouse_intensity_combo.addItems(["SUBTLE", "MODERATE", "ACTIVE"])
        self.mouse_intensity_combo.currentTextChanged.connect(self._on_mouse_intensity_changed)
        intensity_row.addWidget(self.mouse_intensity_combo)
        drift_layout.addLayout(intensity_row)

        tab_mouse_layout.addWidget(drift_card)

        mouse_tip = QLabel("FAILSAFE: If you physically move your mouse, all automated motion and scrolling stop immediately.")
        mouse_tip.setWordWrap(True)
        mouse_tip.setObjectName("infoCalloutLabel")
        tab_mouse_layout.addWidget(mouse_tip)

        tab_mouse_layout.addStretch()
        self.tabs.addTab(tab_mouse, "MOUSE")

        # TAB 4: Target & Automation Mode
        tab_target = QWidget()
        tab_target_layout = QVBoxLayout(tab_target)
        tab_target_layout.setContentsMargins(12, 14, 12, 14)
        tab_target_layout.setSpacing(14)

        target_card = QFrame()
        target_card.setObjectName("innerControlCard")
        target_card_layout = QVBoxLayout(target_card)
        target_card_layout.setSpacing(10)

        entry_lbl = QLabel("KEYBOARD ENTRY MODE:")
        entry_lbl.setObjectName("paramHeaderLabel")
        target_card_layout.addWidget(entry_lbl)

        self.entry_mode_combo = QComboBox()
        self.entry_mode_combo.addItem("Physical Keystrokes (Shift+Key - Real Keyboard)", TextEntryMode.WIN32_PHYSICAL)
        self.entry_mode_combo.addItem("Direct Unicode (Win32 SendInput - Layout Independent)", TextEntryMode.WIN32_UNICODE)
        self.entry_mode_combo.addItem("Line-by-Line Stream (Clipboard Paced)", TextEntryMode.CLIPBOARD_LINE)
        self.entry_mode_combo.addItem("Standard Keystrokes (PyAutoGUI)", TextEntryMode.PYAUTOGUI)
        self.entry_mode_combo.currentIndexChanged.connect(self._on_entry_mode_changed)
        target_card_layout.addWidget(self.entry_mode_combo)

        tgt_win_lbl = QLabel("TARGET APPLICATION WINDOW:")
        tgt_win_lbl.setObjectName("paramHeaderLabel")
        target_card_layout.addWidget(tgt_win_lbl)

        target_row = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.currentIndexChanged.connect(self._on_target_selected)
        target_row.addWidget(self.target_combo, stretch=1)

        self.refresh_btn = QPushButton("REFRESH")
        self.refresh_btn.setToolTip("Refresh window list")
        self.refresh_btn.clicked.connect(self.refresh_windows)
        target_row.addWidget(self.refresh_btn)
        target_card_layout.addLayout(target_row)

        self.detect_vsc_btn = QPushButton("TARGET ACTIVE VS CODE")
        self.detect_vsc_btn.setObjectName("detectVscBtn")
        self.detect_vsc_btn.clicked.connect(self._detect_vscode)
        target_card_layout.addWidget(self.detect_vsc_btn)

        self.allow_any_check = QCheckBox("ALLOW TYPING INTO ANY ACTIVE WINDOW")
        self.allow_any_check.setChecked(self._settings.allow_any_target)
        self.allow_any_check.stateChanged.connect(self._on_allow_any_changed)
        target_card_layout.addWidget(self.allow_any_check)

        self.focus_pause_check = QCheckBox("AUTO-PAUSE IF TARGET LOSES FOCUS")
        self.focus_pause_check.setChecked(self._settings.pause_on_focus_loss)
        self.focus_pause_check.stateChanged.connect(self._on_focus_pause_changed)
        target_card_layout.addWidget(self.focus_pause_check)

        hotkey_row = QHBoxLayout()
        hotkey_lbl = QLabel("EMERGENCY STOP KEY:")
        hotkey_lbl.setObjectName("paramHeaderLabel")
        hotkey_row.addWidget(hotkey_lbl)
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["Escape", "F8"])
        self.hotkey_combo.currentTextChanged.connect(self._on_hotkey_changed)
        hotkey_row.addWidget(self.hotkey_combo)
        target_card_layout.addLayout(hotkey_row)

        tab_target_layout.addWidget(target_card)
        tab_target_layout.addStretch()
        self.tabs.addTab(tab_target, "TARGET")

        layout.addWidget(self.tabs)
        layout.addStretch()

        self.scroll_area.setWidget(content_widget)
        root_layout.addWidget(self.scroll_area)

    def _toggle_autonomous_mode(self) -> None:
        """Toggle autonomous human simulation mode."""
        new_val = not self._settings.autonomous_mode_enabled
        if new_val:
            self._settings.apply_autonomous_mode()
            self.autonomous_toggle_btn.setText("ACTIVE")
            self.autonomous_toggle_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981); "
                "color: #ffffff; font-weight: 800; border-radius: 6px; padding: 6px 14px; border: 1px solid #34d399;"
            )
        else:
            self._settings.autonomous_mode_enabled = False
            self.autonomous_toggle_btn.setText("OFF")
            self.autonomous_toggle_btn.setStyleSheet(
                "background-color: #1a2333; color: #94a3b8; font-weight: 700; border-radius: 6px; padding: 6px 14px; border: 1px solid #28374d;"
            )
        self._sync_ui_from_settings()
        self._emit_settings()

    def _apply_preset(self, preset_name: str) -> None:
        self._settings.apply_preset(preset_name)
        if self._settings.autonomous_mode_enabled:
            self.autonomous_toggle_btn.setText("ACTIVE")
            self.autonomous_toggle_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981); "
                "color: #ffffff; font-weight: 800; border-radius: 6px; padding: 6px 14px; border: 1px solid #34d399;"
            )
        else:
            self.autonomous_toggle_btn.setText("OFF")
            self.autonomous_toggle_btn.setStyleSheet(
                "background-color: #1a2333; color: #94a3b8; font-weight: 700; border-radius: 6px; padding: 6px 14px; border: 1px solid #28374d;"
            )
        self._sync_ui_from_settings()
        self._emit_settings()

    def _sync_ui_from_settings(self) -> None:
        self.target_wpm_slider.setValue(self._settings.target_wpm)
        cpm = self._settings.target_wpm * 5
        self.target_wpm_label.setText(f"TARGET SPEED: {self._settings.target_wpm} WPM (~{cpm} CPM)")

        self.fluct_check.setChecked(self._settings.wpm_fluctuation_enabled)
        self.min_wpm_slider.setValue(self._settings.wpm_min)
        self.max_wpm_slider.setValue(self._settings.wpm_max)
        self.fluct_bounds_label.setText(f"FLUCTUATION BOUNDS: {self._settings.wpm_min} WPM (MIN) — {self._settings.wpm_max} WPM (MAX)")

        self.pause_slider.setValue(self._settings.newline_pause_ms)
        self.pause_label.setText(f"LINE BREAK PAUSE: {self._settings.newline_pause_ms} MS")

        self.typos_check.setChecked(self._settings.enable_typos)
        self.word_slip_check.setChecked(self._settings.enable_word_slip_typos)
        self.typo_rate_slider.setValue(int(self._settings.typo_rate_percent * 10))
        self.typo_rate_label.setText(f"MISTAKE FREQUENCY: {self._settings.typo_rate_percent:.1f}%")

        self.hold_slider.setValue(self._settings.key_hold_time_ms)
        self.hold_label.setText(f"KEY PRESS HOLD DURATION: {self._settings.key_hold_time_ms} MS")

        self.cog_slider.setValue(self._settings.cognitive_pause_ms)
        self.cog_label.setText(f"PUNCTUATION COGNITIVE PAUSE: {self._settings.cognitive_pause_ms} MS")

        self.scroll_check.setChecked(self._settings.enable_inspection_scroll)
        self.hover_check.setChecked(self._settings.enable_random_hovering)
        self.scroll_int_slider.setValue(self._settings.inspection_scroll_interval_lines)
        self.scroll_int_label.setText(f"SCROLL INSPECTION INTERVAL: EVERY {self._settings.inspection_scroll_interval_lines} LINES")

        self.scroll_pause_slider.setValue(int(self._settings.inspection_pause_seconds * 10))
        self.scroll_pause_label.setText(f"INSPECTION / HOVER PAUSE: {self._settings.inspection_pause_seconds:.1f} SECONDS")

        self.mouse_drift_check.setChecked(self._settings.enable_mouse_motion)

        for idx in range(self.entry_mode_combo.count()):
            if self.entry_mode_combo.itemData(idx) == self._settings.entry_mode:
                self.entry_mode_combo.blockSignals(True)
                self.entry_mode_combo.setCurrentIndex(idx)
                self.entry_mode_combo.blockSignals(False)
                break

    def refresh_windows(self) -> None:
        self.target_combo.blockSignals(True)
        self.target_combo.clear()

        self._detected_windows = self.window_detector.list_windows(filter_empty=True)
        self.target_combo.addItem("[Any Active Window]", 0)

        selected_idx = 0
        for i, win in enumerate(self._detected_windows):
            item_text = f"[WIN] {win.title[:45]}" if len(win.title) > 45 else f"[WIN] {win.title}"
            if win.is_vscode:
                item_text = f"[VS CODE] {win.title[:42]}"
            self.target_combo.addItem(item_text, win.hwnd)

            if win.is_vscode and selected_idx == 0:
                selected_idx = i + 1

        self.target_combo.setCurrentIndex(selected_idx)
        self.target_combo.blockSignals(False)
        self._on_target_selected(selected_idx)

    def _detect_vscode(self) -> None:
        vsc_windows = self.window_detector.find_vscode_windows()
        if vsc_windows:
            target = vsc_windows[0]
            for idx in range(self.target_combo.count()):
                if self.target_combo.itemData(idx) == target.hwnd:
                    self.target_combo.setCurrentIndex(idx)
                    return
        else:
            self.refresh_windows()

    def _on_target_selected(self, index: int) -> None:
        hwnd = self.target_combo.itemData(index)
        if hwnd == 0:
            self._settings.target_hwnd = None
            self._settings.target_title = ""
            self._settings.allow_any_target = True
            self.allow_any_check.setChecked(True)
        else:
            self._settings.target_hwnd = hwnd
            for w in self._detected_windows:
                if w.hwnd == hwnd:
                    self._settings.target_title = w.title
                    break
        self._emit_settings()

    def _on_target_wpm_changed(self, val: int) -> None:
        self._settings.target_wpm = val
        self._settings.typing_rate_cpm = val * 5
        self.target_wpm_label.setText(f"TARGET SPEED: {val} WPM (~{val * 5} CPM)")
        self._emit_settings()

    def _on_fluct_enabled_changed(self, state: int) -> None:
        self._settings.wpm_fluctuation_enabled = (state == Qt.Checked)
        self._emit_settings()

    def _on_min_wpm_changed(self, val: int) -> None:
        self._settings.wpm_min = min(val, self._settings.wpm_max - 2)
        self.fluct_bounds_label.setText(f"FLUCTUATION BOUNDS: {self._settings.wpm_min} WPM (MIN) — {self._settings.wpm_max} WPM (MAX)")
        self._emit_settings()

    def _on_max_wpm_changed(self, val: int) -> None:
        self._settings.wpm_max = max(val, self._settings.wpm_min + 2)
        self.fluct_bounds_label.setText(f"FLUCTUATION BOUNDS: {self._settings.wpm_min} WPM (MIN) — {self._settings.wpm_max} WPM (MAX)")
        self._emit_settings()

    def _on_typos_enabled_changed(self, state: int) -> None:
        self._settings.enable_typos = (state == Qt.Checked)
        self._emit_settings()

    def _on_word_slip_changed(self, state: int) -> None:
        self._settings.enable_word_slip_typos = (state == Qt.Checked)
        self._emit_settings()

    def _on_typo_rate_changed(self, val: int) -> None:
        rate = val / 10.0
        self._settings.typo_rate_percent = rate
        self.typo_rate_label.setText(f"MISTAKE FREQUENCY: {rate:.1f}%")
        self._emit_settings()

    def _on_hold_changed(self, val: int) -> None:
        self._settings.key_hold_time_ms = val
        self.hold_label.setText(f"KEY PRESS HOLD DURATION: {val} MS")
        self._emit_settings()

    def _on_cog_changed(self, val: int) -> None:
        self._settings.cognitive_pause_ms = val
        self.cog_label.setText(f"PUNCTUATION COGNITIVE PAUSE: {val} MS")
        self._emit_settings()

    def _on_scroll_enabled_changed(self, state: int) -> None:
        self._settings.enable_inspection_scroll = (state == Qt.Checked)
        self._emit_settings()

    def _on_hover_enabled_changed(self, state: int) -> None:
        self._settings.enable_random_hovering = (state == Qt.Checked)
        self._emit_settings()

    def _on_scroll_interval_changed(self, val: int) -> None:
        self._settings.inspection_scroll_interval_lines = val
        self.scroll_int_label.setText(f"SCROLL INSPECTION INTERVAL: EVERY {val} LINES")
        self._emit_settings()

    def _on_scroll_pause_changed(self, val: int) -> None:
        pause_s = val / 10.0
        self._settings.inspection_pause_seconds = pause_s
        self.scroll_pause_label.setText(f"INSPECTION / HOVER PAUSE: {pause_s:.1f} SECONDS")
        self._emit_settings()

    def _on_mouse_drift_changed(self, state: int) -> None:
        self._settings.enable_mouse_motion = (state == Qt.Checked)
        self._emit_settings()

    def _on_mouse_intensity_changed(self, text: str) -> None:
        self._settings.mouse_intensity = text.lower()
        self._emit_settings()

    def _on_pause_changed(self, val: int) -> None:
        self._settings.newline_pause_ms = val
        self.pause_label.setText(f"LINE BREAK PAUSE: {val} MS")
        self._emit_settings()

    def _on_delay_changed(self, val: int) -> None:
        self._settings.initial_delay_seconds = float(val)
        self.delay_label.setText(f"INITIAL COUNTDOWN DELAY: {val}.0 SECONDS")
        self._emit_settings()

    def _on_entry_mode_changed(self, idx: int) -> None:
        mode = self.entry_mode_combo.itemData(idx)
        if mode:
            self._settings.entry_mode = mode
            self._emit_settings()

    def _on_allow_any_changed(self, state: int) -> None:
        self._settings.allow_any_target = (state == Qt.Checked)
        self._emit_settings()

    def _on_focus_pause_changed(self, state: int) -> None:
        self._settings.pause_on_focus_loss = (state == Qt.Checked)
        self._emit_settings()

    def _on_hotkey_changed(self, text: str) -> None:
        self._settings.emergency_stop_key = text
        self._emit_settings()

    def update_duration_estimate(self, char_count: int, line_count: int) -> None:
        self._last_chars = char_count
        self._last_lines = line_count
        self._refresh_duration_estimate()

    def _refresh_duration_estimate(self) -> None:
        chars = self._last_chars
        lines = self._last_lines
        sec = self._settings.estimate_duration_seconds(chars, lines)
        mins = int(sec // 60)
        secs = int(sec % 60)
        self.duration_badge.setText(f"~{mins:02d}:{secs:02d}")

        scroll_stops = (lines // self._settings.inspection_scroll_interval_lines) if (self._settings.enable_inspection_scroll and self._settings.inspection_scroll_interval_lines > 0) else 0
        typos = int(chars * (self._settings.typo_rate_percent / 100.0)) if self._settings.enable_typos else 0
        wpm = self._settings.target_wpm
        self.est_details_label.setText(
            f"{chars} chars • {lines} lines • {wpm} WPM • ~{scroll_stops} mouse stops • ~{typos} typo fixes"
        )

    def _emit_settings(self) -> None:
        self._refresh_duration_estimate()
        self.settings_changed.emit(self._settings)
