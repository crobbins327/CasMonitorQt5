#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 21:17:52 2020

@author: jackr
"""
from PyQt5 import QtCore
import machine
import logging
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

class manualMachine(QtCore.QObject):
    
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