import QtQuick 2.12
import QtQml.Models 2.12
import Qt.labs.qmlmodels 1.0
import QtQuick.Controls 2.12
import "./Icons/"

Item{
    id:root
    property int contHeight: 35
    property Item draggedItemParent
    // Internal: shortcut to access the attached ListView from everywhere. Shorter than root.ListView.view
    property ListView _listView: null
    // Internal: set to -1 when drag-scrolling up and 1 when drag-scrolling down
    property int _scrollingDirection: 0
    // Size of the area at the top and bottom of the list where drag-scrolling happens
    property int scrollEdgeSize: 6

    width: parent.width
    height: content.height

    MouseArea {
        id: dragArea
        property bool held: false

        anchors { left: parent.left; right: parent.right }
        width: root.width
        height: content.height

        drag.target: held ? content : undefined

        pressAndHoldInterval: 10

        onPressAndHold: held = true
        onReleased: {
            held = false
        }

        drag.onActiveChanged: {
            console.log("Dragging!")
            if (dragArea.drag.active) {
//                console.log("Dragging: ", model.opName)
            }
            content.Drag.drop()
        }


        Rectangle {
            id: content
            property string opName: model.opName
            property string type: "operation"

            anchors {
                horizontalCenter: parent.horizontalCenter
                verticalCenter: parent.verticalCenter
            }
            width: dragArea.width
            height: contHeight

            border.width: 1
            border.color: "lightgray"

            color: dragArea.held ? "lightsteelblue" : "whitesmoke"
            Behavior on color { ColorAnimation { duration: 100 } }

            radius: 4

            Drag.active: dragArea.drag.active
            Drag.source: content
            Drag.hotSpot.x: width / 2
            Drag.hotSpot.y: height / 2
            Drag.keys: ["operation"]


            Text {
                //            text: "Load Dehydrant"
                text: model.opName
                font.weight: Font.Thin
                font.pointSize: 11
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
            }
            //Add icon or image?

        }

    }
    SmoothedAnimation {
        id: upAnimation
        target: _listView
        property: "contentY"
        to: 0
        running: _scrollingDirection == -1
    }

    SmoothedAnimation {
        id: downAnimation
        target: _listView
        property: "contentY"
        to: _listView.contentHeight - _listView.height
        running: _scrollingDirection == 1
    }

    states: State {
        when: dragArea.drag.active

        ParentChange { target: content; parent: draggedItemParent }
        AnchorChanges {
            target: content
            anchors { horizontalCenter: undefined; verticalCenter: undefined }
        }
        PropertyChanges {
            target: root
            _scrollingDirection: {
                var yCoord = _listView.mapFromItem(dragArea, 0, dragArea.mouseY).y;
                if (yCoord < scrollEdgeSize) {
                    -1;
                } else if (yCoord > _listView.height - scrollEdgeSize) {
                    1;
                } else {
                    0;
                }
            }
        }
    }
}



