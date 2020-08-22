import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3

import "./Icons/"

Item {
    id: root
    property int casNumber: 0
    property variant stepModel: StepListModel{}
    property string mainDir: "/home/jackr/testprotocols"

    width: 800
    height: 480


    Rectangle {
        id: rootBG
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        color: "dimgray"

        Rectangle{
            id: menuRect
            width: 800
            height: 60
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: "#434343"
                }

                GradientStop {
                    position: 1
                    color: "#000000"
                }
            }
            x: 0; y: 0

            Button {
                id: homeB
                y: 8
                width: 50
                height: 50
                anchors.left: parent.left
                anchors.leftMargin: 20
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter

                opacity: homeB.down || homeB.checked || homeB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/home-run.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: homeB.down || homeB.checked || homeB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {
                    //Warning if model isn't empty?
                    mainStack.pop(null, StackView.Immediate)
                }
            }

            Button {
                id: backB
                y: 8
                width: 50
                height: 50
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: homeB.right
                anchors.leftMargin: 20

                opacity: backB.down || backB.checked || backB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/back.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: backB.down || backB.checked || backB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {
                    //Warning if model isn't empty?
                    mainStack.pop()
                }
            }

            Button {
                id: settingsB
                x: 692
                y: 8
                width: 50
                height: 50
                display: AbstractButton.IconOnly
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: parent.verticalCenter


                opacity: settingsB.down || settingsB.checked || settingsB.highlighted ? 0.5 : 1
                flat: true

                icon.source: "Icons/settings-icon.png"
                icon.color: "white"
                icon.height: 50
                icon.width: 50

                background: Rectangle {
                    implicitWidth: 50
                    implicitHeight: 50
                    border.width: settingsB.down || settingsB.checked || settingsB.highlighted ? 4 : 3
                    border.color: "white"
                    radius: 30
                    color: "transparent"
                }

                onClicked: {}



            }

            Text {
                id: fileNameLab
                x: 182
                y: 14
                width: 458
                height: 29
                color: "white"
                text: 'testProtocol06-2020.json (' + estRunTime(stepModel) +')'
                elide: Text.ElideMiddle
                wrapMode: Text.NoWrap
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 16
            }


        }



        Rectangle {
            id: rootTangle
            width: rootOperations.width + rootList.width
            height: 405
            x: 5
            y: 70
            color: "transparent"

            Rectangle {
                id: rootOperations
                width: 120
                height: rootTangle.height
                anchors {left: rootTangle.left; top: rootTangle.top; bottom: rootTangle.bottom}
                color: "silver"
                radius: 5

                                DelegateModel {
                                    id: operationsModDel
                                    model: OperationTypes {}
                                    delegate: OperTypeDel {
                                        draggedItemParent: rootList
                                        _listView: stepLView
                                    }
                                }

                                ListView {
                                    id: typeView
                                    anchors { fill: parent; margins: 2 }
//                                    anchors.topMargin: protInfo.height + 5

                                    model: operationsModDel

                                    spacing: 7
                                    cacheBuffer: 50
                                }


            }

            Rectangle {
                id: rootList
                anchors {
                    left: rootOperations.right; top: rootTangle.top; bottom: rootTangle.bottom
                    leftMargin: 5
                }
                width: 550
                height: rootTangle.height
                color: "whitesmoke"
                radius: 5


                                DelegateModel {
                                    id: stepListModDel
                                    model: stepModel
                                    delegate: chooser
                                }

                                DelegateChooser {
                                    id: chooser
                                    role: "opName"
                                    DelegateChoice { roleValue: "Incubation"
                                        DraggableItem {
                                            IncubationContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Mixing"
                                        DraggableItem {
                                            MixingContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Purge"
                                        DraggableItem {
                                            PurgeContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Load Formalin"
                                        DraggableItem {
                                            LoadContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Load Dehydrant"
                                        DraggableItem {
                                            LoadContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Load Stain"
                                        DraggableItem {
                                            LoadContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                    DelegateChoice { roleValue: "Load BABB"
                                        DraggableItem {
                                            LoadContent{
                                                modDel: stepListModDel
                                                itemIndex: model.index
                                                width: stepLView.width
                                            }
                                            draggedItemParent: rootList
                                            onMoveItemRequested: {
                                                stepListModDel.model.move(from, to, 1);
                                            }
                                        }
                                    }

                                }



                                ListView {
                                    id: stepLView

                                    property var operDict: {
                                        'Incubation':{'opName':'Incubation','opTime':'00:00:00', 'mixVol': 'undefined', 'loadType': 'undefined'},
                                        'Mixing':{'opName':'Mixing','opTime':'00:00:00','mixVol': '1', 'loadType': 'undefined'},
                                        'Purge':{'opName':'Purge', 'opTime':'00:05:00', 'mixVol': 'undefined', 'loadType': 'undefined'},
                                        'Load Formalin':{'opName':'Load Formalin', 'opTime':'00:05:00', 'mixVol': 'undefined', 'loadType':'Formalin'},
                                        'Load Dehydrant':{'opName':'Load Dehydrant', 'opTime':'00:05:00', 'mixVol': 'undefined', 'loadType':'Dehydrant'},
                                        'Load Stain':{'opName':'Load Stain', 'opTime':'00:05:00', 'mixVol': 'undefined', 'loadType':'Stain'},
                                        'Load BABB':{'opName':'Load BABB', 'opTime':'00:05:00', 'mixVol': 'undefined', 'loadType':'BABB'}
                                    }

                                    anchors.fill: parent
                                    anchors.margins: 5
//                                    anchors.topMargin: protInfo.height + 5

                                    width: rootList.width
                                    height: rootList.height

                                    clip: true
                                    model: stepListModDel

                                    spacing: 5

                                    //Backup and starting drop area for list model
                                    //Will catch glitch that prevents operation to be appended at end of list
                                    DropArea {
                                        id: listDrop
                                        anchors {
                                            top: stepLView.count == 0 ? stepLView.top : stepLView.contentItem.bottom
                                            left: stepLView.left; right:stepLView.right; bottom: stepLView.bottom
                                        }
                                        keys: ["operation"]

                                        onDropped: {
                                            stepListModDel.model.append(stepLView.operDict[drag.source.opName])
                                            console.log(JSON.stringify(stepLView.operDict[drag.source.opName]))
                //                            var dIndex = stepLView.indexAt(drop.x, drop.y)
                //                            console.log("Index?: ", dIndex)
                //                            if(dIndex == -1){
                //                                stepListModDel.model.append(stepLView.operDict[drag.source.opName])
                //                            } else if(dIndex == (stepListModDel.items.count-1)){
                //                                stepListModDel.model.append(stepLView.operDict[drag.source.opName])
                //                                console.log("End append: ", dIndex)
                //                            }
                //                            else {
                //                                stepListModDel.model.insert(dIndex + 1, stepLView.operDict[drag.source.opName])
                //                            }
                                        }
                                    }



                                }
            }

            BevelRect {
                id: protInfo
                height: 40
                color: "#242424"
                radius: 20
                anchors.right: rootList.right
                anchors.rightMargin: 0
                //                radius: 5
                anchors.top: rootList.top
                anchors.topMargin: 0
                anchors.left: rootList.left
                anchors.leftMargin: 0


                Text {
                    id: casNum
                    y: 8
                    color: "#ffffff"
                    text: qsTr("Cassette 0")
                    font.weight: Font.Medium
                    anchors.left: casNum2.right
                    anchors.leftMargin: 60
                    anchors.verticalCenter: parent.verticalCenter
                    font.pointSize: 14
                }

                Rectangle {
                    id: sampRec
                    y: 48
                    width: 269
                    height: 31
                    color: "#808080"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: casNum.right
                    anchors.leftMargin: 30

                    TextInput {
                        id: sampInput
                        color: "#ffffff"
                        leftPadding: 5
                        anchors.rightMargin: 0
                        anchors.bottomMargin: 0
                        anchors.leftMargin: 0
                        anchors.topMargin: 0
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        anchors.fill: parent
                        font.pointSize: 12
                        selectionColor: "#040450"


                        property string placeholderText: "Enter Sample Name..."

                        Text {
                            id: placeholderTxt
                            anchors.fill: parent
                            text: sampInput.placeholderText
                            leftPadding: 5
                            verticalAlignment: Text.AlignVCenter
                            color: "#aaa"
                            font: sampInput.font
                            visible: !sampInput.text && !sampInput.activeFocus
                        }

                    }
                }

                Text {
                    id: casNum2
                    x: -9
                    y: 0
                    color: "#ffffff"
                    text: qsTr("Steps:")
                    font.pointSize: 14
                    font.weight: Font.Medium
                    anchors.leftMargin: 20
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                }


            }



        }


        Item {
            id: editorButtons
            x: 679
            y: 269
            width: 121
            height: 203
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8

            Button {
                id: openB
                x: 10
                y: 47
                height: 30
                text: qsTr("Open")
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.leftMargin: 5
                anchors.bottom: saveAsB.top
                anchors.left: parent.left
                display: AbstractButton.TextBesideIcon
                anchors.bottomMargin: 60
                font.pointSize: 12

                onClicked: {
                    //                    openDialog.open()
                }
            }

            Button {
                id: saveAsB
                x: -6
                y: 33
                height: 30
                text: qsTr("Save As")
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.bottom: saveB.top
                anchors.bottomMargin: 10
                font.pointSize: 12
                display: AbstractButton.TextBesideIcon
                anchors.left: parent.left
                anchors.leftMargin: 5


                onClicked: {
                    //                    saveDialog.open()
                    var datamodel = []
                    for (var i = 0; i < stepListModDel.model.count; ++i) datamodel.push(stepListModDel.model.get(i))
                    var datastring = JSON.stringify(datamodel)
                    console.log(datastring)

                }
            }

            Button {
                id: saveB
                x: -6
                height: 30
                text: qsTr("Save")
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.bottom: startB.top
                anchors.bottomMargin: 15
                font.pointSize: 12
                anchors.left: parent.left
                anchors.leftMargin: 5

                // When the file has an existing directory + name, set enabled to true. Save under current file directory.
                enabled: false
            }

            Button {
                id: startB
                x: -3
                y: 156
                height: 40
                text: qsTr("Start")
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 25
                font.pointSize: 12
                padding: 0
                rightPadding: 0
                leftPadding: 0
                layer.wrapMode: ShaderEffectSource.ClampToEdge
                display: AbstractButton.TextBesideIcon
                anchors.left: parent.left
                anchors.leftMargin: 5

                icon.source: "Icons/rightArrow-black.png"
                icon.color: "green"
                icon.height: 15

                onClicked: {
                    //Confirm/ask for sample name in dialog box?
                    //Initialize start protocol with model and casNumber
                    //return to sample monitor
                    mainStack.pop(null)
                }
            }

        }
    }

    function addTimes(time1, time2){

        var times = [ 0, 0, 0 ]
        var max = times.length

        var a = (time1 || '').split(':')
        var b = (time2 || '').split(':')

        // normalize time values
        for (var i = 0; i < max; i++) {
            a[i] = isNaN(parseInt(a[i])) ? 0 : parseInt(a[i])
            b[i] = isNaN(parseInt(b[i])) ? 0 : parseInt(b[i])
        }

        // store time values
        for (var i = 0; i < max; i++) {
            times[i] = a[i] + b[i]
        }

        var hours = times[0]
        var minutes = times[1]
        var seconds = times[2]

        if (seconds >= 60) {
            var m = (seconds / 60) << 0
            minutes += m
            seconds -= 60 * m
        }

        if (minutes >= 60) {
            var h = (minutes / 60) << 0
            hours += h
            minutes -= 60 * h
        }

        return ('0' + hours).slice(-2) + ':' + ('0' + minutes).slice(-2) + ':' + ('0' + seconds).slice(-2)
    }

    function estRunTime(model){
        var tally = "00:00:00"
        for(var i = 0; i < model.count; i++){
            console.log(i," time ", model.get(i).opTime)
            tally = addTimes(tally, model.get(i).opTime)
            console.log(tally)
        }
        return tally
    }

    //    FileDialog {
    ////        id:saveDialog
    ////        selectExisting: false
    ////        folder: mainDir
    ////        nameFilters: [ "Protocol Files (*.json)", "All files (*)" ]
    ////        nameFilters: [ "*.json", "All files (*)" ]
    ////        defaultSuffix: ".json"
    ////        modality: Qt.WindowModal
    ////        onAccepted: {
    ////            console.log(fileUrl)
    ////            console.log(fileUrls)
    ////            var datamodel = []
    ////            for (var i = 0; i < stepListModDel.model.count; ++i) datamodel.push(stepListModDel.model.get(i))
    ////            var datastring = JSON.stringify(datamodel)
    ////            console.log(datastring)
    //////            JSONhelper.saveListModel(datastring, fileUrl)

    ////        }

    //    }
}

/*##^##
Designer {
    D{i:23;anchors_height:200;anchors_width:200;anchors_x:8;anchors_y:62}D{i:25;anchors_x:8}
D{i:24;anchors_height:200;anchors_width:60;anchors_x:8;anchors_y:62}
}
##^##*/
