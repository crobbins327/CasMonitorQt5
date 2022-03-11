import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
//import Qt.labs.qmlmodels 1.0
//import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
//import QtGraphicalEffects 1.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: rootApWin
    property string mainDir: '../Protocols/'
    property string visMode: 'Windowed'
    property string otherMode: 'FullScreen'
    property string defPath: ''
    property string defProtName: ''
    property bool isDisconnected: true
    property bool guiJoined: false
    property string waitPopupTxt: 'Connecting....'
    property string operatingSystem: WAMPHandler.OS
    signal exit()
    signal reGUIJoined()
    signal reDCController()
    signal reJoinController()
    signal rePopupTxt(string msg)

    Material.theme: Material.Dark
    Material.accent: Material.Blue

    Component.onCompleted: {
        WAMPHandler.guiJoined.connect(reGUIJoined)
        WAMPHandler.controllerDCed.connect(reDCController)
        WAMPHandler.controllerJoined.connect(reJoinController)
        WAMPHandler.toWaitPopup.connect(rePopupTxt)
        console.debug(operatingSystem)
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
        width: 500
        height: 200
        dim: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.NoAutoClose
        modal: true
//        opacity: 1

        Material.theme: Material.Dark
        Material.background: 'transparent'
        Material.accent: Material.Blue

//        background: Rectangle {
//                implicitWidth: 500
//                implicitHeight: 150
//                color: 'silver'
////                border.color: "#444"
//            }

        contentItem: ColumnLayout {
            spacing: 10
            anchors.fill: parent
            BusyIndicator {
                Layout.topMargin: 20
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                running: true
            }
            Label {
                text: rootApWin.waitPopupTxt
                minimumPointSize: 12
                font.pointSize: 14
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
            }

        }

    }


    StackView {
        id: mainStack
        initialItem: "CasMonitor.qml"
        anchors.fill: parent
    }

    MessageDialog {
        property bool closeStatus: false
        id: exitDialog
        standardButtons: StandardButton.Cancel | StandardButton.Yes
        icon: StandardIcon.Critical
        text: "Are you sure you want to exit? This WILL NOT shutdown the controller nor stop any ongoing runs."
        title: "Exit Application"
        modality: Qt.WindowModal
        onYes: {
            closeStatus = true
            //sends another close signal, this time with closeStatus = true
            //WAMPHandler.closeApp()
//            delay(5, function() {
//                console.log("print")
//            })
            rootApWin.close()
            Qt.quit()
        }
        onRejected: {
    //            console.log("Canceled Exit.")
            this.close
        }
    }

    function delay(delayTime, cb) {
        timer = new Timer();
        timer.interval = delayTime;
        timer.repeat = false;
        timer.triggered.connect(cb);
        timer.start();
    }
}


