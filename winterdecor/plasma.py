"""Связь с KDE Plasma через D-Bus (qdbus).

Плазма умеет выполнять JS прямо в оболочке: evaluateScript. Этого достаточно,
чтобы включать и выключать плазмоиды, менять обои и плотность снега без
перезапуска plasmashell — изменения видны сразу.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from urllib.parse import unquote, urlparse

DBUS_SERVICE = "org.kde.plasmashell"
DBUS_PATH = "/PlasmaShell"
DBUS_IFACE = "org.kde.PlasmaShell"

SNOW_PLUGIN = "org.winter.snow"
IMAGE_PLUGIN = "org.kde.image"

# ключ в программе -> имя плазмоида
WIDGETS = {
    "tree": "org.winter.tree",
    "clock": "org.winter.clock",
    "weather": "org.winter.weather",
    "wish": "org.winter.wish",
}

KEYS = ("snow", "garland", "tree", "clock", "weather", "wish")

DEFAULT_DENSITY = 120

READ_SCRIPT = """
var out = [];
var ds = desktops();
var d = ds[0];

d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
out.push("IMAGE=" + d.readConfig("Image"));

d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
out.push("SNOWIMAGE=" + d.readConfig("Image"));
out.push("DENSITY=" + d.readConfig("Density"));
out.push("SNOW=" + d.readConfig("Snow"));
out.push("GARLAND=" + d.readConfig("Garland"));
out.push("SCREENS=" + ds.length);

var ws = d.widgets();
for (var i = 0; i < ws.length; ++i) {
    ws[i].currentConfigGroup = ["Configuration", "General"];
    out.push("WIDGET:" + ws[i].type + ":" + ws[i].readConfig("enabled"));
}
print(out.join("\\n"));
"""

APPLY_TEMPLATE = """
var on = {%(flags)s};
var density = %(density)d;
var widgets = {%(widgets)s};
var ds = desktops();

for (var k = 0; k < ds.length; ++k) {
    var d = ds[k];

    // запоминаем путь к любимым обоям, чтобы снег рисовался поверх них
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    var img = d.readConfig("Image");
    d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
    if (!img) img = d.readConfig("Image");
    if (img) d.writeConfig("Image", img);

    d.writeConfig("Snow", on.snow);
    d.writeConfig("Garland", on.garland);
    d.writeConfig("Density", density);

    // снег и гирлянда живут в плагине обоев, остальное — обычные виджеты
    if (on.snow || on.garland) {
        if (d.wallpaperPlugin !== "org.winter.snow")
            d.wallpaperPlugin = "org.winter.snow";
    } else if (img) {
        if (d.wallpaperPlugin !== "org.kde.image")
            d.wallpaperPlugin = "org.kde.image";
    }

    var ws = d.widgets();
    for (var i = 0; i < ws.length; ++i) {
        var t = ws[i].type;
        if (widgets[t] === undefined)
            continue;
        ws[i].currentConfigGroup = ["Configuration", "General"];
        ws[i].writeConfig("enabled", widgets[t]);
    }
}
print("OK");
"""

WALLPAPER_TEMPLATE = """
var url = %(url)s;
var ds = desktops();

