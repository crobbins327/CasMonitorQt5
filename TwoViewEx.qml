import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Window 2.3
import Qt.labs.settings 1.0

ApplicationWindow {
  id: main
  width: 640
  height: 480
  visible: true

  property string datastore: ""

  Component.onCompleted: {
    if (datastore) {
      dataModel.clear()
      var datamodel = JSON.parse(datastore)
      for (var i = 0; i < datamodel.length; ++i) dataModel.append(datamodel[i])
    }
  }

  onClosing: {
    var datamodel = []
    for (var i = 0; i < dataModel.count; ++i) datamodel.push(dataModel.get(i))
    datastore = JSON.stringify(datamodel)
  }

  Settings {
    property alias datastore: main.datastore
  }

  ListView {
    id: view
    anchors.fill: parent
    model: ListModel {
      id: dataModel
      ListElement { name: "test1"; value: 1 }
    }
    delegate: Text {
      text: name + " " + value
    }
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    onClicked: {
      if (mouse.button === Qt.LeftButton) {
        var num = Math.round(Math.random() * 10)
        dataModel.append({ "name": "test" + num, "value": num })
      } else if (dataModel.count) {
        dataModel.remove(0, 1)
      }
    }
  }
}
