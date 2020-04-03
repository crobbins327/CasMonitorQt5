import sys
import os
import time
import datetime
os.chdir("/home/jackr/SampleMonitor/Git/CasMonitor")
from PyQt5 import QtCore, QtGui, QtWidgets
from SampMonitor import *
from ProtEditor import *
from ProtSelector import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #Set mainwindow size
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("MainWindow")
        MainWindow.resize(800, 480)
        MainWindow.setFixedSize(MainWindow.size())
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        
        #Setup widget layout
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.mainStack = QtWidgets.QStackedWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainStack.sizePolicy().hasHeightForWidth())
        self.mainStack.setSizePolicy(sizePolicy)
        self.mainStack.setObjectName("mainStack")
        
        #Initialize widgets and pages
        #mainStack indexes
        #0
        self.protSel = ProtSelector(casNumber=0)
        self.mainStack.addWidget(self.protSel)
        self.protSelNav()
        #1
        self.protEditor = ProtEditor()
        self.mainStack.addWidget(self.protEditor)
        self.protEditorNav()
        print("height: " + str(self.protEditor.stepList.height()))
        print("width: " + str(self.protEditor.stepList.width()))
        
        #2
        self.mainMonitor()
        self.mainStack.setCurrentIndex(2)
        
        
        #Menubar....
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        
        self.menuLoad_Program = QtWidgets.QMenu(self.menubar)
        self.menuLoad_Program.setObjectName("menuLoad_Program")
        self.menuLoad_Program.setTitle("Load Program")
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionEdit = QtWidgets.QAction(MainWindow)
        self.actionEdit.setObjectName("actionEdit")
        self.actionEdit.setText("Edit")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText("Exit")
        self.menuFile.addSeparator()
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionEdit)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuLoad_Program.menuAction())
        
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def protSelNav(self):
        self.protSel.back_ProtSel.connect(lambda: self.mainStack.setCurrentIndex(2))
        self.protSel.new_ProtSel.connect(lambda: self.mainStack.setCurrentIndex(1))
        #After selecting the protocol from the list, run the protocol....
        self.protSel.select_ProtSel.connect(self.runSelProt)
    
    def protEditorNav(self):
        self.protEditor.back_ProtEdit.connect(lambda: self.mainStack.setCurrentIndex(0))
        self.protEditor.home_ProtEdit.connect(lambda: self.mainStack.setCurrentIndex(2))
        #I need to update the protocol selector with the edited program and select it....
        #Break this out into separate function
        self.protEditor.next_ProtEdit.connect(self.nextPEdit)
    
    def nextPEdit(self):
        #Make the protocol selector select and preview protocol from editor
        self.mainStack.setCurrentIndex(0)
        
    def runSelProt(self):
        self.mainStack.setCurrentIndex(2)
        #Update the sample monitor
        print(self.protSel.casNumber)
        monW = self.sampMons[self.protSel.casNumber-1]
        monW.monWidget.setCurrentIndex(0)
        
        #Set protocol and sample name based on last Protocol Selector screen
        # monW.sampName = self.protSel.sampName
        # monW.protName = self.protSel.protName
        
        #Get list of steps and time to complete each step?
        #Print to hidden dialog file the progress of each from the fluid functions
        
        monW.step.setText("Running!")
        start = datetime.datetime.now()
    #     self.timer = QtCore.QTimer()        
    #     self.timer.start(1000)
    #     self.timer.timeout.connect(lambda: self.handleTimer(monW))
        
    # def handleTimer(self, monW):
    #         value = monW.progressBar.value()
    #         if value <= 100:
    #             value = value + 1
    #             monW.progressBar.setValue(value)
    #         else:
    #             self.timer.stop()     
        # if self.completed < 100:
        #     self.completed += 0.0001
        #     # now = datetime.datetime.now()
        #     # td = now-start
        #     # diffstring = ":".join(str(td).split(":")[:2])+":"+str(round(float(str(td).split(":")[2:3][0])))
        #     # monW.time.setText(diffstring)
        #     monW.progressBar.setValue(self.completed)
 
        
    def mainMonitor(self):
        self.mainMonitor = QtWidgets.QWidget()
        self.mainMonitor.setObjectName("mainMonitor")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mainMonitor)
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        self.sampMons = []
        
        #Initializing sample monitors for each cassette
        self.monWidget1 = SampMonitor(casNumber = 1, casDetected = True)
        self.sampMons.append(self.monWidget1)
        self.sampMons[0].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[0]))
        self.gridLayout_2.addWidget(self.monWidget1.monWidget, 0, 0, 1, 1)
                
        self.monWidget2 = SampMonitor(casNumber = 2)
        self.sampMons.append(self.monWidget2)
        self.sampMons[1].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[1]))
        self.gridLayout_2.addWidget(self.monWidget2.monWidget, 0, 1, 1, 1)
        
        self.monWidget3 = SampMonitor(casNumber = 3)
        self.sampMons.append(self.monWidget3)
        self.sampMons[2].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[2]))
        self.gridLayout_2.addWidget(self.monWidget3.monWidget, 0, 2, 1, 1)
                
        self.monWidget4 = SampMonitor(casNumber = 4)
        self.sampMons.append(self.monWidget4)
        self.sampMons[3].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[3]))
        self.gridLayout_2.addWidget(self.monWidget4.monWidget, 1, 0, 1, 1)
                
        self.monWidget5 = SampMonitor(casNumber = 5)
        self.sampMons.append(self.monWidget5)
        self.sampMons[4].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[4]))
        self.gridLayout_2.addWidget(self.monWidget5.monWidget, 1, 1, 1, 1)
                
        self.monWidget6 = SampMonitor(casNumber = 6)
        self.sampMons.append(self.monWidget6)
        self.sampMons[5].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[5]))
        self.gridLayout_2.addWidget(self.monWidget6.monWidget, 1, 2, 1, 1)
        
        self.mainStack.addWidget(self.mainMonitor)
        self.gridLayout.addWidget(self.mainStack, 1, 0, 1, 1)
        
        # Connect monitor slots
        # for i in range(0,6):
        #     self.sampMons[i].switchproSel_SampMon.connect(lambda: self.protSelObj(self.sampMons[i]))
            # print(self.sampMons[i].casNumber)
        
    #Why is it only sending the last connected monW casNumber....?
    @QtCore.pyqtSlot(QtWidgets.QStackedWidget)    
    def protSelObj(self, monW):
        print("This is monWidget"+str(monW.casNumber)+"!")
        self.mainStack.setCurrentIndex(0)
        self.protSel.casLab.setText("Cassette " + str(monW.casNumber) + " -- Select Protocol")
        self.protSel.casNumber = monW.casNumber


    # def updateMonitor(self):
        #Check if cassette is in position
        #Coordinate between active runs and when run finishes
        
       
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

