from enum import Enum

from PySide6.QtWidgets import QApplication


class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"


# ── Colour palettes ───────────────────────────────────────────────────────────

_DARK = {
    "window":        "#1e1f2e",
    "panel":         "#252636",
    "widget":        "#2a2b3d",
    "widget_alt":    "#313248",
    "border":        "#3d3f5c",
    "border_focus":  "#7aa2f7",
    "accent":        "#7aa2f7",
    "accent_hover":  "#89b4fa",
    "accent_press":  "#6488d4",
    "text":          "#c0caf5",
    "text_dim":      "#6b7099",
    "text_disabled": "#414868",
    "hover":         "#33355a",
    "selected":      "#364176",
    "scrollbar":     "#3d3f5c",
    "scrollbar_h":   "#565f89",
    "danger":        "#f38ba8",
    "success":       "#a6e3a1",
    "group_title":   "#7aa2f7",
}

_LIGHT = {
    "window":        "#f0f2f5",
    "panel":         "#ffffff",
    "widget":        "#ffffff",
    "widget_alt":    "#f5f6fa",
    "border":        "#d0d4e0",
    "border_focus":  "#2563eb",
    "accent":        "#2563eb",
    "accent_hover":  "#1d4ed8",
    "accent_press":  "#1e40af",
    "text":          "#1e1f2e",
    "text_dim":      "#6b7280",
    "text_disabled": "#9ca3af",
    "hover":         "#e8eaf2",
    "selected":      "#dbeafe",
    "scrollbar":     "#d1d5db",
    "scrollbar_h":   "#9ca3af",
    "danger":        "#dc2626",
    "success":       "#16a34a",
    "group_title":   "#2563eb",
}


# ── QSS template ─────────────────────────────────────────────────────────────

