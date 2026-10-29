import QtQuick 2.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0

Item {
    id: root

    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // включается/выключается из «Новогоднего оформителя»
    visible: plasmoid.configuration.enabled

    readonly property int lightCount: 36

    // общий «тик» для мигания: 10 кадров в секунду вместо 60
    property real tick: 0
    Timer {
        interval: 160
        repeat: true
        running: root.visible
        onTriggered: root.tick += 0.16
    }
    readonly property var lightColors: [
        "#ffd166", "#ff6b6b", "#7bffb2", "#6bb7ff", "#ffffff",
        "#ffa94d", "#ff8ad4"
    ]

    // украшения: x, y (доли), цвет, размер (доля ширины)
    readonly property var baubles: [
        { xf: 0.500, yf: 0.300, c: "#e2413f", s: 0.085 },
        { xf: 0.405, yf: 0.395, c: "#f0b429", s: 0.075 },
        { xf: 0.595, yf: 0.395, c: "#4aa3df", s: 0.075 },
        { xf: 0.440, yf: 0.545, c: "#e86a9a", s: 0.080 },
        { xf: 0.560, yf: 0.545, c: "#7ac74f", s: 0.080 },
        { xf: 0.345, yf: 0.640, c: "#b06ad6", s: 0.075 },
        { xf: 0.655, yf: 0.640, c: "#ff8c42", s: 0.075 },
        { xf: 0.470, yf: 0.720, c: "#f4f4f4", s: 0.070 },
        { xf: 0.570, yf: 0.780, c: "#5dd6c0", s: 0.070 }
    ]

    function tier(which) {
        if (which === 0) return { apex: 0.17, base: 0.45, half: 0.185 };
        if (which === 1) return { apex: 0.33, base: 0.64, half: 0.290 };
        return { apex: 0.50, base: 0.83, half: 0.400 };
    }

    // огоньки по нижним кромкам и по скатам ярусов
    function lightPos(i) {
        var perTier = lightCount / 3;
        var t = Math.floor(i / perTier);
        var k = i % perTier;
        var tr = tier(t);
        var cx = width / 2;
        var ay = height * tr.apex;
        var by = height * tr.base;
        var half = width * tr.half;

        if (k < 6) {                     // по нижней кромке
            var f = k / 5 * 2 - 1;
            return { x: cx + f * half * 0.86, y: by - height * 0.012, t: t };
        }
        var edge = (k - 6) % 3;          // 0..2 по скату
        var side = (k - 6) < 3 ? -1 : 1;
        var tt = 0.30 + edge * 0.24;     // 0.30, 0.54, 0.78
        return {
            x: cx + side * half * tt,
            y: ay + (by - ay) * tt,
            t: t
        };
    }

    // ---- стеклянная карточка ----
    Rectangle {
        anchors.fill: parent
        radius: 22
        color: Qt.rgba(10 / 255, 16 / 255, 26 / 255, 0.72)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.13)

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 21
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.06) }
                GradientStop { position: 0.5; color: Qt.rgba(1, 1, 1, 0.0) }
            }
        }
    }

    // ---- ёлка, снег и свечение ----
    Canvas {
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            var w = width;
            var h = height;
            var cx = w / 2;

            // тёплое свечение вокруг ёлки
            var glow = ctx.createRadialGradient(cx, h * 0.55, h * 0.05, cx, h * 0.55, h * 0.52);
            glow.addColorStop(0.0, "rgba(255,196,110,0.16)");
            glow.addColorStop(1.0, "rgba(255,196,110,0.0)");
            ctx.fillStyle = glow;
            ctx.fillRect(0, 0, w, h);

            // свечение звезды
            var sg = ctx.createRadialGradient(cx, h * 0.115, 1, cx, h * 0.115, h * 0.11);
            sg.addColorStop(0.0, "rgba(255,225,150,0.55)");
            sg.addColorStop(0.45, "rgba(255,215,120,0.20)");
            sg.addColorStop(1.0, "rgba(255,215,120,0.0)");
            ctx.fillStyle = sg;
            ctx.fillRect(0, 0, w, h);

            // ствол
            ctx.fillStyle = "#6b4a2f";
            ctx.fillRect(cx - w * 0.045, h * 0.795, w * 0.09, h * 0.10);
            ctx.fillStyle = "rgba(0,0,0,0.18)";
            ctx.fillRect(cx + w * 0.028, h * 0.795, w * 0.017, h * 0.10);

            function drawTier(tr, c1, c2, snowY) {
                var ay = h * tr.apex;
                var by = h * tr.base;
                var half = w * tr.half;

                var g = ctx.createLinearGradient(cx - half, ay, cx + half, by);
                g.addColorStop(0.0, c1);
                g.addColorStop(0.55, c2);
                g.addColorStop(1.0, c1);
                ctx.beginPath();
                ctx.moveTo(cx, ay);
                ctx.lineTo(cx - half, by);
                ctx.lineTo(cx + half, by);
                ctx.closePath();
                ctx.fillStyle = g;
                ctx.fill();

                // лёгкий контур
                ctx.strokeStyle = "rgba(255,255,255,0.10)";
                ctx.lineWidth = 1;
                ctx.stroke();

                // снежная кромка снизу
                ctx.beginPath();
                ctx.moveTo(cx - half * 0.97, by);
                ctx.quadraticCurveTo(cx, by - h * 0.012, cx + half * 0.97, by);
                ctx.strokeStyle = "rgba(255,255,255,0.12)";
                ctx.lineWidth = Math.max(3, h * 0.016);
                ctx.stroke();
                ctx.strokeStyle = "rgba(255,255,255,0.55)";
                ctx.lineWidth = Math.max(1.2, h * 0.006);
                ctx.stroke();
            }

            // нижний ярус — самый тёмный, верхний — светлее
            drawTier(tier(2), "#1f4c32", "#2f6a45");
            drawTier(tier(1), "#235639", "#356f4b");
            drawTier(tier(0), "#286041", "#3d7d55");
        }
    }

    // ---- звезда ----
    Text {
        text: "\u2605"
        color: "#ffd166"
        font.pixelSize: Math.round(root.height * 0.105)
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.height * 0.062
        opacity: 0.82 + 0.18 * Math.sin(root.tick * 1.6)
    }

    // ---- огоньки гирлянды ----
    Repeater {
        model: root.lightCount

        Item {
            id: light
            width: Math.round(root.width * 0.10)
            height: width
            x: root.lightPos(index).x - width / 2
            y: root.lightPos(index).y - height / 2

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: root.lightColors[index % root.lightColors.length]
                opacity: 0.22
            }

            Rectangle {
                width: Math.round(parent.width * 0.30)
                height: width
                radius: width / 2
                anchors.centerIn: parent
                color: root.lightColors[index % root.lightColors.length]
            }

            Rectangle {
                width: Math.round(parent.width * 0.12)
                height: width
                radius: width / 2
                anchors.centerIn: parent
                color: "#ffffff"
                opacity: 0.9
            }

            opacity: 0.55 + 0.45 * Math.sin(root.tick * 2.6 + index * 0.7)
        }
    }

    // ---- шарики ----
    Repeater {
        model: root.baubles.length

        Item {
            id: bauble
            property var b: root.baubles[index]

            width: Math.round(root.width * b.s)
            height: width
            x: root.width * b.xf - width / 2
            y: root.height * b.yf - height / 2

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: bauble.b.c
                opacity: 0.15
            }

            Rectangle {
                width: parent.width * 0.72
                height: width
                radius: width / 2
                anchors.centerIn: parent
                color: bauble.b.c
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.55)

                Rectangle {
                    width: parent.width * 0.30
                    height: width
                    radius: width / 2
                    color: Qt.rgba(1, 1, 1, 0.70)
                    x: parent.width * 0.18
                    y: parent.height * 0.16
                }
            }
        }
    }
}
