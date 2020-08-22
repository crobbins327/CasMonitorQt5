import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.3

Item {
    id: root
    property int casNumber: 0
    property int stackIndex: 0
    property int runProgVal: 10
    property string runSampleName: "SampleName"
    property string runProtocolName: "ProtocolName"
    property string runStep: "Running!"
    property string runTime: "hh:mm:ss"

    signal setupRun(int casNumber)
    signal defaultRun(int casNumber)
    signal stopRun(int casNumber)
    signal runDetails(int casNumber)
//    signal startRun(int castNumber)

    // Need a listener for whether a cassette is in the slot.... this will switch the current index.
    // Need a listener for premature ejection of cassette during run or during run setup...

    width: 240
    height: 200

    StackLayout {
        id: sampStack
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.fill: parent
        currentIndex: stackIndex

        Rectangle {
            id: noCasDetected
            color: "silver"
            radius: 8
            border.color: "black"
            border.width: 0.5

            Text {
                id: casNum0
                text: casNumber
                anchors.top: parent.top
                anchors.topMargin: 30
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                font.pointSize: 18
            }

            Text {
                id: noCasLab
                text: qsTr("No Cassette Detected")
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                font.bold: false
                font.weight: Font.Medium
                font.pointSize: 16
            }

        }
        Rectangle {
            id: setupRun
            color: "silver"
            radius: 8
            border.color: "black"
            border.width: 0.5

            Text {
                id: casNum1
                text: casNumber
                anchors.top: parent.top
                anchors.topMargin: 30
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                font.pointSize: 18
            }


            GridLayout {
                id: gridLayout
                anchors.top: casNum1.bottom
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.margins: 10
                rowSpacing: 10
                columnSpacing: 10
                flow:  parent.width > parent.height ? GridLayout.LeftToRight : GridLayout.TopToBottom

                Button {
                    id: defRunB
                    text: qsTr("Default Run")
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    width: parent.width/2
                    height: 40

                    onClicked: {root.defaultRun(root.casNumber)}
                }

                Button {
                    id: setupRunB
                    text: qsTr("Setup Run")
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    width: parent.width/2
                    height: 40

                    onClicked: {
                        root.setupRun(root.casNumber)
                        console.log("Setup run: ", casNumber)
//                        push protocol selector screen and populate with casNumber info
                        mainStack.push("ProtocolSelector.qml", {casNumber: casNumber})
                    }
                }
            }

        }
        Rectangle {
            id: runInProg
            color: "silver"
            radius: 8
            border.color: "black"
            border.width: 0.5



            Text {
                id: casNum2
                text: casNumber
                anchors.top: parent.top
                anchors.topMargin: 5
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                font.pointSize: 18
            }

            ProgressBar {
                id: runProgBar
                height: 20
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.bottom: stopRunB.top
                anchors.bottomMargin: 10
                to: 100
                background: Rectangle {
                    color: "#e6e6e6"
                    radius: 3
                    implicitHeight: 4
                    implicitWidth: 200
                }
                contentItem: Item {
                    anchors.fill: parent
                    implicitHeight: 4
                    Rectangle {
                        width: runProgBar.visualPosition * parent.width
                        height: parent.height
                        color: "#17a81a"
                        radius: 2
                    }
                    implicitWidth: 200
                }
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                value: runProgVal

                // Update prog value and step on change
            }

            Button {
                id: stopRunB
                y: 157
                width: 100
                text: qsTr("Stop Run")
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 15

                onClicked: {stopDialog.open()}
            }

            Button {
                id: runDetB
                x: 152
                y: 157
                text: qsTr("Run Details")
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: stopRunB.verticalCenter
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom

                onClicked: {root.runDetails(root.casNumber)}
            }

            Text {
                id: runStepL
                text: runStep
                anchors.left: runProgBar.left
                anchors.leftMargin: 0
                anchors.bottom: runProgBar.top
                anchors.bottomMargin: 7
                font.pointSize: 12
                font.weight: Font.Normal
            }

            Text {
                id: sampNameL
                text: runSampleName
                anchors.bottom: protNameL.top
                anchors.bottomMargin: 7
                style: Text.Normal
                anchors.topMargin: 5
                anchors.top: casNum2.bottom
                font.pointSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                anchors.horizontalCenterOffset: 0
            }

            Text {
                id: protNameL
                text: runProtocolName
                anchors.bottom: runStepL.top
                anchors.bottomMargin: 10
                style: Text.Normal
                font.pointSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                anchors.horizontalCenterOffset: 0
            }

            Text {
                id: runTimeL
                x: 1
                y: 1
                width: 65
                height: 19
                text: runTime
                anchors.right: runProgBar.right
                anchors.rightMargin: 0
                anchors.verticalCenter: runStepL.verticalCenter
                font.pointSize: 12
                font.weight: Font.Normal
            }



        }

    }

    MessageDialog {
        id: stopDialog
        standardButtons: StandardButton.Cancel | StandardButton.Yes
        icon: StandardIcon.Warning
        text: "Do you want to stop run on Cassette " + casNumber +"?"
        title: "Stop Cassette " + casNumber + " run?"
        modality: Qt.WindowModal
        onYes: {
            console.log("Stop run on Cassette " + casNumber + ".")
            stackIndex = 1
            root.stopRun(root.casNumber)
        }
        onRejected: {
            console.log("Canceled.")
            this.close
        }
    }


}
