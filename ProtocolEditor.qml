import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3

import "./Icons/"

Item {
    id: rootEd
    property int casNumber: 0
    property variant stepModel: ListModel{}
    property string mainDir: ''
    property string sampleName: ''
    property string protocolName: 'Protocol Name'
    property string savedPath: ''
    property string runTime: estRunTime(rootEd.stepModel)

    signal reNextModel(string jsondata, string protName, string pathSaved)
    Component.onCompleted: JSONHelper.nextModel.connect(reNextModel)

    //width: parent.width
    //height: parent.height
    
    Connections {
        target: rootEd
        function onReNextModel(jsondata, protName, pathSaved) {
            stepModel.clear()
            //console.log(jsondata)
            var datamodel = JSON.parse(jsondata)
            //console.log(datamodel)
            for (var i = 0; i < datamodel.length; ++i) stepModel.append(datamodel[i])
            
            //Set protocol name
            rootEd.protocolName = protName

            //update savedPath
            rootEd.savedPath = pathSaved
            console.log("SavedP: ", rootEd.savedPath)
        }
    }
    
    Rectangle {
        id: rootEdBG
//        width: 780
//        height: 460
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
            height: 60
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0
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
            Button {
                id: homeB
//                y: 8
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
//                y: 8
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

                onClicked: {
                    settingsMenu.open()
                }

                Menu {
                        id: settingsMenu
                        y: settingsB.height+3

                        MenuItem {
                            text: "Set Default Protocol"
                            onClicked: {
                                defProtSelector.open()
                            }
                        }
                        MenuItem {
                            text: rootApWin.otherMode + " mode"
                            onClicked: {
                                if(rootApWin.otherMode==='FullScreen'){
                                    rootApWin.visMode = 'FullScreen'
                                    rootApWin.otherMode = 'Windowed'
                                } else {
                                    rootApWin.visMode = 'Windowed'
                                    rootApWin.otherMode = 'FullScreen'
                                }
                            }
                        }
                        MenuItem {
                            text: "Exit"
                            onClicked: {
                                exitDialog.open()
                            }
                        }
                    }
            }

            Text {
                id: fileNameLab
                width: 450
                height: 25
                color: "white"
                text: rootEd.protocolName + ' (' + rootEd.runTime +')'
                elide: Text.ElideMiddle
                wrapMode: Text.NoWrap
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pointSize: 16
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
            }


        }



        Rectangle {
            id: rootEdTangle
            color: "transparent"
            anchors.right: editorButtons.left
            anchors.rightMargin: 4
            anchors.left: parent.left
            anchors.leftMargin: 5
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 5
            anchors.top: menuRect.bottom
            anchors.topMargin: 10

            Rectangle {
                id: rootOperations
                width: 120
                height: rootEdTangle.height
                anchors {left: rootEdTangle.left; top: rootEdTangle.top; bottom: rootEdTangle.bottom}
                color: "silver"
                radius: 5

                BevelRect {
                    id: opTab
                    height: 40
                    color: "#242424"
                    radius: 20
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 0

                    Text {
                        id: opLabel
                        color: "#ffffff"
                        text: qsTr("Operations:")
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        anchors.fill: parent
                        font.weight: Font.Medium
                        font.pointSize: 14
                    }
                }

                DelegateModel {
                    id: operationsModDel
                    model: OperationTypes {}
                    delegate: OperTypeDel {
                        draggedItemParent: rootList
                        _listView: stepLView
                        //Where 7 is the number of operation delegates in the model
                        contHeight: (rootEdTangle.height-typeView.spacing*operationsModDel.count-opTab.height)/operationsModDel.count

                    }
                }

                ListView {
                    id: typeView
                    anchors {
                        left: parent.left; right: parent.right; bottom: parent.bottom;
                        top: opTab.bottom; margins: 2
                    }

                    model: operationsModDel

                    spacing: 7
                    cacheBuffer: 50
                }


            }

            Rectangle {
                id: rootList
                anchors {
                    left: rootOperations.right; top: rootEdTangle.top; bottom: rootEdTangle.bottom
                    leftMargin: 5
                }
                height: rootEdTangle.height
                color: "whitesmoke"
                radius: 5
                anchors.right: parent.right
                anchors.rightMargin: 0

                BevelRect {
                    id: protInfo
                    height: 40
                    color: "#242424"
                    radius: 20
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.top: rootList.top
                    anchors.topMargin: 0
                    anchors.left: rootList.left
                    anchors.leftMargin: 0

                    Text {
                        id: casNum
                        color: "#ffffff"
                        text: {
                            if (casNumber == 0){
                                return("None")
                            } else {
                                return("Cassette " + casNumber)
                            }
                        }
                        font.weight: Font.Medium
                        anchors.left: stepLab.right
                        anchors.leftMargin: 50
                        anchors.verticalCenter: parent.verticalCenter
                        font.pointSize: 14
                    }

                    Rectangle {
                        id: sampRec
                        height: 31
                        color: "#808080"
                        anchors.right: parent.right
                        anchors.rightMargin: 20
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: casNum.right
                        anchors.leftMargin: 30

                        TextInput {
                            id: sampInput
                            property string placeholderText: "Enter Sample Name..."
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


                            text: activeFocus ? sampleName : ''
                            clip: true

                            onEditingFinished: {sampleName = sampInput.text}

                            Text {
                                id: placeholderTxt
                                anchors.fill: parent
                                text: sampInput.placeholderText
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#aaa"
                                font: sampInput.font
                                visible: !sampleName && !sampInput.activeFocus
                            }

                            Text {
                                id: shortTxt
                                anchors.fill: parent
                                text: sampleName
                                elide: Text.ElideMiddle
                                leftPadding: 5
                                verticalAlignment: Text.AlignVCenter
                                color: "#ffffff"
                                font: sampInput.font
                                visible: sampInput.activeFocus ? false : true
                            }

                        }
                    }

                    Text {
                        id: stepLab
                        color: "#ffffff"
                        text: qsTr("Steps:")
                        font.pointSize: 14
                        font.weight: Font.Medium
                        anchors.leftMargin: 20
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                    }

                }




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
                        'Incubation':{'opName':'Incubation','opTime':'00:00:00', 'mixAfterSecs': '0', 'volume': 'undefined', 'pSpeed':'undefined', 'numCycles': 'undefined', 'loadType': 'undefined'},
                        'Mixing':{'opName':'Mixing','opTime':'00:05:00', 'mixAfterSecs': 'undefined', 'volume': '1mL', 'pSpeed':'1', 'numCycles': '3', 'loadType': 'undefined'},
                        'Purge':{'opName':'Purge', 'opTime':'00:05:00', 'mixAfterSecs': 'undefined', 'volume': '3mL', 'pSpeed':'1', 'numCycles': 'undefined', 'loadType': 'undefined'},
                        'Load Formalin':{'opName':'Load Formalin', 'opTime':'00:01:30', 'mixAfterSecs': 'undefined', 'volume': '600uL', 'pSpeed':'1', 'numCycles': 'undefined', 'loadType':'Formalin'},
                        'Load Dehydrant':{'opName':'Load Dehydrant', 'opTime':'00:01:30', 'mixAfterSecs': 'undefined', 'volume': '600uL', 'pSpeed':'1', 'numCycles': 'undefined', 'loadType':'Dehydrant'},
                        'Load Stain':{'opName':'Load Stain', 'opTime':'00:01:30', 'mixAfterSecs': 'undefined', 'volume': '600uL', 'pSpeed':'1', 'numCycles': 'undefined', 'loadType':'Stain'},
                        'Load BABB':{'opName':'Load BABB', 'opTime':'00:01:30', 'mixAfterSecs': 'undefined', 'volume': '600uL', 'pSpeed':'1', 'numCycles': 'undefined', 'loadType':'BABB'}
                    }

                    anchors {
                        left: parent.left; right: parent.right; bottom: parent.bottom;
                        top: protInfo.bottom; margins: 5
                    }

                    clip: true
                    model: stepListModDel

                    spacing: 5

                    onModelChanged: {console.log("Model changed?")}

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
//                            console.log(JSON.stringify(stepLView.operDict[drag.source.opName]))
//                                                        var dIndex = stepLView.indexAt(drop.x, drop.y)
//                                                        console.log("Index?: ", dIndex)
//                                                        if(dIndex == -1){
//                                                            stepListModDel.model.append(stepLView.operDict[drag.source.opName])
//                                                        } else if(dIndex == (stepListModDel.items.count-1)){
//                                                            stepListModDel.model.append(stepLView.operDict[drag.source.opName])
//                                                            console.log("End append: ", dIndex)
//                                                        }
//                                                        else {
//                                                            stepListModDel.model.insert(dIndex + 1, stepLView.operDict[drag.source.opName])
//                                                        }
                        }
                    }



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
                    openDialog.open()
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
                    //Validate that mixing and incubation operations are non-zero
                    if(stepListModDel.model.count===0){
                        dataDi.open()
                    } else {
                        saveDialog.open()
                    }
                    
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
                enabled: rootEd.savedPath === '' ? false : true
                
                onClicked: {
                    //Validate protocol
                    //Save to existing file url bypassing opening saveDialog
                    var datamodel = []
                    for (var i = 0; i < stepListModDel.model.count; ++i) datamodel.push(stepListModDel.model.get(i))
                    var datastring = JSON.stringify(datamodel, null, "\t")
                    JSONHelper.saveProtocol(rootEd.savedPath, datastring)
                    console.log("SavedP: ", rootEd.savedPath)
                }
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

                enabled: !rootEd.casNumber == 0 && !rootApWin.isDisconnected

                icon.source: "Icons/rightArrow-black.png"
                icon.color: "green"
                icon.height: 15

                onClicked: {
                    //Confirm/ask for sampleName in dialog box?
                    if (!/\S/.test(rootEd.sampleName)){
                        sampleNameDi.open()
                    //Check if model data is empty
                    } else if (stepListModDel.model.count===0){
                        dataDi.open()
                    //check if saved path is empty, and ask if user wants to save protocol
                    } else if (!/\S/.test(rootEd.savedPath)){
                        saveDi.open()
                    } else {
                        //save before starting run
                        var datamodel = []
                        for (var i = 0; i < stepListModDel.model.count; ++i) datamodel.push(stepListModDel.model.get(i))
                        var datastring = JSON.stringify(datamodel, null, "\t")
                        JSONHelper.saveProtocol(rootEd.savedPath, datastring)
                        console.log("SavedP: ", rootEd.savedPath)
                        //return to sample monitor
                        mainStack.pop(null)
                        //Initialize start protocol with casNumber, model path, runtime, sampleName, protocolName
                        WAMPHandler.startProtocol(rootEd.casNumber, rootEd.savedPath, rootEd.runTime, rootEd.sampleName, rootEd.protocolName)

                    
                    }
                    
                   
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

        if (hours < 10){
            hours = ('0' + hours).slice(-2)
        }

        return hours + ':' + ('0' + minutes).slice(-2) + ':' + ('0' + seconds).slice(-2)
    }

    function estRunTime(model){
        var tally = "00:00:00"
        if (model === null){
            return tally
        }
        if (model.count !== 0){
            for(var i = 0; i < model.count; i++){
                //console.log(i," time ", model.get(i).opTime)
                tally = addTimes(tally, model.get(i).opTime)
                //console.log(tally)
            }
        }
        return tally
    }
    
    MessageDialog {
        id: sampleNameDi
        standardButtons: StandardButton.Ok
        icon: StandardIcon.Critical
        text: "Enter a sample name to start the run."
        title: "Sample name is missing."
        modality: Qt.WindowModal
        onAccepted: {}
    }
    MessageDialog {
        id: dataDi
        standardButtons: StandardButton.Ok
        icon: StandardIcon.Critical
        text: "Model data from protocol is empty. Enter or open a valid protocol!"
        title: "Protocol empty."
        modality: Qt.WindowModal
        onAccepted: {}
    }
    
    MessageDialog {
        id: saveDi
        standardButtons: StandardButton.No | StandardButton.Yes
        icon: StandardIcon.Warning
        text: "Do you want to save protocol before starting run?"
        title: "Saved protocol path empty."
        modality: Qt.WindowModal
        onYes: {
                saveDialog.open()
            }
        onNo: {
                //run without saving protocol....
            
            }
    }
    
    FileDialog {
        id:saveDialog
        selectExisting: false
        folder: mainDir
        nameFilters: [ "Protocol Files (*.json)", "All files (*)" ]
        //nameFilters: [ "*.json", "All files (*)" ]
        defaultSuffix: ".json"
        modality: Qt.WindowModal
        onAccepted: {
            var datamodel = []
            for (var i = 0; i < stepListModDel.model.count; ++i) datamodel.push(stepListModDel.model.get(i))
            var datastring = JSON.stringify(datamodel, null, "\t");
            var path = saveDialog.fileUrl.toString();
            console.log(path)
            // remove prefixed "file:///"
            path = path.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
            path = path.replace(/^(file:)|(qrc:)|(http:)/,"");

            // if path is not actually a path but just a name
            // make it a path by appending it to folder
            console.log("Slash? ", path.includes("/"))
            if(!path.includes("/")){
                var folder = saveDialog.folder.toString();
                folder = folder.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
                path = folder + "/" + path
            }

            // unescape html codes like '%23' for '#'
            var cleanPath = decodeURIComponent(path);

            //Get protocol name
            var protName = cleanPath.split('/').pop()
            rootEd.protocolName = protName.split('.')[0]

            //Check if user saved the file as a .json file
            if(cleanPath.slice(-5) !== ".json"){
                cleanPath = cleanPath.split('.')[0]
                cleanPath = cleanPath + ".json"
            }

            //Send and update savePath
            JSONHelper.saveProtocol(cleanPath, datastring)
            rootEd.savedPath = cleanPath
            console.log("SavedP: ", rootEd.savedPath)
        }

    }

    FileDialog {
        id:openDialog
        selectExisting: true
        folder: mainDir
        nameFilters: [ "Protocol Files (*.json)", "All files (*)" ]
        //nameFilters: [ "*.json", "All files (*)" ]
        defaultSuffix: ".json"
        modality: Qt.WindowModal
        onAccepted: {
            var path = openDialog.fileUrl.toString();
            // remove prefixed "file:///"
            path = path.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
            // unescape html codes like '%23' for '#'
            var cleanPath = decodeURIComponent(path);

            //Get protocol name
            var protName = cleanPath.split('/').pop().split('.')[0]

            //update savedPath
            var pathSaved = cleanPath

            JSONHelper.openProtocol(cleanPath, protName, pathSaved)

        }

    }
}


