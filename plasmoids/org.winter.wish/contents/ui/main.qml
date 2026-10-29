import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0

Item {
    id: root

    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // включается/выключается из «Новогоднего оформителя»
    visible: plasmoid.configuration.enabled

    readonly property var wishes: [
        "Пусть этот день будет как первый снег — чистым и волшебным.",
        "Сегодня отличный день, чтобы слепить снеговика.",
        "Загадай желание — звёзды сегодня особенно близко.",
        "Тёплого чая, уютного пледа и любимого фильма.",
        "Пусть учёба идёт легко, а выходные — медленно.",
        "Улыбнись: снежинки это любят.",
        "Сегодня можно съесть лишнюю конфету. Я разрешаю.",
        "Пусть найдётся время на что-то приятное.",
        "Хорошего дня и побольше снега!",
        "Сделай сегодня одно доброе дело — и мир станет теплее.",
        "Пусть всё сложное сегодня окажется простым.",
        "Снег идёт — значит, сказка уже началась.",
        "Проверь: может, под ёлкой уже что-то лежит?",
        "Пусть найдётся снежинка, которая исполнит желание.",
        "Сегодня идеальный день для горячего шоколада.",
        "Пусть будет больше смеха и меньше суеты.",
        "Ты молодец. Даже если сегодня ничего не успел.",
        "Пусть этот вечер будет уютным, как варежки.",
        "За окном зима — а у тебя в комнате тепло. Это и есть счастье.",
        "Пусть новый день принесёт что-то неожиданно хорошее.",
        "Слепи снежок и запусти в небо. Просто так.",
        "Пусть все дела решатся сами, а ты отдохнёшь.",
        "Хорошего настроения — как гирлянда, яркого!",
        "Пусть сегодня кто-то улыбнётся тебе просто так.",
        "Зима — время чудес. Не забудь заметить одно.",
        "Пусть сбудется то, о чём ты давно мечтаешь.",
        "Сегодня можно ничего не делать. Совсем ничего.",
        "Пусть твой день будет тёплым, даже если на улице минус.",
        "Снежинка на ладони — маленькое чудо. Поймай свою.",
        "Пусть до Нового года каждый день будет чуть волшебнее.",
        "Сегодня хороший день, чтобы написать кому-то приятное.",
        "Пусть за окном метель, а у тебя — тихо и спокойно."
    ]

    property int idx: 0

    function nextWish() {
        root.idx = (root.idx + 1) % root.wishes.length;
    }

    Component.onCompleted: {
        var d = new Date();
        var start = new Date(d.getFullYear(), 0, 0);
        var day = Math.floor((d.getTime() - start.getTime()) / 86400000);
        root.idx = day % root.wishes.length;
    }

    Rectangle {
        id: card
        anchors.fill: parent
        radius: 18
        color: Qt.rgba(10 / 255, 16 / 255, 26 / 255, 0.72)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.13)

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 17
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.06) }
                GradientStop { position: 0.5; color: Qt.rgba(1, 1, 1, 0.0) }
            }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 14
            anchors.rightMargin: 14
            anchors.topMargin: 10
            anchors.bottomMargin: 10
            spacing: 10

            Text {
                text: "\u2744"
                color: "#ffd166"
                font.pixelSize: 18
                Layout.alignment: Qt.AlignTop
            }

            Text {
                text: root.wishes[root.idx]
                color: "#eaf2fb"
                font.pixelSize: 12
                lineHeight: 1.15
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.fillHeight: true
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.nextWish()
    }
}
