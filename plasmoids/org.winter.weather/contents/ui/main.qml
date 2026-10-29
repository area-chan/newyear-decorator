import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0

Item {
    id: root

    property int temp: 0
    property int feels: 0
    property real wind: 0
    property string symbol: ""
    property bool ready: false

    readonly property bool night: {
        var h = new Date().getHours();
        return h < 7 || h > 19;
    }

    readonly property string iconName: {
        var s = symbol.toLowerCase();
        if (s === "") return "weather-none-available";
        if (s.indexOf("thunder") !== -1) return "weather-storm";
        if (s.indexOf("snow") !== -1) return "weather-snow";
        if (s.indexOf("sleet") !== -1) return "weather-sleet";
        if (s.indexOf("rain") !== -1 || s.indexOf("shower") !== -1) return "weather-showers";
        if (s.indexOf("fog") !== -1) return "weather-fog";
        if (s.indexOf("cloudy") !== -1) return s.indexOf("partly") !== -1 ? "weather-few-clouds" : "weather-clouds";
        if (s.indexOf("clear") !== -1 || s.indexOf("fair") !== -1) return night ? "weather-clear-night" : "weather-clear";
        return "weather-few-clouds";
    }

    readonly property string tempText: ready ? ((temp > 0 ? "+" : "") + temp + "\u00B0") : "\u2026"
    readonly property string feelsText: ready ? ("ощущается " + (feels > 0 ? "+" : "") + feels + "\u00B0") : ""
    readonly property string windText: ready ? ("ветер " + Math.round(wind) + " км/ч") : ""
    property int nyDays: 0

    readonly property string nyText: {
        if (nyDays <= 0) return "\u2744 С Новым годом!";
        var n = nyDays % 100;
        var word = "дней";
        if (n < 11 || n > 14) {
            var m = n % 10;
            if (m === 1) word = "день";
            else if (m >= 2 && m <= 4) word = "дня";
        }
        return "\u2744 до Нового года " + nyDays + " " + word;
    }

    function updateCountdown() {
        var now = new Date();
        var ny = new Date(now.getFullYear() + 1, 0, 1, 0, 0, 0);
        root.nyDays = Math.ceil((ny.getTime() - now.getTime()) / 86400000);
    }

    Plasmoid.toolTipMainText: "Великий Новгород"
    Plasmoid.toolTipSubText: ready ? (tempText + "\n" + feelsText + "\n" + windText) : "Загружаю погоду\u2026"
    Plasmoid.icon: iconName
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // включается/выключается из «Новогоднего оформителя»
    readonly property bool enabled: plasmoid.configuration.enabled

    // ---- на случай добавления в панель ----
    Plasmoid.compactRepresentation: RowLayout {
        spacing: 4
        Item {
            Layout.preferredWidth: 16
            Layout.preferredHeight: 16
            PlasmaCore.IconItem { anchors.fill: parent; source: root.iconName }
        }
        Text {
            text: root.tempText
            color: "#f2f2f2"
            font.pixelSize: 13
            Layout.alignment: Qt.AlignVCenter
        }
    }

    // ---- виджет на рабочем столе ----
    Plasmoid.fullRepresentation: Item {
        id: card
        implicitWidth: 200
        implicitHeight: 140
        visible: root.enabled

        Rectangle {
            id: glass
            anchors.fill: parent
            radius: 20
            color: Qt.rgba(10 / 255, 16 / 255, 26 / 255, 0.78)
            border.width: 1
            border.color: Qt.rgba(1, 1, 1, 0.14)

            // лёгкий блик сверху — эффект стекла
            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                radius: 19
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.07) }
                    GradientStop { position: 0.45; color: Qt.rgba(1, 1, 1, 0.01) }
                    GradientStop { position: 1.0; color: Qt.rgba(1, 1, 1, 0.0) }
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 15
                anchors.rightMargin: 15
                anchors.topMargin: 13
                anchors.bottomMargin: 13
                spacing: 0

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 9

                    Item {
                        Layout.preferredWidth: 44
                        Layout.preferredHeight: 44
                        Layout.alignment: Qt.AlignVCenter

                        PlasmaCore.IconItem {
                            anchors.fill: parent
                            source: root.iconName
                        }
                    }

                    ColumnLayout {
                        spacing: -4
                        Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter

                        Text {
                            text: root.tempText
                            color: "#ffffff"
                            font.pixelSize: 32
                            font.weight: Font.DemiBold
                            Layout.alignment: Qt.AlignLeft
                        }
                        Text {
                            text: root.feelsText
                            color: "#c9d6e4"
                            font.pixelSize: 11
                            Layout.alignment: Qt.AlignLeft
                        }
                    }

                    Item { Layout.fillWidth: true }
                }

                Item { Layout.fillHeight: true }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    Layout.bottomMargin: 5
                    color: Qt.rgba(1, 1, 1, 0.09)
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    Text {
                        text: "Великий Новгород"
                        color: "#eaf2fb"
                        font.pixelSize: 13
                        font.weight: Font.Medium
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: root.windText
                        color: "#a8b8c9"
                        font.pixelSize: 10
                        Layout.alignment: Qt.AlignBaseline
                    }
                }
                Text {
                    text: root.nyText
                    color: "#f0c98a"
                    font.pixelSize: 10
                    Layout.topMargin: 3
                }
            }
        }
    }

    function applyMet(body) {
        try {
            var ts = JSON.parse(body).properties.timeseries[0];
            var d = ts.data.instant.details;
            root.temp = Math.round(d.air_temperature);
            root.wind = (d.wind_speed || 0) * 3.6;
            var n = ts.data.next_1_hours;
            root.symbol = (n && n.summary) ? n.summary.symbol_code : "";
            root.feels = root.temp;
            root.ready = true;
            return true;
        } catch (e) {
            console.log("weather: met parse error", e);
            return false;
        }
    }

    function applyWttr(body) {
        var m = body.match(/([-+]?\d+)/);
        if (m) {
            root.temp = parseInt(m[1], 10);
            root.feels = root.temp;
            root.ready = true;
            return true;
        }
        return false;
    }

    function refresh() {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200 && applyMet(xhr.responseText)) return;
            console.log("weather: met.no status " + xhr.status + ", fallback");
            var fb = new XMLHttpRequest();
            fb.onreadystatechange = function () {
                if (fb.readyState !== XMLHttpRequest.DONE) return;
                if (fb.status !== 200 || !applyWttr(fb.responseText)) {
                    console.log("weather: fallback failed " + fb.status);
                }
            };
            fb.open("GET", "http://wttr.in/Veliky+Novgorod?format=%t");
            fb.send();
        };
        xhr.open("GET", "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.52&lon=31.27");
        xhr.setRequestHeader("User-Agent", "newyear-decorator/1.0");
        xhr.send();
    }

    Timer {
        interval: 900000
        running: root.enabled
        repeat: true
        onTriggered: {
            root.refresh();
            root.updateCountdown();
        }
    }

    Component.onCompleted: {
        root.updateCountdown();
        root.refresh();
    }
}
