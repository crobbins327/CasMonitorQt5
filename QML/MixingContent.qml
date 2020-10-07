import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import "./Icons/"



Item {
    id: rootCol
    property DelegateModel modDel: null
    property int itemIndex : DelegateModel.itemsIndex
    property bool minimize: true
//    property int numCycles: 3
//    property string opTime: "00:05:00"
//    property string volume: "3mL"
    property string type: "step"

    width: 540
    height: ribbon.height + container.height

    Rectangle {
        id: ribbon
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
        height: 25
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.524; color: "#f5f5f5"}
            GradientStop {position: 0.826; color: rootCol.minimize ?  "#577dc7" : "#ffc700"}
        }

        Button {
            id: closeButton
            x: 544
            width: 25
            height: 25
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10
            icon.name: "close-X"
            icon.source: "Icons/close.png"
            icon.color: closeButton.down || closeButton.checked || closeButton.highlighted ? "red" : "black"
            icon.width: 25
            icon.height: 25

            onClicked: {
                modDel.items.remove(itemIndex)
                modDel.model.remove(itemIndex)
            }


            background: Rectangle {
                implicitWidth: 25
                implicitHeight: 25
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
            text: opTime
            anchors.verticalCenter: toolButton.verticalCenter
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
            text: (itemIndex+1) + ". Mixing"
//            text: "99. Mixing"
            font.italic: false
            rightPadding: 75
            opacity: 1
            leftPadding: 6
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
//                    //anchors.horizontalCenter: parent.horizontalCenter
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


            onClicked: {rootCol.minimize = rootCol.minimize ? false : true}

        }

        Text {
            id: mixVolText
            y: 4
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

        Text {
            id: numCycleText
            x: 306
            y: 7
            color: "#000000"
            text: {
                if(numCycles==1){
                    return(numCycles+' Cycle')
                }else{
                 return(numCycles+' Cycles')
                }
            }
            anchors.left: opTimeText.right
            anchors.verticalCenter: toolButton.verticalCenter
            font.weight: Font.Medium
            font.pointSize: 11
            anchors.leftMargin: 15
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }
    }
    Rectangle {
        id: container
        anchors.top: ribbon.bottom

        width: rootCol.width
        height: rootCol.minimize ? 0 : 120

        radius: 5
        border.width: 0.5
        border.color: "lightgray"
        color: "#f5f5f5"
        visible: rootCol.minimize ? false : true

        Text {
            id: mixCLab
            color: "#000000"
            text: "# Cycles:"
            anchors.top: parent.top
            anchors.topMargin: 25
            anchors.left: parent.left
            anchors.leftMargin: 8
            font.pointSize: 11
            font.weight: Font.Medium
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }

        Tumbler {
            id: cycleTumbler
            width: 45
            anchors.left: mixCLab.right
            anchors.leftMargin: 100
            anchors.verticalCenter: mixCLab.verticalCenter
            font.pointSize: 12
            transformOrigin: Item.Center
            rotation: -90 // <---- Rotate there
            model: 20
            delegate: Rectangle{
                rotation: 90
                height: parent.width
//                anchors.centerIn: parent
                color: "transparent"
                opacity: 0.4 + Math.max(0, 1 - Math.abs(Tumbler.displacement)) * 0.6
                Text {
                    anchors.centerIn: parent
                    text: index+1
                    font.pointSize: 14
                }
            }

            currentIndex: numCycles-1



            onMovingChanged: {
                numCycles = cycleTumbler.currentIndex+1
            }

        }

        Slider {
            id: volSlider
            x: 8
            height: 30
            anchors.top: cycleTumbler.verticalCenter
            anchors.topMargin: 40
            value: parseInt(volume.slice(0,-2))
            from: 0.25
            to: 3
            stepSize: 0.25

            onMoved: {
                // If value below or above amount, convert to mL or uL
                //Depends on what mixing values are desired..
                var volumeVal = volSlider.value.toString()
                volInput.text = volSlider.value
                volSlider.value = volInput.text
                volume = volumeVal + 'mL'
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
            anchors.leftMargin: 10
            anchors.verticalCenter: volSLab.verticalCenter
            y: 233

            TextInput {
                id: volInput
                color: "#000000"
                font.bold: true
                font.pointSize: 11
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                validator: DoubleValidator {
                       }
                maximumLength: 5
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
                    volume = volSlider.value + 'mL'
                }


            }
        }

        Text {
            id: volSLab1
            y: 239
            width: 32
            height: 19
            color: "#000000"
            text: qsTr("mL")
            anchors.left: rectInput.right
            anchors.leftMargin: 5
            font.pointSize: 11
            anchors.verticalCenter: rectInput.verticalCenter
            font.bold: true
        }


    }

}

