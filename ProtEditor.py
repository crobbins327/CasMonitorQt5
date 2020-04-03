#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 14:56:31 2020

@author: jackr
"""
from PyQt5 import QtCore, QtGui, QtWidgets

class ProtEditor(QtWidgets.QWidget):
    
    #Emitted signals by buttons
    home_ProtEdit = QtCore.pyqtSignal()
    back_ProtEdit = QtCore.pyqtSignal()
    next_ProtEdit = QtCore.pyqtSignal()
    
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.setObjectName("protEditor")
        self.remButton = QtWidgets.QPushButton(self)
        self.remButton.setGeometry(QtCore.QRect(702, 50, 80, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remButton.sizePolicy().hasHeightForWidth())
        self.remButton.setSizePolicy(sizePolicy)
        self.remButton.setMinimumSize(QtCore.QSize(0, 50))
        self.remButton.setObjectName("remButton")
        self.remButton.setText("Remove")
        
        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setGeometry(QtCore.QRect(702, 300, 80, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveButton.sizePolicy().hasHeightForWidth())
        self.saveButton.setSizePolicy(sizePolicy)
        self.saveButton.setMinimumSize(QtCore.QSize(0, 50))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setText("Save")
        
        self.editButton = QtWidgets.QPushButton(self)
        self.editButton.setGeometry(QtCore.QRect(702, 110, 80, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editButton.sizePolicy().hasHeightForWidth())
        self.editButton.setSizePolicy(sizePolicy)
        self.editButton.setMinimumSize(QtCore.QSize(0, 50))
        self.editButton.setObjectName("editButton")
        self.editButton.setText("Edit")
        
        self.saveAsButton = QtWidgets.QPushButton(self)
        self.saveAsButton.setGeometry(QtCore.QRect(702, 250, 80, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveAsButton.sizePolicy().hasHeightForWidth())
        self.saveAsButton.setSizePolicy(sizePolicy)
        self.saveAsButton.setMinimumSize(QtCore.QSize(0, 50))
        self.saveAsButton.setObjectName("saveAsButton")
        self.saveAsButton.setText("Save As")
        
        self.protNameLab = QtWidgets.QLabel(self)
        self.protNameLab.setGeometry(QtCore.QRect(200, 10, 200, 22))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.protNameLab.sizePolicy().hasHeightForWidth())
        self.protNameLab.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.protNameLab.setFont(font)
        self.protNameLab.setObjectName("protNameLab")
        self.protNameLab.setText("Protocol Name:")
        
        self.protNameEdit = QtWidgets.QLineEdit(self)
        self.protNameEdit.setGeometry(QtCore.QRect(380, 8, 142, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.protNameEdit.sizePolicy().hasHeightForWidth())
        self.protNameEdit.setSizePolicy(sizePolicy)
        self.protNameEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.protNameEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.protNameEdit.setInputMask("")
        self.protNameEdit.setReadOnly(False)
        self.protNameEdit.setObjectName("protNameEdit")
        self.protNameEdit.setText("untitled")
        
        self.homeButton = QtWidgets.QPushButton(self)
        self.homeButton.setGeometry(QtCore.QRect(0, 0, 75, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeButton.sizePolicy().hasHeightForWidth())
        self.homeButton.setSizePolicy(sizePolicy)
        self.homeButton.setText( "Home")
        self.homeButton.setObjectName("homeButton")
        self.homeButton.clicked.connect(self.goHome)
        
        
        self.operationList = QtWidgets.QListWidget(self)
        self.operationList.setGeometry(QtCore.QRect(0, 50, 110, 368))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.operationList.sizePolicy().hasHeightForWidth())
        self.operationList.setSizePolicy(sizePolicy)
        self.operationList.setMinimumSize(QtCore.QSize(110, 0))
        self.operationList.setMaximumSize(QtCore.QSize(100, 16777215))
        self.operationList.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.operationList.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.operationList.setAlternatingRowColors(True)
        self.operationList.setObjectName("operationList")
        self.operationList.addItems(["Wash","Clearing Solution","Stain","Incubation"])
        
        self.stepList = QtWidgets.QListWidget(self)
        self.stepList.setGeometry(QtCore.QRect(111, 50, 590, 368))
        self.stepList.setObjectName("stepList")
        self.stepList.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.stepList.setDefaultDropAction(QtCore.Qt.MoveAction)
        
        
        self.backButton = QtWidgets.QPushButton(self)
        self.backButton.setGeometry(QtCore.QRect(80, 0, 75, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy)
        self.backButton.setMinimumSize(QtCore.QSize(50, 50))
        self.backButton.setObjectName("backButton")
        self.backButton.setText("Back")
        self.backButton.clicked.connect(self.goBack)
        
        self.nextButton = QtWidgets.QPushButton(self)
        self.nextButton.setGeometry(QtCore.QRect(702, 368, 80, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setMinimumSize(QtCore.QSize(0, 50))
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setText("Next")
        self.nextButton.clicked.connect(self.goNext)
        
        
    def goHome(self):
        #Save check dialog
        
        self.home_ProtEdit.emit()
    
    def goBack(self):
        #Save check dialog
        
        self.back_ProtEdit.emit()
    
    def goNext(self):
        #Save as check dialog
        
        self.next_ProtEdit.emit()
        
#Define the collapsable widget class and then inherit the layout for the individual operations
#Get the order of the operations in the list
    #Get the parameters of each operation in the list
    #Estimate the time to completion based on parameters
    #Display completion time on the right
#Add completion time
#Save as protocol file....
        

class CollapsableWidget(QtWidgets.QWidget):
   
    def __init__(self):
        
        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        #Drop down widget
        #Hide and unhide portions of widget?
        self.toggle_button.pressed.connect(self.on_pressed)
    
        
        
    