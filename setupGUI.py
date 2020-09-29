#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 21:30:01 2020

@author: jackr
"""
import sys
import os
import logging
import logging.config
from colorlog import ColoredFormatter
# os.chdir("/home/eben/CasQML")
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
import jsonHelper as jh
import wampHandler as wh
import manualMachine as mM
from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './prepbot')
import machine
# import controller

import asyncio

# from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp

from quamash import QEventLoop

guilog = logging.getLogger('gui')
quamashlog = logging.getLogger('quamash')
quamashlog.setLevel(logging.INFO)
guilog.setLevel(logging.DEBUG)

if __name__ == '__main__':    
    #Setup logging
    # Global definitions:
    # workspace_path = os.getcwd()
    # log_path = os.path.join(workspace_path, 'test.log')
    
    # Logger configuration:
    # log_level = logging.DEBUG 
    # log_format = '%(message)s'
    # logger = logging.root
    # logger.basicConfig = logging.basicConfig(format=log_format, filename=log_path, level=log_level)
    #logger.basicConfig = logging.basicConfig(format=log_format, level=log_level)
    
    #Setup QML application with asynchronous event loop
    app = QtWidgets.QApplication(sys.argv)
    
    asyncio_loop = QEventLoop(app)
    asyncio.set_event_loop(asyncio_loop)
    
    engine = QtQml.QQmlApplicationEngine()
    #My context properties that signal-slot between python and QML
    json_helper = jh.JSONHelper()
    manPrepbot = mM.manualMachine()
    wHandler = wh.wampHandler()

    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("ManualPrepbot", manPrepbot)
    engine.rootContext().setContextProperty("WAMPHandler", wHandler)
    engine.load(QtCore.QUrl('CasMonitor.qml'))
    
    # #The WAMP handler will make the WAMP connection so that it can subscribe and send commands through it....
    runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1")
    runner.run(wHandler)
    
    
    

    # json_helper = jh.JSONHelper()
    # manPrepbot = mM.manualMachine()
    # pHandler = ph.protHandler()

    # engine = QtQml.QQmlApplicationEngine()
    # engine.rootContext().setContextProperty("JSONHelper", json_helper)
    # engine.rootContext().setContextProperty("ManualPrepbot", manPrepbot)
    # engine.rootContext().setContextProperty("ProtHandler", pHandler)
    # engine.load(QtCore.QUrl('CasMonitor.qml'))
    
    # if not engine.rootObjects():
    #     sys.exit(-1)
    # sys.exit(app.exec())