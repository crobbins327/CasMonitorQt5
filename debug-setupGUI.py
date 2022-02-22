# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import logging
import logging.config

import asyncio
from qasync import QEventLoop
#from autobahn_autoreconnect import ApplicationRunner
from autobahn.asyncio.wamp import ApplicationRunner
import jsonHelper as jh
import wampHandler as wh
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtQuickControls2 import QQuickStyle

#Setup logging
guilog = logging.getLogger('gui')
qtlog = logging.getLogger('qasync')
qtlog.setLevel(logging.INFO)
guilog.setLevel(logging.INFO)

if __name__ == "__main__":

    # How to set the style for QtQuick :

    # Option 1 - passing or forcing --style argument
    #sys.argv += ['--style', 'material']

    # Option 2 - use QtQuickStyle module
    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        QQuickStyle.setStyle("Material")

#    app = QApplication(sys.argv)
    app = QGuiApplication(sys.argv)

    asyncio_loop = QEventLoop(app)
    asyncio.set_event_loop(asyncio_loop)

    engine = QQmlApplicationEngine()

    #My context properties that signal-slot between python and QML
    json_helper = jh.JSONHelper()
    wHandler = wh.wampHandler()

    engine.rootContext().setContextProperty("JSONHelper", json_helper)
    engine.rootContext().setContextProperty("WAMPHandler", wHandler)
    engine.load(os.fspath(Path(__file__).resolve().parent / "QML/AppStack.qml"))

    # #The WAMP handler will make the WAMP connection so that it can subscribe and send commands through it....
#    runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1")
#    runner.run(wHandler)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
