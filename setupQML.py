#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 21:30:01 2020

@author: jackr
"""
import sys
import os
import logging
import json
import jsonschema
from jsonschema import validate
import logging
# os.chdir("~CasQML/")
# os.chdir("/home/jackr/CasQML/")
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './prepbot')
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



class JSONHelper(QtCore.QObject):
    # Can be redone with getters and setters for the stepModel property. This will be faster with less conversions on the data object.
    # https://qmlbook.github.io/ch18-python/python.html
    
    nextModel = QtCore.pyqtSignal(str, str, str)
    
    @QtCore.pyqtSlot(str, str)
    def saveProtocol(self, fileName, jString):
        # with open(fileName, "w") as outfile: 
        #     json.dump(jString, outfile) 
        with open(fileName, "w") as outfile: 
            outfile.write(jString) 
    
    @QtCore.pyqtSlot(str, str, str)
    def openProtocol(self, fileName, protocolName, pathSaved):
        # take accepted filename and check if it's .json
        jsondata=[]
        try:
            with open(fileName, encoding='utf-8') as data_file:
                jsondata = json.load(data_file)
        except:
            print("An error has occurred with the file selected.")
            return
            
        # validate .json object?
        # check if json object has the propper keys for all elements?
        isValid = self.validateJson(jsondata)
        if not isValid:
            print("JSON has key value error. opName, opTime, mixVol, and loadType are the only keys accepted.")
            return
        else:
            # Send JSON string with file info
            self.nextModel.emit(json.dumps(jsondata), protocolName, pathSaved)
            
    
    def validateJson(self, jsonData):
        # Describe what kind of json you expect.
        # Need to make this more functional with filter masks or regex
        protocolSchema = {
            "type": "array",
            "properties": {
                "opName": {"type": "string"},
                "opTime": {"type": "string"},
                "mixVol": {"type": "string"},
                "loadType": {"type": "string"},
            },
        }
        try:
            validate(instance=jsonData, schema=protocolSchema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True


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
    
    # Testing logger
    logger = logging.root
    logger.basicConfig = logging.basicConfig(format=log_format, filename=log_path, level=log_level)
    #logger.basicConfig = logging.basicConfig(format=log_format, level=log_level)
    logger.info('Testing logger (info)')
    logger.debug('Testing logger (debug)')
    logger.warning('Testing logger (warn)')
    logger.info("")
    #Setup QML application
    app = QtGui.QGuiApplication(sys.argv)

    json_helper = JSONHelper()
    execPrepbot = execMachine()

    engine = QtQml.QQmlApplicationEngine()
    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("ExecPrepbot", execPrepbot)
    engine.load(QtCore.QUrl('CasMonitor.qml'))
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())