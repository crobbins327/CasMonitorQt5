#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 21:30:01 2020

@author: jackr
"""
import sys
import os
import logging
# os.chdir("~CasQML/")
os.chdir("/home/jackr/SampleMonitor/Git/CasQML/")
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
import jsonHelper as jh
import protHandler as ph
from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/jackr/SampleMonitor/Git/CasQML/prepbot')
import machine
import controller
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



class execMachine(QtCore.QObject):
    
    startOp = QtCore.pyqtSignal(str, str, str)
    
    @QtCore.pyqtSlot()
    def connect(self):
        machine.connect()
        print("Connected")
        logger.info("Pressed connect button")
        
    @QtCore.pyqtSlot()
    def home(self):
        print("Homed")
        logger.info("Pressed home button")
        machine.reset()
        machine.home()
        
    @QtCore.pyqtSlot()
    # def halt(self):
    #     controller.halt()
    @QtCore.pyqtSlot()
    def engageSampleD(self):
        machine.engage_sampleD()
    @QtCore.pyqtSlot()
    def disengageSampleD(self):
        machine.disengage_sampleD()
    
    @QtCore.pyqtSlot()
    def btn_waste(self):
        machine.goto_waste()
        
    @QtCore.pyqtSlot()
    def btn_formalin(self):
        machine.goto_formalin()

    @QtCore.pyqtSlot()  
    def btn_meoh(self):
        machine.goto_meoh()

    @QtCore.pyqtSlot()   
    def btn_babb(self):
        machine.goto_babb()

    @QtCore.pyqtSlot()   
    def btn_sample(self):
        machine.goto_sampleD()

    @QtCore.pyqtSlot()   
    def btn_vial(self):
        machine.goto_vial()

    @QtCore.pyqtSlot()    
    def btn_park(self):
        machine.goto_park()

    @QtCore.pyqtSlot()
    def btn_pumpin(self, vol=None):
        machine.pump_in(vol)

    @QtCore.pyqtSlot()    
    def btn_pumpout(self, vol=None):
        machine.pump_out(vol)

    @QtCore.pyqtSlot()
    def btn_dyeprocess(self):
        machine.dye_process()

    @QtCore.pyqtSlot()
    def btn_purge(self):
        machine.purge_syringe()


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
    execPrepbot = execMachine()
    pHandler = ph.protHandler()

    engine = QtQml.QQmlApplicationEngine()
    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("ExecPrepbot", execPrepbot)
    engine.rootContext().setContextProperty("ProtHandler", pHandler)
    engine.load(QtCore.QUrl('CasMonitor.qml'))
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())