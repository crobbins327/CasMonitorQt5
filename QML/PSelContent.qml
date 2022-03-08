import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import "./Icons/"



Item {
    id: rootCol
    property int itemIndex : DelegateModel.itemsIndex
//    property string opTime: '00:05:00'
//    property string numCycles : '3'
//    property string volume : '3000uL'
//    property string pSpeed : '1'
    width: recStepList.width
    height: ribbon.height

    Rectangle {
        id: ribbon
        x: 0
        anchors.top: rootCol.top
        anchors.topMargin: 0

        radius: 5
        width: rootCol.width
        height: 27
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {position: 0.62; color: "#f5f5f5"}
            //            GradientStop {position: 0.848; color: "#737d90"}

            GradientStop {
                position: 0.93
                color: "#577dc7"
            }
        }

        Text {
            id: opTimeText
            y: 7
            color: "#000000"
            text: opTime == null ? "00:05:00" : opTime
            anchors.verticalCenter: ribbon.verticalCenter
            anchors.left: toolButton.right
            anchors.leftMargin: 10

            font.capitalization: Font.MixedCase
            font.weight: Font.Medium
            font.pointSize: 12
            renderType: Text.QtRendering
        }

        Text {
            id: mixAfterText
            y: 4
            color: "#000000"
            text: {
                if(mixAfterSecs=='undefined'){
                    return(null)
                } else if(mixAfterSecs==0){
                    return(null)
                } else if(mixAfterSecs>0){
                    return('mix every '+mixAfterSecs+'s')
                } else{
                    console.log('Error in protocol file? No mixAfterSecs field..')
                    return(null)
                }
            }
            anchors.left: opTimeText.right
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 12
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.leftMargin: 10
            font.capitalization: Font.MixedCase
        }

//        Text {
//            id: speedText
//            y: 4
//            color: "#000000"
//            text: pSpeed == 'undefined' | numCycles != 'undefined' ? null : pSpeed+' Spd.'
//            anchors.left: opTimeText.right
//            anchors.verticalCenter: parent.verticalCenter
//            font.pointSize: 12
//            font.weight: Font.Medium
//            renderType: Text.QtRendering
//            anchors.leftMargin: 10
//            font.capitalization: Font.MixedCase
//        }

        Text {
            id: cycleText
            y: 4
            color: "#000000"
            text: parseInt(numCycles) == 0 ? null : numCycles+' Cyc.'
            anchors.left: opTimeText.right
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 12
            font.weight: Font.Medium
            renderType: Text.QtRendering
            anchors.leftMargin: 10
            font.capitalization: Font.MixedCase
        }

        Text {
            id: volumeText
            y: 4
            color: "#000000"
            text: volume == 'undefined' ? null : volume
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            font.pointSize: 12
            font.weight: Font.Medium
            renderType: Text.QtRendering


            font.capitalization: Font.MixedCase
        }

        ToolButton {
            id: toolButton
            width: 190
            text: (itemIndex+1) + ". "+ opName
            rightPadding: 38
            opacity: 1
            leftPadding: 6
            topPadding: 6
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0

            flat: false

            contentItem: Text{
                text: toolButton.text
                font.weight: Font.Thin
                font.bold: false
                font.pointSize: 12
                anchors.left: parent.left
                anchors.leftMargin: 15
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                opacity: 1.0
                color: toolButton.palette.button
            }
        }

    }
}