def _build_qss(c: dict[str, str]) -> str:
    return f"""
/* ── Global ──────────────────────────────────────────────────────── */
QWidget {{
    background-color: {c['window']};
    color: {c['text']};
    font-size: 13px;
    border: none;
    outline: none;
}}

QMainWindow {{
    background-color: {c['window']};
}}

/* ── Dock widgets ─────────────────────────────────────────────────── */
QDockWidget {{
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background-color: {c['panel']};
    color: {c['accent']};
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;

    padding: 6px 10px;
    border-bottom: 1px solid {c['border']};
}}

/* ── Toolbar ──────────────────────────────────────────────────────── */
QToolBar {{
    background-color: {c['panel']};
    border-bottom: 1px solid {c['border']};
    spacing: 4px;
    padding: 3px 6px;
}}
QToolBar::separator {{
    background-color: {c['border']};
    width: 1px;
    margin: 4px 4px;
}}
QToolButton {{
    background-color: transparent;
    color: {c['text']};
    border: none;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
}}
QToolButton:hover {{
    background-color: {c['hover']};
}}
QToolButton:pressed {{
    background-color: {c['selected']};
}}
QToolButton::menu-indicator {{
    image: none;
    width: 0;
}}

/* ── Menu bar ─────────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {c['panel']};
    color: {c['text']};
    border-bottom: 1px solid {c['border']};
    padding: 2px 4px;
}}
QMenuBar::item {{
    background-color: transparent;
    padding: 5px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: {c['hover']};
}}
QMenuBar::item:pressed {{
    background-color: {c['selected']};
}}

/* ── Menu (dropdown) ──────────────────────────────────────────────── */
QMenu {{
    background-color: {c['panel']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 28px 6px 12px;
    border-radius: 4px;
    margin: 1px 2px;
}}
QMenu::item:selected {{
    background-color: {c['selected']};
    color: {c['accent']};
}}
QMenu::separator {{
    height: 1px;
    background-color: {c['border']};
    margin: 4px 8px;
}}
QMenu::right-arrow {{
    width: 8px;
    height: 8px;
}}

/* ── Buttons ──────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {c['widget_alt']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {c['hover']};
    border-color: {c['border_focus']};
}}
QPushButton:pressed {{
    background-color: {c['selected']};
}}
QPushButton:disabled {{
    color: {c['text_disabled']};
    border-color: {c['border']};
}}
QPushButton#accent_btn {{
    background-color: {c['accent']};
    color: #ffffff;
    border: none;
    font-weight: 600;
}}
QPushButton#accent_btn:hover {{
    background-color: {c['accent_hover']};
}}

/* ── Group box ────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {c['border']};
    border-radius: 6px;
    margin-top: 18px;
    padding: 8px 6px 6px 6px;
    font-weight: 600;
    color: {c['group_title']};
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
    top: 4px;
}}

/* ── Inputs ───────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c['widget']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 4px 8px;
    selection-background-color: {c['selected']};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {c['border_focus']};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {c['widget']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 3px 4px;
    selection-background-color: {c['selected']};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {c['border_focus']};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {c['widget_alt']};
    border: none;
    width: 16px;
    border-radius: 3px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {c['hover']};
}}

/* ── Combo box ────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {c['widget']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 4px 8px;
    min-width: 80px;
}}
QComboBox:hover {{
    border-color: {c['border_focus']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
    subcontrol-origin: padding;
    subcontrol-position: right center;
}}
QComboBox QAbstractItemView {{
    background-color: {c['panel']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    selection-background-color: {c['selected']};
    selection-color: {c['accent']};
    outline: none;
    padding: 2px;
}}

/* ── Slider ───────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 4px;
    background-color: {c['border']};
    border-radius: 2px;
    margin: 0 2px;
}}
QSlider::handle:horizontal {{
    background-color: {c['accent']};
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background-color: {c['accent_hover']};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background-color: {c['accent']};
    border-radius: 2px;
}}

/* ── Checkbox ─────────────────────────────────────────────────────── */
QCheckBox {{
    spacing: 8px;
    color: {c['text']};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {c['border']};
    border-radius: 4px;
    background-color: {c['widget']};
}}
QCheckBox::indicator:hover {{
    border-color: {c['border_focus']};
}}
QCheckBox::indicator:checked {{
    background-color: {c['accent']};
    border-color: {c['accent']};
    image: none;
}}
QCheckBox::indicator:checked:hover {{
    background-color: {c['accent_hover']};
    border-color: {c['accent_hover']};
}}

/* ── List widget ──────────────────────────────────────────────────── */
QListWidget {{
    background-color: {c['widget']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    outline: none;
    padding: 2px;
}}
QListWidget::item {{
    padding: 2px 4px;
    border-radius: 4px;
    margin: 1px 2px;
}}
QListWidget::item:selected {{
    background-color: {c['selected']};
    color: {c['accent']};
}}
QListWidget::item:hover:!selected {{
    background-color: {c['hover']};
}}

/* ── Scroll bars ──────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {c['scrollbar']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {c['scrollbar_h']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background-color: {c['scrollbar']};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {c['scrollbar_h']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Scroll area ──────────────────────────────────────────────────── */
QScrollArea {{
    background-color: transparent;
    border: 1px solid {c['border']};
    border-radius: 6px;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ── Labels ───────────────────────────────────────────────────────── */
QLabel {{
    background-color: transparent;
    color: {c['text']};
}}
QLabel#dim {{
    color: {c['text_dim']};
    font-size: 11px;
}}

/* ── Graphics view (image canvas) ─────────────────────────────────── */
QGraphicsView {{
    background-color: {c['widget']};
    border: 1px solid {c['border']};
    border-radius: 4px;
}}

/* ── Status bar ───────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {c['panel']};
    border-top: 1px solid {c['border']};
    color: {c['text_dim']};
    font-size: 11px;
    padding: 2px 8px;
}}

/* ── Stacked / tab ────────────────────────────────────────────────── */
QStackedWidget {{
    background-color: transparent;
}}
"""


# ── Public API ────────────────────────────────────────────────────────────────

_current_theme = Theme.DARK


def current_theme() -> Theme:
    return _current_theme


def apply_theme(app: QApplication, theme: Theme) -> None:
    global _current_theme
    _current_theme = theme
    colors = _DARK if theme == Theme.DARK else _LIGHT
    app.setStyleSheet(_build_qss(colors))


def toggle_theme(app: QApplication) -> Theme:
    new = Theme.LIGHT if _current_theme == Theme.DARK else Theme.DARK
    apply_theme(app, new)
    return new
