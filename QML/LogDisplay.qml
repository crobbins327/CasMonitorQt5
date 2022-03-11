import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import "./Icons/"

Item{
    property string logText: '>2020-09-09 18:43:05 ctrl.casA    INFO     Starting run!!\n>2020-09-09 18:43:10 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:11 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:12 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:14 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:15 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:05 ctrl.casA    INFO     Starting run!!\n>2020-09-09 18:43:10 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:11 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:12 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:14 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:15 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:05 ctrl.casA    INFO     Starting run!!\n>2020-09-09 18:43:10 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:11 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:12 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:14 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:15 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:05 ctrl.casA    INFO     Starting run!!\n>2020-09-09 18:43:10 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:11 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:12 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:14 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:15 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:05 ctrl.casA    INFO     Starting run!!\n>2020-09-09 18:43:10 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:11 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:12 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:13 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:14 ctrl.casA    INFO     doing stuff\n>2020-09-09 18:43:15 ctrl.casA    INFO     doing stuff\n'
    property string colorBG: 'silver'
    property string casNumber: '0'
    property string sampleName: 'SampleName'
    property string protocolName: 'ProtocolName'
    signal refresh()

    id:logDisplay
    anchors.fill: parent
//    width: 450
//    height: 300

    Rectangle{
        id:rootRect
        color:colorBG
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
                    id: casLabel
                    color: "#ffffff"
                    text: "Cas"+casNumber+" Log"
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                    font.pointSize: 14
                    Layout.fillWidth: false
                }

                Text {
                    id: sampleLabel
                    color: "#ffffff"
                    text: sampleName
                    elide: Text.ElideRight
                    fontSizeMode: Text.Fit
                    Layout.preferredWidth: (labRow.width - casLabel.width)/2 - 2*labRow.spacing
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                    font.pointSize: 12
                    Layout.fillWidth: false
                }

                Text {
                    id: protLabel
                    color: "#ffffff"
                    text: protocolName
                    elide: Text.ElideRight
                    fontSizeMode: Text.Fit
                    Layout.preferredWidth: (labRow.width - casLabel.width)/2 - 2*labRow.spacing
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                    font.pointSize: 12
                    Layout.fillWidth: false
                }
            }
        }

        Rectangle{
            id: txClrRect
            color: 'white'
            anchors.top: labRect.bottom
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.bottomMargin: 50
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.topMargin: 0

            ScrollView{
                id:logScroller
    //            width: parent.width
    //            height: parent.height
                anchors.fill: parent
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
                ScrollBar.vertical.policy: ScrollBar.AlwaysOn
//                ScrollBar.horizontal.interactive: true
//                ScrollBar.vertical.interactive: true

                    TextEdit {
                        id: logTxDisplay
                        readOnly: true
                        selectByMouse: false
                        selectByKeyboard: true
                        text: logText
                        font.pointSize: 11
                        wrapMode: Text.WordWrap
                        anchors.fill: parent
                    }
            }
        }

        BevButton{
            id: refreshB
            width: 45
            height: 40
            anchors.top: txClrRect.bottom
            anchors.topMargin: 5
            anchors.left: parent.left
            anchors.leftMargin: 20
//            text: qsTr("Refresh")

            icon.source: "Icons/icons8-refresh-104.png"
            icon.color: "black"
            icon.height:20

            font.pointSize: 12
            onClicked: {
                logDisplay.refresh()
            }

        }

        BevButton {
            id: saveB
            anchors.top: txClrRect.bottom
            anchors.topMargin: 5
            anchors.left: refreshB.right
            anchors.leftMargin: 30
            text: qsTr("Save Log")
            font.pointSize: 12
        }

    }
}






/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}D{i:10;anchors_x:20;anchors_y:252}D{i:11;anchors_x:126;anchors_y:252}
}
##^##*/
