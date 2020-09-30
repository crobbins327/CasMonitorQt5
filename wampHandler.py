#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 00:40:29 2020

@author: jackr
"""
from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import jsonHelper as jh
import json
import jsonschema
from time import sleep
import pandas as pd
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import numpy as np
import logging
import logging.config
from colorlog import ColoredFormatter
import asyncio

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp


#Import logger config
logging.config.fileConfig(fname='./Log/init/gui-loggers.ini')
guilog = logging.getLogger('gui')
# rootlog = logging.getLogger('')
colorFormat = ColoredFormatter(
    '%(name)-13s: %(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
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
#Replace on each
guilog.handlers[0].setFormatter(colorFormat)
# rootlog.handlers[0].setFormatter(colorFormat)

class wampHandler(ApplicationSession, QtCore.QObject):
    
    #Globals...
    jHelper = jh.JSONHelper()
    convCas = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F'}
    #CasNumber, protStrings, progstrings, runtime, sampleName, protocolName
    setupProt = QtCore.pyqtSignal(str,'QVariantList','QVariantList',str,str,str)
    startedProt = QtCore.pyqtSignal(int, str, int, int)
    # To repopulate the progress bars when there is a GUI disconnection and rejoin
    # repopulateProt = QtCore.pyqtSignal(str,'QVariantList','QVariantList',int,int,int,int,str,str,str)
    guiJoined = QtCore.pyqtSignal()
    toWaitPopup = QtCore.pyqtSignal(str)
    controllerDCed = QtCore.pyqtSignal()
    controllerJoined = QtCore.pyqtSignal()
    repopulateProt = QtCore.pyqtSignal(int, 'QVariantList','QVariantList', 'QVariantList')
    #To update GUI that cassette is engaged and ready
    casEngaged = QtCore.pyqtSignal(int)
    casDisengaged = QtCore.pyqtSignal(int)
    #To update progress bar. CasNumber of current sample to decrement.
    updateProg = QtCore.pyqtSignal(int)
    upLogChunk = QtCore.pyqtSignal(int, str, int)
    reqLogChunk = QtCore.pyqtSignal(int, str, int)
    #Send shutdown is started
    shutdownStart = QtCore.pyqtSignal(int)
    #Send shutdown is finished
    shutdownDone = QtCore.pyqtSignal(int)
    
    cleanStart = QtCore.pyqtSignal(int)
    cleanDone = QtCore.pyqtSignal(int)
    
    recParam = QtCore.pyqtSignal('QVariantMap')
    
    deadspace = 1000 
    
    def __init__(self, cfg=None):
        ApplicationSession.__init__(self, cfg)
        QtCore.QObject.__init__(self)
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','currentFluid','engaged','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName','startlog','endlog'] ,
                                   index=['casA','casB','casC','casD','casE','casF'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.controllerStatus = 'disconnected'
        self.machineHomed = False
        # self.machineHalted = True
        # self.logsOpen = pd.DataFrame(columns = ['isLogOpen'] ,
        #                            index=['casA','casB','casC','casD','casE','casF','ctrl','machine'], dtype=object)
    
    
    # @wamp.subscribe('com.prepbot.prothandler.heartbeat-gui')
    async def heartbeat(self):
        if self.controllerStatus == 'disconnected':
            self.controllerStatus = 'connected'
            await self.conJoined()
        # if self.machineHomed != machineStatus:
        #     self.machineHomed = machineStatus

    async def get_mStatus(self):
        return(self.machineHomed)

    async def set_mStatus(self, mStatus):
        try:
            if mStatus == True:
                self.machineHomed = True
                # self.machineHalted = False
        except Exception as e:
            guilog.ctrl(e)
        
    async def update(self):
        while True:
            #Manual heartbeating to the controller...
            try:
                await self.call('com.prepbot.prothandler.heartbeat-ctrl')
                # guilog.info('Are you there?')
                if self.controllerStatus == 'disconnected':
                    self.controllerStatus = 'connected'
                    guilog.info('Sending controller joined to GUI!')
                    await self.conJoined()
                    # await self.call('com.prepbot.prothandler.gui-get-param')
            except Exception as e:
                guilog.warning(e)
                guilog.warning('Controller disconnected...')
                if self.controllerStatus == 'connected':
                    self.controllerStatus = 'disconnected'
                    guilog.warning('Sending disconnect to GUI!')
                    await self.conDCed()
            await asyncio.sleep(1)
        
    async def onJoin(self, details):
        guilog.info('Registering GUI functions...')
        self.toWaitPopup.emit('Registering GUI functions to router...')
        try:
            self.register(self.heartbeat, 'com.prepbot.prothandler.heartbeat-gui')
            self.register(self.get_mStatus,'com.prepbot.prothandler.is-machine-homed')
            self.register(self.set_mStatus, 'com.prepbot.prothandler.set-machine-homed')
        except Exception as e:
            guilog.error('Could not register GUI functions to router...')
            guilog.error(e)
        guilog.info('Subscribing to procedures...')
        self.toWaitPopup.emit('Subscribing to procedures...')
        try:
            res = await self.subscribe(self)
            guilog.info("Subscribed to {0} procedure(s)".format(len(res)))
            self.toWaitPopup.emit('Subscribed to procedures!')
        except Exception as e:
            guilog.warning("could not subscribe to procedure: {0}".format(e))
            self.toWaitPopup.emit('Could not subscribe to procedures....')
            
        self.toWaitPopup.emit('Connecting to controller...')
        guilog.info("Connecting to controller...")
        # self.publish('com.prepbot.prothandler.request-tasks-gui')
        try:
            self.toWaitPopup.emit('Getting controller task dataframe...')
            guilog.info("Getting controller task dataframe...")
            taskDFJSON = await self.call('com.prepbot.prothandler.controller-tasks')
            # guilog.info(taskDFJSON)
            self.toWaitPopup.emit('Checking if machine is homed...')
            guilog.info("Checking if machine is homed...")
            self.machineHomed = await self.call('com.prepbot.prothandler.gui-get-machine-homed')
            guilog.info('Machine is homed? : {}'.format(self.machineHomed))
            self.toWaitPopup.emit('Getting controller parameters...')
            guilog.info("Getting controller parameters..")
            await self.call('com.prepbot.prothandler.gui-get-param')
        except Exception as e:
            guilog.warning("Waiting until controller is connected...")
            guilog.warning(e)
            await asyncio.sleep(5)
            self.disconnect()
            self.leave()
        
        self.toWaitPopup.emit('Repopulating GUI with tasks...')
        self.set_tasks_repopulate_all(taskDFJSON)
        self.toWaitPopup.emit('Finished setting tasks and repopulating GUI!')
        guilog.info('Finished setting tasks and repopulating GUI!')
        
        self.toWaitPopup.emit('Reconnecting sample loggers and system logger...')
        # self.reconnect_loggers()
        self.toWaitPopup.emit('Finished reconnecting loggers!')
        guilog.info('Finished reconnecting loggers!')
        
        asyncio.ensure_future(self.update())
        self.guiJoined.emit()
        guilog.info('FINISHED JOIN!')
    
    # @wamp.subscribe('com.prepbot.prothandler.controller-joined')
    async def conJoined(self):
        self.controllerJoined.emit()
    
    # @wamp.subscribe('com.prepbot.prothandler.controller-dced')
    async def conDCed(self):
        self.controllerDCed.emit()
     
        
    # def onLeave(self, details):
    #     print("Left")
    #     print(self.taskDF)
    
    def onDisconnect(self):
        guilog.info("Disconnected GUI")
        guilog.info(self.taskDF)
    
    @QtCore.pyqtSlot(str)
    def execScript(self, linesToExec):
        self.publish('com.prepbot.prothandler.exec-script', linesToExec)
       
    @QtCore.pyqtSlot('QVariantMap')
    def updateParam(self, paramDict):
        # guilog.debug(paramDict)
        self.publish('com.prepbot.prothandler.send-param-controller', paramDict)
        
    @QtCore.pyqtSlot()
    def guiParam(self):
        self.recParam.emit(self.paramDict)
        
    @wamp.subscribe('com.prepbot.prothandler.send-param-gui')
    async def receiveParam(self, paramDict):
        self.paramDict = paramDict
        guilog.debug(paramDict)
        self.recParam.emit(paramDict)
        
    @QtCore.pyqtSlot()
    def stopExecTerminal(self):
        self.publish('com.prepbot.prothandler.exec-stop')
    
    #Takes casNumber and protocol.json
    @QtCore.pyqtSlot(str, str, str, str, str)
    def startProtocol(self, casNumber, protPath, runtime, sampleName, protocolName):
        #Check current run status on cassette...
        #Error if run already in progress
        #Error if interpretter cannot interpret protocol
        #Interpret protocol and make list of strings to be executed
        casL, protStrings, progStrings, stepTimes = self.interpret(casNumber, protPath)

        #Start progress bar and track steps completed in protocol for current sample...
        #Setup run by sending info to progress bar and sending protStrings
        self.setupProt.emit(casNumber,progStrings,stepTimes, runtime, sampleName, protocolName)
        #update taskDF
        self.taskDF.loc['cas{}'.format(casL)] = np.array(['running',0,np.nan,'unk',True,protStrings, progStrings, stepTimes, sampleName,protPath,protocolName,np.nan,np.nan],dtype=object)
        guilog.debug(self.taskDF)
        #Send protocol to controller to add to Q
        self.publish('com.prepbot.prothandler.start', casL, self.taskDF.loc['cas{}'.format(casL)].to_json())
        #update log
        guilog.info('cas{}: Starting protocol:\n{}\n{}\n{}'.format(casL,protStrings,progStrings,stepTimes))
    
    #Separate start of gui when protocol is actually started on controller???
    #Hang until the start signal is actually received?
    @wamp.subscribe('com.prepbot.prothandler.started')
    async def startedGUIProtocol(self, casName, taskJSON, samplelog, currentEnd):
        self.taskDF.loc[casName] = pd.read_json(taskJSON, typ='series', dtype=object)
        #prepare run details chunk
        start = int(self.taskDF.loc[casName,'startlog'])
        guilog.debug('start: {} stop: {}'.format(start, int(currentEnd)))
        # samplelog, currentEnd = await self.call('com.prepbot.prothandler.caslog-chunk', casL=casName[-1], start=start, end=0)
        #emit start signal
        casNumber = int(self.__get_key(casName[-1], self.convCas))
        # guilog.debug(currentEnd,'Testing end getter')
        guilog.info('{}: Confirmed protocol and sending sample log.'.format(casName))
        self.startedProt.emit(casNumber, samplelog, start, int(currentEnd))
        
    
    #It may be faster to load the log into chunks rather than requesting all of the log from start to end line
    #The GUI is prone to sending too many calls to refreshRunDet and this causes there to be too many update chunks
    #Also, the current code in the controller has blocking elements that cause the log to propogate slower than the runstep progress...
    #Try adding an asyncio.sleep at the end/beg of each controller protocol step to hope that the updateLogChunk function can be called more often?
    
    @QtCore.pyqtSlot(str, int)
    def refreshRunDet(self, casNumber, currentEnd):
        casL = self.convCas[int(casNumber)]
        casName = 'cas{}'.format(casL)
        start = int(self.taskDF.loc[casName,'startlog'])
        print(start)
        end = int(self.taskDF.loc[casName,'endlog'])
        print(end)
        guilog.info('{}: Requesting a refresh on run details log.'.format(casName))
        # print(self.taskDF.loc[casName])
        #Request next lines (limit=1000) in the log at the current end
        # asyncio.ensure_future(self.updateLogChunk(casL, start=currentEnd+1, end=0))
        asyncio.ensure_future(self.requestLogChunk(casL, start=start, end=end))
        
    
    async def requestLogChunk(self, casL, start, end):
        samplelog, currentEnd = await self.call('com.prepbot.prothandler.caslog-chunk', casL, start, end)
        if len(samplelog) > 0:
            guilog.info('cas{}: Request run details log'.format(casL))
            guilog.debug('\n{}'.format(samplelog))
            casNumber = int(self.__get_key(casL, self.convCas))
            self.reqLogChunk.emit(casNumber, samplelog, int(currentEnd))
        else:
            guilog.info('cas{}: Nothing more to request for run details log'.format(casL))
            pass
    
    @wamp.subscribe('com.prepbot.prothandler.update-cas-log')
    async def updateLogChunk(self, casL, samplelog, currentEnd):
        #Receive log chunk
        if len(samplelog) > 0:
            guilog.info('cas{}: Update run details log'.format(casL))
            guilog.debug('\n{}'.format(samplelog))
            casNumber = int(self.__get_key(casL, self.convCas))
            self.upLogChunk.emit(casNumber, samplelog, int(currentEnd))
        else:
            guilog.info('cas{}: Nothing to update for run details log'.format(casL))
            pass
    
    
    @QtCore.pyqtSlot(str)
    def stopProtocol(self, casNumber):
        casL = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.stop', casL)
        #mark as stopped in taskDF
        guilog.info('cas{}: Requesting to stop run...'.format(casL))
        self.taskDF.loc['cas{}'.format(casL),'status'] = 'stopped'
    
    @QtCore.pyqtSlot(str)
    def nextProtocol(self, casNumber):
        casL = self.convCas[int(casNumber)]
        #Trust the GUI for speed.... if it reached the next button by mistake startProtocol will catch the error
        # self.publish('com.prepbot.prothandler.next', casL)
        self.taskDF.loc['cas{}'.format(casL),'status'] = 'idle'
    
    @wamp.subscribe('com.prepbot.prothandler.start-clean')
    async def start_clean(self, casL):
        await asyncio.sleep(1)
        guilog.info('\nCleaning Line of cas{}!!!\n'.format(casL))
        casNumber = int(self.__get_key(casL, self.convCas))
        self.cleanStart.emit(casNumber)
    
    #Currently isNext does nothing and is always False
    @wamp.subscribe('com.prepbot.prothandler.finish-clean')
    async def finish_clean(self, casL, taskJSON, isNext=False):
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(casL, self.convCas))
        self.taskDF.loc['cas{}'.format(casL)] = pd.read_json(taskJSON, typ='series', dtype=object)
        if not isNext:
            self.cleanDone.emit(casNumber)
    
    @wamp.subscribe('com.prepbot.prothandler.start-shutdown')
    async def start_shutown(self, casL):
        await asyncio.sleep(1)
        guilog.info('\nSHUTTING DOWN cas{}!!!\n'.format(casL))
        casNumber = int(self.__get_key(casL, self.convCas))
        self.shutdownStart.emit(casNumber)
    
    #Currently isNext does nothing and is always False
    @wamp.subscribe('com.prepbot.prothandler.finish-shutdown')
    async def finish_shutown(self, casL, taskJSON, isNext=False):
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(casL, self.convCas))
        self.taskDF.loc['cas{}'.format(casL)] = pd.read_json(taskJSON, typ='series', dtype=object)
        if not isNext:
            self.shutdownDone.emit(casNumber)
    
    #GUI waits until cassette is actually engaged before able to start a protocol
    @QtCore.pyqtSlot(str)
    def engageCas(self, casNumber):
        casL = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.engage', casL)
    
    @wamp.subscribe('com.prepbot.prothandler.ready')
    def casReady(self, casL, engageBool):
        casNumber = int(self.__get_key(casL, self.convCas))
        print(casNumber)
        if engageBool:
            self.casEngaged.emit(casNumber)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = True
            guilog.info('Cas{} engage complete'.format(casL))
        else:
            self.casDisengaged.emit(casNumber)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            guilog.info('Cas{} disengage complete'.format(casL))
    
    #When the disengage button is hit, the GUI immediately switches away from the engaged screen
    #Deactivate the engage button until disengage is completed
    @QtCore.pyqtSlot(str)
    def disengageCas(self, casNumber):
        casL = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.disengage', casL)
        
    @wamp.subscribe('com.com.prepbot.prothandler.secs-remaining')
    async def update_runtime(self, casL, secsRem):
        await asyncio.sleep(1)
        self.taskDF.loc['cas{}'.format(casL), 'secsRemaining'] = secsRem
        guilog.info("cas{}: Getting seconds remaining for current step.... {}secs".format(casL,secsRem))
        guilog.debug('\n{}'.format(self.taskDF.loc['cas{}'.format(casL)]))
    
    @wamp.subscribe('com.prepbot.prothandler.progress')
    async def update_progress(self, casL, taskJSON):
        #Prevent stopped or shutdown runs from updating???
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(casL, self.convCas))
        guilog.info('cas{}: Updating progress to next step'.format(casL))
        self.updateProg.emit(casNumber)
        #Replace entry in taskDF
        self.taskDF.loc['cas{}'.format(casL)] = pd.read_json(taskJSON, typ='series', dtype=object)
        guilog.debug("\n{}".format(self.taskDF.loc['cas{}'.format(casL)]))
        
    @wamp.subscribe('com.prepbot.prothandler.update-taskdf')
    async def update_taskDF(self, casL, taskJSON):
        #Prevent stopped or shutdown runs from updating???
        await asyncio.sleep(1)
        #Replace entry in taskDF
        guilog.info('Updating GUI task DF.')
        self.taskDF.loc['cas{}'.format(casL)] = pd.read_json(taskJSON, typ='series', dtype=object)
        guilog.debug("\n{}".format(self.taskDF.loc['cas{}'.format(casL)]))
    
    
    @wamp.subscribe('com.prepbot.prothandler.one-task-to-gui')
    def set_tasks_repopulate_one(self, casName, taskJSON):
        self.taskDF.loc[casName] = pd.read_json(taskJSON, typ='series', dtype=object)
        self.repopulate_one_GUI(casName)
        #Repopulate logs?
    
    def repopulate_one_GUI(self, casName):
        casNumber = int(self.__get_key(casName[-1], self.convCas))
        
        if self.taskDF.loc[casName,'status'].isin(['running','cleaning','finished','stopping','shutdown']):
            otherVars = self.taskDF.loc[casName,['stepNum','secsRemaining','sampleName','protocolName','status']].tolist()
            # otherVars.append(totalSecs)
            # otherVars.append(tremSecs)
            # print('\npre-Emitted???')
            guilog.info("{}: Repopulating GUI task".format(casName))
            guilog.debug("\n{}".format(self.taskDF.loc[casName]))
            # print(self.taskDF.loc[casName,'progressNames'])
            # print(self.taskDF.loc[casName,'stepTimes'])
            # print(otherVars)
            self.repopulateProt.emit(casNumber,
                                  self.taskDF.loc[casName,'progressNames'],
                                  self.taskDF.loc[casName,'stepTimes'],
                                  otherVars)
            # print('Emitted???')
            
        elif self.taskDF.loc[casName,'engaged']:
            guilog.info('Emitting engages! {}'.format(casName))
            self.casEngaged.emit(casNumber)
    
    
    @wamp.subscribe('com.prepbot.prothandler.tasks-to-gui')
    def set_tasks_repopulate_all(self, taskDFJSON):
        cTasks = pd.read_json(taskDFJSON, typ='frame', dtype=object)
        if cTasks.equals(self.taskDF):
            guilog.info('Controller has same taskDF as GUI')
            #Repopulate anyways??
            self.repopulate_all_GUI()
            #Repopulate logs
        else:
            guilog.info('Repopulating GUI with controller procedures!')
            # print(cTasks)
            self.taskDF = cTasks
            self.repopulate_all_GUI()
            #Repopulate logs
    
    def repopulate_all_GUI(self):
        runfin = self.taskDF[self.taskDF.status.isin(['running','cleaning','finished','stopping','shutdown'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running','cleaning','finished','stopping','shutdown'])].index
        
        for i in self.taskDF.index:
            # print(i)
            # print(i in runfin)
            if i in runfin:
                casNumber = int(self.__get_key(i[-1], self.convCas))
                # stepNum = self.taskDF.loc[i,'stepNum']
                # secsRem = self.taskDF.loc[i,'secsRemaining']
                # totalSecs = sum(self.taskDF.loc[i,'stepTimes'])
                # tremSecs = sum(self.taskDF.loc[i,'stepTimes'][stepNum:]) + secsRem
                otherVars = self.taskDF.loc[i,['stepNum','secsRemaining','sampleName','protocolName','status']].tolist()
                # otherVars.append(totalSecs)
                # otherVars.append(tremSecs)
                guilog.info("{}: Repopulating GUI task".format(i))
                guilog.debug("\n{}".format(self.taskDF.loc[i]))
                # print('\npre-Emitted???')
                # print(i, casNumber)
                # print(self.taskDF.loc[i])
                # print(self.taskDF.loc[i,'progressNames'])
                # print(self.taskDF.loc[i,'stepTimes'])
                # print(otherVars)
                self.repopulateProt.emit(casNumber,
                                      self.taskDF.loc[i,'progressNames'],
                                      self.taskDF.loc[i,'stepTimes'],
                                      otherVars)
                # print('Emitted???')
            elif i in engagedCas:
                guilog.info('Emitting engages! {}'.format(i))
                self.casEngaged.emit(int(self.__get_key(i[-1], self.convCas)))
        
        # guilog.debug("Restore connection with logger(s)......NOT IMPLEMENTED YET...")
        
        #restore connection with logger + rundetails.....
    
    
    # @wamp.subscribe('com.prepbot.prothandler.updateguitasks')
    # def update_tasks(self):
        
    
    def interpret(self, casNumber, protPath):
        #Convert casNumber to sample letter...
        casL = self.convCas[int(casNumber)]
        #Open/Read .json file as a list of dictionaries
        jsonprot = self.jHelper.openToRun(protPath)
        #Strings to execute for protocol->controller
        protstrings = list()
        #Strings for the progress bar
        progstrings = list()
        #Strings for keeping track of runtime
        stepTimes = list()
        #Need to pump out fluid in chamber before loading new fluid....
        for i in range(len(jsonprot)):
            oper = jsonprot[i]
            #Check volume string
            if oper['volume'].lower() == 'undefined':
                pass
            elif oper['volume'][-2:].lower() == 'ul':
                mL = False
            elif oper['volume'][-2:].lower() == 'ml':
                mL = True
            else:
                guilog.error('Volume in protocol step {} is not defined ({})! Use "undefined", mL, or uL for volume'.format(i,oper['volume']))
                break
                    
            fluidType = 'undefined'
            # print(oper)
            if oper['opName'] == 'Incubation':
                inc = self.__incubate(casL, oper['opTime'], oper['mixAfterSecs'])
                protstrings.append(inc)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Mixing':
                mix = self.__mix(casL, oper['numCycles'], oper['volume'], mL=mL)
                protstrings.append(mix)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Purge':
                rem = self.__purge(casL, oper['volume'], mL=mL)
                protstrings.append(rem)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load Formalin':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], oper['washSyr'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Stain':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], oper['washSyr'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load BABB':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], oper['washSyr'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Dehydrant':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], oper['washSyr'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Custom':
                protstrings.append('print("Custom loading reagent....")')
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            else:
                guilog.error('Operation "{}" not in protocol operations!'.format(oper['opName']))
        return(casL, protstrings, progstrings, stepTimes)
            
    

    def __get_key(self, val, my_dict): 
        for key, value in my_dict.items(): 
             if val == value: 
                 return key 
      
        return 0


    #For each dictionary, case switch or if elif opName
    #to make strings to be executed
    def __get_sec(self, time_str):
        #Get Seconds from time.
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

    def __incubate(self, casL, runtime, mixAfter):
        #Convert runtime hh:mm:ss into seconds
        incubateTime = self.__get_sec(runtime)
        
        if mixAfter == 'undefined':
            mixAfter = 0
        # incubate_time_sec =  10
        #Mix every 2x seconds
        # wash_interval = mixAfter
        # washF = int(incubateTime/wash_interval)
        # incStr = '''
        # print('INCUBATING DYE')
        # for i in range({}):
        #     # print('i=',i)
        #     for j in range({}):
        #         sleep(1)
        #         print("Sample{} Seconds remaining: ", ({}-j-(i*{})))
        #     if ((i % 2) == 0):
        #         print('Mix')
        #         machine.pump_in(0.5)
        #         sleep(2)
        #         machine.pump_out(0.5)
        # '''.format(washF,wash_interval,casL,incubateTime,wash_interval)
        incStr = 'self.incubate(casL="{}",incTime={},mixAfter={})'.format(casL,incubateTime,mixAfter)
        return(incStr)
                
    def __mix(self, casL, numCycles, volume, mL=False):
        #Check if volume is in uL or mL??
        if mL:
            vol = float(volume[:-2])
        else:
            vol = float(volume[:-2])/1000
        mixStr = 'self.mix(casL="{}", numCycles={}, volume={})'.format(casL,numCycles,vol)
        return(mixStr)
        
    def __purge(self, casL, volume, mL=False):
        #Check if volume is in uL or mL??
        if mL:
            vol = float(volume[:-2])
        else:
            vol = float(volume[:-2])/1000
        #Convert to mL for machine pump in/out command
#         deVol = vol + self.deadspace/1000
        # purgeStr = '''
        # print('PURGING CHAMBER')
        # machine.goto_sample{}()
        # machine.pump_in({})
        # sleep(5)
        # machine.empty_syringe()
        # '''.format(casL,deVol)
        purgeStr = 'self.purge(casL="{}")'.format(casL)
        return(purgeStr)
        
    def __load_reagent(self, casL, volume, speed, loadType, washSyr, mL=False):
        reaConv = {'Dehydrant':'meoh','BABB':'babb',
                   'Formalin':'formalin','Stain':'vial'}
        #Check if volume is in uL or mL??
        if mL:
            vol = float(volume[:-2])
        else:
            vol = float(volume[:-2])/1000
        #Convert to mL for machine pump in/out command
        # deVol = vol + self.deadspace/1000
        if washSyr == 'true':
            washSyrBool = True
        else:
            washSyrBool = False
            
        # loadString = '''
        # print('ADDING {}')
        # machine.goto_{}()
        # machine.pump_in({},{})
        # sleep(5)
        # machine.goto_sample{}()
        # machine.pump_out({},{})
        # '''.format(loadType,reaConv[loadType],vol,speed,casL,deVol,speed)
        loadStr= 'self.loadReagent(casL="{}",reagent="{}",vol={},speed={}, washSyr={}, loadstr="{}")'.format(casL, reaConv[loadType], vol, speed, washSyrBool, loadType)
        return(loadStr)
        
    
    