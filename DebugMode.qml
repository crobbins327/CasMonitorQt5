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
                text: qsTr("Debug Mode")
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
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: menuRect.bottom
            anchors.topMargin: 10

            Button {
                id: homeSyrB
                x: 58
                y: 119
                text: qsTr("Home")
                anchors.bottom: meohB.top
                anchors.bottomMargin: 50

                onClicked: {root.syrHome(); console.log("Home")}
            }

            Button {
                id: findVialB
                y: 119
                text: qsTr("Find Vial")
                anchors.left: homeSyrB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: homeSyrB.verticalCenter

                onClicked: {root.findVial(); console.log("Find Vial")}
            }

            Button {
                id: engageVialB
                y: 119
                text: qsTr("Engage Vial")
                anchors.left: findVialB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: homeSyrB.verticalCenter

                onClicked: {root.engageVial(); console.log("Engage Vial")}
            }

            Button {
                id: dropVialB
                y: 119
                text: qsTr("Drop Vial")
                anchors.left: engageVialB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: homeSyrB.verticalCenter

                onClicked: {root.dropVial(); console.log("Drop Vial")}
            }

            Button {
                id: meohB
                x: 58
                y: 212
                text: qsTr("MeOH")
                anchors.bottom: neInB.top
                anchors.bottomMargin: 50

                onClicked: {root.syrMeOH(); console.log("MeOH")}
            }

            Button {
                id: babbB
                y: 212
                text: qsTr("BABB")
                anchors.left: meohB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: meohB.verticalCenter

                onClicked: {root.syrBABB(); console.log("BABB")}
            }

            Button {
                id: formalinB
                y: 212
                text: qsTr("Formalin")
                anchors.left: babbB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: meohB.verticalCenter

                onClicked: {root.syrFormalin(); console.log("Formalin")}
            }

            Button {
                id: wasteB
                y: 212
                text: qsTr("Waste")
                anchors.left: formalinB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: meohB.verticalCenter

                onClicked: {root.syrWaste(); console.log("Waste")}
            }

            Button {
                id: sampleB
                y: 212
                text: qsTr("Sample")
                anchors.left: wasteB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: meohB.verticalCenter

                onClicked: {root.syrSample(); console.log("Sample")}
            }

            Button {
                id: neInB
                x: 58
                y: 293
                text: qsTr("Needle In")

                onClicked: {root.needleIn(); console.log("Needle In")}
            }

            Button {
                id: neOutB
                y: 293
                text: qsTr("Needle Out")
                anchors.left: neInB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: neInB.verticalCenter

                onClicked: {root.needleOut(); console.log("Needle Out")}
            }

            Button {
                id: pumpInB
                y: 293
                text: qsTr("Pump in")
                anchors.left: neOutB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: neInB.verticalCenter

                onClicked: {root.pumpIn(); console.log("Pump In")}
            }

            Button {
                id: pumpOutB
                y: 293
                text: qsTr("Pump Out")
                anchors.left: pumpInB.right
                anchors.leftMargin: 30
                anchors.verticalCenter: neInB.verticalCenter

                onClicked: {root.pumpOut(); console.log("Pump Out")}
            }

            SpinBox {
                id: casBox
                x: 58
                y: 29
                to: 6
                from: 1
                value: casNumber
            }

            Text {
                id: casSelectLab
                x: 58
                y: 0
                width: 156
                height: 23
                color: "#ffffff"
                text: qsTr("Select Cassette Number:")
                font.pointSize: 14
            }



    }

}

}

