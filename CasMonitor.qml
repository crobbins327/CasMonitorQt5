import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12

import "./Icons/"


ApplicationWindow {
    id: rootApWin
    property string mainDir: './Protocols/'
    property string visMode: 'Windowed'
    property string otherMode: 'FullScreen'
    property string defPath: ''
    property string defProtName: ''
    property bool isDisconnected: true
    property bool guiJoined: false
    property string waitPopupTxt: 'Connecting....'
    signal exit()
    signal reGUIJoined()
    signal reDCController()
    signal reJoinController()
    signal rePopupTxt(string msg)

    Component.onCompleted: {
        WAMPHandler.guiJoined.connect(reGUIJoined)
        WAMPHandler.controllerDCed.connect(reDCController)
        WAMPHandler.controllerJoined.connect(reJoinController)
        WAMPHandler.toWaitPopup.connect(rePopupTxt)
        waitPopup.open()
    }
    Connections {
        target: rootApWin
        function onRePopupTxt(msg){
            rootApWin.waitPopupTxt = msg

        }
        function onReGUIJoined() {
            rootApWin.waitPopupTxt = 'GUI and controller are connected!'
            rootApWin.isDisconnected = false
            rootApWin.guiJoined = true
            waitPopup.close()
        }
        function onReDCController() {
            rootApWin.isDisconnected = true
            rootApWin.waitPopupTxt = 'Controller disconnected.  Waiting on reconnection...'
            waitPopup.open()
        }
        function onReJoinController() {
            rootApWin.isDisconnected = false
            rootApWin.waitPopupTxt = 'Controller joined!'
            waitPopup.close()
        }
    }

    visible: true
    width: 800
    height: 415
    maximumWidth: 801
    maximumHeight: 481
    minimumWidth: 780
    minimumHeight: 410
    flags: rootApWin.visMode === 'Windowed' ? Qt.WindowMinimized :  Qt.FramelessWindowHint
    visibility: rootApWin.visMode === 'Windowed' ? Window.Windowed : Window.FullScreen
    title: "Prepbot Sample Monitor"
    
    onClosing: {
        close.accepted = exitDialog.closeStatus
        exitDialog.open()
    }

    Popup {
        id: waitPopup
        parent: Overlay.overlay
        x: Math.round((parent.width - waitPopup.width) / 2)
        y: Math.round((parent.height - waitPopup.height) / 2)
//        width: 150
//        height: 150
        dim: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.NoAutoClose
        modal: true
        opacity: 0.8

        background: Rectangle {
                implicitWidth: 500
                implicitHeight: 150
                color: 'silver'
//                border.color: "#444"
            }

        contentItem: ColumnLayout {
            spacing: 10
            anchors.fill: parent
            BusyIndicator {
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                running: true
            }
            Text {
                text: rootApWin.waitPopupTxt
                minimumPointSize: 12
                font.pointSize: 14
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
            }

        }

    }


    StackView {
        id: mainStack
        initialItem: casMonitor
        anchors.fill: parent
        Component.onCompleted:{
//            currentItem.setVisMode.connect(setVisMode)
            console.log('Completed!')
        }
//        Connections {
//            target:rootApWin
//            function onSetVisMode(){
//                console.log('Setting Vis Mode!')
//            }

//        }

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
//                layer.effect: menuRect

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

                    onClicked: {mainStack.push("DebugMode.qml", {visMode, otherMode})}


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
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 1
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
//                    stackIndex: 1

//                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas2
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 2
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
//                    stackIndex: 1


//                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas3
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 3
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
//                    stackIndex: 1


//                    onRunDetails: {console.log("Run details: ", casNumber)}


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
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 4
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
//                    stackIndex: 1


//                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas5
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 5
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
//                    stackIndex: 1


//                    onRunDetails: {console.log("Run details: ", casNumber)}


                }

                SampleStack {
                    id: cas6
                    height: (rootApWin.height-menuRect.height)/2.1
                    width: rootApWin.width/3.4
                    casNumber: 6
//                    runStep: "Testing!"
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
//                    stackIndex: 1


//                    onRunDetails: {console.log("Run details: ", casNumber)}


                }
            }


        }
    }

    MessageDialog {
        property bool closeStatus: false
        id: exitDialog
        standardButtons: StandardButton.Cancel | StandardButton.Yes
        icon: StandardIcon.Critical
        text: "Are you sure you want to exit? This WILL NOT stop any ongoing runs."
        title: "Exit Application"
        modality: Qt.WindowModal
        onYes: {
            closeStatus = true
            //sends another close signal, this time with closeStatus = true
            rootApWin.close()
        }
        onRejected: {
            console.log("Canceled Exit.")
            this.close
        }
    }

    FileDialog {
        id:defProtSelector
        selectExisting: true
        folder: mainDir
        nameFilters: [ "Protocol Files (*.json)", "All files (*)" ]
        //nameFilters: [ "*.json", "All files (*)" ]
        defaultSuffix: ".json"
        modality: Qt.WindowModal
        onAccepted: {
            var path = defProtSelector.fileUrl.toString();
            // remove prefixed "file:///"
            path = path.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
            // unescape html codes like '%23' for '#'
            var cleanPath = decodeURIComponent(path);

            //Get protocol name
            var protName = cleanPath.split('/').pop().split('.')[0]

            rootApWin.defPath = cleanPath
            rootApWin.defProtName = protName

        }

    }
}



