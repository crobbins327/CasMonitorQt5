import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3
import Qt.labs.folderlistmodel 2.12
import QtQuick.Layouts 1.12

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

    //parameters
    property double mixSpd
    property double incSpd
    property double removeSpd
    property double wasteSpd
    property double fillLnSpd
    property double fillSyrSpd
    property double washSyrSpd
    property double lineVol
    property double removeVol
    property double purgeVol
    property double denseVol
    property double denseSpd
    property double settleTime

    signal reRecParam(var paramDict)


    Component.onCompleted: {
        WAMPHandler.recParam.connect(reRecParam)
        WAMPHandler.guiParam()
    }
    Connections {
        target: root
        function onReRecParam(paramDict){
//            console.log(paramDict['mixSpeed'],
//                        paramDict['incSpeed'],
//                        paramDict['removeSpeed'],
//                        paramDict['wasteSpeed'],
//                        paramDict['fillLineSpeed'],
//                        paramDict['fillSyrSpeed'],
//                        paramDict['washSyrSpeed'],
//                        paramDict['LINEVOL'],
//                        paramDict['removeVol'],
//                        paramDict['purgeVol'],
//                        paramDict['densVol'],
//                        paramDict['densSpeed'],
//                        paramDict['settleTime'])

            mixSpd = paramDict['mixSpeed']
            incSpd = paramDict['incSpeed']
            removeSpd = paramDict['removeSpeed']
            wasteSpd = paramDict['wasteSpeed']
            fillLnSpd = paramDict['fillLineSpeed']
            fillSyrSpd = paramDict['fillSyrSpeed']
            washSyrSpd = paramDict['washSyrSpeed']

            lineVol = paramDict['LINEVOL']
            removeVol = paramDict['removeVol']
            purgeVol = paramDict['purgeVol']

            denseVol = paramDict['densVol']
            denseSpd = paramDict['densSpeed']
            settleTime = paramDict['settleTime']
        }

    }

