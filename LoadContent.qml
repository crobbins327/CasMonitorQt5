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

    property string type: "step"

    width: parent.width
    height: ribbon.height

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
            GradientStop {position: 0.826; color: "#577dc7"}
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
            anchors.leftMargin: 15

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 14
            renderType: Text.QtRendering
        }

        ToolButton {
            id: toolButton
//            property bool tCheck: false
            width: 170
            text: (itemIndex+1) + ". " + model.loadType
            rightPadding: 38
            opacity: 1
            leftPadding: 6
            topPadding: 6
            font.weight: Font.Thin
            font.bold: false
            font.pointSize: 14
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0


            contentItem: Text{
                text: toolButton.text
                font.weight: Font.Thin
                font.bold: false
                font.pointSize: 14
                anchors.left: parent.left
                anchors.leftMargin: 15
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                    opacity: 1.0
                    color: toolButton.palette.button
                }

        }

        }
    }



