import QtQuick 2.12

Rectangle{
    id:doubleRect
    property double doubleVal: 0
    property int maxLength: 4
    property int maxVal: 10
    property string placeholderText: "speed"

    signal setVal()

    TextInput {
        id: doubleIn
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
        text: doubleVal == 0 ? '' : doubleVal
        validator: DoubleValidator{
            bottom: 0
            top: maxVal
        }
        maximumLength: maxLength
        echoMode: (doubleVal==0 && !activeFocus) ? TextInput.NoEcho : TextInput.Normal
        clip: true

        onTextEdited: {
            if(parseFloat(doubleIn.text)>maxVal){
                doubleIn.text = 0
                doubleVal = 0
                doubleRect.setVal()
            } else if(doubleIn.text == ''){
                doubleVal = 0
                doubleRect.setVal()
            }
        }

        onEditingFinished: {
            if (doubleIn.text == ''){
                doubleVal = 0
                doubleRect.setVal()
                doubleIn.text = 0
            } else if (Math.abs(doubleVal)>maxVal){
                doubleVal = 0
                doubleRect.setVal()
                doubleIn.text = 0
            } else {
                doubleVal = parseFloat(doubleIn.text)
                doubleRect.setVal()
                doubleIn.text = doubleVal
            }
        }

        Text {
            id: phDoubleTxt
            anchors.fill: parent
            text: doubleRect.placeholderText
            leftPadding: 5
            verticalAlignment: Text.AlignVCenter
            color: "#aaa"
            font: doubleIn.font
            visible: doubleVal==0 && !doubleIn.activeFocus
        }
    }
}



