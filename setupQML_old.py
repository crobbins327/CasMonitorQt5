#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 21:30:01 2020

@author: jackr
"""
import sys
import os
import logging
os.chdir("/home/jackr/SampleMonitor/Git/CasQML")
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
import jsonHelper as jh
import protHandler as ph
import manualMachine as mM
from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/jackr/SampleMonitor/Git/CasQML/prepbot')
import machine
# import controller



if __name__ == '__main__':    
    #Setup logging
    # Global definitions:
    workspace_path = os.getcwd()
    log_path = os.path.join(workspace_path, 'test.log')
    
    # Logger configuration:
    log_level = logging.DEBUG 
    log_format = '%(message)s'
    logger = logging.root
    logger.basicConfig = logging.basicConfig(format=log_format, filename=log_path, level=log_level)
    #logger.basicConfig = logging.basicConfig(format=log_format, level=log_level)
    
    #Setup QML application
    # app = QtGui.QGuiApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)

    json_helper = jh.JSONHelper()
    manPrepbot = mM.manualMachine()
    pHandler = ph.protHandler()

    engine = QtQml.QQmlApplicationEngine()
    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("ManualPrepbot", manPrepbot)
    engine.rootContext().setContextProperty("ProtHandler", pHandler)
    engine.load(QtCore.QUrl('CasMonitor.qml'))
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())