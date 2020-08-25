import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import "./Icons/"



Item {
    id: rootCol

//    property string opName: model.opName
//    property string opTime: model.opTime
//    property string loadType: model.loadType
    property DelegateModel modDel: null
    property int itemIndex : DelegateModel.itemsIndex
    property bool minimize: true
//    property string opTime: "00:05:00"
//    property string volume: "750uL"
//    property string pSpeed: '1'

    property string type: "step"

    width: 540
    height: ribbon.height + container.height

    Rectangle {
        id: ribbon
        x: 0
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
        height: 35
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.524; color: "#f5f5f5"}
            GradientStop {position: 0.826; color: rootCol.minimize ?  "#577dc7" : "#ffc700"}
        }

        Button {
            id: closeButton
            x: 544
            width: 30
            height: 30
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10
            icon.name: "close-X"
            icon.source: "Icons/close.png"
            icon.color: closeButton.down || closeButton.checked || closeButton.highlighted ? "red" : "black"
            icon.width: 30
            icon.height: 30

            onClicked: {
                modDel.items.remove(itemIndex)
                modDel.model.remove(itemIndex)
            }


            background: Rectangle {
                implicitWidth: 30
                implicitHeight: 30
//                border.width: 0.5
//                border.color: closeButton.down || closeButton.checked || closeButton.highlighted ? "black" : "transparent"
//                radius: 8
//                opacity: closeButton.down ? 0.75 : 1
                color: "transparent"
            }
        }

        Text {
            id: opTimeText
            y: 7
            color: "#000000"
            //            text: {return opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec}
            text: opTime == null ? "00:05:00" : opTime
            anchors.verticalCenter: ribbon.verticalCenter
            anchors.left: toolButton.right
            anchors.leftMargin: 10

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 12
            renderType: Text.QtRendering
        }

        ToolButton {
            id: toolButton
            width: 180
            text: (itemIndex+1) + ". " + model.loadType
//            text: "99. Formalin"
            padding: 6
            opacity: 1
            leftPadding: 6
            rightPadding: 59
            topPadding: 6
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            display: AbstractButton.TextBesideIcon

            contentItem: Item {
                id: element
//                Row {
//                    id: row
//                    anchors.verticalCenter: parent.verticalCenter
//                    layoutDirection: Qt.LeftToRight
////                    anchors.horizontalCenter: parent.horizontalCenter
//                    spacing: 5
                    Image {
                        source: rootCol.minimize ? "Icons/rightArrow-black.png" : "Icons/downArrow-black.png"
                        width: 8
                        height: 8
                        anchors.left: parent.left
                        anchors.leftMargin: 2
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: toolButton.text
                        anchors.left: parent.left
                        anchors.leftMargin: 18
                        anchors.verticalCenter: parent.verticalCenter
                        font.weight: Font.Thin
                        font.bold: true
                        font.pointSize: 13
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                    }
//                }
            }

            background: Rectangle {
                    opacity: toolButton.down ? 1.0 : 0.5
                    color: toolButton.down || toolButton.checked || toolButton.highlighted ? toolButton.palette.mid : toolButton.palette.button
                }


            onClicked: {
                rootCol.minimize = rootCol.minimize ? false : true
            }

        }

        Text {
            id: volText
            y: 4
            color: "#000000"
            text: volume
            anchors.right: closeButton.left
            anchors.rightMargin: 15
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 12
            font.weight: Font.Medium
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }

        Text {
            id: pSpeedText
            x: 292
            y: 0
            color: "#000000"
            text: pSpeed+ ' Speed'
            anchors.verticalCenterOffset: 0
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.verticalCenter: ribbon.verticalCenter
            anchors.leftMargin: 15
            anchors.left: opTimeText.right
            font.pointSize: 12
            font.capitalization: Font.MixedCase
        }

        }
    Rectangle {
        id: container
        anchors.top: ribbon.bottom

        width: rootCol.width
        height: rootCol.minimize ? 0 : 150

        radius: 5
        border.width: 0.5
        border.color: "lightgray"
        color: "#f5f5f5"
        visible: rootCol.minimize ? false : true

        Slider {
            id: volSlider
            y: 19
            anchors.left: parent.left
            anchors.leftMargin: 25
            value: parseInt(volume.slice(0,-2))
            from: 1
            to: 3000
            stepSize: 1

            onMoved: {
                // If value below or above amount, convert to mL or uL
                //Depends on what mixing values are desired..
                var volumeVal = volSlider.value.toString()
                volInput.text = volSlider.value
                volSlider.value = volInput.text
                volume = volumeVal + 'uL'
            }
        }

        Text {
            id: volSLab
            x: 0
            y: 234
            width: 74
            height: 19
            color: "#000000"
            text: qsTr("Volume:")
            font.bold: true
            anchors.verticalCenter: volSlider.verticalCenter
            font.pointSize: 12
            anchors.left: volSlider.right
            anchors.leftMargin: 15
        }

        Rectangle{
            id:rectInput
            border.color: "#515151"
            border.width: 1
            width: 70
            height: 30
            color: "#00000000"
            anchors.left: volSLab.right
            anchors.leftMargin: 20
            anchors.verticalCenter: volSLab.verticalCenter
            y: 233

            TextInput {
                id: volInput
                color: "#000000"
                font.bold: true
                font.pointSize: 12
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                validator: IntValidator {
                       }
                maximumLength: 4
                text: volSlider.value
                anchors.rightMargin: 5
                anchors.leftMargin: 10
                anchors.fill: parent
                font.underline: false
                selectionColor: "#66000080"
                selectedTextColor: "#ffffff"
                clip: true
                onEditingFinished: {
                    volSlider.value = volInput.text
                    volInput.text = volSlider.value
                    volume = volSlider.value + 'uL'
                }


            }
        }

        Text {
            id: volUnits
            y: 239
            width: 32
            height: 19
            color: "#000000"
            text: qsTr("uL")
            anchors.left: rectInput.right
            anchors.leftMargin: 5
            font.pointSize: 12
            anchors.verticalCenter: rectInput.verticalCenter
            font.bold: true
        }

        Slider {
            id: speedSlider
            x: 25
            width: 200
            height: 40
            stepSize: 1
            value: parseInt(pSpeed)
            to: 10
            anchors.topMargin: 20
            anchors.top: volSlider.bottom
            from: 1
            onMoved: {
                // If value below or above amount, convert to mL or uL
                //Depends on what mixing values are desired..
                pSpeed = speedSlider.value.toString()
                speedInput.text = speedSlider.value
                speedSlider.value = speedInput.text
            }
        }

        Text {
            id: speedLab
            x: 7
            y: 241
            width: 120
            height: 19
            color: "#000000"
            text: qsTr("Pump Speed:")
            anchors.verticalCenterOffset: 0
            anchors.verticalCenter: speedSlider.verticalCenter
            anchors.leftMargin: 15
            font.bold: true
            anchors.left: speedSlider.right
            font.pointSize: 12
        }

        Rectangle {
            id: rectSpIn
            x: 7
            y: 240
            width: 40
            height: 30
            color: "#00000000"
            anchors.verticalCenterOffset: 0
            TextInput {
                id: speedInput
                color: "#000000"
                text: speedSlider.value
                horizontalAlignment: Text.AlignLeft
                anchors.fill: parent
                clip: true
                font.underline: false
                anchors.leftMargin: 10
                selectionColor: "#66000080"
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                selectedTextColor: "#ffffff"
                validator: IntValidator {
                }
                font.pointSize: 12
                maximumLength: 2
                anchors.rightMargin: 10
                onEditingFinished: {
                    speedSlider.value = speedInput.text
                    speedInput.text = speedSlider.value
                    pSpeed = speedSlider.value
                }
            }
            anchors.verticalCenter: speedLab.verticalCenter
            anchors.leftMargin: 20
            anchors.left: speedLab.right
            border.width: 1
            border.color: "#515151"
        }


    }
}




/*##^##
Designer {
    D{i:16;anchors_x:25}D{i:17;anchors_x:25}D{i:19;anchors_y:81}D{i:18;anchors_y:81}D{i:21;anchors_y:81}
D{i:22;anchors_y:81}D{i:23;anchors_y:81}
}
##^##*/
