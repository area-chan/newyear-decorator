"""Цвета и стили «Новогоднего оформителя»."""

from PyQt5.QtGui import QColor

GOLD = QColor("#ffd27a")
ICE = QColor("#a8dcff")
TEXT = QColor("#eef4ff")
MUTED = QColor("#94a6bd")
BG_TOP = QColor("#0a1120")
BG_BOTTOM = QColor("#141d31")
DANGER = QColor("#ff8f8f")
OK = QColor("#8ef0c0")

QSS = """
QWidget {
    color: #eef4ff;
    font-size: 13px;
}

QLabel#title {
    font-size: 25px;
    font-weight: 600;
    color: #ffffff;
}
QLabel#subtitle {
    font-size: 12px;
    color: #93a5bd;
}
QLabel#section {
    font-size: 12px;
    font-weight: 600;
    color: #8fa2ba;
    letter-spacing: 1px;
}
QLabel#status {
    font-size: 12px;
    color: #8fa2ba;
}
QLabel#chip {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 13px;
    padding: 5px 12px;
    font-size: 11px;
    color: #c8d5e6;
}
QLabel#chipOk {
    background: rgba(142, 240, 192, 0.08);
    border: 1px solid rgba(142, 240, 192, 0.30);
    border-radius: 13px;
    padding: 5px 12px;
    font-size: 11px;
    color: #8ef0c0;
}
QLabel#chipErr {
    background: rgba(255, 143, 143, 0.08);
    border: 1px solid rgba(255, 143, 143, 0.32);
    border-radius: 13px;
    padding: 5px 12px;
    font-size: 11px;
    color: #ff9e9e;
}

QPushButton#preset {
    background: rgba(255, 255, 255, 0.055);
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 15px;
    padding: 9px 16px;
    color: #dbe6f5;
}
QPushButton#preset:hover {
    background: rgba(255, 255, 255, 0.10);
    border-color: rgba(255, 255, 255, 0.22);
}
QPushButton#preset:pressed {
    background: rgba(255, 210, 122, 0.20);
    border-color: rgba(255, 210, 122, 0.45);
}

QPushButton#close {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 17px;
    padding: 8px 22px;
    color: #e7eefb;
}
QPushButton#close:hover {
    background: rgba(255, 255, 255, 0.13);
}

QToolTip {
    background: #111a2b;
    color: #eef4ff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 6px;
}
"""
