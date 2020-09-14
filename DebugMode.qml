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
    property string incTime: "00:00:00"
    property int incSecs: 0
    property int mixAfterSecs: 0
    property int numCycles: mixCycles.currentValue + 1
    property int pSpeedV: pSpeed.currentValue + 1
    property double mixVol: 0
    property int loadVol: 0
    property string scriptText: ''
    property var casNames: ['A','B','C','D','E','F']

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

//    width: 780
//    height: 410
    //    anchors.fill: parent


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
            color: "#434343"
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
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
            //            border.width: 1
            color: 'transparent'
            anchors.bottom: parent.bottom
            anchors.bottomMargin: -2
            //            border.color: "#3b3b3b"
            anchors.right: parent.right
            anchors.rightMargin: -2
            anchors.left: parent.left
            anchors.leftMargin: -2
            anchors.top: casBar.bottom
            anchors.topMargin: 10

            SwipeView {
                id: view
                anchors.fill: parent
                currentIndex: 1

                Item{
                    id: manualPg
                    BevButton {
                        id: homeSyrB
                        width: 75
                        height: 40
                        text: qsTr("Home")
                        anchors.top: manualLab.bottom
                        anchors.topMargin: 15
                        anchors.left: parent.left
                        anchors.leftMargin: 25
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
                        anchors.topMargin: 20
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
                        height: 45
                        text: qsTr("Pump in")
                        anchors.top: wasteB.bottom
                        anchors.topMargin: 20
                        anchors.left: wasteB.left
                        anchors.leftMargin: 0
                        palette {
                            button: 'white'
                        }

                        onClicked: {root.pumpIn(); console.log("Pump In")}
                    }

                    BevButton {
                        id: pumpOutB
                        y: 293
                        height: 45
                        text: qsTr("Pump Out")
                        anchors.left: pumpInB.right
                        anchors.leftMargin: 45
                        anchors.verticalCenter: pumpInB.verticalCenter
                        palette {
                            button: 'white'
                        }

                        onClicked: {root.pumpOut(); console.log("Pump Out")}
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
                        anchors.topMargin: 20
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
                        height: 30
                        anchors.left: pumpOutB.right
                        anchors.leftMargin: 50
                        anchors.verticalCenter: pumpOutB.verticalCenter
                        value: 3
                        to: 10
                        stepSize: 0.01
                    }

                    Text {
                        id: manualLab
                        x: 545
                        width: 152
                        height: 23
                        color: "#ffffff"
                        text: qsTr("Manual Control")
                        anchors.top: parent.top
                        font.bold: true
                        anchors.topMargin: 0
                        anchors.left: parent.left
                        font.pointSize: 14
                        anchors.leftMargin: 10
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
                        font.pointSize: 13
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
                        anchors.leftMargin: 10
                        anchors.verticalCenter: volSLab.verticalCenter
                        y: 233

                        TextInput {
                            id: volInput
                            color: "#ffffff"
                            font.bold: true
                            font.pointSize: 13
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
                        font.pointSize: 13
                        anchors.verticalCenter: rectInput.verticalCenter
                        font.bold: true
                    }

                }

                Item{
                    id: operationPg

                    BevButton {
                        id: purgeBtn
                        width: 95
                        height: 35
                        text: "Purge"
                        anchors.top: pSpeed.bottom
                        anchors.topMargin: 5
                        anchors.left: loadBtn.left
                        anchors.leftMargin: 0
                        palette {
                            button: 'white'
                        }

                        onClicked: {
                            if(scriptSwitch.checked){
                                //make the command for purge
                                //currently set to 3mL purge with 1mL dead volume...
//                                console.log(casBar.currentIndex)
                                var casL = casNames[casBar.currentIndex]
                                var purge = 'self.purge(casL="'+ casL + '", deadvol=4)'
                                //add to scriptText
                                scriptText = scriptText + '\n' + purge
                            }
                            //else execute directly

                        }
                    }
                    BevButton {
                        id: incubateBtn
                        width: 95
                        height: 35
                        text: "Incubate"
                        anchors.top: parent.top
                        anchors.topMargin: 40
                        anchors.left: mixAfRect.right
                        anchors.leftMargin: 15
                        palette {
                            button: 'white'
                        }

                        onClicked: {
                            if(scriptSwitch.checked){
                                //make the command for purge
                                //currently set to 3mL purge with 1mL dead volume...
//                                console.log(casBar.currentIndex)
                                var casL = casNames[casBar.currentIndex]
                                var incubate = 'self.incubate(casL="'+ casL + '", incTime='+ incSecs +', mixAfter='+ mixAfterSecs +')'
                                //add to scriptText
                                scriptText = scriptText + '\n' + incubate
                            }
                            //else execute directly

                        }
                    }
                    BevButton {
                        id: loadBtn
                        height: 35
                        text: "Load Reagent"
                        anchors.right: mixBtn.right
                        anchors.rightMargin: -20
                        anchors.top: mixBtn.bottom
                        anchors.topMargin: 15
                        anchors.left: reagentSel.right
                        anchors.leftMargin: 64
                        palette {
                            button: 'white'
                        }
                        //loadReagent(self, casL, loadstr, reagent, vol, speed, deadvol):
                        onClicked: {
                            if(scriptSwitch.checked){
                                //make the command for purge
                                //currently set to 3mL purge with 1mL dead volume...
//                                console.log(casBar.currentIndex)
                                var casL = casNames[casBar.currentIndex]
                                var loadstr = reagentSel.currentValue
                                var reagentstr = reagentSel.currentValue
                                var deadvol = 1 + loadVol/1000

                                var loadRea = 'self.loadReagent(casL="'+ casL + '", loadstr="'+ loadstr +'", reagent="' + reagentstr + '", vol='+ loadVol +', speed='+ pSpeedV +', deadvol='+deadvol+')'
                                //add to scriptText
                                scriptText = scriptText + '\n' + loadRea
                            }
                            //else execute directly
                        }
                    }
                    BevButton {
                        id: mixBtn
                        height: 35
                        text: "Mix"
                        anchors.right: incubateBtn.right
                        anchors.rightMargin: 0
                        anchors.top: incubateBtn.bottom
                        anchors.topMargin: 15
                        anchors.left: mixVolRect.right
                        anchors.leftMargin: 12
                        palette {
                            button: 'white'
                        }

                        onClicked: {
                            if(scriptSwitch.checked){
                                //make the command for purge
                                //currently set to 3mL purge with 1mL dead volume...
//                                console.log(casBar.currentIndex)
                                var casL = casNames[casBar.currentIndex]
                                var mix = 'self.mix(casL="'+ casL + '", numCycles='+ numCycles +', volume='+ mixVol +')'
                                //add to scriptText
                                scriptText = scriptText + '\n' + mix
                            }
                            //else execute directly

                        }
                    }

                    BevButton {
                        id: execBtn
                        width: 140
                        height: 35
                        text: "Execute Code"
                        anchors.top: parent.top
                        anchors.topMargin: 0
                        anchors.left: scriptSwitch.right
                        anchors.leftMargin: 25
                        anchors.right: casLogBtn.left
                        anchors.rightMargin: 25
                        palette {
                            button: 'white'
                        }

                        enabled: scriptSwitch.checked

                        onClicked: {}
                    }

                    BevButton {
                        id: casLogBtn
                        width: 95
                        height: 35
                        text: "Get Log"
                        anchors.top: parent.top
                        anchors.topMargin: 0
                        anchors.right: scriptRec.right
                        anchors.rightMargin: 0
                        palette {
                            button: 'white'
                        }

                        onClicked: {}
                    }

                    ComboBox {
                        id: reagentSel
                        y: 120
                        width: 130
                        height: 30
                        anchors.verticalCenter: loadBtn.verticalCenter
                        anchors.left: mixCycles.left
                        anchors.leftMargin: 0
                        currentIndex: 0
                        model: ["meoh", "formalin", "babb", "vial"]
                    }

                    Text {
                        id: operationsLab
                        x: 123
                        width: 118
                        height: 23
                        color: "#ffffff"
                        text: qsTr("Operations")
                        anchors.top: parent.top
                        font.bold: true
                        anchors.topMargin: 0
                        anchors.left: parent.left
                        font.pointSize: 14
                        anchors.leftMargin: 10
                    }

                    ComboBox {
                        id: mixCycles
                        y: 65
                        width: 70
                        height: 30
                        anchors.verticalCenter: mixBtn.verticalCenter
                        anchors.left: incRect.left
                        anchors.leftMargin: 0
                        displayText: currentValue + 1
                        model: 20
                        delegate: ItemDelegate {
                            width: mixCycles.width
                            contentItem: Text {
                                text: modelData + 1
                                //                                color: "#21be2b"
                                font: mixCycles.font
                                elide: Text.ElideRight
                                verticalAlignment: Text.AlignVCenter
                            }
                            highlighted: mixCycles.highlightedIndex === index
                        }
                    }

                    ComboBox {
                        id: pSpeed
                        width: 70
                        height: 30
                        anchors.top: reagentSel.bottom
                        anchors.topMargin: 15
                        anchors.left: reagentSel.left
                        anchors.leftMargin: 0
                        displayText: currentValue + 1
                        model: 8
                        delegate: ItemDelegate {
                            width: pSpeed.width
                            highlighted: pSpeed.highlightedIndex === index
                            contentItem: Text {
                                //                                color: "#21be2b"
                                text: modelData + 1
                                verticalAlignment: Text.AlignVCenter
                                font: pSpeed.font
                                elide: Text.ElideRight
                            }
                        }

                    }

                    Rectangle{
                        id:incRect
                        y: 13
                        width: 82
                        height: 30
                        color: "#808080"
                        anchors.verticalCenter: incubateBtn.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 15
                        TextInput {
                            property string placeholderText: "hh:mm:ss"
                            id: incTimeIn
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
                            text: incTime
                            inputMask: "99:99:99"
                            echoMode: (incTime=='::' || incTime=='00:00:00' && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
                            clip: true

                            onTextEdited: {
                                incTime = incTimeIn.text
                                incSecs = get_sec(incTimeIn.text)
                                //                                incTime = get_time(incSecs)
                            }
                            onEditingFinished: {
                                //convert directly into seconds
                                incSecs = get_sec(incTime)
//                                console.log(get_sec(incTime))
                                //convert again into runtime to fix 'empty' inputs
                                incTime = get_time(incSecs)
                            }

                            Text {
                                id: incTimeTxt
                                anchors.fill: parent
                                text: incTimeIn.placeholderText
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#aaa"
                                font: incTimeIn.font
                                visible: (incTime=='::' || incTime == "00:00:00") && !incTimeIn.activeFocus
                            }
                        }
                    }
                    Rectangle{
                        id:mixAfRect
                        y: 13
                        width: 82
                        height: 30
                        color: "#808080"
                        anchors.verticalCenter: incRect.verticalCenter
                        anchors.left: incRect.right
                        anchors.leftMargin: 15
                        TextInput {
                            property string placeholderText: "No mixing"
                            id: mixAfIn
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
                            text: mixAfterSecs
                            validator: IntValidator{
                                bottom: 0
                                top: 99999
                            }
                            maximumLength: 5
                            echoMode: (mixAfterSecs==0 && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
                            clip: true

                            onEditingFinished: {
                                mixAfterSecs = parseInt(mixAfIn.text)
                            }

                            Text {
                                id: phMixTxt
                                anchors.fill: parent
                                text: mixAfIn.placeholderText
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#aaa"
                                font: mixAfIn.font
                                visible: mixAfterSecs==0 && !mixAfIn.activeFocus
                            }
                        }
                    }

                    Rectangle{
                        id:mixVolRect
                        y: 13
                        width: 92
                        height: 30
                        color: "#808080"
                        anchors.verticalCenter: mixBtn.verticalCenter
                        anchors.left: mixCycles.right
                        anchors.leftMargin: 20
                        TextInput {
                            property string placeholderText: "volume (mL)"
                            id: mixVolIn
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
                            text: mixVol
                            validator: DoubleValidator{
                                bottom: 0
                                top: 10
                            }
                            maximumLength: 5
                            echoMode: (mixVol==0 && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
                            clip: true

                            onTextEdited: {
                                if(parseFloat(mixVolIn.text)>10){
                                    mixVolIn.text = 0
                                }
                            }

                            onEditingFinished: {
                                if (mixVolIn.text == ''){
                                    mixVol = 0
                                    mixVolIn.text = 0
                                } else if (Math.abs(mixVol)>10){
                                    mixVol = 0
                                    mixVolIn.text = 0
                                } else {
                                    mixVol = parseFloat(mixVolIn.text)
                                }
                            }

                            Text {
                                id: phMixVolTxt
                                anchors.fill: parent
                                text: mixVolIn.placeholderText
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#aaa"
                                font: mixAfIn.font
                                visible: mixVol==0 && !mixVolIn.activeFocus
                            }
                        }
                    }

                    Rectangle{
                        id:loadVolRect
                        y: 188
                        width: 92
                        height: 30
                        color: "#808080"
                        anchors.left: pSpeed.right
                        anchors.leftMargin: 20
                        anchors.verticalCenter: pSpeed.verticalCenter
                        TextInput {
                            property string placeholderText: "volume (uL)"
                            id: loadVolIn
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
                            text: loadVol
                            validator: IntValidator{
                                bottom: 0
                                top: 3000
                            }
                            maximumLength: 4
                            echoMode: (loadVol==0 && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
                            clip: true

                            onTextEdited: {
                                if(parseInt(loadVolIn.text)>3000){
                                    loadVolIn.text = 0
                                }
                            }

                            onEditingFinished: {
                                if (loadVolIn.text == ''){
                                    loadVol = 0
                                    loadVolIn.text = 0
                                } else if (Math.abs(loadVol)>3000){
                                    loadVol = 0
                                    loadVolIn.text = 0
                                } else {
                                    loadVol = parseInt(loadVolIn.text)
                                }
                            }

                            Text {
                                id: phLoadVolTxt
                                anchors.fill: parent
                                text: loadVolIn.placeholderText
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#aaa"
                                font: loadVolIn.font
                                visible: loadVol==0 && !loadVolIn.activeFocus
                            }
                        }
                    }

                    Switch {
                        id: scriptSwitch
                        width: 167
                        height: 35
                        text: scriptSwitch.checked ? "Scripting ON" : "Scripting OFF"
                        anchors.left: scriptRec.left
                        anchors.leftMargin: -25
                        anchors.top: parent.top
                        anchors.topMargin: 0
                        checked: true
                        font.bold: true
                        font.pointSize: 12

                        contentItem: Text {
                                text: scriptSwitch.text
                                font: scriptSwitch.font
                                opacity: enabled ? 1.0 : 0.3
                                color: scriptSwitch.checked ? "#17a81a" : "darkred"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: scriptSwitch.indicator.width + scriptSwitch.spacing
                            }

                    }

                    Rectangle{
                        id: scriptRec
                        color: 'white'
                        anchors.top: parent.top
                        anchors.topMargin: 40
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 10
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                        anchors.left: loadBtn.right
                        anchors.leftMargin: 10
                        enabled: scriptSwitch.checked
                        ScrollView{
                            id:scriptScroller
                            anchors.fill: parent
                            clip: true
//                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
//                            ScrollBar.vertical.policy: ScrollBar.AlwaysOn
                            //                ScrollBar.horizontal.interactive: true
                            //                ScrollBar.vertical.interactive: true
                            enabled: scriptSwitch.checked

                            TextEdit {
                                id: scriptEditor
                                height: scriptRec.height
                                width: scriptRec.width
                                readOnly: false
                                selectByMouse: true
                                selectByKeyboard: true
                                text: scriptText
                                anchors.topMargin: 5
                                anchors.bottomMargin: 5
                                anchors.rightMargin: 10
                                anchors.leftMargin: 5
                                font.pointSize: 11
                                wrapMode:{
                                    if(scriptEditor.text.length > 40){
//                                        console.log('Wrapping!', scriptEditor.text.length)
                                        return(Text.WordWrap)
                                    } else {
//                                        console.log('no wrap')
                                        return(Text.NoWrap)
                                    }
                                }

                                opacity: scriptSwitch.checked ? 1 : 0.3
                                anchors.fill: parent
                                enabled: scriptSwitch.checked

                                onEditingFinished: {
                                    scriptText = scriptEditor.text
                                }
                            }
                        }
                    }





                }
            }

            PageIndicator {
                id: indicator
                anchors.left: parent.left
                anchors.leftMargin: 10
                count: view.count
                currentIndex: view.currentIndex
                anchors.bottom: view.bottom
            }
        }

        TabBar {
            id: casBar
            y: -5
            width: 300
            height: 40
            TabButton {
                id: casA
                text: "A"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }

            TabButton {
                id: casB
                text: "B"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }

            TabButton {
                id: casC
                text: "C"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }

            TabButton {
                id: casD
                text: "D"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }

            TabButton {
                id: casE
                text: "E"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }

            TabButton {
                id: casF
                text: "F"
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
            }
            anchors.verticalCenter: casSelectLab.verticalCenter
            anchors.left: casSelectLab.right
            font.pointSize: 10
            anchors.leftMargin: 20
        }

        Text {
            id: casSelectLab
            x: -9
            y: -8
            width: 152
            height: 23
            color: "#ffffff"
            text: qsTr("Select Cassette:")
            anchors.top: menuRect.bottom
            font.bold: true
            anchors.topMargin: 15
            anchors.left: parent.left
            font.pointSize: 14
            anchors.leftMargin: 10
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
