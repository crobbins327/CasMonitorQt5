#!/home/jackr/anaconda/envs/QML36/bin/python
import sys
import os
import platform
from pathlib import Path
import logging
import logging.config
from colorlog import ColoredFormatter
# os.chdir("/home/eben/CasQML")
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
import jsonHelper as jh
import wampHandler as wh
from PySide2 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
from PySide2.QtQuickControls2 import QQuickStyle
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './prepbot')

import asyncio

#from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp

#from quamash import QEventLoop
from qasync import QEventLoop

#Setup logging
guilog = logging.getLogger('gui')
qtlog = logging.getLogger('qasync')
qtlog.setLevel(logging.INFO)
guilog.setLevel(logging.INFO)

if __name__ == '__main__':
    # How to set the style for QtQuick :

    # Option 1 - passing or forcing --style argument
    #sys.argv += ['--style', 'material']

    # Option 2 - use QtQuickStyle module
    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        QQuickStyle.setStyle("Material")

    #Setup QML application with asynchronous event loop
    app = QtWidgets.QApplication(sys.argv)

    #app = QtGui.QGuiApplication(sys.argv)


    asyncio_loop = QEventLoop(app)
    asyncio.set_event_loop(asyncio_loop)

    engine = QtQml.QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    #My context properties that signal-slot between python and QML
    json_helper = jh.JSONHelper()
    wHandler = wh.wampHandler()

    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("WAMPHandler", wHandler)
    #Load the first QML file onto the engine
#    engine.load(QtCore.QUrl('QML/CasMonitor.qml'))
    engine.load(os.fspath(Path(__file__).resolve().parent / "QML/AppStack.qml"))
    
    
    # #The WAMP handler will make the WAMP connection so that it can subscribe and send commands through it....
    runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1")
    runner.run(wHandler)
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
