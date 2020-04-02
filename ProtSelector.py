#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:04:52 2020

@author: jackr
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class ProtSelector(QtWidgets.QWidget):
    
    #Emitted signals by buttons
    back_ProtSel = QtCore.pyqtSignal()
    new_ProtSel = QtCore.pyqtSignal()
    select_ProtSel = QtCore.pyqtSignal()
    
    def __init__(self, casNumber = 0):
        QtWidgets.QWidget.__init__(self)
        
        # self.protSel = QtWidgets.QWidget()
        # self.protSel.
        
        self.setObjectName("protSel")
        
        self.selButton = QtWidgets.QPushButton(self)
        self.selButton.setGeometry(QtCore.QRect(40, 290, 89, 25))
        self.selButton.setObjectName("selButton")
        self.selButton.setText("Select")
        self.selButton.clicked.connect(self.goSelect)
        
        self.loadButton = QtWidgets.QPushButton(self)
        self.loadButton.setGeometry(QtCore.QRect(220, 290, 89, 25))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.setText("Load")
        
        self.backButton = QtWidgets.QPushButton(self)
        self.backButton.setGeometry(QtCore.QRect(50, 370, 89, 25))
        self.backButton.setObjectName("backButton")
        self.backButton.setText("Back")
        self.backButton.clicked.connect(self.goBack)
        
        self.editButton = QtWidgets.QPushButton(self)
        self.editButton.setGeometry(QtCore.QRect(410, 260, 89, 25))
        self.editButton.setObjectName("editButton")
        self.editButton.setText("Edit")
        
        self.savePtitle = QtWidgets.QLabel(self)
        self.savePtitle.setGeometry(QtCore.QRect(50, 40, 121, 17))
        self.savePtitle.setObjectName("savePtitle")
        self.savePtitle.setText("Saved Protocols")
        
        self.prevLab = QtWidgets.QLabel(self)
        self.prevLab.setGeometry(QtCore.QRect(410, 30, 67, 17))
        self.prevLab.setObjectName("prevLab")
        self.prevLab.setText("Preview Protocol Selected")
        
        self.casLab = QtWidgets.QLabel(self)
        self.casLab.setGeometry(QtCore.QRect(50, 10, 201, 17))
        self.casLab.setObjectName("casLab")
        self.casLab.setText("Cassette " + str(casNumber) + " -- Select Protocol")
        
        self.newButton = QtWidgets.QPushButton(self)
        self.newButton.setGeometry(QtCore.QRect(130, 290, 89, 25))
        self.newButton.setObjectName("newButton")
        self.newButton.setText("New")
        self.newButton.clicked.connect(self.goNew)
        
        self.previewPList = QtWidgets.QListWidget(self)
        self.previewPList.setGeometry(QtCore.QRect(30, 80, 291, 192))
        self.previewPList.setObjectName("previewPList")
        
        
        
        
        
        
        
        
    def goBack(self):
        self.back_ProtSel.emit()
        
    def goNew(self):
        self.new_ProtSel.emit()
        
    def goSelect(self):
        self.select_ProtSel.emit()
        
    
        