import QtQuick 2.14
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import QtQml.Models 2.12
//import Qt.labs.platform 1.1
import QtQuick.Dialogs 1.3
import Qt.labs.folderlistmodel 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls.Material 2.12
//import QtQuick.VirtualKeyboard 2.12

import "./Icons/"

Item {
    id: rootSel
//    width: 800
//    height: 400
    property int casNumber: 0
    property variant stepModel: ListModel{}
    property string mainDir: rootApWin.mainDir
    property string sampleName: ''
    property string protocolName: 'Protocol Name'
    property string savedPath: ''
    property string runTime: estRunTime(rootSel.stepModel)
    property string defPath: rootApWin.defPath
    property string defProtName: rootApWin.defProtName
    property string operatingSystem: rootApWin.operatingSystem

    signal reNextModel(string jsondata, string protName, string pathSaved)
    Component.onCompleted: {
//        console.log('completed Selector!')
        JSONHelper.nextModel.connect(reNextModel)
        checkDefaultProt()
    }
    
    Connections {
        target: rootSel
        function onReNextModel(jsondata, protName, pathSaved) {
            stepModel.clear()
            //console.log(jsondata)
            var datamodel = JSON.parse(jsondata)
            //console.log(datamodel)
            for (var i = 0; i < datamodel.length; ++i) stepModel.append(datamodel[i])
            
            //Set protocol name
            rootSel.protocolName = protName
            
            //update savedPath
            rootSel.savedPath = pathSaved
//            console.log("SavedP: ", rootSel.savedPath)
        }
    }

    Rectangle {
        id: rootSelBG
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

//        color: "dimgray"
//        Material.theme: Material.Dark
//        Material.accent: Material.Blue
//        Material.primary:
        color: Material.backgroundColor


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
                width: 60
                height: 60
                anchors.left: parent.left
                anchors.leftMargin: 20
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter
                flat: true

                icon.source: "Icons/home-run.png"
                icon.color: "white"
                icon.height: 60
                icon.width: 60

                onClicked: {mainStack.pop(null)}
            }

            Button {
                id: backB
                width: 60
                height: 60
                display: AbstractButton.IconOnly
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: homeB.right
                anchors.leftMargin: 20
                flat: true

                icon.source: "Icons/back.png"
                icon.color: "white"
                icon.height: 60
                icon.width: 60


                onClicked: {mainStack.pop()}
            }

            Button {
                id: settingsB
                x: 692
                y: 8
                width: 60
                height: 60
                display: AbstractButton.IconOnly
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                flat: true

                icon.source: "Icons/settings-icon.png"
                icon.color: "white"
                icon.height: 60
                icon.width: 60


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
                id: protSelLab
                x: 327
                y: 23
                width: 173
                height: 25
                color: "#ffffff"
                text: qsTr("Protocol Selector")
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.weight: Font.Medium
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.pointSize: 16
            }
        }



        Rectangle {
            id: rootSelTangle
            color: "transparent"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: menuRect.bottom
            anchors.topMargin: 10

            Rectangle {
                id: recFileSel
                width: 300
                height: parent.height
                anchors {left: rootSelTangle.left; top: rootSelTangle.top; bottom: rootSelTangle.bottom}
                color: "#999999"
                radius: 5

                ListView {
                    id: fileSelector
                    anchors.bottom: buttonSel.top
                    anchors.right: parent.right
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors {topMargin: 35; bottomMargin: 0}
                    clip: true
                    highlightFollowsCurrentItem: true
                    spacing: 0

                    model: FolderListModel {
                        id: folderListModel
                        showDirsFirst: true
                        showDirs: true
                        showFiles: true
//                        rootFolder: "file:///home/jackr/"
                        folder: mainDir
                        nameFilters: ["*.json"]
                    }

                    delegate: Button {
                        id: fileButton
                        width: fileSelector.width
                        height: 50
                        text: fileName
//                        opacity: fileButton.down || fileButton.checked || fileButton.highlighted ? 0.5 : 1
                        flat: true
                        onClicked: {
                            if (fileIsDir) {
                                folderListModel.folder = fileURL
                            } else {
                                //read file i/o
                                var path = fileURL.toString();
                                // remove prefixed "file:///"
                                path = path.replace(/^(file:\/{3})|(qrc:\/{3})|(http:\/{3})/,"");
                                // unescape html codes like '%23' for '#'
                                var cleanPath = decodeURIComponent(path);
                                
                                //change protocol name with file name less .json
//                                console.log("path ", cleanPath)
                                var protName = fileName.split('.')[0]
                                
                                //change savedPath location
                                var pathSaved = cleanPath
                                
                                JSONHelper.openProtocol(cleanPath, protName, pathSaved)
                                //change data model on preview screen using reNextModel
                            }
                        }

                        contentItem: Item {
                            id: element
                            RowLayout{
                                id: elementRow
                                spacing: 5
                                Image {
                                    source: fileIsDir ? "Icons/color-folder-240.png" : "Icons/color-document-240.png"
                                    Layout.preferredHeight: 30
                                    Layout.preferredWidth: 30
                                    Layout.maximumHeight: 30
                                    Layout.maximumWidth: 30
                                    Layout.minimumHeight: 15
                                    Layout.minimumWidth: 15
                                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                                }
                                Text {
                                    text: fileButton.text
                                    elide: Text.ElideRight
                                    fontSizeMode: Text.Fit
                                    font.pointSize: 11
                                    horizontalAlignment: Text.AlignLeft
                                    verticalAlignment: Text.AlignVCenter
                                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                                    Layout.maximumWidth: fileButton.width-60
                                    Layout.maximumHeight: 40
                                }
                            }

                        }

//                        background: Rectangle {
//                            color: fileIsDir ? "whitesmoke" : "whitesmoke"
//                            border.color: "black"
//                        }
                    }
                }

                Rectangle {
                    id: buttonSel
                    y: 351
                    height: 50
                    color: "#242424"
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    radius: 5

                    Button {
                        id: openDirB
                        y: 3
                        height: 45
                        text: qsTr("Open Protocol")
                        font.capitalization: Font.MixedCase
                        anchors.left: backFileB.right
                        anchors.right: parent.right
                        anchors.rightMargin: 7
                        anchors.leftMargin: 40
                        anchors.verticalCenter: parent.verticalCenter
                        display: AbstractButton.TextBesideIcon
                        font.pointSize: 12
                        Material.theme: Material.Light
                        Material.foreground: "black"

                        onClicked: {openDialog.open()}
                    }

                    Button {
                        id: backFileB
                        height: 45
                        text: qsTr("Back")
                        font.capitalization: Font.MixedCase
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 7
                        font.pointSize: 12
                        display: AbstractButton.TextBesideIcon
                        Material.theme: Material.Light
                        Material.foreground: "black"

                        onClicked: folderListModel.folder = folderListModel.parentFolder
                    }
                }
            }

            Rectangle {
                id: recStepList
                anchors {
                    left: recFileSel.right; top: rootSelTangle.top; bottom: rootSelTangle.bottom
                    leftMargin: 10
                }
                height: parent.height
                color: "whitesmoke"
                radius: 5
                anchors.right: parent.right
                anchors.rightMargin: 0



                DelegateModel {
                    id: stepListModDel


                    model: stepModel
                    delegate: chooser

                }

                DelegateChooser {
                    id: chooser
                    role: "opName"
                    DelegateChoice { roleValue: "Incubation"; PSelContent{}}

                    DelegateChoice { roleValue: "Mixing"; PSelContent{}}

                    DelegateChoice { roleValue: "Purge"; PSelContent{}}

                    DelegateChoice { roleValue: "Load Formalin"; PSelContent{}}

                    DelegateChoice { roleValue: "Load Dehydrant"; PSelContent{}}

                    DelegateChoice { roleValue: "Load Stain"; PSelContent{}}

                    DelegateChoice { roleValue: "Load BABB"; PSelContent{}}

                }



                ListView {
                    id: stepListView

//                    property var operDict: {
//                        'Incubation':{'opName':'Incubation','opTime':'00:00:00', 'mixAfterSecs':'0'},
//                        'Mixing':{'opName':'Mixing','opTime':'00:00:00','mixVol': '1'},
//                        'Purge':{'opName':'Purge'},
//                        'Load Formalin':{'opName':'Load Formalin','loadType':'Formalin'},
//                        'Load Dehydrant':{'opName':'Load Dehydrant','loadType':'Dehydrant'},
//                        'Load Stain':{'opName':'Load Stain','loadType':'Stain'},
//                        'Load BABB':{'opName':'Load BABB','loadType':'BABB'}
//                    }

                    anchors.margins: 5
                    anchors.bottomMargin: 0
                    anchors.top: protInfo.bottom
                    anchors.right: parent.right
                    anchors.bottom: buttonStep.top
                    anchors.left: parent.left

                    clip: true
                    model: stepListModDel

                    spacing: 5

                }

                Rectangle {
                    id: buttonStep
                    y: 351
                    height: 50
                    color: "#242424"
                    radius: 5
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 0
                    anchors.rightMargin: 0
                    anchors.bottomMargin: 0

                    Button {
                        id: startB
                        width: 100
                        height: 45
                        text: qsTr("Start")
                        font.capitalization: Font.MixedCase
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 7
                        font.pointSize: 12
                        padding: 0
                        rightPadding: 0
                        leftPadding: 0
                        layer.wrapMode: ShaderEffectSource.ClampToEdge
                        display: AbstractButton.TextBesideIcon
                        Material.theme: Material.Light
                        Material.foreground: "black"

                        icon.source: "Icons/rightArrow-black.png"
                        icon.color: "green"
                        icon.height: 15

                        enabled: !rootApWin.isDisconnected

                        onClicked: {
                            //Confirm/ask for sampleName in dialog box?
                            if (!/\S/.test(rootSel.sampleName)){
                                sampleNameDi.open()
                            //Check if model data is empty
                            } else if (stepListModDel.model.count===0){
                                dataDi.open()
                            } else {
                                //return to sample monitor
                                mainStack.pop(null)
                                //Initialize start protocol with casNumber, model path, runtime, sampleName, protocolName
//                                console.log(rootSel.casNumber)
//                                console.log(rootSel.savedPath)
//                                console.log(rootSel.runTime)
//                                console.log(rootSel.sampleName)
//                                console.log(rootSel.protocolName)
                                WAMPHandler.startProtocol(rootSel.casNumber, rootSel.savedPath, rootSel.runTime, rootSel.sampleName, rootSel.protocolName)


                            }
                        }
                    }

                    Button {
                        id: editB
                        height: 45
                        text: qsTr("Edit Protocol")
                        font.capitalization: Font.MixedCase
                        anchors.left: parent.left
                        anchors.leftMargin: 7
                        anchors.verticalCenterOffset: 0
                        font.pointSize: 12
                        display: AbstractButton.TextBesideIcon
                        anchors.verticalCenter: parent.verticalCenter
                        Material.theme: Material.Light
                        Material.foreground: "black"
                        
                        enabled: stepModel.count > 0 ? true : false
                        
                        onClicked: {mainStack.push("ProtocolEditor.qml",{casNumber: casNumber, sampleName: sampleName, protocolName: protocolName, stepModel: stepModel, savedPath: savedPath})}
                        
                        
                    }

                    Button {
                        id: newB
                        height: 45
                        text: qsTr("New Protocol")
                        font.capitalization: Font.MixedCase
                        anchors.left: editB.right
                        anchors.leftMargin: 15
                        anchors.verticalCenterOffset: 0
                        font.pointSize: 12
                        display: AbstractButton.TextBesideIcon
                        anchors.verticalCenter: parent.verticalCenter
                        Material.theme: Material.Light
                        Material.foreground: "black"

                        onClicked: {mainStack.push("ProtocolEditor.qml",{casNumber: casNumber, sampleName: sampleName})}
                    }
                }

                BevelRect {
                    id: protInfo
                    height: 75
                    color: "#242424"
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    radius: 30

                    Rectangle {
                        id: sampRec
                        y: 48
                        width: 269
                        height: 31
                        color: "#808080"
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 8
                        anchors.left: parent.left
                        anchors.leftMargin: 8

                        TextInput {
                            id: sampInput
                            property string placeholderText: "Enter Sample Name..."
                            font.capitalization: Font.MixedCase
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

                            onEditingFinished: {
                                sampleName = sampInput.text
//                                console.log(sampleName)
                            }

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
                        id: protName
                        width: 269
                        height: 22
                        color: "#ffffff"
                        text: protocolName
                        elide: Text.ElideMiddle
                        verticalAlignment: Text.AlignTop
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        font.pointSize: 12
                        font.weight: Font.Medium
                    }

                    Text {
                        id: casNum
                        x: 9
                        width: 97
                        height: 25
                        color: "#ffffff"
                        text: "Cassette " + casNumber
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        anchors.right: parent.right
                        anchors.rightMargin: 16
                        font.weight: Font.Medium
                        font.pointSize: 14
                    }

                    Text {
                        id: runTime
                        x: 10
                        y: 15
                        width: 83
                        height: 25
                        color: "#ffffff"
                        text: stepModel.count > 0 ?  rootSel.runTime : "- - : - - : - -"
                        anchors.right: parent.right
                        anchors.rightMargin: 23
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 8
                        anchors.horizontalCenter: casNum.horizontalCenter
                        font.pointSize: 14
                        font.weight: Font.Medium
                    }

                }

            }


        }

    }
    

    function checkDefaultProt(){
        if (/\S/.test(rootSel.defPath)){
            JSONHelper.openProtocol(rootSel.defPath, rootSel.defProtName, rootSel.defPath)
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

    FileDialog {
        id: openDialog
        selectFolder: false
        folder: mainDir
        nameFilters: ["Protocol Files (*.json)", "All files (*)"]
        modality: Qt.WindowModal
        onAccepted: {
            //if selected, change the directory folder
            folderListModel.folder = openDialog.folder

            //open protocol
            var path = openDialog.fileUrl.toString();
            if (rootApWin.operatingSystem == 'Windows'){
                //IF WINDOWS
                // remove prefixed "file:///"
                path = path.replace(/^(file:\/{3})|(qrc:\/{3})|(http:\/{3})/,"");
            } else {
                //IF LINUX OR OTHER
                // remove prefixed "file://"  only 2 /'s
                path = path.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
            }
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


