import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Controls.Material 2.12
import "./Icons/"



Item {
    id: rootCol
//    property string opName: model.opName
//    property string opTime: model.opTime
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
        height: 25
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.524; color: "#f5f5f5"}
            GradientStop {position: 0.826; color: "#577dc7"}
        }

        Button {
            id: closeButton
            x: 544
            width: 25
            height: 25
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
            y: 7
            color: "#000000"
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
//            property bool tCheck: false
            width: 180
            text: (itemIndex+1) + ". " + opName
            rightPadding: 38
            opacity: 1
            leftPadding: 6
            topPadding: 6
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0

            flat: false

            contentItem: Text{
                text: toolButton.text
                font.weight: Font.Thin
                font.bold: true
                font.pointSize: 12
                anchors.left: parent.left
                anchors.leftMargin: 25
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



