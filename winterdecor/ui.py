"""Окно и виджеты «Новогоднего оформителя»."""

from __future__ import annotations

import math
import os
import random
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import (
    QEasingCurve,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QUrl,
    QVariantAnimation,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QDesktopServices,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt5.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import plasma
from .theme import BG_BOTTOM, BG_TOP, GOLD, MUTED, TEXT

CARDS = [
    ("snow", "Снегопад", "Мягкий снег поверх обоев", "snow"),
    ("garland", "Гирлянда", "Огоньки вдоль верхнего края", "garland"),
    ("tree", "Ёлка", "Украшенная ёлка с огнями", "tree"),
    ("clock", "Часы", "Крупные часы с датой", "clock"),
    ("weather", "Погода", "Температура и ветер", "weather"),
    ("wish", "Пожелание дня", "Тёплая фраза на утро", "wish"),
]

WALLPAPERS = [
    ("polar-night", "Полярная ночь"),
    ("aurora", "Северное сияние"),
    ("sunset", "Зимний закат"),
    ("minimal", "Тихий вечер"),
    ("bokeh", "Огни в снегу"),
    ("moon-forest", "Лунный лес"),
    ("cabin", "Домик в лесу"),
    ("frost", "Морозные узоры"),
]

DENSITIES = [
    (60, "Лёгкий"),
    (120, "Обычный"),
    (180, "Сильный"),
]

BASE_DIR = Path(__file__).resolve().parent.parent
AUTOSTART_FILE = Path.home() / ".config" / "autostart" / "newyear-decorator.desktop"


def wallpaper_dir() -> Path:
    local = BASE_DIR / "assets" / "wallpapers"
    if local.is_dir():
        return local
    return Path.home() / ".local" / "share" / "newyear-decorator" / "wallpapers"


def autostart_enabled() -> bool:
    return AUTOSTART_FILE.exists()


def launcher_command() -> str:
    launcher = Path.home() / ".local" / "bin" / "newyear-decorator"
    if launcher.exists():
        return str(launcher)
    return 'python3 "%s"' % (BASE_DIR / "main.py")


def set_autostart(enabled: bool) -> None:
    if enabled:
        AUTOSTART_FILE.parent.mkdir(parents=True, exist_ok=True)
        AUTOSTART_FILE.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Новогодний оформитель\n"
            "Comment=Меню зимних украшений рабочего стола\n"
            "Exec=%s\n"
            "Icon=newyear-decorator\n"
            "Terminal=false\n"
            "OnlyShowIn=KDE;\n"
            "X-GNOME-Autostart-enabled=true\n" % launcher_command(),
            encoding="utf-8",
        )
    elif AUTOSTART_FILE.exists():
        AUTOSTART_FILE.unlink()


def _screens_text(count: int) -> str:
    if count == 1:
        return "1 экран"
    if 2 <= count <= 4:
        return "%d экрана" % count
    return "%d экранов" % count


