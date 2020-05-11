import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12

import "./Icons/"


ApplicationWindow {
    id: root
    signal settings_CasMonitor()
    property string mainDir: "/home/jackr/testprotocols"
    visible: true
    width: 800
    height: 480

    StackView {
        id: mainStack
        initialItem: casMonitor
        anchors.fill: parent

    }

    Component {
        id: casMonitor

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
                height: 60
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.right: parent.right
                anchors.rightMargin: 0
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
                //            layer.effect: menuRect

                Button {
                    id: settingsB
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

                    onClicked: {root.settings_CasMonitor()}

                }

                Text {
                    id: casMonLab
                    color: "#ffffff"
                    text: qsTr("Sample Monitor")
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 16
                }

                Button {
                    id: debugB
                    x: 2
                    y: 7
                    width: 50
                    height: 50
                    anchors.right: settingsB.left
                    anchors.rightMargin: 30
                    anchors.verticalCenter: parent.verticalCenter
                    opacity: debugB.down || debugB.checked || debugB.highlighted ? 0.5 : 1
                    display: AbstractButton.IconOnly
                    flat: true

                    background: Rectangle {
                        color: "#00000000"
                        radius: 30
                        border.width: 0
                        implicitWidth: 50
                        border.color: "#ffffff"
                        implicitHeight: 50
                    }
                    Image {
                        id: debugImage
                        source: "Icons/debug-mode.png"
                        anchors.fill: parent
                        width: 60
                        fillMode: Image.PreserveAspectFit
                    }
                    ColorOverlay {
                        anchors.fill: debugImage
                        source: debugImage
                        color: "#ffffff"
                    }

                    onClicked: {mainStack.push("DebugMode.qml")}


                }



            }

            Row {
                id: topRow
                anchors.topMargin: 5
                anchors.rightMargin: 20
                anchors.leftMargin: 20
                anchors.bottomMargin: -30
                anchors.top: menuRect.bottom
                anchors.right: parent.right
                anchors.bottom: parent.verticalCenter
                anchors.left: parent.left

                spacing: (topRow.width - 3*cas1.width)/2


                SampleStack {
                    id: cas1
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 1
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas2
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 2
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas3
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 3
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }
            }

            Row {
                id: botRow
                anchors.topMargin: 5
                anchors.rightMargin: 20
                anchors.leftMargin: 20
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: topRow.bottom

                spacing: (botRow.width - 3*cas4.width)/2

                SampleStack {
                    id: cas4
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 4
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas5
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 5
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas6
                    height: (root.height-menuRect.height)/2.1
                    width: root.width/3.4
                    casNumber: 6
                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                    stackIndex: 1

                    onSetupRun: {}

                    onDefaultRun: {
                        console.log("Default run: ", casNumber)
                        stackIndex = 2
                        //Check for the default protocol and main directory for saving logs (from settings)
                        //If empty, dialog box error to choose default protocol in settings menu
                        //Else, send the default protocol information and signal to startRun
                    }

                    onStopRun: {}

                    onRunDetails: {console.log("Run details: ", casNumber)}


                }
            }


        }
    }
}



