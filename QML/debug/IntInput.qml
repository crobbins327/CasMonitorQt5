import QtQuick 2.12

Rectangle{
    id:intRect
    property int intVal
    property int maxLength: 4
    property int maxVal: 9999
    property string placeholderText: "secs"

    signal setVal()

    TextInput {
        id: intIn
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
        text: intVal == 0 ? '' : intVal
        validator: IntValidator{
            bottom: 0
            top: maxVal
        }
        maximumLength: maxLength
        echoMode: (intVal==0 && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
        clip: true


        onTextEdited: {
            if(parseInt(intIn.text)>maxVal){
                intIn.text = 0
                intVal = 0
                intRect.setVal()
            } else if(intIn.text == ''){
                intVal = 0
                intRect.setVal()
            }
        }

        onEditingFinished: {
            if (intIn.text == ''){
                intVal = 0
                intRect.setVal()
                intIn.text = 0
            } else if (Math.abs(intVal)>maxVal){
                intVal = 0
                intRect.setVal()
                intIn.text = 0
            } else {
                intVal = parseInt(intIn.text)
                intRect.setVal()
                intIn.text = intVal
            }
        }


        Text {
            id: phIntTxt
            anchors.fill: parent
            text: intRect.placeholderText
            leftPadding: 5
            verticalAlignment: Text.AlignVCenter
            color: "#aaa"
            font: intIn.font
            visible: intVal==0 && !intIn.activeFocus
        }
    }
}