for (var k = 0; k < ds.length; ++k) {
    var d = ds[k];
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", url);
    d.writeConfig("FillMode", 2);
    d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
    d.writeConfig("Image", url);
}
print("OK");
"""

DENSITY_TEMPLATE = """
var value = %(density)d;
var ds = desktops();
for (var k = 0; k < ds.length; ++k) {
    var d = ds[k];
    d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
    d.writeConfig("Density", value);
}
print("OK");
"""


class PlasmaError(RuntimeError):
    """Плазма недоступна или отказалась выполнять скрипт."""


def _qdbus_binary() -> str:
    for name in ("qdbus", "qdbus-qt5"):
        path = shutil.which(name)
        if path:
            return path
    raise PlasmaError(
        "Не найден qdbus. Установи пакет qdbus (в Linux Mint он обычно уже есть)."
    )


def _call(script: str) -> str:
    try:
        result = subprocess.run(
            [
                _qdbus_binary(),
                DBUS_SERVICE,
                DBUS_PATH,
                f"{DBUS_IFACE}.evaluateScript",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired as exc:
        raise PlasmaError("Plasma не ответила вовремя.") from exc
    except OSError as exc:
        raise PlasmaError(f"Не удалось запустить qdbus: {exc}") from exc

    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise PlasmaError(message or "Plasma вернула ошибку.")

    return result.stdout


def _as_bool(raw: str | None) -> bool:
    """Пустое значение = настройка ещё не сохранялась, значит включено."""
    if raw is None:
        return True
    value = raw.strip().lower()
    if value in ("true", "1"):
        return True
    if value in ("false", "0"):
        return False
    return True


def to_url(path: str) -> str:
    """Путь к файлу в виде file://..., как его хранит Plasma."""
    if path.startswith("file://"):
        return path
    from pathlib import Path

    return Path(path).expanduser().resolve().as_uri()


def to_path(value: str | None) -> str:
    """Обратное преобразование: file://... -> обычный путь."""
    if not value:
        return ""
    value = value.strip()
    if value.startswith("file://"):
        return unquote(urlparse(value).path)
    return value


def read_all() -> dict:
    """Состояние украшений, текущие обои и плотность снега одним запросом."""
    text = _call(READ_SCRIPT)

    values: dict[str, str] = {}
    widgets: list[tuple[str, str]] = []
    for line in text.splitlines():
        if line.startswith("WIDGET:"):
            parts = line.split(":", 2)
            if len(parts) == 3:
                widgets.append((parts[1], parts[2]))
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value

    state = {key: True for key in KEYS}
    state["snow"] = _as_bool(values.get("SNOW"))
    state["garland"] = _as_bool(values.get("GARLAND"))
    for plugin, raw in widgets:
        for key, name in WIDGETS.items():
            if name == plugin:
                state[key] = _as_bool(raw)

    try:
        density = int(values.get("DENSITY", ""))
    except ValueError:
        density = DEFAULT_DENSITY
    if density < 20:
        density = DEFAULT_DENSITY

    try:
        screens = max(1, int(values.get("SCREENS", "1")))
    except ValueError:
        screens = 1

    wallpaper = to_path(values.get("IMAGE")) or to_path(values.get("SNOWIMAGE"))

    return {
        "state": state,
        "wallpaper": wallpaper,
        "density": density,
        "screens": screens,
    }


def apply_state(state: dict[str, bool], density: int | None = None) -> None:
    """Записать состояние в Plasma — применится сразу, без перезапуска."""
    flags = ", ".join(
        "%s: %s" % (key, "true" if state.get(key, False) else "false") for key in KEYS
    )
    widgets = ", ".join(
        '"%s": %s' % (plugin, "true" if state.get(key, False) else "false")
        for key, plugin in WIDGETS.items()
    )
    script = APPLY_TEMPLATE % {
        "flags": flags,
        "density": DEFAULT_DENSITY if density is None else int(density),
        "widgets": widgets,
    }

    out = _call(script)
    if "OK" not in out:
        raise PlasmaError("Plasma не подтвердила изменение настроек.")


def set_wallpaper(path: str) -> None:
    """Поставить картинку на все мониторы, не трогая украшения."""
    script = WALLPAPER_TEMPLATE % {"url": json.dumps(to_url(path))}
    out = _call(script)
    if "OK" not in out:
        raise PlasmaError("Plasma не подтвердила смену обоев.")


def set_density(count: int) -> None:
    """Сколько снежинок рисовать (на всех мониторах)."""
    script = DENSITY_TEMPLATE % {"density": max(20, int(count))}
    out = _call(script)
    if "OK" not in out:
        raise PlasmaError("Plasma не подтвердила плотность снега.")


def check_ready() -> None:
    """Быстрая проверка, что Plasma вообще отвечает."""
    text = _call('print("READY");')
    if "READY" not in text:
        raise PlasmaError("Plasma не ответила на проверку связи.")
