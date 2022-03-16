import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import "./Icons/"
import QtQuick.Controls.Material 2.12

Item{
    signal open()
    signal close()

    id:logDisplay
    anchors.fill: parent
    width: 510
    height: 350

//    Component.onCompleted: {
//        console.log('starting refresh temp timer')
//        refreshTime.start()
//    }
//    Component.onDestruction: {
//        console.log('stoping refresh temp timer')
//        refreshTime.stop()
//    }

    Rectangle{
        id:rootRect

        Material.theme: Material.Dark
        Material.accent: Material.Blue
        color: Material.background

        anchors.fill: parent
        BevelRect {
            id: labRect
            color: "#242424"
            height: 40
            radius: 20
            width: parent.width
            RowLayout{
                id: labRow
                anchors.top: parent.top
                anchors.topMargin: 3
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 3
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.left: parent.left
                anchors.leftMargin: 20
                spacing: 20

                Text {
                    id: casTempMainLabel
                    color: "#ffffff"
                    text: "Cassette Temperatures"
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                    font.pointSize: 14
                    Layout.fillWidth: false
                }
            }
        }

        Rectangle{
            id: tempSampleRect
//            color: 'white'
            Material.theme: Material.Dark
            Material.accent: Material.Blue
            color: Material.background
            height: 220

            anchors.top: labRect.bottom
            anchors.right: parent.right
//            anchors.bottom: parent.bottom
            anchors.left: parent.left
//            anchors.bottomMargin: 30
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.topMargin: 15

            ScrollView {
                id: casTempScroll
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: swipeGrid.width < tempSampleRect.width ? parent.horizontalCenter : undefined
                anchors.left: swipeGrid.width < tempSampleRect.width ? undefined : parent.left
                width: swipeGrid.width < tempSampleRect.width ? swipeGrid.width : tempSampleRect.width
    //            anchors.right: swipeRow.width < rootBG.width ? undefined : parent.right
                anchors.topMargin: 0
                anchors.leftMargin: 5
                anchors.rightMargin: 5
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded
                ScrollBar.vertical.policy: ScrollBar.AlwaysOff

                Grid {
                    id: swipeGrid
                    columns: rootApWin.availableCasNum <= 6 ? 3 : Math.round(rootApWin.availableCasNum/2)
//                    columns: 3
                    rows:  2
                    spacing: 5
//                    spacing: casTempRepeater.count == 4 ? 3 : 20
                    width: childrenRect.width

                    Repeater {
                        id: casTempRepeater
                        model: rootApWin.availableCasNum
                        //model: 20
                        delegate: Item {
                            width: casTempContent.width
                            height: casTempScroll.height/2

                            TempContent {
                                id: casTempContent
                                casNumber: index+1
                                height: parent.height
                                width: 160
                            }
                        }
                    }
                }
            }

            Button{
                id: refreshB
                width: 80
                height: 45
                anchors.top: casTempScroll.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 7
                //      text: qsTr("Refresh")

                icon.source: "Icons/icons8-refresh-104.png"
                icon.color: "black"
                icon.height: 30

                Material.theme: Material.Light
                Material.foreground: "black"

                font.pointSize: 12
                onClicked: {
                    WAMPHandler.refreshTemps(0)
                }

            }
        }
    }
}

