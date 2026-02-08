
from __future__ import annotations

from PyQt5.QtWidgets import QApplication
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16
SPACING_XL = 24
SIDEBAR_WIDTH = 220
TOOLBAR_HEIGHT = 48
STATUS_HEIGHT = 28
COLOR_BG_MAIN = "#0f1117"
COLOR_BG_PANEL = "#161827"
COLOR_BG_ELEVATED = "#1e2139"
COLOR_BG_HOVER = "#252842"
COLOR_BORDER = "#2d3142"
COLOR_BORDER_LIGHT = "#3b3f5c"
COLOR_TEXT = "#e4e4e7"
COLOR_TEXT_MUTED = "#a1a1aa"
COLOR_ACCENT = "#6366f1"
COLOR_ACCENT_HOVER = "#818cf8"
COLOR_DESTRUCTIVE = "#dc2626"
COLOR_DESTRUCTIVE_HOVER = "#ef4444"


def get_app_stylesheet() -> str:
    return """
    /* Global Styles - Professional Data Tool */
    QMainWindow {
        background-color: #0f1117;
        color: #e4e4e7;
    }
    
    QWidget {
        background-color: transparent;
        color: #e4e4e7;
        font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
        font-size: 10pt;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #161827;
        color: #e4e4e7;
        border-bottom: 1px solid #2d3142;
        padding: 6px 12px;
        font-weight: 500;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 10px 18px;
        border-radius: 6px;
        margin: 0 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #252842;
        color: #e4e4e7;
    }

    QMenuBar::item:pressed {
        background-color: #6366f1;
        color: #ffffff;
    }
    
    QMenu {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 10px;
        padding: 6px;
    }
    
    QMenu::item {
        padding: 10px 36px 10px 20px;
        border-radius: 6px;
        margin: 2px;
    }
    
    QMenu::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #6366f1, stop:1 #818cf8);
        color: #ffffff;
    }
    
    QMenu::separator {
        height: 1px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 transparent, stop:0.5 #3b3f5c, stop:1 transparent);
        margin: 6px 12px;
    }
    
    /* Labels */
    QLabel {
        color: #e4e4e7;
        background-color: transparent;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #252842;
        color: #e4e4e7;
        border: 1px solid #2d3142;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 10pt;
        min-height: 22px;
    }

    QPushButton:hover {
        background-color: #2d3142;
        border-color: #3b3f5c;
    }

    QPushButton:pressed {
        background-color: #1e2139;
    }
    
    QPushButton:disabled {
        background-color: #3b3f5c;
        color: #71717a;
    }
    
    /* Line Edits - Modern Input Fields */
    QLineEdit {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        padding: 10px 14px;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        font-size: 10pt;
    }
    
    QLineEdit:focus {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QLineEdit:hover {
        border: 2px solid #4f46e5;
    }
    
    /* Combo Boxes - Enhanced Dropdowns */
    QComboBox {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        padding: 10px 14px;
        min-width: 140px;
        font-size: 10pt;
    }
    
    QComboBox:hover {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QComboBox:focus {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 32px;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    
    QComboBox::down-arrow {
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 7px solid #e4e4e7;
        margin-right: 10px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 10px;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        padding: 6px;
    }
    
    /* Table Widget - Professional Data Grid */
    QTableWidget {
        background-color: #161827;
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 12px;
        gridline-color: #2a2d3f;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        alternate-background-color: #1a1d2e;
    }
    
    QTableWidget::item {
        padding: 8px;
        border: none;
    }
    
    QTableWidget::item:selected {
        background-color: #6366f1;
        color: #ffffff;
    }
    
    QTableWidget::item:alternate {
        background-color: #1a1d2e;
    }
    
    QHeaderView::section {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #252842, stop:1 #1e2139);
        color: #e4e4e7;
        padding: 12px;
        border: none;
        border-right: 1px solid #3b3f5c;
        border-bottom: 2px solid #6366f1;
        font-weight: 600;
        font-size: 10pt;
    }
    
    QHeaderView::section:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2d3152, stop:1 #252842);
    }
    
    /* Radio Buttons - Modern Toggle */
    QRadioButton {
        color: #e4e4e7;
        spacing: 10px;
        font-size: 10pt;
    }
    
    QRadioButton::indicator {
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 2px solid #3b3f5c;
        background-color: #1e2139;
    }
    
    QRadioButton::indicator:hover {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QRadioButton::indicator:checked {
        border: 2px solid #6366f1;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
            stop:0 #818cf8, stop:1 #6366f1);
    }
    
    /* Dialog Windows - Professional Modals */
    QDialog {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e2139, stop:1 #161827);
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 12px;
    }
    
    /* Tab Widget - Modern Tabs */
    QTabWidget::pane {
        border: 1px solid #3b3f5c;
        border-radius: 12px;
        background-color: #161827;
        top: -1px;
    }
    
    QTabBar::tab {
        background-color: #1e2139;
        color: #a1a1aa;
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom: 2px solid transparent;
        font-weight: 500;
    }
    
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #6366f1, stop:1 #4f46e5);
        color: #ffffff;
        font-weight: 600;
        border-bottom: 2px solid #818cf8;
    }
    
    QTabBar::tab:hover {
        background-color: #252842;
        color: #e4e4e7;
    }
    
    /* Message Box - Enhanced Alerts */
    QMessageBox {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e2139, stop:1 #161827);
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 12px;
    }
    
    QMessageBox QLabel {
        color: #e4e4e7;
        min-width: 320px;
        padding: 10px;
        font-size: 10pt;
    }
    
    QMessageBox QPushButton {
        min-width: 90px;
        padding: 10px 20px;
        margin: 4px;
    }
    
    /* Scroll Bars - Sleek Modern Scrollbars */
    QScrollBar:vertical {
        background-color: #161827;
        width: 14px;
        border: none;
        border-radius: 7px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #3b3f5c, stop:1 #4f46e5);
        border-radius: 7px;
        min-height: 30px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #6366f1, stop:1 #818cf8);
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #161827;
        height: 14px;
        border: none;
        border-radius: 7px;
        margin: 0;
    }
    
    QScrollBar::handle:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3b3f5c, stop:1 #4f46e5);
        border-radius: 7px;
        min-width: 30px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #6366f1, stop:1 #818cf8);
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* File Dialog - Enhanced File Browser */
    QFileDialog {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e2139, stop:1 #161827);
        color: #e4e4e7;
    }
    
    QFileDialog QListView, QFileDialog QTreeView {
        background-color: #161827;
        color: #e4e4e7;
        border: 1px solid #3b3f5c;
        border-radius: 8px;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
    }
    
    QFileDialog QLineEdit {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 8px;
        padding: 8px;
    }
    
    QFileDialog QPushButton {
        min-width: 100px;
    }
    
    /* Input Dialog */
    QInputDialog {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e2139, stop:1 #161827);
        color: #e4e4e7;
    }
    
    QInputDialog QLabel {
        color: #e4e4e7;
        font-size: 10pt;
    }
    
    /* Check Boxes - Modern Checkboxes */
    QCheckBox {
        color: #e4e4e7;
        spacing: 10px;
        font-size: 10pt;
    }
    
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border: 2px solid #3b3f5c;
        border-radius: 5px;
        background-color: #1e2139;
    }
    
    QCheckBox::indicator:hover {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QCheckBox::indicator:checked {
        border: 2px solid #6366f1;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #818cf8, stop:1 #6366f1);
    }
    
    /* Progress Bar - Animated Progress */
    QProgressBar {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        height: 24px;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #6366f1, stop:1 #818cf8);
        border-radius: 8px;
    }
    
    /* Spin Box - Enhanced Number Inputs */
    QSpinBox, QDoubleSpinBox {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        padding: 10px 14px;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        font-size: 10pt;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QSpinBox:hover, QDoubleSpinBox:hover {
        border: 2px solid #4f46e5;
    }
    
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        background-color: #252842;
        border: none;
        width: 24px;
        border-radius: 6px;
    }
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #6366f1;
    }
    
    QSpinBox::up-arrow, QSpinBox::down-arrow, QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
    }
    
    QSpinBox::up-arrow {
        border-bottom: 6px solid #e4e4e7;
    }
    
    QSpinBox::down-arrow {
        border-top: 6px solid #e4e4e7;
    }
    
    QDoubleSpinBox::up-arrow {
        border-bottom: 6px solid #e4e4e7;
    }
    
    QDoubleSpinBox::down-arrow {
        border-top: 6px solid #e4e4e7;
    }
    
    /* Text Edit - Rich Text Input */
    QTextEdit {
        background-color: #1e2139;
        color: #e4e4e7;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        padding: 10px;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        font-size: 10pt;
    }
    
    QTextEdit:focus {
        border: 2px solid #6366f1;
        background-color: #252842;
    }
    
    QTextEdit:hover {
        border: 2px solid #4f46e5;
    }
    
    /* Group Box - Section Containers */
    QGroupBox {
        font-weight: 600;
        border: 2px solid #3b3f5c;
        border-radius: 10px;
        margin-top: 1.5ex;
        color: #e4e4e7;
        padding-top: 12px;
        font-size: 10pt;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 10px 0 10px;
        color: #818cf8;
        background-color: #1e2139;
    }

    /* Sidebar / Dataset Explorer */
    QWidget#datasetExplorer {
        background-color: #161827;
        border-right: 1px solid #2d3142;
        padding: 12px;
    }

    QListWidget#datasetList {
        background-color: transparent;
        border: none;
        outline: none;
        padding: 4px 0;
        font-size: 10pt;
    }

    QListWidget#datasetList::item {
        padding: 10px 12px;
        border-radius: 6px;
        margin: 2px 0;
    }

    QListWidget#datasetList::item:selected {
        background-color: #252842;
        color: #e4e4e7;
        border-left: 3px solid #6366f1;
    }

    QListWidget#datasetList::item:hover {
        background-color: #1e2139;
    }

    /* Toolbar / Header bar */
    QWidget#mainToolbar {
        background-color: #1e2139;
        border-bottom: 1px solid #2d3142;
        padding: 8px 16px;
        min-height: 40px;
    }

    /* Secondary / muted buttons for toolbar */
    QPushButton[flat="true"] {
        background-color: transparent;
        color: #a1a1aa;
        border: none;
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: 500;
    }

    QPushButton[flat="true"]:hover {
        background-color: #252842;
        color: #e4e4e7;
    }

    QPushButton[flat="true"]:pressed {
        background-color: #2d3142;
    }

    /* Primary action button (accent) */
    QPushButton[primary="true"] {
        background-color: #6366f1;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }

    QPushButton[primary="true"]:hover {
        background-color: #818cf8;
    }

    /* Status bar */
    QStatusBar {
        background-color: #161827;
        color: #a1a1aa;
        border-top: 1px solid #2d3142;
        padding: 4px 16px;
        font-size: 9pt;
    }

    /* Empty state */
    QWidget#emptyState {
        background-color: transparent;
    }

    QLabel#emptyTitle {
        font-size: 18pt;
        font-weight: 600;
        color: #e4e4e7;
        padding: 0 0 8px 0;
    }

    QLabel#emptySubtitle {
        font-size: 11pt;
        color: #a1a1aa;
        padding: 0;
    }
    """


def apply_app_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(get_app_stylesheet())