//    width: 780
//    height: 1700
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

                onClicked: {mainStack.pop(null)}
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

                onClicked: {
                    settingsMenu.open()
                }

                Menu {
                        id: settingsMenu
                        y: settingsB.height+3

                        MenuItem {
                            text: "Goto Protocol Editor"
                            onClicked: {
                                mainStack.push("ProtocolEditor.qml", {casNumber: 0})
                            }
                        }
                        MenuItem {
                            text: "Set Default Protocol"
                            onClicked: {
                                defProtSelector.open()
                            }
                        }
                        MenuItem {
                            text: otherMode + " mode"
                            onClicked: {
                                if(otherMode=='FullScreen'){
                                    visMode = 'FullScreen'
                                    otherMode = 'Windowed'
                                } else {
                                    visMode = 'Windowed'
                                    otherMode = 'FullScreen'
                                }
                            }
                        }
                        MenuItem {
                            text: "Exit"
                            onClicked: {
                                exitDialog.open()
                            }
                        }
                    }

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
            anchors.top: menuRect.bottom
            anchors.topMargin: 0

            BevButton {
                id: execBtn
                y: -117
                height: 35
                text: "Execute Code"
                anchors.verticalCenter: scriptSwitch.verticalCenter
                anchors.left: scriptSwitch.right
                anchors.leftMargin: 15
                anchors.right: casLogBtn.left
                anchors.rightMargin: 15
                palette {
                    button: 'white'
                }

                enabled: scriptSwitch.checked

                onClicked: {
                    //Send the protocol in the exec terminal into the WAMPHandler
                    WAMPHandler.execScript(scriptText)
                    //Clear script text
                    scriptText = ''
                }
            }

            ScrollView {
                id: view
                width: 340
                //                width: 400
                anchors.leftMargin: 5
                anchors.topMargin: 15
                anchors.bottomMargin: 10
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: casBar.bottom
                contentHeight: flickCol.implicitHeight
                contentWidth: flickCol.implicitWidth
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AlwaysOn

                ColumnLayout{
                    id:flickCol
                    spacing: 20
                    anchors.fill: parent
                    Rectangle{
                        id:manualPg
                        width: view.width
                        height: 650
                        color:'transparent'

                        BevButton {
                            id: homeSyrB
                            width: 75
                            height: 35
                            text: qsTr("Home")
                            anchors.top: setupLab.bottom
                            anchors.topMargin: 15
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var homeStr = 'machine.reset()\nmachine.home()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + homeStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(homeStr)
                                }
                            }
                        }

                        BevButton {
                            id: connectB
                            y: 119
                            width: 85
                            height: 35
                            text: qsTr("Connect")
                            anchors.verticalCenterOffset: 0
                            anchors.left: homeSyrB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: homeSyrB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var connectStr = 'machine.acquire()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + connectStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(connectStr)
                                }
                            }
                        }

                        BevButton {
                            id: engageSaB
                            height: 35
                            text: qsTr("Engage Sample")
                            anchors.top: homeSyrB.bottom
                            anchors.topMargin: 25
                            anchors.left: homeSyrB.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var engageStr = 'machine.engage_sample'+casL+'()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + engageStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(engageStr)
                                }
                            }
                        }

                        BevButton {
                            id: disengageSaB
                            y: 119
                            height: 35
                            text: qsTr("Disengage Sample")
                            anchors.verticalCenterOffset: 0
                            anchors.left: engageSaB.right
                            anchors.leftMargin: 25
                            anchors.verticalCenter: engageSaB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var disengageStr = 'machine.disengage_sample'+casL+'()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + disengageStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(disengageStr)
                                }
                            }
                        }

                        BevButton {
                            id: meohB
                            y: 188
                            width: 75
                            height: 35
                            text: qsTr("MeOH")
                            anchors.left: formalinB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: formalinB.verticalCenter
                            anchors.bottomMargin: 50
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var meohStr = 'machine.goto_meoh()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + meohStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(meohStr)
                                }
                            }
                        }

                        BevButton {
                            id: babbB
                            width: 75
                            height: 35
                            text: qsTr("BABB")
                            anchors.top: wasteB.bottom
                            anchors.topMargin: 25
                            anchors.left: wasteB.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var babbStr = 'machine.goto_babb()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + babbStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(babbStr)
                                }
                            }
                        }

                        BevButton {
                            id: formalinB
                            y: 188
                            width: 85
                            height: 35
                            text: qsTr("Formalin")
                            anchors.left: wasteB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: wasteB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var formalinStr = 'machine.goto_formalin()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + formalinStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(formalinStr)
                                }
                            }
                        }

                        BevButton {
                            id: wasteB
                            width: 75
                            height: 35
                            text: qsTr("Waste")
                            anchors.top: gotoLab.bottom
                            anchors.topMargin: 15
                            anchors.left: homeSyrB.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var wasteStr = 'machine.goto_waste()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + wasteStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(wasteStr)
                                }
                            }
                        }

                        BevButton {
                            id: sampleB
                            y: 188
                            width: 75
                            height: 35
                            text: qsTr("Sample")
                            anchors.left: babbB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: babbB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var sampleStr = 'machine.goto_sample'+casL+'()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + sampleStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(sampleStr)
                                }
                            }
                        }

                        BevButton {
                            id: stainB
                            y: 188
                            width: 75
                            height: 35
                            text: qsTr("Stain")
                            anchors.verticalCenterOffset: 0
                            anchors.left: sampleB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: sampleB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var stainStr = 'machine.goto_vial()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + stainStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(stainStr)
                                }
                            }
                        }

                        BevButton {
                            id: pumpInB
                            height: 35
                            text: qsTr("Pump in")
                            anchors.top: pumpLab.bottom
                            anchors.topMargin: 15
                            anchors.left: pumpLab.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var volVal = volInput.text
                                var pumpInStr = 'machine.pump_in('+volVal+', speed=1)'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + pumpInStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(pumpInStr)
                                }
                            }
                        }

                        BevButton {
                            id: pumpOutB
                            y: 293
                            height: 35
                            text: qsTr("Pump Out")
                            anchors.left: pumpInB.right
                            anchors.leftMargin: 45
                            anchors.verticalCenter: pumpInB.verticalCenter
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var volVal = volInput.text
                                var pumpOutStr = 'machine.pump_out('+volVal+', speed=1)'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + pumpOutStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(pumpOutStr)
                                }
                            }
                        }

                        BevButton {
                            id: parkB
                            height: 35
                            text: qsTr("Park")
                            anchors.top: babbB.bottom
                            anchors.topMargin: 25
                            anchors.left: babbB.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var parkStr = 'machine.goto_park()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + parkStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(parkStr)
                                }
                            }
                        }

                        BevButton {
                            id: purgeB
                            width: 140
                            height: 35
                            text: qsTr("Purge Syringe")
                            anchors.top: rectInput.bottom
                            anchors.topMargin: 25
                            anchors.left: volSlider.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var purgeStr = 'machine.empty_syringe(purgeVol=5, speed=4)'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + purgeStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(purgeStr)
                                }
                            }
                        }

                        BevButton {
                            id: haltB
                            y: 98
                            width: 75
                            height: 35
                            text: qsTr("Halt")
                            anchors.left: connectB.right
                            anchors.leftMargin: 30
                            anchors.verticalCenter: connectB.verticalCenter

                            palette {
                                button: 'red'
                                buttonText: 'white'
                            }

                            onClicked: {
                                var haltStr = 'self.halt()'

                                if(scriptSwitch.checked){
                                    scriptText = scriptText + '\n' + haltStr
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(haltStr)
                                }
                            }

                        }


                        Slider {
                            id: volSlider
                            width: 245
                            height: 30
                            anchors.top: pumpInB.bottom
                            anchors.topMargin: 25
                            anchors.left: pumpInB.left
                            anchors.leftMargin: 0
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
                            width: 66
                            height: 18
                            color: "#ffffff"
                            text: qsTr("Volume:")
                            anchors.top: volSlider.bottom
                            anchors.topMargin: 25
                            font.bold: true
                            font.pointSize: 11
                            anchors.left: volSlider.left
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
                                }

                            }
                        }

                        Text {
                            id: volUniLab
                            width: 32
                            height: 22
                            color: "#ffffff"
                            text: qsTr("mL")
                            anchors.left: rectInput.right
                            anchors.leftMargin: 5
                            font.pointSize: 11
                            anchors.verticalCenter: rectInput.verticalCenter
                            font.bold: true
                        }

                        Text {
                            id: gotoLab
                            x: 535
                            y: -8
                            width: 162
                            height: 21
                            color: "#ffffff"
                            text: qsTr("Move Syringe:")
                            font.pointSize: 12
                            anchors.leftMargin: 15
                            anchors.top: engageSaB.bottom
                            anchors.left: parent.left
                            font.bold: true
                            anchors.topMargin: 15
                        }

                        Text {
                            id: setupLab
                            x: 547
                            y: 7
                            width: 152
                            height: 23
                            color: "#ffffff"
                            text: qsTr("Setup:")
                            font.pointSize: 12
                            anchors.leftMargin: 15
                            anchors.top: manualLab.bottom
                            anchors.left: parent.left
                            font.bold: true
                            anchors.topMargin: 10
                        }

                        Text {
                            id: pumpLab
                            x: 535
                            y: 349
                            width: 108
                            height: 21
                            color: "#ffffff"
                            text: qsTr("Pump:")
                            anchors.leftMargin: 15
                            font.pointSize: 12
                            anchors.left: parent.left
                            anchors.top: parkB.bottom
                            font.bold: true
                            anchors.topMargin: 15
                        }

                    }



                    Rectangle{
                        id: operationPg
                        color:'transparent'
                        width: view.width
                        height: 360

                        Text {
                            id: operationsLab
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

                        BevButton {
                            id: purgeBtn
                            width: 95
                            height: 35
                            text: "Purge"
                            anchors.verticalCenter: cleanBtn.verticalCenter
                            anchors.left: loadBtn.left
                            anchors.leftMargin: 0
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var purge = 'self.purge(casL="'+ casL + '", deadvol='+lineVol+')'

                                if(scriptSwitch.checked){
                                    //add to scriptText
                                    scriptText = scriptText + '\n' + purge
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(purge)
                                }
                            }
                        }

                        BevButton {
                            id: cleanBtn
                            width: 95
                            height: 35
                            text: "Clean Line"
                            anchors.right: purgeBtn.left
                            anchors.rightMargin: 35
                            anchors.top: washSyrBox.bottom
                            anchors.topMargin: 15
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var clean = 'self.clean(casL="'+ casL +'")'

                                if(scriptSwitch.checked){
                                    //add to scriptText
                                    scriptText = scriptText + '\n' + clean
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(clean)
                                }
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
                                var casL = casNames[casBar.currentIndex]
                                var incubate = 'self.incubate(casL="'+ casL + '", incTime='+ incSecs +', mixAfter='+ mixAfterSecs +')'

                                if(scriptSwitch.checked){
                                    //add to scriptText
                                    scriptText = scriptText + '\n' + incubate
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(incubate)
                                }
                            }
                        }
                        BevButton {
                            id: loadBtn
                            width: 115
                            height: 35
                            text: "Load Reagent"
                            anchors.top: mixBtn.bottom
                            anchors.topMargin: 25
                            anchors.left: reagentSel.right
                            anchors.leftMargin: 64
                            palette {
                                button: 'white'
                            }
                            //loadReagent(self, casL, loadstr, reagent, vol, speed, deadvol):
                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var reagentstr = reagentSel.currentValue
                                var washBool = washSyrBox.checked ? 'True': 'False'
                                var loadRea = 'self.loadReagent(casL="'+ casL + '", reagent="' + reagentstr + '", vol='+ loadVol/1000 +', speed='+ pSpeedV +', washSyr='+washBool+')'

                                if(scriptSwitch.checked){
                                    //add to scriptText
                                    scriptText = scriptText + '\n' + loadRea
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(loadRea)
                                }
                            }
                        }
                        BevButton {
                            id: mixBtn
                            width: 95
                            height: 35
                            text: "Mix"
                            anchors.right: incubateBtn.right
                            anchors.rightMargin: 0
                            anchors.top: incubateBtn.bottom
                            anchors.topMargin: 25
                            anchors.left: mixVolRect.right
                            anchors.leftMargin: 12
                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                var casL = casNames[casBar.currentIndex]
                                var mix = 'self.mix(casL="'+ casL + '", numCycles='+ numCycles +', volume='+ mixVol +')'

                                if(scriptSwitch.checked){
                                    //add to scriptText
                                    scriptText = scriptText + '\n' + mix
                                } else {
                                    //else execute directly
                                    WAMPHandler.execScript(mix)
                                }

                            }
                        }

                        ComboBox {
                            id: reagentSel
                            width: 130
                            height: 30
                            anchors.verticalCenter: loadBtn.verticalCenter
                            anchors.left: mixCycles.left
                            anchors.leftMargin: 0
                            currentIndex: 0
                            model: ["meoh", "formalin", "babb", "vial"]
                        }


                        ComboBox {
                            id: mixCycles
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
                            width: 85
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

                        IntInput{
                            id:mixAfRect
                            width: 85
                            height: 30
                            color: "#808080"
                            anchors.verticalCenter: incRect.verticalCenter
                            anchors.left: incRect.right
                            anchors.leftMargin: 15

                            maxLength: 5
                            maxVal: 99999
                            intVal: mixAfterSecs
                            placeholderText: "No mixing"
                            onSetVal: {mixAfterSecs = mixAfRect.intVal}
                        }

                        DoubleInput{
                            id:mixVolRect
                            width: 100
                            height: 30
                            color: "#808080"
                            anchors.verticalCenter: mixBtn.verticalCenter
                            anchors.left: mixCycles.right
                            anchors.leftMargin: 15

                            maxLength: 5
                            maxVal: 10
                            doubleVal: 0
                            placeholderText: "volume (mL)"
                            onSetVal: {mixVol = mixVolRect.doubleVal}
                        }

                        IntInput{
                            id:loadVolRect
                            width: 100
                            height: 30
                            color: "#808080"
                            anchors.left: pSpeed.right
                            anchors.leftMargin: 80
                            anchors.verticalCenter: pSpeed.verticalCenter

                            maxLength: 4
                            maxVal: 3000
                            intVal: loadVol
                            placeholderText: "volume (uL)"
                            onSetVal: {loadVol = loadVolRect.intVal}

                        }

                        CheckBox {
                            id: washSyrBox
                            width: 189
                            height: 30
                            text: qsTr("Wash Syringe & Line")
                            anchors.top: pSpeed.bottom
                            anchors.topMargin: 15
                            font.pointSize: 11
                            anchors.left: pSpeed.left
                            anchors.leftMargin: 0
                            contentItem: Text {
                                    text: washSyrBox.text
                                    font: washSyrBox.font
                                    color: 'white'
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: washSyrBox.indicator.width + washSyrBox.spacing
                                }
                        }

                        Text {
                            id: speedLab
                            width: 49
                            height: 18
                            color: "#ffffff"
                            text: qsTr("speed")
                            anchors.verticalCenterOffset: 2
                            anchors.verticalCenter: pSpeed.verticalCenter
                            font.pointSize: 11
                            font.bold: false
                            anchors.leftMargin: 7
                            anchors.left: pSpeed.right
                        }
                    }

                    Rectangle{
                        id: paramPg
                        color:'transparent'
                        width: view.width
                        height: 500

                        Text {
                            id: paramLab
                            width: 118
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Parameters:")
                            anchors.top: parent.top
                            font.bold: true
                            anchors.topMargin: 0
                            anchors.left: parent.left
                            font.pointSize: 14
                            anchors.leftMargin: 10
                        }

                        Text {
                            id: mixSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Mix Speed:")
                            font.bold: true
                            anchors.topMargin: 10
                            font.pointSize: 11
                            anchors.top: paramLab.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: mixSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: mixSpLb.verticalCenter
                            anchors.left: mixSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: mixSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {mixSpd = mixSpdIn.doubleVal}
                        }

                        Text {
                            id: incSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Incubate Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: mixSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: incSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: incSpLb.verticalCenter
                            anchors.left: incSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: incSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {incSpd = incSpdIn.doubleVal}
                        }

                        Text {
                            id: remSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Remove Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: incSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: remSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: remSpLb.verticalCenter
                            anchors.left: remSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: removeSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {removeSpd = remSpdIn.doubleVal}
                        }

                        Text {
                            id: wasteSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Waste Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: remSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: wasteSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: wasteSpLb.verticalCenter
                            anchors.left: wasteSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: wasteSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {wasteSpd = wasteSpdIn.doubleVal}
                        }

                        Text {
                            id: fillLineSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Fill Line Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: wasteSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: fillLnSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: fillLineSpLb.verticalCenter
                            anchors.left: fillLineSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: fillLnSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {fillLnSpd = fillLnSpdIn.doubleVal}
                        }

                        Text {
                            id: fillSyrSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Fill Syringe Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: fillLineSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: fillSyrSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: fillSyrSpLb.verticalCenter
                            anchors.left: fillSyrSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: fillSyrSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {fillSyrSpd = fillSyrSpdIn.doubleVal}
                        }

                        Text {
                            id: washSyrSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Wash Syringe Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: fillSyrSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: washSyrSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: washSyrSpLb.verticalCenter
                            anchors.left: washSyrSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: washSyrSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {washSyrSpd = washSyrSpdIn.doubleVal}
                        }

                        Text {
                            id: densSpLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Density Adj Speed:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: washSyrSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: densSpdIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: densSpLb.verticalCenter
                            anchors.left: densSpLb.right
                            anchors.leftMargin: 20

                            doubleVal: denseSpd
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "speed"
                            onSetVal: {denseSpd = densSpdIn.doubleVal}
                        }

                        Text {
                            id: densVolLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Density Adj Vol:")
                            font.bold: true
                            anchors.topMargin: 12
                            font.pointSize: 11
                            anchors.top: densSpLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: densVolIn
                            width: 70
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: densVolLb.verticalCenter
                            anchors.left: densVolLb.right
                            anchors.leftMargin: 20

                            doubleVal: denseVol
                            maxLength: 4
                            maxVal: 5
                            placeholderText: "vol (mL)"
                            onSetVal: {denseVol = densVolIn.doubleVal}
                        }

                        Text {
                            id: lineVolLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Line Volume:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: densVolLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: lineVolIn
                            width: 70
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: lineVolLb.verticalCenter
                            anchors.left: lineVolLb.right
                            anchors.leftMargin: 20

                            doubleVal: lineVol
                            maxLength: 4
                            maxVal: 5
                            placeholderText: "vol (mL)"
                            onSetVal: {lineVol = lineVolIn.doubleVal}
                        }

                        Text {
                            id: remVolLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Remove Volume:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: lineVolLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: remVolIn
                            width: 70
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: remVolLb.verticalCenter
                            anchors.left: remVolLb.right
                            anchors.leftMargin: 20

                            doubleVal: removeVol
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "vol (mL)"
                            onSetVal: {removeVol = remVolIn.doubleVal}
                        }

                        Text {
                            id: purgeVolLb
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Purge Volume:")
                            font.bold: true
                            anchors.topMargin: 5
                            font.pointSize: 11
                            anchors.top: remVolLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        DoubleInput{
                            id: purgeVolIn
                            width: 70
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: purgeVolLb.verticalCenter
                            anchors.left: purgeVolLb.right
                            anchors.leftMargin: 20

                            doubleVal: purgeVol
                            maxLength: 4
                            maxVal: 10
                            placeholderText: "vol (mL)"
                            onSetVal: {purgeVol = purgeVolIn.doubleVal}
                        }

                        Text {
                            id: settleTLb
                            x: 8
                            y: 9
                            width: 165
                            height: 25
                            color: "#ffffff"
                            text: qsTr("Settle Time:")
                            font.bold: true
                            anchors.topMargin: 12
                            font.pointSize: 11
                            anchors.top: purgeVolLb.bottom
                            anchors.left: parent.left
                            anchors.leftMargin: 15
                        }

                        IntInput{
                            id: settleTIn
                            width: 55
                            height: 25
                            color: "#808080"
                            anchors.verticalCenter: settleTLb.verticalCenter
                            anchors.left: settleTLb.right
                            anchors.leftMargin: 20

                            intVal: settleTime
                            maxLength: 4
                            maxVal: 9999
                            placeholderText: "secs"
                            onSetVal: {settleTime = settleTIn.intVal}

                        }

                        BevButton {
                            id: paramBtn
                            height: 35
                            width: 165
                            text: "Update Parameters"
                            anchors.top: settleTIn.bottom
                            anchors.topMargin: 12
                            anchors.left: parent.left
                            anchors.leftMargin: 15

                            palette {
                                button: 'white'
                            }

                            onClicked: {
                                //send to controller
                                var paramDict = {'mixSpeed': mixSpd,
                                             'incSpeed': incSpd,
                                             'removeSpeed': removeSpd,
                                             'wasteSpeed': wasteSpd,
                                             'fillLineSpeed': fillLnSpd,
                                             'fillSyrSpeed': fillSyrSpd,
                                             'washSyrSpeed': washSyrSpd,
                                             'densSpeed': denseSpd,
                                             'densVol': denseVol,
                                             'LINEVOL': lineVol,
                                             'removeVol': removeVol,
                                             'purgeVol': purgeVol,
                                             'settleTime': settleTime}
                                WAMPHandler.updateParam(paramDict)

                            }
                        }

                    }
                }
            }

            Switch {
                id: scriptSwitch
                width: 175
                height: 35
                text: scriptSwitch.checked ? "Scripting ON" : "Scripting OFF"
                anchors.left: view.right
                anchors.leftMargin: 0
                anchors.top: casBar.bottom
                anchors.topMargin: 20
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
                anchors.left: view.right
                anchors.leftMargin: 20
                anchors.top: scriptSwitch.bottom
                anchors.topMargin: 5
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 10
                anchors.right: parent.right
                anchors.rightMargin: 10
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

                    TextArea {
                        id: scriptEditor
                        //height: scriptRec.height
                        //width: scriptRec.width
                        readOnly: false
                        selectByMouse: true
                        selectByKeyboard: true
                        focus: true
                        placeholderText: 'Execute functions from controlNQ.py or machine.py!'
                        //placeholderText: scriptEditor.text == '' ? 'Execute functions from controlNQ.py or machine.py using script editor!' : ''
                        text: scriptText
                        //anchors.fill: parent
                        anchors.topMargin: 5
                        anchors.bottomMargin: 5
                        anchors.rightMargin: 10
                        anchors.leftMargin: 5
                        font.pointSize: 11
                        wrapMode: Text.Wrap

                        opacity: scriptSwitch.checked ? 1 : 0.3
                        enabled: scriptSwitch.checked

                        background: Rectangle{
                            implicitWidth: scriptRec.width
                            implicitHeight: scriptRec.height
                        }

                        onEditingFinished: {
                            scriptText = scriptEditor.text
                        }

                    }
                }
            }

            BevButton {
                id: casLogBtn
                x: 0
                y: 0
                width: 95
                height: 35
                text: "Get Log"
                anchors.verticalCenter: scriptSwitch.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 10
                palette {
                    button: 'white'
                }

                onClicked: {}
            }

            BevButton {
                id: stopExecB
                x: 584
                y: 7
                width: 175
                height: 40
                text: qsTr("Stop Task!")
                anchors.left: execBtn.horizontalCenter
                anchors.leftMargin: 0
                anchors.right: casLogBtn.horizontalCenter
                anchors.rightMargin: 0
                anchors.verticalCenterOffset: 0
                anchors.verticalCenter: casBar.verticalCenter

                palette {
                    button: 'red'
                    buttonText: 'white'
                }
                onClicked: {
                    //Stop execution of code by sending signal to the WAMPHandler
                    WAMPHandler.stopExecTerminal()
                }


            }

            Text {
                id: casSelectLab
                x: 12
                y: 15
                width: 152
                height: 23
                color: "#ffffff"
                text: qsTr("Select Cassette:")
                anchors.top: parent.top
                font.bold: true
                anchors.topMargin: 15
                anchors.left: parent.left
                font.pointSize: 14
                anchors.leftMargin: 10
            }

            TabBar {
                id: casBar
                x: 204
                y: 7
                anchors.verticalCenter: casSelectLab.verticalCenter
                anchors.left: casSelectLab.right
                font.pointSize: 10
                anchors.leftMargin: 40
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
            }

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
    D{i:20;anchors_y:119}D{i:23;anchors_y:188}D{i:30;anchors_y:203}D{i:31;anchors_y:295}
