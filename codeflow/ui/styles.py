"""
Modern Dark Theme Stylesheet and Visual Styling for CodeFlow Studio.
Features modern glass/slate dark styling, glowing accents, and intuitive card designs.
"""

DARK_THEME_QSS = """
/* CodeFlow Studio Modern Dark Theme */

QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QMainWindow {
    background-color: #090a0f;
}

/* Menu Bar */
QMenuBar {
    background-color: #0f1117;
    border-bottom: 1px solid #1e2230;
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
    background-color: #1e293b;
    color: #38bdf8;
}

QMenu {
    background-color: #171b26;
    border: 1px solid #334155;
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
    background-color: #0f1117;
    border-bottom: 1px solid #1e2230;
    spacing: 8px;
    padding: 6px 12px;
}

/* Autonomous Mode Hero Card */
QFrame#autonomousHeroCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 10px 12px;
}

QFrame#autonomousHeroCard:hover {
    border: 1px solid #58a6ff;
}

QLabel#heroTitle {
    color: #f0f6fc;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#heroSubtitle {
    color: #8b949e;
    font-size: 10px;
    font-weight: 600;
}

/* Estimated Runtime Card */
QFrame#estCard {
    background-color: #0d1117;
    border: 1px solid #1f6feb;
    border-radius: 4px;
    padding: 10px 12px;
}

QLabel#estTitle {
    color: #58a6ff;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QLabel#estDurationBadge {
    color: #58a6ff;
    font-weight: 900;
    font-size: 16px;
    letter-spacing: 0.5px;
}

QLabel#estDetailsLabel {
    color: #8b949e;
    font-size: 11px;
    font-weight: 500;
}

/* Param Labels */
QLabel#paramHeaderLabel {
    color: #c9d1d9;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QLabel#paramSubLabel {
    color: #8b949e;
    font-size: 11px;
}

QLabel#infoCalloutLabel {
    color: #8b949e;
    font-size: 11px;
    border: 1px dashed #30363d;
    border-radius: 4px;
    padding: 6px;
}

QFrame#innerControlCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 8px;
}

QPushButton#detectVscBtn {
    background-color: #1f6feb;
    border: 1px solid #388bfd;
    border-radius: 4px;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 8px 12px;
}

QPushButton#detectVscBtn:hover {
    background-color: #388bfd;
}

/* Tab Widget (Settings Categories) */
QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 8px;
    background-color: #0f1117;
    top: -1px;
}

QTabBar::tab {
    background-color: #171b26;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 14px;
    margin-right: 3px;
    font-weight: 600;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #0f1117;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #ffffff;
}

/* Card Containers & Groups */
QGroupBox {
    background-color: #171b26;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
    font-weight: bold;
    color: #38bdf8;
    font-size: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #38bdf8;
}

/* Preset Buttons */
QPushButton.presetBtn {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton.presetBtn:hover {
    background-color: #334155;
    border-color: #38bdf8;
    color: #ffffff;
}

QPushButton.presetBtn:pressed {
    background-color: #1d4ed8;
    border-color: #60a5fa;
}

/* Standard Buttons */
QPushButton {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #334155;
    color: #ffffff;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #0f1117;
    color: #475569;
    border-color: #1e293b;
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
    background-color: #1e293b;
    color: #fde047;
    border: 1px solid #eab308;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
}

QPushButton#pauseButton:hover {
    background-color: #334155;
    border-color: #facc15;
}

QPushButton#resumeButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    color: #ffffff;
    border: 1px solid #7dd3fc;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
}

QPushButton#resumeButton:hover {
    background-color: #0369a1;
}

/* Inputs, Spinners & Dropdowns */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #171b26;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 24px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
    background-color: #1e293b;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #334155;
}

QComboBox QAbstractItemView {
    background-color: #171b26;
    border: 1px solid #334155;
    selection-background-color: #0284c7;
    color: #ffffff;
    padding: 4px;
    border-radius: 6px;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #1e293b;
    height: 6px;
    background: #1e293b;
    margin: 2px 0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #2563eb);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #f8fafc;
    border: 1px solid #38bdf8;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
    border: 2px solid #60a5fa;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #1e293b;
    border-radius: 6px;
    background-color: #090a0f;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #3b82f6);
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #090a0f;
    color: #94a3b8;
    border-top: 1px solid #1e2230;
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
    background-color: #090a0f;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 24px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar:horizontal {
    border: none;
    background-color: #090a0f;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    min-width: 24px;
    border-radius: 5px;
    margin: 2px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #171b26;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

/* Focus Warning Banner */
QFrame#focusWarningBanner {
    background-color: #0d1117;
    border: 1px solid #f85149;
    border-radius: 4px;
    padding: 8px 14px;
}

QLabel#focusWarningText {
    color: #f85149;
    font-weight: bold;
    font-size: 12px;
}

/* Scrolling Inspection Banner */
QFrame#inspectionBanner {
    background-color: #0d1117;
    border: 1px solid #1f6feb;
    border-radius: 4px;
    padding: 8px 14px;
}

QLabel#inspectionText {
    color: #58a6ff;
    font-weight: bold;
    font-size: 12px;
}

/* Live HUD Activity Card */
QFrame#liveHudCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px 12px;
}

QFrame#liveHudCard:hover {
    border-color: #58a6ff;
}

QLabel#liveHudStatusTag {
    color: #79c0ff;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
}

/* Status Badges */
QLabel#statusBadgeGreen {
    background-color: #0d1117;
    color: #3fb950;
    border: 1px solid #238636;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#statusBadgeAmber {
    background-color: #0d1117;
    color: #d29922;
    border: 1px solid #9e6a03;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#statusBadgeRed {
    background-color: #0d1117;
    color: #f85149;
    border: 1px solid #b62324;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#statusBadgeBlue {
    background-color: #0d1117;
    color: #58a6ff;
    border: 1px solid #1f6feb;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 11px;
}
"""
