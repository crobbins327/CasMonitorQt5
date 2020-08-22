import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import "./Icons/"



Item {
    id: rootCol
    property int itemIndex : DelegateModel.itemsIndex
    width: parent.width
    height: ribbon.height

    Rectangle {
        id: ribbon
        x: 0
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
        height: 27
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.62; color: "#f5f5f5"}
            //            GradientStop {position: 0.848; color: "#737d90"}

            GradientStop {
                position: 0.93
                color: "#577dc7"
            }
        }

        Text {
            id: opTimeText
            y: 7
            color: "#000000"
            text: opTime == null ? "00:05:00" : opTime
            anchors.verticalCenter: ribbon.verticalCenter
            anchors.left: toolButton.right
            anchors.leftMargin: 15

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 14
            renderType: Text.QtRendering
        }

        Text {
            id: mixVolText
            y: 4
            color: "#000000"
            text: mixVol == 'undefined' ? null : mixVol + " mL"
            anchors.left: opTimeText.right
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 14
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.leftMargin: 50

            font.capitalization: Font.MixedCase
        }

        ToolButton {
            id: toolButton
            width: 190
            text: (itemIndex+1) + ". "+ opName
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

            flat: false

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



