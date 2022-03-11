import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.3
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import "./Icons/"

Item {
    id: root
    property int casNumber: 0
    property int stackIndex: 0
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
    property bool isFinished: false
    property int hangSecs: 0
    property variant progStrings: []
    property variant stepRunTimes: []
    property int totalSteps: root.progStrings.length
    property int stepIndex: 0
    property string logText: ''
    property int startlog: 0
    property int endlog: 0
    property int currentEnd: 0
    property bool isLogRefreshed: false

    property string sampleName: ''
    property string fullProcessProt: './Protocols/default/Full Process.json'
    property string noStainProt: './Protocols/default/No Stain.json'
    property string noFormProt: './Protocols/default/No Fixative.json'

    signal reSetupProt(string casNum, variant progS, variant stepTimes, string runtime, string samplen, string protocoln)
    signal reStartedProt(int casNum, string logChunk, int start, int currentEnd)
    signal reUpdateProg(int casNum)
    signal reReqLogChunk(int casNum, string logChunk, int currentEnd)
    signal reUpLogChunk(int casNum, string logChunk, int currentEnd)
//    signal reRepopulate(string casNum, variant progS, variant stepTimes, int stepInd, int secsRem, int totalRemaining, int totalRunSecs, string samplen, string protocoln, string status)
    signal reRepopulate(int casNum, variant progS, variant stepTimes, variant otherVars)
    signal reCleanStart(int casNum)
    signal reCleanFinished(int casNum)
    signal reShutdownStart(int casNum)
    signal reShutdownFinished(int casNum)
    signal reEngaged(int casNum)
    signal reDisengaged(int casNum)
    signal reDCController()
    signal reJoinController()

    Component.onCompleted: {
        WAMPHandler.setupProt.connect(reSetupProt)
        WAMPHandler.startedProt.connect(reStartedProt)
        WAMPHandler.updateProg.connect(reUpdateProg)
        WAMPHandler.reqLogChunk.connect(reReqLogChunk)
        WAMPHandler.upLogChunk.connect(reUpLogChunk)
        WAMPHandler.repopulateProt.connect(reRepopulate)
        WAMPHandler.cleanStart.connect(reCleanStart)
        WAMPHandler.cleanDone.connect(reCleanFinished)
        WAMPHandler.shutdownStart.connect(reShutdownStart)
        WAMPHandler.shutdownDone.connect(reShutdownFinished)
        WAMPHandler.casEngaged.connect(reEngaged)
        WAMPHandler.casDisengaged.connect(reDisengaged)
        WAMPHandler.controllerDCed.connect(reDCController)
        WAMPHandler.controllerJoined.connect(reJoinController)
    }

    width: 195
    height: 300

    Connections {
        target: root
        function onReSetupProt(casNum, progS, stepTimes, runtime, samplen, protocoln) {
            //Check if casNumber corresponds with this casNumber
            if (root.casNumber==casNum && !root.isRunning){
                //setup run
//                console.log(progS)
//                console.log(stepTimes)
                runProgBar.progColor = "#17a81a"
                root.runTime = runtime
                root.runSecs = get_sec(runtime)
                root.firstRunTime = runtime
                root.firstRunSecs = get_sec(runtime)
                root.runSampleName = samplen
                root.runProtocolName = protocoln
                root.stackIndex = 2
                root.stepIndex = 0
                root.progStrings = progS
                root.runStep = 'Setting up run....'
                root.stepRunTimes = stepTimes
                root.hangSecs = parseInt(root.stepRunTimes[root.stepIndex])
                root.runProgVal = 0
                root.isRunning = true
                root.isHanging = true
                stopRunB.visible = true
                nextRunB.visible = false
                runDetB.enabled = false
            }
        }
        function onReStartedProt(casNum, logChunk, start, currentEnd) {
            if (root.casNumber==casNum && root.isHanging){
//                console.log('Starting Run, Cas', casNumber)
//                console.log(logChunk)
                //start run
                root.runStep = root.progStrings[root.stepIndex]
                root.isHanging = false
                runDetB.enabled = true
                root.startlog = start
                root.currentEnd = currentEnd
                root.logText = logChunk

                runProgBar.progColor = "#17a81a"
                root.runTime = runtime
                root.runSecs = get_sec(runtime)
                root.firstRunTime = runtime
                root.firstRunSecs = get_sec(runtime)
                root.runSampleName = samplen
                root.runProtocolName = protocoln
                root.stackIndex = 2
                root.stepIndex = 0
                root.progStrings = progS
                root.runStep = 'Setting up run....'
                root.stepRunTimes = stepTimes
                root.hangSecs = parseInt(root.stepRunTimes[root.stepIndex])
                root.runProgVal = 0
                root.isRunning = true
                root.isHanging = true
                stopRunB.visible = true
                nextRunB.visible = false
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
//                    console.log('New run secs: ', root.runSecs)
//                    console.log('New index: ', root.stepIndex)
                    root.runTime = get_time(root.runSecs)
                    //Get new progress bar value
                    root.runProgVal = 100*(root.firstRunSecs - root.runSecs)/root.firstRunSecs
                    //Sum next stepRunTimes for the current stepIndex to find next hangSecs
                    root.hangSecs = root.hangSecs + parseInt(root.stepRunTimes[root.stepIndex])

                    root.isRunning = true
                    root.isHanging = false
                } else {
//                    console.log('Protocol Finished! Cas', root.casNumber)
                    root.isHanging = true
                    root.isFinished = true
                    root.isRunning = false
                    root.runTime = "00:00:00"
                    root.runSecs = get_sec(root.runTime)
                    root.runProgVal = 100
//                    stopRunB.visible = false
//                    nextRunB.visible = true
                }
            }
        }
        function onReReqLogChunk(casNum, logChunk, currentEnd){
            if (root.casNumber==casNum){
//                console.log('Refreshed Cas', root.casNumber)
                //Replaces entire log chunk
                root.logText = logChunk
                root.currentEnd = currentEnd
                //Finish refresh, prepare for next one
                root.isLogRefreshed = false
            }
        }
        function onReUpLogChunk(casNum, logChunk, currentEnd){
            if (root.casNumber==casNum){
//                console.log('Refreshed Cas', root.casNumber)
                //updates current log text with a new chunk
                root.logText = root.logText + logChunk
                root.currentEnd = currentEnd
                //Finish refresh, prepare for next one
                root.isLogRefreshed = false
            }
        }
        //['stepNum','secsRemaining','sampleName','protocolName','status']
        function onReRepopulate(casNum, progS, stepTimes, otherVars) {
            //Check if casNumber corresponds with this casNumber
            if (root.casNumber==casNum){
//                console.log('trying to repopulate... Cas', casNumber)
                var status = otherVars[otherVars.length-1]
//                console.log(status)
                if (status == 'running'){
                    //setup run
                    var stepInd = otherVars[0]
                    var secsRem = otherVars[1]
                    var samplen = otherVars[2]
                    var protocoln = otherVars[3]
                    runProgBar.progColor = "#17a81a"
//                    console.log(progS)
//                    console.log(stepTimes)
                    root.stepIndex = stepInd-1
                    root.firstRunSecs = sum_arr(stepTimes)
                    root.firstRunTime = get_time(root.firstRunSecs)
                    root.runSecs = secsRem + sum_arr(stepTimes.slice(stepInd,))
                    root.runTime = get_time(runSecs)

                    root.runSampleName = samplen
                    root.runProtocolName = protocoln
                    root.stackIndex = 2

                    root.progStrings = progS
                    root.runStep = root.progStrings[root.stepIndex]
                    root.stepRunTimes = stepTimes
                    root.hangSecs = sum_arr(stepTimes.slice(0,stepInd))
                    root.runProgVal = 100*(root.firstRunSecs - root.runSecs)/root.firstRunSecs
                    root.isRunning = true
                    root.isHanging = false
                    stopRunB.visible = true
                    nextRunB.visible = false
                } else if (status == 'stopping'){
                    //setup run
                    var stepInd = otherVars[0]
                    var secsRem = otherVars[1]
                    var samplen = otherVars[2]
                    var protocoln = otherVars[3]
                    runProgBar.progColor = "darkred"
//                    console.log(progS)
//                    console.log(stepTimes)
                    root.stepIndex = stepInd-1
                    root.firstRunSecs = sum_arr(stepTimes)
                    root.firstRunTime = get_time(root.firstRunSecs)
                    root.runSecs = secsRem + sum_arr(stepTimes.slice(stepInd,))
                    root.runTime = get_time(runSecs)

                    root.runSampleName = samplen
                    root.runProtocolName = protocoln
                    root.stackIndex = 2

                    root.progStrings = progS
                    root.runStep = 'Shutting down...'
                    root.stepRunTimes = stepTimes
                    root.hangSecs = sum_arr(stepTimes.slice(0,stepInd))
                    root.runProgVal = 100*(root.firstRunSecs - root.runSecs)/root.firstRunSecs
                    root.isRunning = true
                    root.isHanging = true
                    stopRunB.visible = true
                    nextRunB.visible = false
                    stopRunB.enabled = false
//                    stopRunB.checked = true
//                    engageCasB.enabled = false
                } else if (status == 'cleaning'){
                    //setup run
                    var stepInd = otherVars[0]
                    var secsRem = otherVars[1]
                    var samplen = otherVars[2]
                    var protocoln = otherVars[3]
                    runProgBar.progColor = "#17a81a"
                    root.runTime = "00:00:00"
                    root.runSecs = get_sec(root.runTime)
                    root.runSampleName = samplen
                    root.runProtocolName = protocoln
                    root.stackIndex = 2
                    root.stepIndex = stepInd-1
                    root.progStrings = progS
                    root.runStep = 'Cleaning...'
                    root.runProgVal = 100
                    root.stepRunTimes = stepTimes
                    root.isRunning = true
                    root.isHanging = true
                    stopRunB.visible = true
                    nextRunB.visible = false
//                    engageCasB.enabled = false
                } else if(status == 'finished'){
//                    console.log('Protocol Finished! Cas', root.casNumber)
                    var stepInd = otherVars[0]
                    var secsRem = otherVars[1]
                    var samplen = otherVars[2]
                    var protocoln = otherVars[3]
                    runProgBar.progColor = "#17a81a"
                    root.isRunning = false
                    root.isHanging = true
                    root.isFinished = true
                    root.runTime = "00:00:00"
                    root.runSecs = get_sec(root.runTime)
                    root.runSampleName = samplen
                    root.runProtocolName = protocoln
                    root.stackIndex = 2
                    root.stepIndex = stepInd-1
                    root.progStrings = progS
                    root.runStep = root.progStrings[root.stepIndex]
                    root.runProgVal = 100
                    root.stepRunTimes = stepTimes
                    stopRunB.visible = false
                    nextRunB.visible = true
                    engageCasB.enabled = true
                } else if(status == 'shutdown'){
                    var stepInd = otherVars[0]
                    var secsRem = otherVars[1]
                    var samplen = otherVars[2]
                    var protocoln = otherVars[3]
                    runProgBar.progColor = "darkred"
                    root.stepIndex = 0
                    root.firstRunSecs = sum_arr(stepTimes)
                    root.firstRunTime = get_time(root.firstRunSecs)
                    root.runSecs = secsRem + sum_arr(stepTimes.slice(stepInd,))
                    root.runTime = get_time(runSecs)
                    root.runSampleName = samplen
                    root.runProtocolName = protocoln
                    root.stackIndex = 2
                    root.progStrings = progS
                    root.runStep = 'Shutdown.'
                    root.stepRunTimes = stepTimes
                    root.hangSecs = sum_arr(stepTimes.slice(0,stepInd))
                    root.runProgVal = 100*(root.firstRunSecs - root.runSecs)/root.firstRunSecs
                    root.isRunning = false
                    root.isHanging = true
                    stopRunB.visible = false
                    stopRunB.enabled = true
//                    stopRunB.checked = false
                    nextRunB.visible = true
                    engageCasB.enabled = true
                }
            } else {
//                console.log('Not repopulating! Cas', casNumber)
            }
        }
        function onReCleanStart(casNum){
            if (root.casNumber==casNum){
                root.runStep = 'Cleaning...'
                root.isRunning = true
                root.isHanging = true
//                engageCasB.enabled = false
            }
        }
        function onReCleanFinished(casNum){
            if (root.casNumber==casNum){
                root.runStep = 'Cleaned.'
                root.isRunning = false
                stopRunB.visible = false
                stopRunB.enabled = true
//                stopRunB.checked = false
                nextRunB.visible = true
//                engageCasB.enabled = true
            }
        }
        function onReShutdownStart(casNum){
            if (root.casNumber==casNum){
                //Start a separate shutdown protocol???
                root.runStep = 'Shutting down...'
                runProgBar.progColor = "darkred"
                root.isRunning = true
                root.isHanging = true
                stopRunB.visible = true
                nextRunB.visible = false
                stopRunB.enabled = false
//                stopRunB.checked = true


            }
        }
        function onReShutdownFinished(casNum){
            if (root.casNumber==casNum){
                root.runStep = 'Shutdown.'
                runProgBar.progColor = "darkred"
                root.isRunning = false
                stopRunB.visible = false
                stopRunB.enabled = true
//                stopRunB.checked = false
                nextRunB.visible = true
//                engageCasB.enabled = true
            }
        }
        function onReEngaged(casNum) {
                    //Check if casNumber corresponds with this casNumber
                    if (root.casNumber==casNum){
                        root.stackIndex = 1
                        engageCasB.enabled = true
//                        engageCasB.checked = false
//                        console.log('Engaged Cas', casNumber)
                    }
        }
        function onReDisengaged(casNum) {
                    //Check if casNumber corresponds with this casNumber
                    if (root.casNumber==casNum){
                        root.stackIndex = 0
                        engageCasB.enabled = true
//                        engageCasB.checked = false
//                        console.log('Disengaged Cas', casNumber)
                    }
        }
        function onReDCController() {
            //hang the controller progress and disable the buttons that advance the sample stack
            root.isHanging = true
            engageCasB.enabled = false
            disengageCasB.enabled = false
            stopRunB.enabled = false
            nextRunB.enabled = false
            setupRunB.enabled = false
//            defRunB.enabled = false
        }
        function onReJoinController() {
//            root.isHanging = false
            engageCasB.enabled = true
            disengageCasB.enabled = true
            stopRunB.enabled = true
            nextRunB.enabled = true
            setupRunB.enabled = true
//            defRunB.enabled = true
        }
    }

    StackLayout {
        id: sampStack
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.fill: parent
        currentIndex: stackIndex
        Material.theme: Material.Dark
//        Material.background: Material.BlueGrey
        Material.accent: Material.Blue

        RoundPane {
            id: noCasDetected
            Material.elevation: 9
            radius: 15
            backgroundColor: "#777777"
//            radius: 8
//            border.color: "black"
//            border.width: 0.5

            Text {
                id: casNum0
                text: casNumber
                anchors.top: parent.top
                anchors.topMargin: 30
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                font.pointSize: 18
            }

            ColumnLayout {
                id:engCol
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
                anchors.top: casNum0.bottom
                anchors.topMargin: 10
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.right: parent.right
                anchors.rightMargin: 0

                Button {
                    id: engageCasB
                    Layout.preferredHeight: 50
                    Layout.minimumHeight: 40
                    text: qsTr("Engage")
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    font.pointSize: 12
                    font.capitalization: Font.MixedCase
//                    palette {
//                        button: 'green'
//                        buttonText: 'white'
//                    }
                    Material.background: 'green'
                    Material.foreground: 'white'

                    onClicked: {
                        WAMPHandler.engageCas(root.casNumber)
                        engageCasB.enabled = false
//                        engageCasB.checked = true
                    }
                }
           }
        }
        RoundPane {
            id: setupRun
            Material.elevation: 9
            radius: 15
            backgroundColor: "#777777"

            Text {
                id: casNum1
                text: casNumber
                anchors.top: parent.top
                anchors.topMargin: 15
                anchors.horizontalCenter: parent.horizontalCenter
                font.weight: Font.Medium
                font.pointSize: 18
            }


            ColumnLayout {
                id: colLayout
                anchors.topMargin: 5
                anchors.top: casNum1.bottom
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.margins: 10
                spacing: 10
//                flow:  parent.width > parent.height ? GridLayout.LeftToRight : GridLayout.TopToBottom
//                flow: GridLayout.TopToBottom

                Button {
                    id: disengageCasB
                    Layout.preferredWidth: colLayout.width/1.5
                    Layout.preferredHeight: 50
                    Layout.minimumHeight: 30
                    text: qsTr("Disengage")
                    font.pointSize: 12
                    font.capitalization: Font.MixedCase
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
//                    palette {
//                        button: 'darkred'
//                        buttonText: 'white'
//                    }
                    Material.background: 'darkred'
                    Material.foreground: 'white'

                    onClicked: {
                        root.stackIndex = 0
                        WAMPHandler.disengageCas(root.casNumber)
                        engageCasB.enabled = false
//                        engageCasB.checked = false
                    }
                }

                Rectangle {
                    id: sampRec
                    Layout.preferredWidth: colLayout.width
                    Layout.preferredHeight: 31
                    Layout.minimumHeight: 25
                    color: "#808080"

                    TextInput {
                        id: sampInput
                        property string placeholderText: "Enter Sample Name"
                        font.capitalization: Font.MixedCase
                        color: "#ffffff"
                        leftPadding: 5
                        anchors.rightMargin: 0
                        anchors.bottomMargin: 0
                        anchors.leftMargin: 0
                        anchors.topMargin: 0
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        anchors.fill: parent
                        font.pointSize: 11
                        selectionColor: "#040450"

                        text: activeFocus ? sampleName : ''
                        clip: true

                        onEditingFinished: {
                            sampleName = sampInput.text
//                                console.log(sampleName)
                        }

                        Text {
                            id: placeholderTxt
                            anchors.fill: parent
                            text: sampInput.placeholderText
                            leftPadding: 5
                            verticalAlignment: Text.AlignVCenter
                            color: "#aaa"
                            font: sampInput.font
                            visible: !sampleName && !sampInput.activeFocus
                        }

                        Text {
                            id: shortTxt
                            anchors.fill: parent
                            text: sampleName
                            elide: Text.ElideMiddle
                            leftPadding: 5
                            verticalAlignment: Text.AlignVCenter
                            color: "#ffffff"
                            font: sampInput.font
                            visible: sampInput.activeFocus ? false : true
                        }
                    }
                }

                ComboBox {
                    id: comboProt
                    Material.accent: Material.Blue
//                    Material.background: '#999999'
//                    Material.primary: 'silver'
                    Material.elevation: 5
//                    popup.Material.background: '#999999'
                    popup.font.pointSize: 11

                    model: ["Full Process", "No Stain", "No Fixation", "Custom"]

                    font.pointSize: 11
                    Layout.topMargin: 10
                    Layout.preferredWidth: colLayout.width
                    Layout.preferredHeight: 50
                    Layout.minimumHeight: 30
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                }

                Button {
                    id: setupRunB
                    Layout.preferredWidth: colLayout.width/2
                    text: qsTr("Start")
                    font.pointSize: 12
                    font.capitalization: Font.MixedCase
                    Layout.preferredHeight: 50
                    Layout.minimumHeight: 30
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    Material.theme: Material.Light

                    onClicked: {
                        console.log(comboProt.currentValue)
                        if (comboProt.currentValue=='Custom'){
                            //push protocol selector screen and populate with casNumber info
                            mainStack.push("ProtocolSelector.qml", {casNumber: root.casNumber, sampleName: root.sampleName})
                        } else {
                            // Check if sample name exists, if not push warning popup
                            if (!/\S/.test(root.sampleName)){
                                sampleNameDi.open()
                            //Check if model data is empty
                            } else {
                                // Start protocol with sample name depending on combobox choice
                                if (comboProt.currentValue=='Full Process'){
                                    WAMPHandler.startProtocol(root.casNumber, root.fullProcessProt, 'undefined', root.sampleName, 'Full Process')
                                } else if (comboProt.currentValue=='No Stain'){
                                    WAMPHandler.startProtocol(root.casNumber, root.noStainProt, 'undefined', root.sampleName, 'No Stain')
                                } else if (comboProt.currentValue=='No Fixation'){
                                    WAMPHandler.startProtocol(root.casNumber, root.noFormProt, 'undefined', root.sampleName, 'No Fixation')
                                }
                            }
                        }
                    }
                }
            }

        }
        RoundPane {
            id: runInProg
            Material.elevation: 9
            radius: 15
            backgroundColor: "#777777"
//            radius: 8
//            border.color: "black"
//            border.width: 0.5

            Timer {
                id: progTimer
                interval: 1000
                running: {root.isRunning && !root.isHanging}
                repeat: true
                onTriggered: {
                    var timeElap = root.firstRunSecs - root.runSecs


                    if(timeElap >= root.hangSecs){
                        root.isHanging = true
//                        console.log(root.casNumber,' Hanging: ',timeElap)
                    } else {
                        root.runSecs = root.runSecs - 1
                        root.runProgVal = root.runProgVal + 100/root.firstRunSecs
                        if(root.runSecs === 0){
                            root.isHanging = true
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
//                Layout.preferredHeight: 70
//                Layout.minimumHeight: 50

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
                    font.bold: false
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    //                    anchors.horizontalCenter: parent.horizontalCenter
                    elide: Text.ElideMiddle
                    fontSizeMode: Text.Fit
                    style: Text.Normal
                    font.weight: Font.Normal
                    font.pointSize: 12
                    minimumPointSize: 12
                    Layout.maximumWidth: parent.width-40
                }

                Text {
                    id: protNameL
                    text: runProtocolName
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    //                    anchors.horizontalCenter: parent.horizontalCenter
                    elide: Text.ElideMiddle
                    fontSizeMode: Text.Fit
                    //                    anchors.bottom: runStepL.top
                    //                    anchors.bottomMargin: 10
                    style: Text.Normal
                    font.weight: Font.Normal
                    font.pointSize: 12
                    minimumPointSize: 12
                    Layout.maximumWidth: parent.width-40
                }

            }

            Text {
                id: runStepL
                text: runStep
                style: Text.Normal
                fontSizeMode: Text.VerticalFit
                anchors.left: parent.left
                anchors.bottom: runProgBar.top
                anchors.bottomMargin: 5
                anchors.leftMargin: 0
                font.pointSize: 11
                font.weight: Font.Thin
                minimumPointSize: 11
            }

            Text {
                id: runTimeL
                width: 69
                height: 19
                text: runTime
                fontSizeMode: Text.VerticalFit
                anchors.right: parent.right
                horizontalAlignment: Text.AlignRight
                anchors.rightMargin: 0
                anchors.verticalCenter: runStepL.verticalCenter
                font.pointSize: 11
                font.weight: Font.Thin
                minimumPointSize: 11
            }

            ProgressBar {
                property string progColor: "#17a81a"
                id: runProgBar
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
                    implicitHeight: 20
                    implicitWidth: 200
                }
                contentItem: Item {
                    anchors.fill: parent
                    implicitHeight: 20
                    implicitWidth: 200
                    Rectangle {
                        width: runProgBar.visualPosition * parent.width
                        height: parent.height
                        color: runProgBar.progColor
                        radius: 2
                    }

                }

                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                value: runProgVal
//                indeterminate: (root.isHanging | rootApWin.isDisconnected) && !root.isFinished

                // Update prog value and step on change
            }

            Text {
                id: runStepNum
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

            Button {
                id: stopRunB
                width: (runInProg.width - (runDetB.anchors.rightMargin + stopRunB.anchors.leftMargin))/2 - 15
//                Layout.preferredWidth: 80
                Layout.minimumWidth: 60
                Layout.preferredHeight: 50
                Layout.minimumHeight: 30

                text: qsTr("Stop")
                font.pointSize: 12
                font.capitalization: Font.MixedCase
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 15
//                palette {
//                    button: 'darkred'
//                    buttonText: 'white'
//                }
                Material.background: 'darkred'
                Material.foreground: 'white'

                onClicked: {stopDialog.open()}
            }

            Button {
                id: runDetB
//                Layout.preferredWidth: 80
                width: (runInProg.width - (runDetB.anchors.rightMargin + stopRunB.anchors.leftMargin))/2 - 15
//                Layout.preferredWidth: 80
                Layout.minimumWidth: 60
                Layout.preferredHeight: 50
                Layout.minimumHeight: 30
                text: qsTr("Log")
                font.pointSize: 12
                font.capitalization: Font.MixedCase
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: stopRunB.verticalCenter
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                Material.theme: Material.Light

                onClicked: {
                    runDetWin.close()
                    runDetWin.show()
                    runDetWin.raise()
                    if (!root.isLogRefreshed){
                        WAMPHandler.refreshRunDet(root.casNumber, root.currentEnd)
                        root.isLogRefreshed = true
                    }
                }
            }

            Button {
                id: nextRunB
                visible: false
                width: (runInProg.width - (runDetB.anchors.rightMargin + stopRunB.anchors.leftMargin))/2 - 15
//                Layout.preferredWidth: 80
                Layout.minimumWidth: 60
                Layout.preferredHeight: 50
                Layout.minimumHeight: 30
                text: qsTr("Next")
                anchors.bottom: parent.bottom
                font.pointSize: 12
                font.capitalization: Font.MixedCase
                anchors.leftMargin: 10
                anchors.left: parent.left
                anchors.bottomMargin: 15
                Material.theme: Material.Light


                onClicked: {
                    //Erase all info from progress bar
                    //Make sure run is stopped
                    runProgBar.progColor = "#17a81a"
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
                    root.isFinished = false
                    root.isHanging = false
                    stopRunB.visible = true
                    stopRunB.enabled = true
//                    stopRunB.checked = false
                    nextRunB.visible = false
                    WAMPHandler.nextProtocol(root.casNumber)

                    //switch index
                    stackIndex = 0
                    //reset sample name
                    sampleName = ''
                }
            }

        }

    }

    Window{
        id:runDetWin
        y: menuRect.height + runDetWin.height/2
        x: 100+(casNumber-1)*50
        width: 550
        height: 300
        minimumWidth: 220
        minimumHeight: 110
        visible: false
        title: "Cas"+casNumber+" Log"
        flags: Qt.WindowMinimized
        color:'silver'

        Component.onCompleted: {runDetWin.close()}
        
//        onClosing: {
//            root.isLogRefreshed = false
////            close.accepted = false
////            runDetWin.width = 550
////            runDetWin.height = 300
////            runDetWin.hide()

//        }

        LogDisplay {
            id:logDisplay
            colorBG:'silver'
            casNumber: root.casNumber
            sampleName: root.runSampleName
            protocolName: root.runProtocolName
            logText: root.logText
            onRefresh: {
                if (!root.isLogRefreshed){
                    WAMPHandler.refreshRunDet(root.casNumber, root.currentEnd)
                    root.isLogRefreshed = true
                }
            }
        }

    }

    MessageDialog {
        id: sampleNameDi
        standardButtons: StandardButton.Ok
        icon: StandardIcon.Critical
        text: "Enter a sample name to start the run on Cassette "+root.casNumber.toString()+"."
        title: "Sample name is missing."
        modality: Qt.WindowModal
        onAccepted: {}
    }

    MessageDialog {
        id: stopDialog
        standardButtons: StandardButton.Cancel | StandardButton.Yes
        icon: StandardIcon.Warning
        text: "Do you want to stop run on Cassette " + casNumber +"?"
        title: "Stop Cassette " + casNumber + " run?"
        modality: Qt.WindowModal
        onYes: {
//            console.log("Stoping run on Cassette " + casNumber + ".")
            root.runStep = 'Stopping run...'
            runProgBar.progColor = 'darkred'
            root.isRunning = true
            root.isHanging = true
            stopRunB.visible = true
            nextRunB.visible = false
            WAMPHandler.stopProtocol(root.casNumber)
        }
        onRejected: {
//            console.log("Canceled.")
//            stopRunB.checked = false
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

    function sum_arr(array){
        var s = 0
        for (var i = 0; i < array.length; i++)
           {
            s += array[i];
        }
        return(s)
    }
}