def _draw_icon(painter: QPainter, rect: QRectF, kind: str, color: QColor) -> None:
    """Рисует иконку украшения вручную — без эмодзи и внешних картинок."""
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(color, 1.9)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    cx, cy = x + w / 2, y + h / 2
    side = min(w, h)

    if kind == "snow":
        radius = side / 2 - 1
        for i in range(6):
            angle = math.radians(60 * i)
            tip = QPointF(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
            painter.drawLine(QPointF(cx, cy), tip)
            base = QPointF(
                cx + math.cos(angle) * radius * 0.60,
                cy + math.sin(angle) * radius * 0.60,
            )
            for offset in (-42, 42):
                branch = angle + math.radians(offset)
                painter.drawLine(
                    base,
                    QPointF(
                        base.x() + math.cos(branch) * radius * 0.33,
                        base.y() + math.sin(branch) * radius * 0.33,
                    ),
                )

    elif kind == "garland":
        top = y + h * 0.26
        sag = h * 0.34
        left, right = x + 1, x + w - 1
        for seg in range(2):
            x0 = left + seg * (right - left) / 2
            x1 = left + (seg + 1) * (right - left) / 2
            mid = (x0 + x1) / 2
            path = QPainterPath(QPointF(x0, top))
            path.quadTo(QPointF(mid, top + sag * 2), QPointF(x1, top))
            painter.drawPath(path)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            for t in (0.25, 0.5, 0.75):
                px = x0 + (x1 - x0) * t
                py = top + sag * 2 * t * (1 - t)
                painter.drawEllipse(QPointF(px, py + 1.6), 2.1, 2.1)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

    elif kind == "tree":
        fill = QColor(color)
        fill.setAlpha(55)
        painter.setBrush(fill)
        for top_f, half_f, bottom_f in ((0.10, 0.22, 0.44), (0.30, 0.30, 0.66), (0.50, 0.38, 0.86)):
            triangle = QPainterPath()
            triangle.moveTo(cx, y + top_f * h)
            triangle.lineTo(cx - half_f * w, y + bottom_f * h)
            triangle.lineTo(cx + half_f * w, y + bottom_f * h)
            triangle.closeSubpath()
            painter.drawPath(triangle)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(cx - w * 0.06, y + h * 0.84, w * 0.12, h * 0.12))
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        star = side * 0.10
        painter.drawLine(QPointF(cx - star, y + h * 0.10), QPointF(cx + star, y + h * 0.10))
        painter.drawLine(QPointF(cx, y + h * 0.10 - star), QPointF(cx, y + h * 0.10 + star))

    elif kind == "clock":
        radius = side / 2 - 1
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
        painter.drawLine(QPointF(cx, cy), QPointF(cx, cy - radius * 0.52))
        painter.drawLine(QPointF(cx, cy), QPointF(cx + radius * 0.42, cy + radius * 0.22))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 1.7, 1.7)

    elif kind == "weather":
        sun = QPointF(x + w * 0.34, y + h * 0.30)
        painter.drawEllipse(sun, side * 0.15, side * 0.15)
        for i in range(8):
            angle = math.radians(45 * i)
            inner = QPointF(
                sun.x() + math.cos(angle) * side * 0.21,
                sun.y() + math.sin(angle) * side * 0.21,
            )
            outer = QPointF(
                sun.x() + math.cos(angle) * side * 0.29,
                sun.y() + math.sin(angle) * side * 0.29,
            )
            painter.drawLine(inner, outer)
        cloud = QPainterPath()
        cloud.addEllipse(QRectF(x + w * 0.06, y + h * 0.48, w * 0.36, h * 0.34))
        cloud.addEllipse(QRectF(x + w * 0.24, y + h * 0.34, w * 0.44, h * 0.44))
        cloud.addEllipse(QRectF(x + w * 0.48, y + h * 0.50, w * 0.34, h * 0.30))
        cloud.addRoundedRect(QRectF(x + w * 0.10, y + h * 0.62, w * 0.70, h * 0.20), 6, 6)
        painter.drawPath(cloud.simplified())

    elif kind == "wish":
        bubble = QPainterPath()
        bubble.addRoundedRect(
            QRectF(x + w * 0.08, y + h * 0.16, w * 0.84, h * 0.54), 6, 6
        )
        tail = QPainterPath()
        tail.moveTo(x + w * 0.30, y + h * 0.70)
        tail.lineTo(x + w * 0.24, y + h * 0.86)
        tail.lineTo(x + w * 0.42, y + h * 0.70)
        tail.closeSubpath()
        painter.drawPath(bubble)
        painter.drawPath(tail)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        for i in range(3):
            painter.drawEllipse(
                QPointF(x + w * (0.34 + 0.16 * i), y + h * 0.43), 1.6, 1.6
            )

    elif kind == "start":
        radius = side * 0.36
        painter.drawArc(
            QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
            55 * 16,
            290 * 16,
        )
        painter.drawLine(QPointF(cx, cy - radius * 1.25), QPointF(cx, cy - radius * 0.15))

    painter.restore()


