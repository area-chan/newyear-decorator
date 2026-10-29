#!/usr/bin/env python3
"""Запуск «Новогоднего оформителя».

    python3 main.py
"""

from __future__ import annotations

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtWidgets import QApplication

from winterdecor.theme import QSS
from winterdecor.ui import DecoratorWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "assets", "newyear-decorator.svg")


def dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0c1424"))
    palette.setColor(QPalette.WindowText, QColor("#eef4ff"))
    palette.setColor(QPalette.Base, QColor("#0f1828"))
    palette.setColor(QPalette.Text, QColor("#eef4ff"))
    palette.setColor(QPalette.Button, QColor("#162033"))
    palette.setColor(QPalette.ButtonText, QColor("#eef4ff"))
    palette.setColor(QPalette.Highlight, QColor("#ffd27a"))
    palette.setColor(QPalette.HighlightedText, QColor("#1a1206"))
    palette.setColor(QPalette.ToolTipBase, QColor("#111a2b"))
    palette.setColor(QPalette.ToolTipText, QColor("#eef4ff"))
    return palette


def main() -> int:
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Новогодний оформитель")
    app.setApplicationDisplayName("Новогодний оформитель")
    app.setDesktopFileName("newyear-decorator")
    app.setStyle("Fusion")
    app.setPalette(dark_palette())
    app.setStyleSheet(QSS)

    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    window = DecoratorWindow()
    if os.path.exists(ICON_PATH):
        window.setWindowIcon(QIcon(ICON_PATH))
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