D{i:45;anchors_width:95}D{i:47;anchors_width:95}D{i:44;anchors_width:95}D{i:68;anchors_width:420;anchors_y:29}
D{i:69;anchors_x:151}D{i:70;anchors_y:82}D{i:72;anchors_x:209;anchors_y:188}D{i:73;anchors_width:75;anchors_x:238}
D{i:74;anchors_x:91;anchors_y:195}D{i:77;anchors_width:420;anchors_y:29}D{i:78;anchors_x:151}
D{i:79;anchors_y:82}D{i:81;anchors_y:111}D{i:82;anchors_width:75;anchors_x:238}D{i:83;anchors_y:157}
D{i:84;anchors_width:420;anchors_y:29}D{i:86;anchors_width:420;anchors_y:29}D{i:89;anchors_width:420}
D{i:91;anchors_width:420}D{i:93;anchors_width:420;anchors_y:29}D{i:94;anchors_width:420;anchors_y:457}
D{i:95;anchors_width:420;anchors_x:238;anchors_y:29}D{i:97;anchors_width:75;anchors_x:238}
D{i:96;anchors_width:75;anchors_x:238;anchors_y:29}D{i:101;anchors_width:75;anchors_x:238}
D{i:100;anchors_width:420;anchors_x:238}D{i:99;anchors_width:75;anchors_x:238}D{i:98;anchors_width:420;anchors_x:238}
D{i:102;anchors_width:420;anchors_x:238}D{i:103;anchors_width:420}D{i:104;anchors_width:75;anchors_x:238}
D{i:106;anchors_width:75;anchors_x:238}D{i:107;anchors_width:75;anchors_x:238}D{i:108;anchors_width:75;anchors_x:238}
D{i:109;anchors_width:75;anchors_x:238}D{i:110;anchors_width:75;anchors_x:238}D{i:105;anchors_width:75;anchors_x:238}
D{i:14;anchors_width:140;anchors_x:"-165"}
}
##^##*/
