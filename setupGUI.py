#!/home/jackr/anaconda/envs/QML36/bin/python
import sys
import os
import logging
import logging.config
from colorlog import ColoredFormatter
# os.chdir("/home/eben/CasQML")
# os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
import jsonHelper as jh
import wampHandler as wh
from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './prepbot')

import asyncio

# from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp

from quamash import QEventLoop

#Setup logging
guilog = logging.getLogger('gui')
quamashlog = logging.getLogger('quamash')
quamashlog.setLevel(logging.INFO)
guilog.setLevel(logging.INFO)

if __name__ == '__main__':    
    #Setup QML application with asynchronous event loop
    app = QtWidgets.QApplication(sys.argv)
    
    asyncio_loop = QEventLoop(app)
    asyncio.set_event_loop(asyncio_loop)
    
    engine = QtQml.QQmlApplicationEngine()
    #My context properties that signal-slot between python and QML
    json_helper = jh.JSONHelper()
    wHandler = wh.wampHandler()

    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("WAMPHandler", wHandler)
    #Load the first QML file onto the engine
    engine.load(QtCore.QUrl('QML/CasMonitor.qml'))
    
    # #The WAMP handler will make the WAMP connection so that it can subscribe and send commands through it....
    runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1")
    runner.run(wHandler)
    