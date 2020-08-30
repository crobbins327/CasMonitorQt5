import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.3

Item {
    id: root
    property int casNumber: 0
    property int stackIndex: 1
    property double runProgVal: 0
    property string firstRunTime : "01:31:55"
    property int firstRunSecs : get_sec(root.firstRunTime)
    property string runSampleName: "SampleName"
    property string runProtocolName: "ProtocolName"
    property string runStep: "Testing..."
    property string runTime: "01:31:55"
    property int runSecs: get_sec(root.runTime)
    property bool isRunning: false
    property bool isHanging: false
    property int hangSecs: 0
    property variant progStrings: []
    property variant stepRunTimes: []
    property int totalSteps: root.progStrings.length
    property int stepIndex: 0

    signal reSetupProt(string casNum, variant progS, variant stepTimes, string runtime, string samplen, string protocoln)
    signal reUpdateProg(string casNum)
    Component.onCompleted: {
        WAMPHandler.setupProt.connect(reSetupProt)
        WAMPHandler.updateProg.connect(reUpdateProg)
    }
    Connections {
        target: root
        function onReSetupProt(casNum, progS, stepTimes, runtime, samplen, protocoln) {
            //Check if casNumber corresponds with this casNumber
            if (root.casNumber==casNum && !root.isRunning){
                //setup run
                console.log(progS)
                console.log(stepTimes)
                root.runTime = runtime
                root.runSecs = get_sec(runtime)
                root.firstRunTime = runtime
                root.firstRunSecs = get_sec(runtime)
                root.runSampleName = samplen
                root.runProtocolName = protocoln
                root.stackIndex = 2
                root.stepIndex = 0
                root.progStrings = progS
                root.runStep = root.progStrings[root.stepIndex]
                root.stepRunTimes = stepTimes
                root.hangSecs = parseInt(root.stepRunTimes[root.stepIndex])
                root.runProgVal = 0
                root.isRunning = true
                root.isHanging = false
            } else {
                console.log('Not me! ', root.casNumber)
            }
        }
        function onReUpdateProg(casNum) {
            //Check if casNumber corresponds with this casNumber
            if (root.casNumber==casNum && root.isRunning){
                if (root.stepIndex < root.totalSteps-1){
                    //setup run
                    root.stepIndex += 1
                    root.runStep = root.progStrings[root.stepIndex]
                    //Set runSecs to where hangSecs should be (just incase step finished sooner than what was estimated)
                    root.runSecs = root.firstRunSecs - root.hangSecs
                    print('New run secs: ', root.runSecs)
                    print('New index: ', root.stepIndex)
                    root.runTime = get_time(root.runSecs)
                    //Get new progress bar value
                    root.runProgVal = 100*(root.firstRunSecs - root.runSecs)/root.firstRunSecs
                    //Sum next stepRunTimes for the current stepIndex to find next hangSecs
                    root.hangSecs = root.hangSecs + parseInt(root.stepRunTimes[root.stepIndex])

                    root.isRunning = true
                    root.isHanging = false
                } else {
                    console.log('Protocol Finished! ', root.casNumber)
                }
            } else {
                console.log('Not me! ', root.casNumber)
            }
        }
    }



    signal setupRun(int casNumber)
    signal defaultRun(int casNumber)
    signal stopRun(int casNumber)
    signal runDetails(int casNumber)
    //    signal startRun(int casNumber)

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

            Timer {
                interval: 100
                running: {root.isRunning && !root.isHanging}
                repeat: true
                onTriggered: {
                    var timeElap = root.firstRunSecs - root.runSecs


                    if(timeElap >= root.hangSecs){
                        root.isHanging = true
                        console.log(root.casNumber,' Hanging: ',timeElap)
                    } else {
                        root.runSecs = root.runSecs - 1
                        root.runProgVal = root.runProgVal + 100/root.firstRunSecs
                        if(root.runSecs === 0){
                            root.isRunning = false
                        }
                        root.runTime = get_time(root.runSecs)
                    }
                }

            }

            ColumnLayout{
                id: column
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 128
                anchors.right: parent.right
                anchors.rightMargin: 0
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: parent.top
                anchors.topMargin: 0
                spacing: 1
                Layout.preferredHeight: 70
                Layout.minimumHeight: 50

                Text {
                    id: casNum2
                    text: casNumber
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    fontSizeMode: Text.Fit
                    //                    anchors.horizontalCenter: parent.horizontalCenter
                    font.weight: Font.Medium
                    font.pointSize: 18
                    minimumPointSize: 16
                }

                Text {
                    id: sampNameL
                    text: runSampleName
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    //                    anchors.horizontalCenter: parent.horizontalCenter
                    fontSizeMode: Text.Fit
                    style: Text.Normal
                    font.weight: Font.Medium
                    font.pointSize: 11
                    minimumPointSize: 11
                }

                Text {
                    id: protNameL
                    text: runProtocolName
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    //                    anchors.horizontalCenter: parent.horizontalCenter
                    fontSizeMode: Text.Fit
                    //                    anchors.bottom: runStepL.top
                    //                    anchors.bottomMargin: 10
                    style: Text.Normal
                    font.weight: Font.Medium
                    font.pointSize: 11
                    minimumPointSize: 11
                }

            }

            ProgressBar {
                id: runProgBar
                height: 20
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.bottom: stopRunB.top
                anchors.bottomMargin: 7
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
                font.pointSize: 11
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
                font.pointSize: 11
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: stopRunB.verticalCenter
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom

                onClicked: {root.runDetails(root.casNumber)}
            }

            Text {
                id: runStepL
                text: runStep
                style: Text.Normal
                anchors.verticalCenterOffset: -22
                anchors.verticalCenter: runProgBar.verticalCenter
                fontSizeMode: Text.VerticalFit
                anchors.left: runProgBar.left
                anchors.leftMargin: 0
                font.pointSize: 12
                font.weight: Font.Thin
                minimumPointSize: 10
            }


            Text {
                id: runStepNum
                x: 58
                y: 119
                text: (stepIndex+1).toString() + '/' + totalSteps.toString()
                anchors.horizontalCenterOffset: 0
                font.bold: false
                anchors.horizontalCenter: runProgBar.horizontalCenter
                style: Text.Normal
                minimumPointSize: 10
                font.weight: Font.Normal
                font.pointSize: 11
                anchors.verticalCenterOffset: 0
                anchors.verticalCenter: runProgBar.verticalCenter
                fontSizeMode: Text.VerticalFit
            }

            Text {
                id: runTimeL
                x: 161
                y: 1
                width: 69
                height: 19
                text: runTime
                fontSizeMode: Text.VerticalFit
                anchors.right: runProgBar.right
                anchors.rightMargin: 0
                anchors.verticalCenter: runStepL.verticalCenter
                font.pointSize: 11
                font.weight: Font.Normal
                minimumPointSize: 10
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
            root.isRunning = false
            root.runTime = "00:00:00"
            root.runSecs = get_sec(root.runTime)
            root.firstRunTime = root.runTime
            root.firstRunSecs = get_sec(root.runTime)
            root.runSampleName = 'SampleName'
            root.runProtocolName = 'ProtocolName'
            root.runStep = 'Testing...'
            root.progStrings = []
            root.runProgVal = 0
            root.stepIndex = 0
            root.isRunning = false
            root.isHanging = false
            WAMPHandler.stopProtocol(root.casNumber)
        }
        onRejected: {
            console.log("Canceled.")
            this.close
        }
    }
    function get_sec(runtime){
        var timesplit = (runtime || '').split(':')
        var secs = 0
        for (var i = 0; i < timesplit.length; i++) {
            secs += isNaN(parseInt(timesplit[i])) ? 0 : parseInt(timesplit[i])*Math.pow(60,2-i);
        }

        return(secs)
    }

    function get_time(runSecs){
        var rtime = new Date(runSecs * 1000).toISOString().substr(11, 8);
        return(rtime)
    }


}



/*##^##
Designer {
    D{i:12;anchors_width:240}D{i:23;anchors_y:1}D{i:24;anchors_y:1}
}
##^##*/
