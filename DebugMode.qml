import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3
import Qt.labs.folderlistmodel 2.12

import "./Icons/"

Item {
    id: root
    property int casNumber: 1
    property string mainDir: "/home/jackr/testprotocols"

    signal syrHome()
    signal findVial()
    signal engageVial()
    signal dropVial()
    signal syrMeOH()
    signal syrBABB()
    signal syrFormalin()
    signal syrWaste()
    signal syrSample()
    signal needleIn()
    signal needleOut()
    signal pumpIn()
    signal pumpOut()

    width: 800
    height: 480


    Rectangle {
        id: rootBG
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        color: "dimgray"

        Rectangle{
            id: menuRect
            width: 800
            height: 60
            color: "#434343"
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: "#434343"
                }

                GradientStop {
                    position: 1
                    color: "#000000"
                }
            }
            x: 0; y: 0

            Button {
                id: homeB
                y: 8
                width: 50
                height: 50
                anchors.left: parent.left
                anchors.leftMargin: 20
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter

                opacity: homeB.down || homeB.checked || homeB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/home-run.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: homeB.down || homeB.checked || homeB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {mainStack.pop(null, StackView.Immediate)}
            }

            Button {
                id: backB
                y: 8
                width: 50
                height: 50
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: homeB.right
                anchors.leftMargin: 20

                opacity: backB.down || backB.checked || backB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/back.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: backB.down || backB.checked || backB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {mainStack.pop()}
            }

            Button {
                id: settingsB
                x: 692
                y: 8
                width: 50
                height: 50
                display: AbstractButton.IconOnly
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: parent.verticalCenter


                opacity: settingsB.down || settingsB.checked || settingsB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/settings-icon.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: settingsB.down || settingsB.checked || settingsB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {}

            }

            Text {
                id: protSelLab
                x: 327
                y: 23
                width: 173
                height: 25
                color: "#ffffff"
                text: qsTr("Prepbot Control")
                font.weight: Font.Medium
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pointSize: 16
            }
        }



        Rectangle {
            id: rootTangle
            height: 405
            color: "transparent"
            border.color: "#a69d9d"
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: menuRect.bottom
            anchors.topMargin: 10

            BevButton {
                id: homeSyrB
                width: 75
                height: 40
                text: qsTr("Home")
                anchors.top: casSelectLab.bottom
                anchors.topMargin: 38
                anchors.left: casSelectLab.left
                anchors.leftMargin: 0
                palette {
                    button: 'white'
                }

                onClicked: {ManualPrepbot.home()}
            }

            BevButton {
                id: connectB
                y: 119
                width: 85
                height: 40
                text: qsTr("Connect")
                anchors.verticalCenterOffset: 0
                anchors.left: homeSyrB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: homeSyrB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.findVial(); console.log("Find Vial")}
            }

            BevButton {
                id: engageSaB
                y: 119
                height: 40
                text: qsTr("Engage Sample")
                anchors.left: haltB.right
                anchors.leftMargin: 50
                anchors.verticalCenterOffset: 0
                anchors.verticalCenter: haltB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {ManualPrepbot.engageSampleD; console.log("Engage Sample "+casNumber)}
            }

            BevButton {
                id: disengageSaB
                y: 119
                height: 40
                text: qsTr("Disengage Sample")
                anchors.left: engageSaB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: homeSyrB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.dropVial(); console.log("Drop Vial")}
            }

            BevButton {
                id: meohB
                y: 188
                width: 75
                height: 40
                text: qsTr("MeOH")
                anchors.left: formalinB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: formalinB.verticalCenter
                anchors.bottom: neInB.top
                anchors.bottomMargin: 50
                palette {
                    button: 'white'
                }

                onClicked: {root.syrMeOH(); console.log("MeOH")}
            }

            BevButton {
                id: babbB
                y: 188
                width: 75
                height: 40
                text: qsTr("BABB")
                anchors.verticalCenter: meohB.verticalCenter
                anchors.left: meohB.right
                anchors.leftMargin: 30
                palette {
                    button: 'white'
                }

                onClicked: {root.syrBABB(); console.log("BABB")}
            }

            BevButton {
                id: formalinB
                y: 188
                width: 85
                height: 40
                text: qsTr("Formalin")
                anchors.left: wasteB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: wasteB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.syrFormalin(); console.log("Formalin")}
            }

            BevButton {
                id: wasteB
                width: 75
                height: 40
                text: qsTr("Waste")
                anchors.top: homeSyrB.bottom
                anchors.topMargin: 45
                anchors.left: homeSyrB.left
                anchors.leftMargin: 0
                palette {
                    button: 'white'
                }

                onClicked: {root.syrWaste(); console.log("Waste")}
            }

            BevButton {
                id: sampleB
                y: 188
                width: 75
                height: 40
                text: qsTr("Sample")
                anchors.left: babbB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: babbB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.syrSample(); console.log("Sample")}
            }

            BevButton {
                id: pumpInB
                height: 50
                text: qsTr("Pump in")
                anchors.top: wasteB.bottom
                anchors.topMargin: 35
                anchors.left: wasteB.left
                anchors.leftMargin: 0
                anchors.verticalCenter: neInB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.pumpIn(); console.log("Pump In")}
            }

            BevButton {
                id: pumpOutB
                y: 293
                height: 50
                text: qsTr("Pump Out")
                anchors.left: pumpInB.right
                anchors.leftMargin: 45
                anchors.verticalCenter: pumpInB.verticalCenter
                palette {
                    button: 'white'
                }

                onClicked: {root.pumpOut(); console.log("Pump Out")}
            }

            SpinBox {
                id: casBox
                //y: 8
                //x: 350
                anchors.verticalCenter: casSelectLab.verticalCenter
                anchors.left: casSelectLab.right
                anchors.leftMargin: 100
                to: 6
                from: 1
                value: casNumber
            }

            Text {
                id: casSelectLab
                y: 16
                width: 223
                height: 23
                color: "#ffffff"
                text: qsTr("Select Cassette Number:")
                font.bold: true
                anchors.left: parent.left
                anchors.leftMargin: 55
                font.pointSize: 14
            }

            BevButton {
                id: parkB
                y: 203
                height: 40
                text: qsTr("Park")
                anchors.left: sampleB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: sampleB.verticalCenter
                palette {
                    button: 'white'
                }
            }

            BevButton {
                id: takeDyeB
                width: 120
                height: 40
                text: qsTr("Take up Dye")
                anchors.top: pumpInB.bottom
                anchors.topMargin: 35
                anchors.left: pumpInB.left
                anchors.leftMargin: 0
                palette {
                    button: 'white'
                }
            }

            BevButton {
                id: purgeB
                y: 295
                width: 140
                height: 40
                text: qsTr("Purge Syringe")
                anchors.verticalCenter: takeDyeB.verticalCenter
                anchors.left: takeDyeB.right
                anchors.leftMargin: 25
                palette {
                    button: 'white'
                }
            }

            BevButton {
                id: haltB
                y: 98
                width: 75
                height: 40
                text: qsTr("Halt")
                anchors.left: connectB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: connectB.verticalCenter

                palette {
                    button: 'red'
                    buttonText: 'white'
                }


            }

            Slider {
                id: volSlider
                y: 225
                anchors.left: pumpOutB.right
                anchors.leftMargin: 50
                anchors.verticalCenter: pumpOutB.verticalCenter
                value: 3
                to: 25
                stepSize: 0.01
            }

            Text {
                id: volSLab
                x: 0
                y: 234
                width: 74
                height: 23
                color: "#ffffff"
                text: qsTr("Volume:")
                font.bold: true
                anchors.verticalCenter: volSlider.verticalCenter
                font.pointSize: 14
                anchors.left: volSlider.right
                anchors.leftMargin: 15
            }

            Rectangle{
                id:rectInput
                color: "#848484"
                border.color: "#515151"
                border.width: 2
                width: 70
                height: 30
                anchors.left: volSLab.right
                anchors.leftMargin: 20
                anchors.verticalCenter: volSLab.verticalCenter
                y: 233

                TextInput {
                    id: volInput
                    color: "#ffffff"
                    font.bold: true
                    font.pointSize: 14
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
                    clip: True
                    onEditingFinished: {
                        volSlider.value = volInput.text
                    }


                }
            }

            Text {
                id: volSLab1
                y: 239
                width: 32
                height: 22
                color: "#ffffff"
                text: qsTr("mL")
                anchors.left: rectInput.right
                anchors.leftMargin: 5
                font.pointSize: 14
                anchors.verticalCenter: rectInput.verticalCenter
                font.bold: true
            }




    }

}

}

