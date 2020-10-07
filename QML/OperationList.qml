import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
import "../"


Rectangle {
    id: rootList
    width: 500
    height: 368

    DelegateModel {
        id: visualModel


        model: OperModel {}
        delegate: chooser
        //            delegate: ContainerWid {
        //                runTime: opTime
        //                modDel: visualModel
        //                listView: operList
        //                itemIndex: DelegateModel.itemsIndex
        //            }



    }

    DelegateChooser {
        id: chooser
        role: "opName"
        //DelegateChoice { roleValue: "yes"; ContainerWid {md: visualModel; index: DelegateModel.itemsIndex}}
        DelegateChoice { roleValue: "Incubation"
            ContainerWid {
                runTime: opTime;
                modDel: visualModel
                listView: operList
                itemIndex: DelegateModel.itemsIndex
            }
        }
        //DelegateChoice { roleValue: "Stain"; ContainerWid { rootT: rootTangle; visualModel: visualModel}}

    }

    ListView {
        id: operList
        anchors.fill: rootList
        anchors.margins: 0
        width: rootList.width

        clip: true

        model: visualModel

        spacing: 3
    }
}
