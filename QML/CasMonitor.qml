import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
import Qt.labs.platform 1.1 as Platform
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12
import QtQuick.Controls.Material 2.12

import "./Icons/"

Item {
    id: casMonitor
//    width: 776
//    height: 400
    property int numberOfCassettes: 6

    Rectangle {
        id: rootBG
        anchors.fill: parent
//        anchors.right: parent.right
//        anchors.rightMargin: 0
//        anchors.left: parent.left
//        anchors.leftMargin: 0
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: 0
//        anchors.top: parent.top
//        anchors.topMargin: 0

//        color: "dimgray"
        Material.theme: Material.Dark
        Material.accent: Material.Blue
        color: Material.background


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
                width: 60
                height: 60
                display: AbstractButton.IconOnly
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: parent.verticalCenter


//                opacity: settingsB.down || settingsB.checked || settingsB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/settings-icon.png"
                icon.color: "white"
                icon.height: 60
                icon.width: 60

//                background: Rectangle {
//                    implicitWidth: 50
//                    implicitHeight: 50
//                    border.width: settingsB.down || settingsB.checked || settingsB.highlighted ? 4 : 3
//                    border.color: "white"
//                    radius: 30
//                    color: "transparent"
//                }

                onClicked: {
                    settingsMenu.open()
                }

                Menu {
                        id: settingsMenu
//                        y: settingsB.height+3

                        MenuItem {
                            text: "Goto Protocol Editor"
                            onTriggered: {
                                mainStack.push("ProtocolEditor.qml", {casNumber: 0})
                            }
                        }
                        MenuItem {
                            text: "Set Default Protocol"
                            onTriggered: {
                                defProtSelector.open()
                            }
                        }
                        MenuItem {
                            text: otherMode + " mode"
                            onTriggered: {
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
                            onTriggered: {
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

//            Button {
//                id: debugB
//                x: 2
//                y: 7
//                width: 60
//                height: 60
//                anchors.right: settingsB.left
//                anchors.rightMargin: 30
//                anchors.verticalCenter: parent.verticalCenter
//                opacity: debugB.down || debugB.checked || debugB.highlighted ? 0.5 : 1
//                display: AbstractButton.IconOnly
//                flat: true

////                background: Rectangle {
////                    color: "#00000000"
////                    radius: 30
////                    border.width: 0
////                    implicitWidth: 50
////                    border.color: "#ffffff"
////                    implicitHeight: 50
////                }
//                Image {
//                    id: debugImage
//                    source: "Icons/debug-mode.png"
//                    anchors.horizontalCenter: debugB.horizontalCenter
//                    anchors.verticalCenter: debugB.verticalCenter
//                    width: 45
//                    height: 45
//                    fillMode: Image.PreserveAspectFit
//                }
//                ColorOverlay {
//                    anchors.fill: debugImage
//                    source: debugImage
//                    color: "#ffffff"
//                }

//                onClicked: {mainStack.push("DebugMode.qml", {visMode, otherMode})}


//            }



        }

        ScrollView
        {
            id: casScroll
            anchors.top: menuRect.bottom
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: swipeRow.width < rootBG.width ? parent.horizontalCenter : undefined
            anchors.left: swipeRow.width < rootBG.width ? undefined : parent.left
            width: swipeRow.width < rootBG.width ? swipeRow.width : rootBG.width
//            anchors.right: swipeRow.width < rootBG.width ? undefined : parent.right
            anchors.topMargin: 30
            anchors.bottomMargin: 5
            anchors.leftMargin: 5
            anchors.rightMargin: 5
            ScrollBar.horizontal.policy: ScrollBar.AsNeeded
            ScrollBar.vertical.policy: ScrollBar.AlwaysOff

            Row {
                id: swipeRow
                spacing: casRepeater.count == 4 ? 3 : 20
//                width: childrenRect.width

                Repeater {
                    id: casRepeater
                    model: casMonitor.numberOfCassettes
                    delegate: Item {
                        width: cas.width
                        height: casScroll.height-5

                        SampleStack {
                            id: cas
                            height: parent.height
                            width: {
                                if (casRepeater.count >= 4){
                                    return ((casMonitor.width-3*swipeRow.spacing - casScroll.anchors.leftMargin - casScroll.anchors.rightMargin)/4)
                                } else {
                                    return (196)
                                }
                            }
                            casNumber: index+1
                        }
                    }
                }
            }
        }

//        Row {
//            id: topRow
//            anchors.topMargin: 5
//            anchors.rightMargin: 20
//            anchors.leftMargin: 20
//            anchors.bottomMargin: -30
//            anchors.top: menuRect.bottom
//            anchors.right: parent.right
//            anchors.bottom: parent.verticalCenter
//            anchors.left: parent.left

//            spacing: (topRow.width - 3*cas1.width)/2


//            SampleStack {
//                id: cas1
//                height: (casMonitor.height-menuRect.height)/2.1
//                width: casMonitor.width/3.4
//                casNumber: 1
//                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
//            }

//            SampleStack {
//                id: cas2
//                height: (casMonitor.height-menuRect.height)/2.1
//                width: casMonitor.width/3.4
//                casNumber: 2
//                Layout.alignment: Qt.AlignLeft | Qt.AlignTop       }

//            SampleStack {
//                id: cas3
//                height: (casMonitor.height-menuRect.height)/2.1
//                visible: true
//                width: casMonitor.width/3.4
//                casNumber: 3
//                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
//            }
//        }

//        Row {
//            id: botRow
//            anchors.topMargin: 5
//            anchors.rightMargin: 20
//            anchors.leftMargin: 20
//            anchors.bottom: parent.bottom
//            anchors.left: parent.left
//            anchors.right: parent.right
//            anchors.top: topRow.bottom

//            spacing: (botRow.width - 3*cas4.width)/2

//            SampleStack {
//                id: cas4
//                height: (casMonitor.height-menuRect.height)/2.1
//                width: casMonitor.width/3.4
//                casNumber: 4
//                Layout.alignment: Qt.AlignLeft | Qt.AlignBottom

//            }

//            SampleStack {
//                id: cas5
//                height: (casMonitor.height-menuRect.height)/2.1
//                width: casMonitor.width/3.4
//                casNumber: 5
//                Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
//            }

//            SampleStack {
//                id: cas6
//                height: (casMonitor.height-menuRect.height)/2.1
//                width: casMonitor.width/3.4
//                casNumber: 6
//                Layout.alignment: Qt.AlignLeft | Qt.AlignBottom

//            }
//        }


    }

    Platform.FileDialog {
        id:defProtSelector
        fileMode: Platform.FileDialog.OpenFile
//        selectExisting: true
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

