#!/usr/bin/env bash
# Установка «Новогоднего оформителя» и его украшений (без root).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
PLASMA="$DATA/plasma"
APPS="$DATA/applications"
ICONS="$DATA/icons/hicolor/scalable/apps"
BIN="$HOME/.local/bin"
APP="$DATA/newyear-decorator"

say() { printf '\033[1;36m==>\033[0m %s\n' "$1"; }

if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "Не найден PyQt5. Установи его:"
    echo "  sudo apt install python3-pyqt5"
    exit 1
fi

say "Ставлю украшения рабочего стола (виджеты и плагин обоев)"
mkdir -p "$PLASMA/plasmoids" "$PLASMA/wallpapers"
for package in "$HERE"/plasmoids/*; do
    rm -rf "$PLASMA/plasmoids/$(basename "$package")"
    cp -R "$package" "$PLASMA/plasmoids/"
done
for package in "$HERE"/wallpapers/*; do
    rm -rf "$PLASMA/wallpapers/$(basename "$package")"
    cp -R "$package" "$PLASMA/wallpapers/"
done

say "Ставлю программу, обои и иконку"
mkdir -p "$APPS" "$ICONS" "$BIN" "$APP/assets"
rm -rf "$APP/winterdecor" "$APP/assets/wallpapers" "$APP/assets/thumbs"
cp "$HERE/main.py" "$APP/"
cp -R "$HERE/winterdecor" "$APP/"
rm -rf "$APP/winterdecor/__pycache__"
cp "$HERE/assets/newyear-decorator.svg" "$APP/assets/"
cp -R "$HERE/assets/wallpapers" "$APP/assets/"
cp "$APP/assets/newyear-decorator.svg" "$ICONS/newyear-decorator.svg"

cat > "$BIN/newyear-decorator" <<LAUNCHER
#!/usr/bin/env bash
exec python3 "$APP/main.py" "\$@"
LAUNCHER
chmod +x "$BIN/newyear-decorator"

sed "s|^Exec=.*|Exec=$BIN/newyear-decorator|" \
    "$HERE/newyear-decorator.desktop" > "$APPS/newyear-decorator.desktop"
chmod +x "$APPS/newyear-decorator.desktop"

update-desktop-database "$APPS" 2>/dev/null || true
gtk-update-icon-cache -f -t "$DATA/icons/hicolor" 2>/dev/null || true

cat <<'DONE'

Готово!

1. Перезапусти Plasma, чтобы она увидела новые виджеты:
     kquitapp5 plasmashell && setsid plasmashell >/dev/null 2>&1 &
   (или просто выйди из системы и зайди снова)

2. Правый клик по рабочему столу → «Добавить виджеты»:
     Погода · Часы · Ёлка · Пожелание дня
   Расставь их как нравится и нажми «Закрепить виджеты».

3. Запускай «Новогодний оформитель» из меню приложений.
   Внутри — шесть украшений, восемь зимних обоев 4K, плотность снега
   и автозапуск. Всё применяется сразу, без перезапуска.

DONE
