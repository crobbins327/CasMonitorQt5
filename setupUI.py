import sys
import os
# os.chdir("/home/jackr/SampleMonitor/Git/CasMonitor")
from PyQt5 import QtCore, QtGui, QtWidgets
from SampMonitor import *
from ProtEditor import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #Set mainwindow size
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("MainWindow")
        MainWindow.resize(800, 480)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
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
        
        self.protSel(casNumber = 0)
        self.protEditor = ProtEditor()
        self.mainStack.addWidget(self.protEditor)
        
        self.mainMonitor()
        self.mainStack.setCurrentIndex(2)
        
        

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
        
    def print_test(self):
        print("testing")
        
    def protSel(self, casNumber = 0):
        self.protSel = QtWidgets.QWidget()
        self.protSel.setObjectName("protSel")
        
        self.selButton = QtWidgets.QPushButton(self.protSel)
        self.selButton.setGeometry(QtCore.QRect(40, 290, 89, 25))
        self.selButton.setObjectName("selButton")
        self.selButton.setText("Select")
        self.selButton.clicked.connect(self.print_test)
        
        self.loadButton = QtWidgets.QPushButton(self.protSel)
        self.loadButton.setGeometry(QtCore.QRect(220, 290, 89, 25))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.setText("Load")
        
        self.backButton = QtWidgets.QPushButton(self.protSel)
        self.backButton.setGeometry(QtCore.QRect(50, 370, 89, 25))
        self.backButton.setObjectName("backButton")
        self.backButton.setText("Back")
        
        self.editButton = QtWidgets.QPushButton(self.protSel)
        self.editButton.setGeometry(QtCore.QRect(410, 260, 89, 25))
        self.editButton.setObjectName("editButton")
        self.editButton.setText("Edit")
        
        self.savePtitle = QtWidgets.QLabel(self.protSel)
        self.savePtitle.setGeometry(QtCore.QRect(50, 40, 121, 17))
        self.savePtitle.setObjectName("savePtitle")
        self.savePtitle.setText("Saved Protocols")
        
        self.prevLab = QtWidgets.QLabel(self.protSel)
        self.prevLab.setGeometry(QtCore.QRect(410, 30, 67, 17))
        self.prevLab.setObjectName("prevLab")
        self.prevLab.setText("Preview Protocol Selected")
        
        self.casLab = QtWidgets.QLabel(self.protSel)
        self.casLab.setGeometry(QtCore.QRect(50, 10, 201, 17))
        self.casLab.setObjectName("casLab")
        self.casLab.setText("Cassette " + str(casNumber) + " -- Select Protocol")
        
        self.newButton = QtWidgets.QPushButton(self.protSel)
        self.newButton.setGeometry(QtCore.QRect(130, 290, 89, 25))
        self.newButton.setObjectName("newButton")
        self.newButton.setText("New")
        
        self.previewPList = QtWidgets.QListWidget(self.protSel)
        self.previewPList.setGeometry(QtCore.QRect(30, 80, 291, 192))
        self.previewPList.setObjectName("previewPList")
        
        self.mainStack.addWidget(self.protSel)
    
    
    def mainMonitor(self):
        self.mainMonitor = QtWidgets.QWidget()
        self.mainMonitor.setObjectName("mainMonitor")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mainMonitor)
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        #Initializing sample monitors for each cassette
        self.monWidget1 = SampMonitor(casNumber = 1)
        self.monWidget1.monWidget.setCurrentIndex(1)
        # self.monWidget1.setupB.clicked.connect(MainWindow.monWidget1.monWidget.hide)
        self.gridLayout_2.addWidget(self.monWidget1.monWidget, 0, 0, 1, 1)
                
        self.monWidget2 = SampMonitor(casNumber = 2)
        self.monWidget2.monWidget.setCurrentIndex(1)
        self.gridLayout_2.addWidget(self.monWidget2.monWidget, 0, 1, 1, 1)
        
        self.monWidget3 = SampMonitor(casNumber = 3)
        self.monWidget3.monWidget.setCurrentIndex(1)
        self.gridLayout_2.addWidget(self.monWidget3.monWidget, 0, 2, 1, 1)
                
        self.monWidget4 = SampMonitor(casNumber = 4)
        self.monWidget4.monWidget.setCurrentIndex(0)
        self.gridLayout_2.addWidget(self.monWidget4.monWidget, 1, 0, 1, 1)
                
        self.monWidget5 = SampMonitor(casNumber = 5)
        self.monWidget5.monWidget.setCurrentIndex(0)
        self.gridLayout_2.addWidget(self.monWidget5.monWidget, 1, 1, 1, 1)
                
        self.monWidget6 = SampMonitor(casNumber = 6)
        self.monWidget6.monWidget.setCurrentIndex(0)
        self.gridLayout_2.addWidget(self.monWidget6.monWidget, 1, 2, 1, 1)
        
        
        self.mainStack.addWidget(self.mainMonitor)
        self.gridLayout.addWidget(self.mainStack, 1, 0, 1, 1)
        
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

