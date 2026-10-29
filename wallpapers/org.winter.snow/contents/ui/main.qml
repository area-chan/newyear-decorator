import QtQuick 2.15

Item {
    id: root

    // настройки из «Новогоднего оформителя»
    readonly property bool snowOn: wallpaper.configuration.Snow !== false
    readonly property bool garlandOn: wallpaper.configuration.Garland !== false
    readonly property int density: Math.max(20, Number(wallpaper.configuration.Density) || 120)

    // общий тик для снега и гирлянды (12 кадров в секунду)
    property real tick: 0

    // Обои, поверх которых идёт снег (путь подставляет «Новогодний оформитель»)
    property string imagePath: wallpaper.configuration.Image || ""

    // подстраховка: если картинка не задана, рисуем зимний градиент, а не чёрный экран
    Rectangle {
        anchors.fill: parent
        visible: root.imagePath === ""
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0b1526" }
            GradientStop { position: 0.55; color: "#16243c" }
            GradientStop { position: 1.0; color: "#24405f" }
        }
    }

    Image {
        anchors.fill: parent
        visible: root.imagePath !== ""
        source: root.imagePath
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: true
    }

    Item {
        id: field
        anchors.fill: parent
        clip: true
        visible: root.snowOn

        Repeater {
            model: root.density

            Rectangle {
                property real speed: 0.55 + Math.random() * 1.5
                property real sway: 5 + Math.random() * 15
                property real phase: Math.random() * 6.283
                property real baseX: Math.random() * root.width

                width: 1.3 + Math.random() * 3.2
                height: width
                radius: width / 2
                color: "#ffffff"
                opacity: 0.20 + Math.random() * 0.55
                x: baseX
                y: Math.random() * root.height - root.height * 0.2
                antialiasing: true
                smooth: true
            }
        }
    }

    // один таймер на всё: снег и мигание гирлянды
    Timer {
        interval: 95
        repeat: true
        running: root.snowOn || root.garlandOn
        onTriggered: {
            if (root.snowOn) {
                var w = field.width;
                var h = field.height;
                for (var i = 0; i < field.children.length; ++i) {
                    var f = field.children[i];
                    if (f.speed === undefined)
                        continue;
                    f.y += f.speed;
                    if (f.y > h + 8) {
                        f.y = -8 - Math.random() * 40;
                        f.baseX = Math.random() * w;
                    }
                    f.x = f.baseX + Math.sin(f.phase + f.y / 55) * f.sway;
                }
            }
            root.tick += 0.095;
        }
    }

    // ---- гирлянда вдоль верхнего края ----
    Item {
        id: garland
        x: 0
        y: 34
        width: parent.width
        height: 28
        visible: root.garlandOn

        readonly property int lightCount: Math.max(24, Math.round(width / 46))
        readonly property var colors: [
            "#ffd166", "#ff6b6b", "#7bffb2", "#6bb7ff", "#ffffff",
            "#ffa94d", "#ff8ad4"
        ]

        function dotX(i) {
            return 14 + i * (width - 28) / (lightCount - 1);
        }
        function dotY(i) {
            return 7 + 11 * Math.sin(Math.PI * i / (lightCount - 1));
        }

        Canvas {
            anchors.fill: parent

            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                ctx.strokeStyle = "rgba(255,255,255,0.25)";
                ctx.lineWidth = 1.6;
                ctx.beginPath();
                for (var i = 0; i < garland.lightCount; ++i) {
                    var px = garland.dotX(i);
                    var py = garland.dotY(i);
                    if (i === 0)
                        ctx.moveTo(px, py);
                    else
                        ctx.lineTo(px, py);
                }
                ctx.stroke();
            }

            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
        }

        Repeater {
            model: garland.lightCount

            Item {
                width: 26
                height: 26
                x: garland.dotX(index) - width / 2
                y: garland.dotY(index) - height / 2

                Rectangle {
                    anchors.fill: parent
                    radius: width / 2
                    color: garland.colors[index % garland.colors.length]
                    opacity: 0.25
                }

                Rectangle {
                    width: 7
                    height: 7
                    radius: 3.5
                    anchors.centerIn: parent
                    color: garland.colors[index % garland.colors.length]
                }

                Rectangle {
                    width: 3
                    height: 3
                    radius: 1.5
                    anchors.centerIn: parent
                    color: "#ffffff"
                    opacity: 0.95
                }

                opacity: 0.6 + 0.4 * Math.sin(root.tick * 2.8 + index * 0.75)
            }
        }
    }
}
