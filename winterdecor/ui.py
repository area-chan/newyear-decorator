"""Окно и виджеты «Новогоднего оформителя»."""

from __future__ import annotations

import math
import random
from datetime import datetime

from PyQt5.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt5.QtWidgets import (
    QAbstractButton,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import plasma
from .theme import BG_BOTTOM, BG_TOP, GOLD, ICE, MUTED, OK, TEXT

CARDS = [
    ("snow", "Снегопад", "Мягкий снег поверх обоев", "snow"),
    ("garland", "Гирлянда", "Огоньки вдоль верхнего края", "garland"),
    ("tree", "Ёлка", "Украшенная ёлка с огнями", "tree"),
    ("clock", "Часы", "Крупные часы с датой", "clock"),
    ("weather", "Погода", "Температура и ветер", "weather"),
    ("wish", "Пожелание дня", "Тёплая фраза на утро", "wish"),
]

PRESETS = [
    (
        "Полный Новый год",
        {
            "snow": True,
            "garland": True,
            "tree": True,
            "clock": True,
            "weather": True,
            "wish": True,
        },
    ),
    (
        "Уютный минимум",
        {
            "snow": True,
            "garland": True,
            "tree": True,
            "clock": False,
            "weather": False,
            "wish": False,
        },
    ),
    (
        "Только снег",
        {
            "snow": True,
            "garland": False,
            "tree": False,
            "clock": False,
            "weather": False,
            "wish": False,
        },
    ),
    (
        "Выключить всё",
        {
            "snow": False,
            "garland": False,
            "tree": False,
            "clock": False,
            "weather": False,
            "wish": False,
        },
    ),
]


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
        self._cards: dict[str, DecorCard] = {}
        self._build_ui()
        QTimer.singleShot(120, self._load_state)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setFocus()

    # ---------- интерфейс ----------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(46, 40, 46, 38)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(14)

        header.addWidget(IconBadge(54), 0, Qt.AlignVCenter)

        titles = QVBoxLayout()
        titles.setSpacing(3)
        title = QLabel("Новогодний оформитель")
        title.setObjectName("title")
        subtitle = QLabel("Выбери украшения — рабочий стол меняется сразу, без перезапуска")
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch(1)

        self.chip = QLabel("Проверяю Plasma…")
        self.chip.setObjectName("chip")
        header.addWidget(self.chip, 0, Qt.AlignVCenter)
        layout.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for index, (key, card_title, card_subtitle, kind) in enumerate(CARDS):
            card = DecorCard(key, card_title, card_subtitle, kind)
            card.toggled.connect(
                lambda checked, k=key: self._on_toggle(k, checked)
            )
            self._cards[key] = card
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)

        presets_label = QLabel("ПРЕСЕТЫ")
        presets_label.setObjectName("section")
        layout.addWidget(presets_label)

        presets_row = QHBoxLayout()
        presets_row.setSpacing(10)
        for name, preset in PRESETS:
            button = QPushButton(name)
            button.setObjectName("preset")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, p=preset: self._apply_preset(p)
            )
            presets_row.addWidget(button)
        layout.addLayout(presets_row)

        layout.addStretch(1)

        footer = QHBoxLayout()
        footer.setSpacing(12)
        self.status = QLabel("Готово")
        self.status.setObjectName("status")
        footer.addWidget(self.status)
        footer.addStretch(1)

        close_button = QPushButton("Закрыть")
        close_button.setObjectName("close")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.close)
        footer.addWidget(close_button)
        layout.addLayout(footer)

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

    def _load_state(self) -> None:
        try:
            plasma.check_ready()
            state = plasma.read_state()
        except plasma.PlasmaError as error:
            self._set_chip("Нет связи с Plasma", "err")
            self._set_status(f"Plasma недоступна: {error}", error=True)
            return

        self._state = state
        for key, card in self._cards.items():
            card.set_on(state.get(key, True), animate=False)
        self._set_chip("Plasma на связи", "ok")
        self._set_status("Текущий вид загружен · " + datetime.now().strftime("%H:%M"))

    def _apply(self) -> bool:
        try:
            plasma.apply_state(self._state)
        except plasma.PlasmaError as error:
            self._set_status(f"Не применилось: {error}", error=True)
            return False
        self._set_status("Применено · " + datetime.now().strftime("%H:%M"))
        return True

    def _on_toggle(self, key: str, checked: bool) -> None:
        self._state[key] = checked
        self._apply()

    def _apply_preset(self, preset: dict[str, bool]) -> None:
        for key, value in preset.items():
            self._state[key] = value
            card = self._cards.get(key)
            if card is not None:
                card.set_on(value)
        if self._apply():
            self._set_status(
                "Пресет применён · " + datetime.now().strftime("%H:%M")
            )
