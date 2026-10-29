import QtQuick 2.15
import QtGraphicalEffects 1.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0

Item {
    id: root

    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // включается/выключается из «Новогоднего оформителя»
    visible: plasmoid.configuration.enabled

    property date now: new Date()

    readonly property var weekdays: [
        "воскресенье", "понедельник", "вторник", "среда",
        "четверг", "пятница", "суббота"
    ]
    readonly property var months: [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]

    function two(n) {
        return n < 10 ? "0" + n : "" + n;
    }

    readonly property string hh: two(now.getHours())
    readonly property string mm: two(now.getMinutes())
    readonly property string ss: two(now.getSeconds())
    readonly property bool colonOn: now.getSeconds() % 2 === 0
    readonly property string dateText: weekdays[now.getDay()] + ", " + now.getDate() + " " + months[now.getMonth()]

    Timer {
        interval: 1000
        repeat: true
        running: root.visible
        triggeredOnStart: true
        onTriggered: root.now = new Date()
    }

    // ---- стеклянная карточка ----
    Rectangle {
        id: card
        anchors.fill: parent
        radius: 20
        color: Qt.rgba(10 / 255, 16 / 255, 26 / 255, 0.72)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.13)

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 19
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.07) }
                GradientStop { position: 0.45; color: Qt.rgba(1, 1, 1, 0.0) }
            }
        }

        // мягкий отсвет сверху
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            width: parent.width
            height: 84
            opacity: 0.5
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(255 / 255, 196 / 255, 110 / 255, 0.10) }
                GradientStop { position: 0.55; color: Qt.rgba(255 / 255, 196 / 255, 110 / 255, 0.03) }
                GradientStop { position: 1.0; color: Qt.rgba(255 / 255, 196 / 255, 110 / 255, 0.0) }
            }
        }

        // тонкий блик по верхней кромке
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 1
            width: parent.width * 0.55
            height: 1
            color: Qt.rgba(1, 1, 1, 0.10)
        }
    }

    // маленькая снежинка в углу
    Text {
        text: "\u2744"
        color: Qt.rgba(1, 1, 1, 0.22)
        font.pixelSize: 13
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 13
        anchors.topMargin: 9
    }

    // ---- само время ----
    Row {
        id: timeRow
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10
        height: 66
        spacing: 0

        Text {
            id: hhText
            text: root.hh
            width: 66
            height: 66
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            color: "#fff6e6"
            font.pixelSize: 52
            font.weight: Font.Light
            font.letterSpacing: 1
        }

        Text {
            id: colon
            text: ":"
            width: 20
            height: 66
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            color: "#ffd166"
            font.pixelSize: 42
            font.weight: Font.Light
            opacity: root.colonOn ? 1.0 : 0.22
        }

        Text {
            id: mmText
            text: root.mm
            width: 66
            height: 66
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            color: "#fff6e6"
            font.pixelSize: 52
            font.weight: Font.Light
            font.letterSpacing: 1
        }

        Item { width: 12; height: 1 }

        // секунды в золотой «таблетке»
        Rectangle {
            id: secBadge
            width: 50
            height: 32
            radius: 16
            y: (66 - height) / 2
            color: Qt.rgba(255 / 255, 209 / 255, 102 / 255, 0.12)
            border.width: 1
            border.color: Qt.rgba(255 / 255, 209 / 255, 102 / 255, 0.34)

            Text {
                anchors.centerIn: parent
                text: root.ss
                color: "#ffd166"
                font.pixelSize: 20
                font.weight: Font.Medium
                font.letterSpacing: 1
            }
        }
    }

    // ---- разделитель ----
    Rectangle {
        id: divider
        width: 54
        height: 1
        anchors.horizontalCenter: parent.horizontalCenter
        y: 92
        color: Qt.rgba(255 / 255, 209 / 255, 102 / 255, 0.35)
    }

    // ---- дата ----
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 14
        spacing: 6

        Text {
            text: "\u2744"
            color: Qt.rgba(255 / 255, 209 / 255, 102 / 255, 0.75)
            font.pixelSize: 12
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.dateText
            color: "#a8b8c9"
            font.pixelSize: 12
            font.letterSpacing: 0.4
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
