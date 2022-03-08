import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12
import QtQuick.Controls.Material 2.12
import "./Icons/"



Item {
    id: rootCol

    //    property string opName: model.opName
    //    property string opTime: model.opTime
    property DelegateModel modDel: null
    property int itemIndex : DelegateModel.itemsIndex
    property bool minimize: true
//    property string mixAfterSecs: 600
    property string mixAfterTime: get_time(mixAfterSecs)

    property string type: "step"


    width: parent.width
    height: ribbon.height + container.height

    Rectangle {
        id: ribbon
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
//        height: 35
        height: 25
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.524; color: "#f5f5f5"}
            GradientStop {position: 0.826; color: rootCol.minimize ?  "#577dc7" : "#ffc700"}
        }

        Button {
            id: closeButton
            width: 25
            height: 25
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10

            Image {
                id: closeImage
                source: "Icons/close.png"
                anchors.horizontalCenter: closeButton.horizontalCenter
                anchors.verticalCenter: closeButton.verticalCenter
                width: closeButton.width*0.5
                height: closeButton.height*0.5
                fillMode: Image.PreserveAspectFit
            }
            ColorOverlay {
                anchors.fill: closeImage
                source: closeImage
                color: closeButton.down || closeButton.checked || closeButton.highlighted ? "red" : "black"
            }

            background: Rectangle {
                implicitWidth: closeButton.width*0.5
                implicitHeight: closeButton.height*0.5
                color: "transparent"
            }

            onClicked: {
                modDel.items.remove(itemIndex)
                modDel.model.remove(itemIndex)
            }

        }

        Text {
            id: opTimeText
            property string opHour: opTime.substring(0,2)
            property string opMin: opTime.substring(3,5)
            property string opSec: opTime.substring(6,8)
            y: 7
            color: "#000000"
            text: opTime
            //                text: "12:59:59"
            anchors.verticalCenter: toolButton.verticalCenter
            anchors.left: toolButton.right
            anchors.leftMargin: 10

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 11
            renderType: Text.QtRendering
        }

        ToolButton {
            id: toolButton
            width: 180
            text: (itemIndex+1) + ". Incubation"
            //            text: "99. Incubation"
            opacity: 1
            leftPadding: 6
            rightPadding: 43
            topPadding: 6
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            display: AbstractButton.TextBesideIcon

            contentItem: Item {
                id: element
                //                Row {
                //                    id: row
                //                    anchors.verticalCenter: parent.verticalCenter
                //                    layoutDirection: Qt.LeftToRight
                ////                    anchors.horizontalCenter: parent.horizontalCenter
                //                    spacing: 5
                Image {
                    source: rootCol.minimize ? "Icons/rightArrow-black.png" : "Icons/downArrow-black.png"
                    width: 8
                    height: 8
                    anchors.left: parent.left
                    anchors.leftMargin: 2
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: toolButton.text
                    anchors.left: parent.left
                    anchors.leftMargin: 18
                    anchors.verticalCenter: parent.verticalCenter
                    font.weight: Font.Thin
                    font.bold: true
                    font.pointSize: 12
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                }
                //                }
            }

            background: Rectangle {
                opacity: toolButton.down ? 1.0 : 0.5
                color: toolButton.down || toolButton.checked || toolButton.highlighted ? toolButton.palette.mid : toolButton.palette.button
            }


            onClicked: {
                rootCol.minimize = rootCol.minimize ? false : true
            }
        }

        Text {
            id: mixAfterTText
            x: -6
            y: 7
            color: "#000000"
            text: {
                if(!mixSwitch.checked){
                    return('no mixing')
                } else if(mixAfterSecs==0){
                    return('no mixing')
                } else if(mixAfterSecs > 0){
                    return('mix every '+ mixAfterSecs + 's')
                } else{
                    console.log(mixAfterSecs, ', value error for mixAfterSecs')
                    mixAfterSecs = 0
                    return('no mixing')
                }
            }
            font.capitalization: Font.MixedCase
            font.pointSize: 11
            anchors.left: opTimeText.right
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.leftMargin: 15
            anchors.verticalCenter: toolButton.verticalCenter
        }
    }
    Rectangle {
        id: container
        anchors.top: ribbon.bottom
        Material.theme: Material.Light
        Material.accent: Material.Blue

        width: rootCol.width
        height: rootCol.minimize ? 0 : 120

        radius: 5
        border.width: 0.5
        border.color: "lightgray"
        color: "#f5f5f5"
        visible: rootCol.minimize ? false : true

        Text {
            id: runTimeLabel
            color: "#000000"
            text: "Run Time:"
            anchors.top: parent.top
            anchors.topMargin: 30
            anchors.left: parent.left
            anchors.leftMargin: 15
            font.pointSize: 11
            font.weight: Font.Medium
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }

        Tumbler {
            id: hoursTumbler
            width: 60
            anchors.left: runTimeLabel.right
            anchors.leftMargin: 10
            font.pointSize: 12
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            anchors.top: parent.top
            anchors.topMargin: 10
            transformOrigin: Item.Center
            model: 12

            currentIndex: getHour(opTime)



            onMovingChanged: {
                if(hoursTumbler.currentIndex < 10){
                    opTimeText.opHour = "0"+hoursTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                } else {
                    opTimeText.opHour = hoursTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                }
                console.log("Hours: ", hoursTumbler.currentIndex)
            }

        }

        Tumbler {
            id: minutesTumbler
            width: 60
            anchors.left: hoursTumbler.right
            anchors.leftMargin: 0
            font.pointSize: 12
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            anchors.top: parent.top
            anchors.topMargin: 10
            transformOrigin: Item.Center
            scale: 1
            rotation: 0
            model: 60

            currentIndex: getMin(opTime)

            onMovingChanged: {
                if(minutesTumbler.currentIndex < 10){
                    opTimeText.opMin = "0"+minutesTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                } else {
                    opTimeText.opMin = minutesTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                }
                console.log("Minutes: ", minutesTumbler.currentIndex)
            }
        }

        Tumbler {
            id: secondsTumbler
            width: 60
            anchors.left: minutesTumbler.right
            anchors.leftMargin: 0
            font.pointSize: 12
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            anchors.top: parent.top
            anchors.topMargin: 10
            transformOrigin: Item.Center
            model: 60

            currentIndex: getSec(opTime)

            onMovingChanged: {
                if(secondsTumbler.currentIndex < 10){
                    opTimeText.opSec = "0"+secondsTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                } else {
                    opTimeText.opSec = secondsTumbler.currentIndex
                    opTime = opTimeText.opHour+":"+opTimeText.opMin+":"+opTimeText.opSec
                }
                console.log("Secs: ", secondsTumbler.currentIndex)
            }
        }

        Text {
            id: runTimeLabel1
            x: 9
            color: "#000000"
            text: "(hh:mm:ss)"
            anchors.horizontalCenter: runTimeLabel.horizontalCenter
            anchors.top: runTimeLabel.bottom
            anchors.topMargin: 2
            font.pointSize: 10
            font.weight: Font.Medium
            renderType: Text.QtRendering
            font.capitalization: Font.MixedCase
        }

        Text {
            id: mixAfterLabel
            color: "#000000"
            text: "Mix after:"
            font.pointSize: 11
            font.capitalization: Font.MixedCase
            anchors.left: secondsTumbler.right
            anchors.verticalCenterOffset: 0
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.leftMargin: 15
            anchors.verticalCenter: runTimeLabel.verticalCenter
        }

        Text {
            id: mixAfterUnits
            color: mixSwitch.checked ? "#000000" : 'red'
            text: mixSwitch.checked ? "(min:sec)" : "No mixing"
            font.pointSize: 10
            anchors.left: mixAfterLabel.left
            anchors.leftMargin: 0
            anchors.topMargin: 2
            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.top: mixAfterLabel.bottom
        }

        Tumbler {
            id: minMix
            visible: mixSwitch.checked
            width: 60
            anchors.topMargin: 10
            anchors.bottomMargin: 8
            anchors.bottom: parent.bottom
            font.pointSize: 12
            anchors.left: mixAfterLabel.right
            model: 60
            scale: 1
            anchors.leftMargin: 10
            rotation: 0
            anchors.top: parent.top
            transformOrigin: Item.Center

            currentIndex: getMin(mixAfterTime)

            onMovingChanged: {
                mixAfterSecs = minMix.currentIndex*60 + secMix.currentIndex
//                console.log(mixAfterSecs)
//                console.log(mixAfterTime)
            }

        }

        Tumbler {
            id: secMix
            visible: mixSwitch.checked
            width: 60
            anchors.left: minMix.right
            anchors.leftMargin: 0
            anchors.topMargin: 10
            anchors.bottomMargin: 8
            anchors.bottom: parent.bottom
            font.pointSize: 12
            model: 60
            anchors.top: parent.top
            transformOrigin: Item.Center

            currentIndex: getSec(mixAfterTime)

            onMovingChanged: {
                mixAfterSecs = minMix.currentIndex*60 + secMix.currentIndex
//                console.log(mixAfterTime)
//                console.log(mixAfterSecs)
            }
        }

        Switch {
            id: mixSwitch
            height: 30
            display: AbstractButton.TextBesideIcon
            checked: true
            anchors.top: mixAfterUnits.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: mixAfterLabel.horizontalCenter
            onClicked: {
                if(!mixSwitch.checked){
                    mixAfterSecs = 0
                    minMix.currentIndex = 0
                    secMix.currentIndex = 0
                }
            }
        }




    }


    function getHour(opTime){
        var hour = opTime.substring(0,2)
        if(parseInt(hour.substring(0,1)) == 0){
            return parseInt(hour.substring(1,2))
        } else {
            return parseInt(hour)
        }
    }

    function getMin(opTime){
        var mn = opTime.substring(3,5)
        if(parseInt(mn.substring(0,1)) == 0){
            return parseInt(mn.substring(1,2))
        } else {
            return parseInt(mn)
        }
    }

    function getSec(opTime){
        var sec = opTime.substring(6,8)
        if(parseInt(sec.substring(0,1)) == 0){
            return parseInt(sec.substring(1,2))
        } else {
            return parseInt(sec)
        }
    }

    function get_time(runSecs){
        var rtime = new Date(runSecs * 1000).toISOString().substr(11, 8);
        return(rtime)
    }

}



