import QtQuick 2.0
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls.Material 2.12

Item {
    id: root
    property int casNumber: 0
    property int currentTemp: 25
    property int setTemp: 47
    signal refresh()
    Rectangle {
        id: rootRect
        Material.elevation: 9
        radius: 15
        color: '#777777'
        Material.theme: Material.Dark
        Material.accent: Material.Blue
        width: 160
        height: 100

        ColumnLayout {
            id: colLayout
            anchors.fill: rootRect
            spacing: 5

            Text {
                id: casLab
                text: 'Cas '+casNumber
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                font.pointSize: 12
            }

            Text {
                id: currentTempText
                text: currentTemp + ' \xB0 C'
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
//                anchors.bottom: tempSpin.top
//                anchors.bottomMargin: 7
//                anchors.horizontalCenter: parent.horizontalCenter
                font.pointSize: 11
            }

            SpinBox {
                id: tempSpin
                Layout.preferredWidth: colLayout.width/1.1
                Layout.preferredHeight: 30
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
//                anchors.bottom: parent.bottom
//                anchors.horizontalCenter: parent.horizontalCenter
//                anchors.bottomMargin: 7
                scale: 1
                editable: true
                from: 25
                to: 60
                stepSize: 1
                value: setTemp
                font.pointSize: 11
                onValueModified: {
                    console.log(tempSpin.value)
                    setTemp = tempSpin.value
                    delayTimer.start()
                }

                Material.theme: Material.Dark
                Material.accent: Material.Blue

            }
        }
    }

Timer {
        id: delayTimer
        //Wait 1 seconds before sending a set temp signal
        interval: 1000
        onTriggered: {
            console.log('set temp of CAS'+casNumber)
            WAMPHandler.setCasTemp(casNumber, setTemp)
        }
    }

}

