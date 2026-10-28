"""
Modern Dark Theme Stylesheet and Visual Styling for CodeFlow Studio.
Features modern glass/slate dark styling, glowing accents, and intuitive card designs.
"""

DARK_THEME_QSS = """
/* CodeFlow Studio Modern Dark Theme */

QWidget {
    background-color: #0a0e17;
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QMainWindow {
    background-color: #070a10;
}

/* Splitter */
QSplitter::handle {
    background-color: #1e293b;
    width: 3px;
    margin: 1px;
    border-radius: 1px;
}

QSplitter::handle:hover {
    background-color: #38bdf8;
}

/* Menu Bar */
QMenuBar {
    background-color: #0a0e17;
    border-bottom: 1px solid #1a2333;
    padding: 3px 6px;
    font-weight: 500;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 12px;
    border-radius: 5px;
    color: #94a3b8;
}

QMenuBar::item:selected {
    background-color: #162032;
    color: #38bdf8;
}

QMenu {
    background-color: #0f172a;
    border: 1px solid #23334d;
    border-radius: 8px;
    padding: 6px 0px;
}

QMenu::item {
    padding: 7px 28px 7px 18px;
    color: #cbd5e1;
    border-radius: 4px;
    margin: 1px 4px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #1e293b;
    margin: 5px 8px;
}

/* Toolbars */
QToolBar {
    background-color: #0a0e17;
    border-bottom: 1px solid #1a2333;
    spacing: 8px;
    padding: 6px 12px;
}

/* Scroll Area for Settings */
QScrollArea#settingsScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea#settingsScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Autonomous Mode Hero Card */
QFrame#autonomousHeroCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111d30, stop:1 #0c1422);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 12px 14px;
}

QFrame#autonomousHeroCard:hover {
    border-color: #38bdf8;
}

QLabel#heroTitle {
    color: #f1f5f9;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#heroSubtitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 500;
    line-height: 1.3;
}

QPushButton#autonomousToggleBtn {
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
    border-radius: 6px;
    padding: 6px 14px;
    min-width: 65px;
}

/* Estimated Runtime Card */
QFrame#estCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0d1a2d, stop:1 #08111e);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 10px 14px;
}

QLabel#estTitle {
    color: #38bdf8;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QLabel#estDurationBadge {
    color: #38bdf8;
    font-weight: 900;
    font-size: 18px;
    letter-spacing: 0.5px;
}

QLabel#estDetailsLabel {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 500;
}

/* Presets GroupBox */
QGroupBox#presetGroup {
    background-color: #0d131f;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 10px 10px 10px;
    font-weight: 800;
    color: #38bdf8;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QGroupBox#presetGroup::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 8px;
    background-color: #0d131f;
    border: 1px solid #1e293b;
    border-radius: 4px;
    color: #38bdf8;
}

QPushButton.presetBtn {
    background-color: #131d2e;
    color: #e2e8f0;
    border: 1px solid #23334d;
    border-radius: 6px;
    padding: 8px 10px;
    font-weight: 700;
    font-size: 11px;
    min-height: 28px;
}

QPushButton.presetBtn:hover {
    background-color: #1e2d47;
    border-color: #38bdf8;
    color: #ffffff;
}

QPushButton.presetBtn:pressed {
    background-color: #0284c7;
    border-color: #38bdf8;
    color: #ffffff;
}

/* Tab Widget (Settings Categories) */
QTabWidget#settingsTabs {
    background-color: transparent;
}

QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 8px;
    background-color: #0d131f;
    padding: 10px;
    top: -1px;
}

QTabBar::tab {
    background-color: #131d2e;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QTabBar::tab:selected {
    background-color: #0d131f;
    color: #38bdf8;
    border-color: #1e293b;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #f1f5f9;
}

/* Inner Parameter Cards */
QFrame#innerControlCard {
    background-color: #111a2a;
    border: 1px solid #1e2d42;
    border-radius: 8px;
    padding: 12px;
}

QLabel#paramHeaderLabel {
    color: #f1f5f9;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QLabel#paramSubLabel {
    color: #94a3b8;
    font-size: 11px;
}

QLabel#infoCalloutLabel {
    color: #94a3b8;
    font-size: 11px;
    border: 1px dashed #28374d;
    border-radius: 6px;
    padding: 8px 10px;
    background-color: #0a0f18;
}

QPushButton#detectVscBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb);
    border: 1px solid #3b82f6;
    border-radius: 6px;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 8px 14px;
    min-height: 28px;
}

QPushButton#detectVscBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #3b82f6);
    border-color: #60a5fa;
}

/* Standard Buttons */
QPushButton {
    background-color: #162032;
    color: #e2e8f0;
    border: 1px solid #28374d;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #1e2d47;
    color: #ffffff;
    border-color: #38bdf8;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #0a0e17;
    color: #475569;
    border-color: #1a2333;
}

/* Action Execution Buttons */
QPushButton#startButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: 1px solid #34d399;
    font-weight: 800;
    padding: 12px 28px;
    font-size: 14px;
    border-radius: 8px;
    letter-spacing: 0.5px;
}

QPushButton#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
    border-color: #6ee7b7;
}

QPushButton#startButton:pressed {
    background-color: #064e3b;
}

QPushButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #ef4444);
    color: #ffffff;
    border: 1px solid #f87171;
    font-weight: 800;
    padding: 12px 28px;
    font-size: 14px;
    border-radius: 8px;
    letter-spacing: 0.5px;
}

QPushButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #dc2626);
    border-color: #fca5a5;
}

QPushButton#stopButton:pressed {
    background-color: #7f1d1d;
}

QPushButton#pauseButton {
    background-color: #1a2333;
    color: #fde047;
    border: 1px solid #eab308;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
}

QPushButton#pauseButton:hover {
    background-color: #243247;
    border-color: #facc15;
}

QPushButton#resumeButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    color: #ffffff;
    border: 1px solid #7dd3fc;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
}

QPushButton#resumeButton:hover {
    background-color: #0369a1;
}

/* Inputs, Spinners & Dropdowns */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #131d2e;
    color: #f8fafc;
    border: 1px solid #23334d;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 26px;
    font-size: 12px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
    background-color: #172237;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #23334d;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #23334d;
    selection-background-color: #0284c7;
    color: #ffffff;
    padding: 4px;
    border-radius: 6px;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #1a2333;
    height: 6px;
    background: #0f172a;
    margin: 2px 0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #38bdf8;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #f8fafc;
    border: 2px solid #60a5fa;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #1e293b;
    border-radius: 6px;
    background-color: #090e17;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #070a10;
    color: #94a3b8;
    border-top: 1px solid #1a2333;
    font-size: 12px;
    padding: 4px 12px;
}

QStatusBar QLabel {
    background: transparent;
    color: #94a3b8;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #28374d;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #38bdf8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #28374d;
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #38bdf8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #131d2e;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

/* Focus Warning Banner */
QFrame#focusWarningBanner {
    background-color: #200d0e;
    border: 1px solid #ef4444;
    border-radius: 6px;
    padding: 8px 14px;
}

QLabel#focusWarningText {
    color: #fca5a5;
    font-weight: bold;
    font-size: 12px;
}

/* Scrolling Inspection Banner */
QFrame#inspectionBanner {
    background-color: #091a2e;
    border: 1px solid #38bdf8;
    border-radius: 6px;
    padding: 8px 14px;
}

QLabel#inspectionText {
    color: #7dd3fc;
    font-weight: bold;
    font-size: 12px;
}

/* Live HUD Activity Card */
QFrame#liveHudCard {
    background-color: #111a2a;
    border: 1px solid #1e2d42;
    border-radius: 6px;
    padding: 6px 12px;
}

QFrame#liveHudCard:hover {
    border-color: #38bdf8;
}

QLabel#liveHudStatusTag {
    color: #38bdf8;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
}

/* Status Badges */
QLabel#statusBadgeGreen {
    background-color: #0a1b14;
    color: #34d399;
    border: 1px solid #059669;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#statusBadgeAmber {
    background-color: #1f1807;
    color: #fbbf24;
    border: 1px solid #d97706;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#statusBadgeRed {
    background-color: #200d0e;
    color: #f87171;
    border: 1px solid #dc2626;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#statusBadgeBlue {
    background-color: #0b192c;
    color: #38bdf8;
    border: 1px solid #0284c7;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 700;
    font-size: 11px;
}
"""
