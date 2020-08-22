import QtQuick 2.12

Rectangle {
    id: bevelRect

    Rectangle {
        id: leftRect
        width: parent.width/2
        color: parent.color
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
    }
    Rectangle {
        id: topRect
        height: parent.height/2
        color: parent.color
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.top: parent.top
    }
}



