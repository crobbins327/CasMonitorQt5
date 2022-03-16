import QtQuick 2.15
import QtQml.Models 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import QtQuick.Controls.Material 2.15
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
//    property string washSyr: 'false'

    property string type: "step"

//    width: 540
    width: parent.width
    height: ribbon.height + container.height

    Rectangle {
        id: ribbon
        x: 0
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
        height: 25
//        height: 35
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.524; color: "#f5f5f5"}
            GradientStop {position: 0.826; color: rootCol.minimize ?  "#577dc7" : "#ffc700"}
        }

        Button {
            id: closeButton
            width: parent.height
            height: parent.height
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10

            Image {
                id: closeImage
                source: "Icons/close.png"
                anchors.horizontalCenter: closeButton.horizontalCenter
                anchors.verticalCenter: closeButton.verticalCenter
                width: closeButton.width*0.5
                height: closeButton.height*0.5
                fillMode: Image.PreserveAspectFit
            }
            ColorOverlay {
                anchors.fill: closeImage
                source: closeImage
                color: closeButton.down || closeButton.checked || closeButton.highlighted ? "red" : "black"
            }

            background: Rectangle {
                implicitWidth: closeButton.width*0.5
                implicitHeight: closeButton.height*0.5
                color: "transparent"
            }

            onClicked: {
                modDel.items.remove(itemIndex)
                modDel.model.remove(itemIndex)
            }


        }

        Text {
            id: opTimeText
            color: "#000000"
            //            text: {return opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec}
            text: opTime == null ? "00:05:00" : opTime
            anchors.verticalCenter: ribbon.verticalCenter
            anchors.left: toolButton.right
            anchors.leftMargin: 10

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 11
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
                        font.pointSize: 12
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
            color: "#000000"
            text: volume
            anchors.right: closeButton.left
            anchors.rightMargin: 15
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 11
            font.weight: Font.Medium
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }

        }
    Rectangle {
        id: container
        anchors.top: ribbon.bottom
        Material.theme: Material.Light
        Material.accent: Material.Blue

        width: rootCol.width
        height: rootCol.minimize ? 0 : 120

        radius: 5
        border.width: 0.5
        border.color: "lightgray"
        color: "#f5f5f5"
        visible: rootCol.minimize ? false : true

        Slider {
            id: volSlider
            width: 150
            height: 30
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.topMargin: 19
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
            width: 71
            height: 19
            color: "#000000"
            text: qsTr("Volume:")
            font.bold: true
            anchors.verticalCenter: volSlider.verticalCenter
            font.pointSize: 11
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
                font.pointSize: 11
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
            font.pointSize: 11
            anchors.verticalCenter: rectInput.verticalCenter
            font.bold: true
        }

        CheckBox {
            id: washCheckBox
            width: 326
            height: 44
            text: qsTr("Wash Syringe & Line")
            anchors.verticalCenterOffset: 0
            display: AbstractButton.TextBesideIcon
            font.pointSize: 10
            font.bold: true
            anchors.left: volSlider.left
            anchors.top: volSlider.bottom
            anchors.topMargin: 12
            anchors.leftMargin: 0
            checked: washSyr == 'true' ? true : false

            onClicked: {
                if (washCheckBox.checked){
                    washSyr = 'true'
                } else {
                    washSyr = 'auto'
                }
//                console.log(washSyr)
            }
        }


    }
}





