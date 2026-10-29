"""Связь с KDE Plasma через D-Bus (qdbus).

Плазма умеет выполнять JS прямо в оболочке: evaluateScript. Этого достаточно,
чтобы включать и выключать плазмоиды и снег с гирляндой без перезапуска
plasmashell — изменения видны сразу.
"""

from __future__ import annotations

import re
import shutil
import subprocess

DBUS_SERVICE = "org.kde.plasmashell"
DBUS_PATH = "/PlasmaShell"
DBUS_IFACE = "org.kde.PlasmaShell"

WALLPAPER_PLUGIN = "org.winter.snow"

# ключ в программе -> имя плазмоида
WIDGETS = {
    "tree": "org.winter.tree",
    "clock": "org.winter.clock",
    "weather": "org.winter.weather",
    "wish": "org.winter.wish",
}

KEYS = ("snow", "garland", "tree", "clock", "weather", "wish")

READ_SCRIPT = """
var out = [];
var d = desktops()[0];
d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
out.push("SNOW=" + d.readConfig("Snow"));
out.push("GARLAND=" + d.readConfig("Garland"));
var ws = d.widgets();
for (var i = 0; i < ws.length; ++i) {
    ws[i].currentConfigGroup = ["Configuration", "General"];
    out.push("WIDGET:" + ws[i].type + ":" + ws[i].readConfig("enabled"));
}
print(out.join("\\n"));
"""

APPLY_TEMPLATE = """
var on = {%(flags)s};
var d = desktops()[0];

// запоминаем путь к любимым обоям, чтобы снег рисовался поверх них
d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
var img = d.readConfig("Image");
d.currentConfigGroup = ["Wallpaper", "org.winter.snow", "General"];
var snowImg = d.readConfig("Image");
if (!img) img = snowImg;
if (img) d.writeConfig("Image", img);

d.writeConfig("Snow", on.snow);
d.writeConfig("Garland", on.garland);

// снег и гирлянда живут в плагине обоев, остальное — обычные виджеты
var plugin = "org.winter.snow";
if (!on.snow && !on.garland && img) plugin = "org.kde.image";
if (d.wallpaperPlugin !== plugin) d.wallpaperPlugin = plugin;

var widgets = {%(widgets)s};
var ws = d.widgets();
for (var i = 0; i < ws.length; ++i) {
    var t = ws[i].type;
    if (widgets[t] === undefined)
        continue;
    ws[i].currentConfigGroup = ["Configuration", "General"];
    ws[i].writeConfig("enabled", widgets[t]);
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


def read_state() -> dict[str, bool]:
    """Текущее состояние украшений."""
    text = _call(READ_SCRIPT)
    state = {key: True for key in KEYS}

    match = re.search(r"SNOW=(\S*)", text)
    if match:
        state["snow"] = _as_bool(match.group(1))

    match = re.search(r"GARLAND=(\S*)", text)
    if match:
        state["garland"] = _as_bool(match.group(1))

    for plugin, raw in re.findall(r"WIDGET:([\w.]+):(\S*)", text):
        for key, name in WIDGETS.items():
            if name == plugin:
                state[key] = _as_bool(raw)

    return state


def apply_state(state: dict[str, bool]) -> None:
    """Записать состояние в Plasma — применится сразу, без перезапуска."""
    flags = ", ".join(
        "%s: %s" % (key, "true" if state.get(key, False) else "false") for key in KEYS
    )
    widgets = ", ".join(
        '"%s": %s' % (plugin, "true" if state.get(key, False) else "false")
        for key, plugin in WIDGETS.items()
    )
    script = APPLY_TEMPLATE % {"flags": flags, "widgets": widgets}

    out = _call(script)
    if "OK" not in out:
        raise PlasmaError("Plasma не подтвердила изменение настроек.")


def check_ready() -> None:
    """Быстрая проверка, что Plasma вообще отвечает."""
    text = _call('print("READY");')
    if "READY" not in text:
        raise PlasmaError("Plasma не ответила на проверку связи.")