class DecorCard(QAbstractButton):
    """Карточка украшения: иконка, название, описание и переключатель."""

    def __init__(self, key: str, title: str, subtitle: str, kind: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.title = title
        self.subtitle = subtitle
        self.kind = kind

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(104)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_Hover, True)

        self._hover = False
        self._pos = 0.0

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(170)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)
        self.toggled.connect(self._on_toggled)

    # ---------- состояние ----------

    def _on_anim(self, value) -> None:
        self._pos = float(value)
        self.update()

    def _on_toggled(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def set_on(self, on: bool, animate: bool = True) -> None:
        self.blockSignals(True)
        self.setChecked(on)
        self.blockSignals(False)
        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._pos)
            self._anim.setEndValue(1.0 if on else 0.0)
            self._anim.start()
        else:
            self._pos = 1.0 if on else 0.0
        self.update()

    # ---------- события ----------

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(360, 104)

    # ---------- отрисовка ----------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        shape = QPainterPath()
        shape.addRoundedRect(rect, 18, 18)

        accent = GOLD if self.isChecked() else QColor(150, 205, 255)
        hover_boost = 1 if self._hover else 0

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self.isChecked():
            gradient.setColorAt(0.0, QColor(255, 208, 128, 40 + 10 * hover_boost))
            gradient.setColorAt(1.0, QColor(120, 190, 255, 16 + 6 * hover_boost))
            border = QColor(255, 208, 128, 130 if self._hover else 95)
        else:
            gradient.setColorAt(0.0, QColor(255, 255, 255, 16 + 8 * hover_boost))
            gradient.setColorAt(1.0, QColor(255, 255, 255, 7 + 4 * hover_boost))
            border = QColor(255, 255, 255, 40 if self._hover else 22)

        painter.fillPath(shape, QBrush(gradient))
        painter.setPen(QPen(border, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(shape)

        # плитка с иконкой
        tile = QRectF(18, (self.height() - 46) / 2, 46, 46)
        tile_shape = QPainterPath()
        tile_shape.addRoundedRect(tile, 14, 14)
        tile_color = QColor(accent)
        tile_color.setAlpha(30 + int(18 * self._pos))
        painter.fillPath(tile_shape, tile_color)

        icon_color = QColor(accent)
        if not self.isChecked():
            icon_color.setAlpha(215)
        _draw_icon(painter, tile.adjusted(11, 11, -11, -11), self.kind, icon_color)

        # текст
        text_left = 78.0
        text_width = self.width() - text_left - 84

        title_font = QFont(self.font())
        title_font.setPixelSize(15)
        title_font.setWeight(QFont.DemiBold)
        painter.setFont(title_font)
        painter.setPen(TEXT)
        painter.drawText(
            QRectF(text_left, 24, text_width, 22),
            int(Qt.AlignLeft | Qt.AlignVCenter),
            self.title,
        )

        subtitle_font = QFont(self.font())
        subtitle_font.setPixelSize(11)
        painter.setFont(subtitle_font)
        painter.setPen(MUTED if not self.isChecked() else QColor(214, 226, 240))
        painter.drawText(
            QRectF(text_left, 47, text_width, 38),
            int(Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap),
            self.subtitle,
        )

        # переключатель
        track = QRectF(self.width() - 18 - 44, (self.height() - 24) / 2, 44, 24)
        track_color = QColor(255, 208, 128)
        track_color.setAlpha(int(70 + 120 * self._pos))
        if self._pos < 0.5:
            base = QColor(255, 255, 255, 34 + 12 * hover_boost)
            mix = 1 - self._pos * 2
            track_color = QColor(
                int(base.red() * mix + track_color.red() * (1 - mix)),
                int(base.green() * mix + track_color.green() * (1 - mix)),
                int(base.blue() * mix + track_color.blue() * (1 - mix)),
                int(base.alpha() * mix + track_color.alpha() * (1 - mix)),
            )
        painter.setPen(QPen(QColor(255, 255, 255, 45), 1))
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, 12, 12)

        knob_x = track.left() + 3 + self._pos * (track.width() - 20 - 6)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#fff7ea") if self.isChecked() else QColor("#dfe8f5"))
        painter.drawEllipse(QRectF(knob_x, track.top() + 3, 18, 18))


class WallpaperTile(QAbstractButton):
    """Плитка галереи: миниатюра, название и золотая рамка у выбранной."""

    def __init__(self, path: Path, title: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.title = title
        self._hover = False

        thumb = path.parent / "thumbs" / (path.stem + ".jpg")
        source = thumb if thumb.exists() else path
        self._pix = QPixmap(str(source))

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(146)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(200, 146)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        image_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() - 26)
        shape = QPainterPath()
        shape.addRoundedRect(image_rect, 13, 13)

        painter.save()
        painter.setClipPath(shape)
        painter.fillRect(image_rect, QColor("#162033"))
        if not self._pix.isNull():
            scaled = self._pix.scaled(
                int(image_rect.width()),
                int(image_rect.height()),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            source = QRect(
                max(0, (scaled.width() - int(image_rect.width())) // 2),
                max(0, (scaled.height() - int(image_rect.height())) // 2),
                int(image_rect.width()),
                int(image_rect.height()),
            )
            painter.drawPixmap(image_rect.toRect(), scaled, source)
        painter.restore()

        if self.isChecked():
            border, width = QColor(255, 210, 122, 235), 2.0
        elif self._hover:
            border, width = QColor(255, 255, 255, 110), 1.0
        else:
            border, width = QColor(255, 255, 255, 34), 1.0
        painter.setPen(QPen(border, width))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(shape)

        if self.isChecked():
            cx, cy = image_rect.right() - 16, image_rect.top() + 16
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 210, 122, 240))
            painter.drawEllipse(QPointF(cx, cy), 9, 9)
            check = QPen(QColor("#2b1e06"), 1.8)
            check.setCapStyle(Qt.RoundCap)
            check.setJoinStyle(Qt.RoundJoin)
            painter.setPen(check)
            painter.drawLine(QPointF(cx - 4, cy), QPointF(cx - 1, cy + 3))
            painter.drawLine(QPointF(cx - 1, cy + 3), QPointF(cx + 4, cy - 3))

        label_font = QFont(self.font())
        label_font.setPixelSize(12)
        label_font.setWeight(QFont.DemiBold if self.isChecked() else QFont.Normal)
        painter.setFont(label_font)
        if self.isChecked():
            color = GOLD
        elif self._hover:
            color = QColor("#e8f0fb")
        else:
            color = QColor("#c3d2e6")
        painter.setPen(color)
        painter.drawText(
            QRectF(rect.left(), image_rect.bottom() + 4, rect.width(), 22),
            int(Qt.AlignHCenter | Qt.AlignVCenter),
            self.title,
        )


class IconBadge(QWidget):
    """Золотая плитка со снежинкой для шапки окна."""

    def __init__(self, size: int = 54, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        shape = QPainterPath()
        shape.addRoundedRect(rect, 17, 17)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#ffe4ad"))
        gradient.setColorAt(1.0, QColor("#eeb45a"))
        painter.fillPath(shape, QBrush(gradient))

        painter.setPen(QPen(QColor(255, 255, 255, 90), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(shape)

        _draw_icon(painter, rect.adjusted(11, 11, -11, -11), "snow", QColor("#3a2708"))


class SnowWindow(QWidget):
    """Окно с фоном-градиентом и падающим снегом."""

    SHADOW = 16

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Новогодний оформитель")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(940, 664)
        self.setFocusPolicy(Qt.StrongFocus)

        self._flakes: list[dict] = []
        self._dragging = False
        self._drag_offset = None

        self._snow_timer = QTimer(self)
        self._snow_timer.setInterval(40)
        self._snow_timer.timeout.connect(self._tick)
        self._snow_timer.start()

    def _make_flakes(self) -> None:
        width, height = self.width(), self.height()
        self._flakes = [
            {
                "x": random.uniform(0, width),
                "y": random.uniform(0, height),
                "r": random.uniform(0.9, 2.5),
                "v": random.uniform(0.25, 1.05),
                "sway": random.uniform(4, 14),
                "phase": random.uniform(0, 6.283),
                "alpha": random.uniform(0.10, 0.42),
            }
            for _ in range(55)
        ]

    def content_rect(self) -> QRectF:
        shadow = self.SHADOW
        return QRectF(self.rect()).adjusted(shadow, shadow - 2, -shadow, -shadow - 2)

    def _tick(self) -> None:
        if not self._flakes:
            self._make_flakes()
        for flake in self._flakes:
            flake["y"] += flake["v"]
            if flake["y"] > self.height() + 4:
                flake["y"] = -6
                flake["x"] = random.uniform(0, self.width())
        self.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._make_flakes()

    # ---------- перетаскивание своего окна ----------

    def mousePressEvent(self, event) -> None:
        header_bottom = self.content_rect().top() + 88
        if event.button() == Qt.LeftButton and event.pos().y() < header_bottom:
            self._dragging = True
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging and self._drag_offset is not None:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self._drag_offset)
                event.accept()
                return
            self._dragging = False
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._dragging = False
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        content = self.content_rect()
        shape = QPainterPath()
        shape.addRoundedRect(content, 22, 22)

        # мягкая тень вокруг окна
        for step in range(self.SHADOW, 0, -2):
            alpha = int(30 * (1 - step / self.SHADOW) ** 2) + 2
            layer = content.adjusted(-step, -step + 4, step, step + 4)
            layer_shape = QPainterPath()
            layer_shape.addRoundedRect(layer, 22 + step, 22 + step)
            painter.fillPath(layer_shape, QColor(0, 0, 0, alpha))

        painter.save()
        painter.setClipPath(shape)

        background = QLinearGradient(0, content.top(), 0, content.bottom())
        background.setColorAt(0.0, BG_TOP)
        background.setColorAt(1.0, BG_BOTTOM)
        painter.fillRect(content, background)

        gold_glow = QRadialGradient(
            QPointF(content.right() - 60, content.top() - 30), content.width() * 0.6
        )
        gold_glow.setColorAt(0.0, QColor(255, 200, 120, 46))
        gold_glow.setColorAt(1.0, QColor(255, 200, 120, 0))
        painter.fillRect(content, gold_glow)

        ice_glow = QRadialGradient(
            QPointF(content.left() + 40, content.bottom() + 20), content.width() * 0.55
        )
        ice_glow.setColorAt(0.0, QColor(90, 160, 255, 34))
        ice_glow.setColorAt(1.0, QColor(90, 160, 255, 0))
        painter.fillRect(content, ice_glow)

        painter.setPen(Qt.NoPen)
        for flake in self._flakes:
            x = flake["x"] + math.sin(flake["phase"] + flake["y"] / 60) * flake["sway"]
            color = QColor(255, 255, 255)
            color.setAlphaF(flake["alpha"])
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, flake["y"]), flake["r"], flake["r"])

        painter.restore()

        painter.setPen(QPen(QColor(255, 255, 255, 34), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(shape)


class DecoratorWindow(SnowWindow):
    def __init__(self):
        super().__init__()
        self._state = {key: True for key, _, _, _ in CARDS}
        self._density = plasma.DEFAULT_DENSITY
        self._wallpaper = ""
        self._cards: dict[str, DecorCard] = {}
        self._tiles: dict[str, WallpaperTile] = {}
        self._density_buttons: dict[int, QPushButton] = {}
        self._build_ui()
        self._autostart_card.set_on(autostart_enabled(), animate=False)
        QTimer.singleShot(120, self._load_state)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setFocus()

    # ---------- интерфейс ----------

    def _section(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("section")
        return label

    def _hint(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("hint")
        label.setWordWrap(True)
        return label

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 26)
        layout.setSpacing(13)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_tabs())

        self.stack = QStackedWidget()
        self.stack.setFrameShape(QFrame.NoFrame)
        self.stack.setStyleSheet("QStackedWidget { background: transparent; }")
        self.stack.addWidget(self._build_decorations_page())
        self.stack.addWidget(self._build_wallpapers_page())
        self.stack.addWidget(self._build_settings_page())
        layout.addWidget(self.stack, 1)

        layout.addLayout(self._build_footer())

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(14)

        header.addWidget(IconBadge(54), 0, Qt.AlignVCenter)

        titles = QVBoxLayout()
        titles.setSpacing(3)
        title = QLabel("Новогодний оформитель")
        title.setObjectName("title")
        subtitle = QLabel("Зимние украшения рабочего стола — без перезапуска оболочки")
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch(1)

        self.chip = QLabel("Проверяю Plasma…")
        self.chip.setObjectName("chip")
        header.addWidget(self.chip, 0, Qt.AlignVCenter)
        return header

    def _build_tabs(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)

        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)
        self._tab_buttons: list[QPushButton] = []

        for index, name in enumerate(("Украшения", "Обои", "Настройки")):
            button = QPushButton(name)
            button.setObjectName("tab")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(
                lambda _checked=False, i=index: self.stack.setCurrentIndex(i)
            )
            self._tab_group.addButton(button)
            self._tab_buttons.append(button)
            row.addWidget(button)

        self._tab_buttons[0].setChecked(True)
        row.addStretch(1)
        return row

    def _build_decorations_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(0)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for index, (key, card_title, card_subtitle, kind) in enumerate(CARDS):
            card = DecorCard(key, card_title, card_subtitle, kind)
            card.toggled.connect(lambda checked, k=key: self._on_toggle(k, checked))
            self._cards[key] = card
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def _build_wallpapers_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(11)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(self._section("ЗИМНИЕ ОБОИ 4K"))
        top.addStretch(1)
        self._wall_label = QLabel("Сейчас: —")
        self._wall_label.setObjectName("wallname")
        top.addWidget(self._wall_label)
        layout.addLayout(top)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self._tile_group = QButtonGroup(self)
        self._tile_group.setExclusive(True)

        folder = wallpaper_dir()
        self._wallpaper_paths: list[Path] = []
        for index, (slug, title) in enumerate(WALLPAPERS):
            path = folder / (slug + ".jpg")
            if not path.exists():
                continue
            tile = WallpaperTile(path, title)
            tile.clicked.connect(lambda _checked=False, t=tile: self._on_wallpaper(t))
            self._tile_group.addButton(tile)
            self._tiles[slug] = tile
            self._wallpaper_paths.append(path)
            grid.addWidget(tile, index // 4, index % 4)

        if self._wallpaper_paths:
            layout.addLayout(grid)
        else:
            layout.addWidget(self._hint("Папка с обоями не найдена — переустанови программу."))

        actions = QHBoxLayout()
        actions.setSpacing(10)

        own = QPushButton("Своя картинка…")
        own.setObjectName("action")
        own.setCursor(Qt.PointingHandCursor)
        own.clicked.connect(self._pick_wallpaper)
        actions.addWidget(own)

        shuffle = QPushButton("Случайные обои")
        shuffle.setObjectName("action")
        shuffle.setCursor(Qt.PointingHandCursor)
        shuffle.clicked.connect(self._random_wallpaper)
        actions.addWidget(shuffle)

        actions.addStretch(1)
        actions.addWidget(
            self._hint("Обои ставятся на все мониторы; любимую картинку можно вернуть в любой момент.")
        )
        layout.addLayout(actions)
        layout.addStretch(1)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._section("СНЕГОПАД"))
        layout.addWidget(
            self._hint("Сколько снежинок падает поверх обоев. Меняется сразу, перезапуск не нужен.")
        )

        choice_row = QHBoxLayout()
        choice_row.setSpacing(8)
        self._density_group = QButtonGroup(self)
        self._density_group.setExclusive(True)
        for value, name in DENSITIES:
            button = QPushButton(name)
            button.setObjectName("choice")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(
                lambda _checked=False, v=value, n=name: self._on_density(v, n)
            )
            self._density_group.addButton(button)
            self._density_buttons[value] = button
            choice_row.addWidget(button)
        choice_row.addStretch(1)
        layout.addLayout(choice_row)

        layout.addSpacing(6)
        layout.addWidget(self._section("ПРИ ВХОДЕ В СИСТЕМУ"))

        self._autostart_card = DecorCard(
            "autostart",
            "Автозапуск",
            "Открывать меню при входе в систему",
            "start",
        )
        self._autostart_card.set_on(autostart_enabled(), animate=False)
        self._autostart_card.toggled.connect(self._on_autostart)
        layout.addWidget(self._autostart_card)

        layout.addSpacing(4)
        row = QHBoxLayout()
        row.setSpacing(10)

        folder = QPushButton("Открыть папку с обоями")
        folder.setObjectName("action")
        folder.setCursor(Qt.PointingHandCursor)
        folder.clicked.connect(self._open_wallpaper_folder)
        row.addWidget(folder)

        refresh = QPushButton("Обновить состояние")
        refresh.setObjectName("action")
        refresh.setCursor(Qt.PointingHandCursor)
        refresh.clicked.connect(self._load_state)
        row.addWidget(refresh)

        row.addStretch(1)
        layout.addLayout(row)

        layout.addWidget(
            self._hint(
                "Украшения и обои применяются на все подключённые мониторы. "
                "Окно таскается за шапку, Esc закрывает."
            )
        )
        layout.addStretch(1)
        return page

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(12)
        self.status = QLabel("Готово")
        self.status.setObjectName("status")
        footer.addWidget(self.status)
        footer.addStretch(1)

        close_button = QPushButton("Закрыть")
        close_button.setObjectName("close")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setFocusPolicy(Qt.NoFocus)
        close_button.clicked.connect(self.close)
        footer.addWidget(close_button)
        return footer

    # ---------- логика ----------

    def _set_chip(self, text: str, mode: str) -> None:
        self.chip.setText(text)
        self.chip.setObjectName({"ok": "chipOk", "err": "chipErr"}.get(mode, "chip"))
        self.chip.style().unpolish(self.chip)
        self.chip.style().polish(self.chip)

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status.setText(text)
        color = "#ff9e9e" if error else "#8fa2ba"
        self.status.setStyleSheet(f"color: {color};")

    def _current_tile_key(self) -> str:
        if not self._wallpaper:
            return ""
        target = os.path.realpath(self._wallpaper)
        for slug, tile in self._tiles.items():
            if os.path.realpath(str(tile.path)) == target:
                return slug
        return ""

    def _select_wallpaper(self, path: str) -> None:
        self._wallpaper = path
        key = self._current_tile_key()

        self._tile_group.setExclusive(False)
        for slug, tile in self._tiles.items():
            tile.setChecked(slug == key)
            tile.update()
        self._tile_group.setExclusive(True)

        name = Path(path).name if path else "—"
        if len(name) > 42:
            name = name[:39] + "…"
        self._wall_label.setText("Сейчас: " + name)

    def _select_density(self, density: int) -> None:
        self._density = density
        nearest = min(DENSITIES, key=lambda item: abs(item[0] - density))[0]
        for value, button in self._density_buttons.items():
            button.setChecked(value == nearest)

    def _load_state(self) -> None:
        try:
            info = plasma.read_all()
        except plasma.PlasmaError as error:
            self._set_chip("Нет связи с Plasma", "err")
            self._set_status(f"Plasma недоступна: {error}", error=True)
            return

        self._state = info["state"]
        for key, card in self._cards.items():
            card.set_on(self._state.get(key, True), animate=False)

        self._select_density(info["density"])
        self._select_wallpaper(info["wallpaper"])
        self._autostart_card.set_on(autostart_enabled(), animate=False)

        chip = "Plasma на связи"
        if info["screens"] > 1:
            chip += " · " + _screens_text(info["screens"])
        self._set_chip(chip, "ok")
        self._set_status("Текущий вид загружен · " + datetime.now().strftime("%H:%M"))

    def _apply(self) -> bool:
        try:
            plasma.apply_state(self._state, self._density)
        except plasma.PlasmaError as error:
            self._set_status(f"Не применилось: {error}", error=True)
            return False
        self._set_status("Применено · " + datetime.now().strftime("%H:%M"))
        return True

    def _on_toggle(self, key: str, checked: bool) -> None:
        self._state[key] = checked
        self._apply()

    def _on_density(self, value: int, name: str) -> None:
        previous = self._density
        try:
            plasma.set_density(value)
        except plasma.PlasmaError as error:
            self._select_density(previous)
            self._set_status(f"Не применилось: {error}", error=True)
            return

        self._density = value
        self._set_status("Снег: " + name.lower())

    def _apply_wallpaper(self, path: Path) -> bool:
        try:
            plasma.set_wallpaper(str(path))
        except plasma.PlasmaError as error:
            self._select_wallpaper(self._wallpaper)
            self._set_status(f"Обои не сменились: {error}", error=True)
            return False

        self._select_wallpaper(str(path))
        self._set_status("Обои: " + path.name)
        return True

    def _on_wallpaper(self, tile: WallpaperTile) -> None:
        self._apply_wallpaper(tile.path)

    def _pick_wallpaper(self) -> None:
        pictures = Path.home() / "Pictures"
        start = str(pictures if pictures.is_dir() else Path.home())
        name, _filter = QFileDialog.getOpenFileName(
            self,
            "Выбери картинку для рабочего стола",
            start,
            "Изображения (*.jpg *.jpeg *.png *.webp *.bmp)",
        )
        if name:
            self._apply_wallpaper(Path(name))

    def _random_wallpaper(self) -> None:
        if not self._wallpaper_paths:
            return
        current = self._current_tile_key()
        pool = [path for path in self._wallpaper_paths if path.stem != current]
        if not pool:
            pool = self._wallpaper_paths
        self._apply_wallpaper(random.choice(pool))

    def _open_wallpaper_folder(self) -> None:
        folder = wallpaper_dir()
        if folder.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
        else:
            self._set_status("Папка с обоями не найдена.", error=True)

    def _on_autostart(self, checked: bool) -> None:
        try:
            set_autostart(checked)
        except OSError as error:
            self._autostart_card.set_on(not checked, animate=False)
            self._set_status(f"Не получилось: {error}", error=True)
            return
        self._set_status("Автозапуск включён" if checked else "Автозапуск выключен")
