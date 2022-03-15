
from PySide2 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
import jsonHelper as jh
import json
import jsonschema
from time import sleep
import datetime
import numpy as np
import pandas as pd
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
from collections import OrderedDict
import logging
import logging.config
from colorlog import ColoredFormatter
import asyncio
import platform

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
    
    #Self Globals...
    jHelper = jh.JSONHelper()
    #CasNumber, protStrings, progstrings, runtime, sampleName, protocolName
    setupProt = QtCore.Signal(str, 'QVariantList', 'QVariantList', str, str, str)
    startedProt = QtCore.Signal(int, str, int, int)
    # To repopulate the progress bars when there is a GUI disconnection and rejoin
    # repopulateProt = QtCore.Signal(str,'QVariantList','QVariantList',int,int,int,int,str,str,str)
    guiJoined = QtCore.Signal()
    toWaitPopup = QtCore.Signal(str)
    controllerDCed = QtCore.Signal()
    controllerJoined = QtCore.Signal()
    repopulateProt = QtCore.Signal(int, 'QVariantList', 'QVariantList', 'QVariantList')
    #To update GUI that cassette is engaged and ready
    casEngaged = QtCore.Signal(int)
    casDisengaged = QtCore.Signal(int)
    #To update progress bar. CasNumber of current sample to decrement.
    updateProg = QtCore.Signal(int)
    upLogChunk = QtCore.Signal(int, str, int)
    reqLogChunk = QtCore.Signal(int, str, int)
    updateCasTemps = QtCore.Signal(int, float, int)
    #Send shutdown is started
    shutdownStart = QtCore.Signal(int)
    #Send shutdown is finished
    shutdownDone = QtCore.Signal(int)
    
    cleanStart = QtCore.Signal(int)
    cleanDone = QtCore.Signal(int)
    
    recParam = QtCore.Signal('QVariantMap')

    def getOS(self):
        if platform.system() == 'Windows':
            return 'Windows'
        elif platform.system() == 'Linux':
            return 'Linux'
        else:
            return 'Other'

    #Don't really need to change the OS once it has been set
    @QtCore.Signal
    def sendOS(self):
        pass

    OS = QtCore.Property(str, getOS, notify=sendOS)

    def getAvailCasNum(self):
        return self._availCasNum

    # @QtCore.Signal
    # def sendAvailCasNum(self):
    #     return self._availCasNum

    sendAvailCasNum = QtCore.Signal(int) 

    availCasNum = QtCore.Property(int, getAvailCasNum, notify=sendAvailCasNum)
    
    def __init__(self, config=None):
        QtCore.QObject.__init__(self)
        ApplicationSession.__init__(self, config=config)
        #Could change index to number of available CAS in DF, but not super important... A couple extra rows won't change performance too much.
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','currentFluid','volInLine','engaged','protocolList','progressNames',
                                              'stepTimes','sampleName','protocolPath','protocolName','startlog','endlog'] ,
                                   index=['CAS1','CAS2','CAS3','CAS4','CAS5','CAS6'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.controllerStatus = 'disconnected'
        self.machineHomed = False
        self.paramDict = OrderedDict()
        self.reaConv = {'Dehydrant': 'MEOH',
                        'BABB': 'BABB',
                        'Formalin': 'FORMALIN',
                        'Stain': 'DYE'}
        #Used to initiallize GUI but will be replaced OnJoin()
        self.convCas = {1:'CAS1', 2:'CAS2', 3:'CAS3', 4:'CAS4', 5:'CAS5', 6:'CAS6'}
        self._availCasNum = 6
        self.casTemps = {k: {'current': 25.0, 'set': 47} for k in self.convCas.values()}
        guilog.debug(platform.uname())


            #signal to gui
        # self.machineHalted = True
        # self.logsOpen = pd.DataFrame(columns = ['isLogOpen'] ,
        #                            index=['casA','casB','casC','casD','casE','casF','ctrl','machine'], dtype=object)
    
    #Override because of QObject disconnect()
    def disconnect(self):
        if self._transport:
            self._transport.close()
    
    # @wamp.subscribe('com.prepbot.prothandler.heartbeat-gui')
    async def heartbeat(self):
        if self.controllerStatus == 'disconnected':
            self.controllerStatus = 'connected'
            await self.conJoined()
        # if self.machineHomed != machineStatus:
        #     self.machineHomed = machineStatus

    # async def get_homeStatus(self):
    #     return(self.machineHomed)

    async def set_homeStatus(self, homeStatus):
        try:
            if homeStatus:
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
            await asyncio.sleep(30)
        
    async def onJoin(self, details):
        guilog.info('Registering GUI functions...')
        self.toWaitPopup.emit('Registering GUI functions to router...')
        try:
            self.register(self.heartbeat, 'com.prepbot.prothandler.heartbeat-gui')
            # self.register(self.get_homeStatus,'com.prepbot.prothandler.is-machine-homed')
            self.register(self.set_homeStatus, 'com.prepbot.prothandler.set-machine-homed')
            guilog.info('Registered all procedures!')
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

        try:
            self.toWaitPopup.emit('Getting hardware lock and homing...')
            guilog.info("Getting hardware lock and homing...")
            self.machineHomed = await self.call('com.prepbot.prothandler.gui-get-machine-homed')
            guilog.info('Machine is homed? : {}'.format(self.machineHomed))
            self.toWaitPopup.emit('Getting available cassettes... updating GUI...')
            guilog.info("Getting available cassettes..")
            availCas = await self.call('com.prepbot.prothandler.gui-get-available-cas')
            self._availCasNum = len(availCas)
            self.sendAvailCasNum.emit(self._availCasNum)
            self.convCas = {k+1: v for k, v in enumerate(availCas)}
            guilog.info('convCas: {}'.format(self.convCas))
            self.toWaitPopup.emit('Getting cassette temperatures... updating GUI...')
            guilog.info("Getting cassette temperatures..")
            self.casTemps = await self.call('com.prepbot.prothandler.gui-refresh-cas-temps')
            self.toWaitPopup.emit('Getting controller parameters...')
            guilog.info("Getting controller parameters..")
            await self.call('com.prepbot.prothandler.gui-get-param')
            self.toWaitPopup.emit('Getting controller task dataframe...')
            guilog.info("Getting controller task dataframe...")
            taskDFJSON = await self.call('com.prepbot.prothandler.controller-tasks')
            self.toWaitPopup.emit('Repopulating GUI with tasks...')
            self.set_tasks_repopulate_all(taskDFJSON)
        except Exception as e:
            guilog.warning("Waiting until controller is connected...")
            guilog.warning(e)
            await asyncio.sleep(5)
            self.leave()
            self.disconnect()
        
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
    
    @wamp.subscribe('com.prepbot.prothandler.controller-dced')
    async def conDCed(self):
        self.controllerDCed.emit()
     
        
    # def onLeave(self, details):
    #     print("Left")
    #     print(self.taskDF)
    
    def onDisconnect(self):
        guilog.info("Disconnected GUI")
        guilog.info(self.taskDF)

    @QtCore.Slot()
    def closeApp(self):
    	self.call('com.prepbot.prothandler.discconnect-ctrl')


    @QtCore.Slot(str)
    def execScript(self, linesToExec):
        self.publish('com.prepbot.prothandler.exec-script', linesToExec)
       
    @QtCore.Slot('QVariantMap')
    def updateParam(self, paramDict):
        # guilog.debug(paramDict)
        self.publish('com.prepbot.prothandler.send-param-controller', paramDict)
        
    @QtCore.Slot()
    def guiParam(self):
        self.recParam.emit(self.paramDict)
        
    @wamp.subscribe('com.prepbot.prothandler.send-param-gui')
    async def receiveParam(self, paramDict):
        self.paramDict = paramDict
        guilog.debug(paramDict)
        # self.recParam.emit(paramDict)

        
    @QtCore.Slot()
    def stopExecTerminal(self):
        self.publish('com.prepbot.prothandler.exec-stop')
    
    #Takes casNumber and protocol.json
    @QtCore.Slot(str, str, str, str, str)
    def startProtocol(self, casNumber, protPath, runtime, sampleName, protocolName):
        #Check current run status on cassette...
        #Error if run already in progress
        #Error if interpretter cannot interpret protocol
        #Interpret protocol and make list of strings to be executed
        cas, protStrings, progStrings, stepTimes = self.interpret(casNumber, protPath)

        #Start progress bar and track steps completed in protocol for current sample...
        #Setup run by sending info to progress bar and sending protStrings
        # self.publish('com.prepbot.prothandler.setup-protocol', casNumber, progStrings, stepTimes, runtime, sampleName, protocolName)
        if runtime == 'undefined':
        	#Calculate runtime from stepTimes in seconds
        	totalSecs = sum(stepTimes)
        	runtime = str(datetime.timedelta(seconds=totalSecs))


        self.setupProt.emit(casNumber, progStrings, stepTimes, runtime, sampleName, protocolName)
        #update taskDF
        self.taskDF.loc[cas] = np.array(['running', 0, np.nan, 'unk', 0, True, protStrings, progStrings,
                                         stepTimes, sampleName, protPath, protocolName, np.nan, np.nan], dtype=object)
        guilog.debug(self.taskDF)
        #Send protocol to controller to add to Q
        self.publish('com.prepbot.prothandler.start', cas, self.taskDF.loc[cas].to_json())
        #update log
        guilog.info('{}: Starting protocol:\n{}\n{}\n{}'.format(cas, protStrings, progStrings, stepTimes))
    
    
    @wamp.subscribe('com.prepbot.prothandler.setup-protocol')
    async def setupProtocol(self, casNumber, progStrings, stepTimes, runtime, sampleName, protocolName):
        self.setupProt.emit(casNumber, progStrings, stepTimes, runtime, sampleName, protocolName)
    
    #Separate start of gui when protocol is actually started on controller???
    #Hang until the start signal is actually received?
    @wamp.subscribe('com.prepbot.prothandler.started')
    async def startedGUIProtocol(self, cas, taskJSON, samplelog, currentEnd):
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        #prepare run details chunk
        start = int(self.taskDF.loc[cas, 'startlog'])
        guilog.debug('start: {} stop: {}'.format(start, int(currentEnd)))
        # samplelog, currentEnd = await self.call('com.prepbot.prothandler.caslog-chunk', cas=cas, start=start, end=0)
        #emit start signal
        casNumber = int(self.__get_key(cas, self.convCas))
        # guilog.debug(currentEnd,'Testing end getter')
        guilog.info('{}: Confirmed protocol and sending sample log.'.format(cas))
        self.startedProt.emit(casNumber, samplelog, start, int(currentEnd))
        
    
    #It may be faster to load the log into chunks rather than requesting all of the log from start to end line
    #The GUI is prone to sending too many calls to refreshRunDet and this causes there to be too many update chunks
    #Also, the current code in the controller has blocking elements that cause the log to propogate slower than the runstep progress...
    #Try adding an asyncio.sleep at the end/beg of each controller protocol step to hope that the updateLogChunk function can be called more often?
    
    @QtCore.Slot(str, int)
    def refreshRunDet(self, casNumber, currentEnd):
        cas = self.convCas[int(casNumber)]
        start = int(self.taskDF.loc[cas, 'startlog'])
        end = int(self.taskDF.loc[cas, 'endlog'])
        guilog.info('{}: Requesting a refresh on run details log. Lines {} to {}.'.format(cas, start, end))
        #Request next lines (limit=1000) in the log at the current end
        # asyncio.ensure_future(self.updateLogChunk(cas, start=currentEnd+1, end=0))
        asyncio.ensure_future(self.requestLogChunk(cas, start=start, end=end))

    @wamp.subscribe('com.prepbot.prothandler.refresh-cas-temps-gui')
    async def receiveCasTemps(self, newCasTemps):
        for c in newCasTemps.keys():
            nCurrT = round(newCasTemps[c]['current'], 1)
            currT = round(self.casTemps[c]['current'], 1)
            nSetT = int(newCasTemps[c]['set'])
            setT = int(self.casTemps[c]['set'])

            if nSetT != setT or nCurrT != currT:
                casNumber = self.__get_key(c, self.convCas)
                newCasTemps[c]['current'] = nCurrT
                newCasTemps[c]['set'] = nSetT
                self.updateCasTemps.emit(casNumber, nCurrT, nSetT)

        self.casTemps = newCasTemps
        guilog.info(self.casTemps)


    @QtCore.Slot(int)
    def refreshTemps(self, casNumber=0):
        if casNumber == 0:
            guilog.info('refeshing all temps')
            #call a funciton to fetch current temps
            self.call('com.prepbot.prothandler.gui-refresh-cas-temps')
        else:
            guilog.info('refreshing temp of CAS {}'.format(casNumber))
            guilog.warn('currently not implemented!')

    @QtCore.Slot(int, int)
    def setCasTemp(self, casNumber, setTemp):
        cas = self.convCas[int(casNumber)]
        guilog.info('requesting to set temp of {} to {} C'.format(cas, setTemp))
        self.call('com.prepbot.prothandler.gui-set-one-cas-temp', cas, setTemp)
    
    async def requestLogChunk(self, cas, start, end):
        samplelog, currentEnd = await self.call('com.prepbot.prothandler.caslog-chunk', cas, start, end)
        if len(samplelog) > 0:
            guilog.info('{}: Request run details log'.format(cas))
            guilog.debug('\n{}'.format(samplelog))
            casNumber = int(self.__get_key(cas, self.convCas))
            self.reqLogChunk.emit(casNumber, samplelog, int(currentEnd))
        else:
            guilog.info('{}: Nothing more to request for run details log'.format(cas))
            pass
    
    @wamp.subscribe('com.prepbot.prothandler.update-cas-log')
    async def updateLogChunk(self, cas, samplelog, currentEnd):
        #Receive log chunk
        if len(samplelog) > 0:
            guilog.info('{}: Update run details log'.format(cas))
            guilog.debug('\n{}'.format(samplelog))
            casNumber = int(self.__get_key(cas, self.convCas))
            self.upLogChunk.emit(casNumber, samplelog, int(currentEnd))
        else:
            guilog.info('{}: Nothing to update for run details log'.format(cas))
            pass
    
    
    @QtCore.Slot(str)
    def stopProtocol(self, casNumber):
        cas = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.stop', cas)
        #mark as stopped in taskDF
        guilog.info('{}: Requesting to stop run...'.format(cas))
        self.taskDF.loc[cas, 'status'] = 'stopped'
    
    @QtCore.Slot(str)
    def nextProtocol(self, casNumber):
        cas = self.convCas[int(casNumber)]
        #Trust the GUI for speed.... if it reached the next button by mistake startProtocol will catch the error
        # self.publish('com.prepbot.prothandler.next', cas)
        self.taskDF.loc[cas, 'status'] = 'idle'
    
    @wamp.subscribe('com.prepbot.prothandler.start-clean')
    async def start_clean(self, cas):
        await asyncio.sleep(1)
        guilog.info('\nCleaning Line of {}!!!\n'.format(cas))
        casNumber = int(self.__get_key(cas, self.convCas))
        self.cleanStart.emit(casNumber)
    
    #Currently isNext does nothing and is always False
    @wamp.subscribe('com.prepbot.prothandler.finish-clean')
    async def finish_clean(self, cas, taskJSON, isNext=False):
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(cas, self.convCas))
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        if not isNext:
            self.cleanDone.emit(casNumber)
    
    @wamp.subscribe('com.prepbot.prothandler.start-shutdown')
    async def start_shutown(self, cas):
        await asyncio.sleep(1)
        guilog.info('\nSHUTTING DOWN {}!!!\n'.format(cas))
        casNumber = int(self.__get_key(cas, self.convCas))
        self.shutdownStart.emit(casNumber)
    
    #Currently isNext does nothing and is always False
    @wamp.subscribe('com.prepbot.prothandler.finish-shutdown')
    async def finish_shutown(self, cas, taskJSON, isNext=False):
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(cas, self.convCas))
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        if not isNext:
            self.shutdownDone.emit(casNumber)
    
    #GUI waits until cassette is actually engaged before able to start a protocol
    @QtCore.Slot(str)
    def engageCas(self, casNumber):
        cas = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.engage', cas)
    
    @wamp.subscribe('com.prepbot.prothandler.ready')
    def casReady(self, cas, engageBool, insertError=False):
        casNumber = int(self.__get_key(cas, self.convCas))
        if engageBool:
            self.casEngaged.emit(casNumber)
            self.taskDF.loc[cas, 'engaged'] = True
            guilog.info('{} engage complete'.format(cas))
        elif insertError:
            #Make a warning popup when there is an insert error
            # self.casInsertError.emit(casNumber)
            self.taskDF.loc[cas, 'engaged'] = False
            guilog.warning('{} is not inserted!'.format(cas))
            self.casDisengaged.emit(casNumber)
        else:
            self.casDisengaged.emit(casNumber)
            self.taskDF.loc[cas, 'engaged'] = False
            guilog.info('{} disengage complete'.format(cas))
    
    #When the disengage button is hit, the GUI immediately switches away from the engaged screen
    #Deactivate the engage button until disengage is completed
    @QtCore.Slot(str)
    def disengageCas(self, casNumber):
        cas = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.disengage', cas)
        
    @wamp.subscribe('com.com.prepbot.prothandler.secs-remaining')
    async def update_runtime(self, cas, secsRem):
        await asyncio.sleep(1)
        self.taskDF.loc[cas, 'secsRemaining'] = secsRem
        guilog.info("{}: Getting seconds remaining for current step.... {}secs".format(cas, secsRem))
        guilog.debug('\n{}'.format(self.taskDF.loc[cas]))
    
    @wamp.subscribe('com.prepbot.prothandler.progress')
    async def update_progress(self, cas, taskJSON):
        #Prevent stopped or shutdown runs from updating???
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(cas, self.convCas))
        guilog.info('{}: Updating progress to next step'.format(cas))
        self.updateProg.emit(casNumber)
        #Replace entry in taskDF
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        guilog.debug("\n{}".format(self.taskDF.loc[cas]))
        
    @wamp.subscribe('com.prepbot.prothandler.update-taskdf')
    async def update_taskDF(self, cas, taskJSON):
        #Prevent stopped or shutdown runs from updating???
        await asyncio.sleep(1)
        #Replace entry in taskDF
        guilog.debug('Updating GUI task DF.')
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        guilog.debug("\n{}".format(self.taskDF.loc[cas]))
    
    
    @wamp.subscribe('com.prepbot.prothandler.one-task-to-gui')
    def set_tasks_repopulate_one(self, cas, taskJSON):
        self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
        self.repopulate_one_GUI(cas)
        #Repopulate logs?
    
    def repopulate_one_GUI(self, cas):
        casNumber = int(self.__get_key(cas, self.convCas))
        
        if self.taskDF.loc[cas,'status'] in ['running','cleaning','finished','stopping','shutdown']:
            otherVars = self.taskDF.loc[cas, ['stepNum','secsRemaining','sampleName','protocolName','status']].tolist()

            guilog.info("{}: Repopulating GUI task".format(cas))
            guilog.debug("\n{}".format(self.taskDF.loc[cas]))

            self.repopulateProt.emit(casNumber,
                                  self.taskDF.loc[cas,'progressNames'],
                                  self.taskDF.loc[cas,'stepTimes'],
                                  otherVars)
            
        elif self.taskDF.loc[cas, 'engaged']:
            guilog.info('Emitting engages! {}'.format(cas))
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
            self.taskDF = cTasks
            self.repopulate_all_GUI()
            #Repopulate logs
    
    def repopulate_all_GUI(self):
        runfin = self.taskDF[self.taskDF.status.isin(['running','cleaning','finished','stopping','shutdown'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running','cleaning','finished','stopping','shutdown'])].index
        
        for i in self.taskDF.index:
            if i in runfin:
                casNumber = int(self.__get_key(i, self.convCas))
                # stepNum = self.taskDF.loc[i,'stepNum']
                # secsRem = self.taskDF.loc[i,'secsRemaining']
                # totalSecs = sum(self.taskDF.loc[i,'stepTimes'])
                # tremSecs = sum(self.taskDF.loc[i,'stepTimes'][stepNum:]) + secsRem
                otherVars = self.taskDF.loc[i, ['stepNum','secsRemaining','sampleName','protocolName','status']].tolist()
                # otherVars.append(totalSecs)
                # otherVars.append(tremSecs)
                guilog.info("{}: Repopulating GUI task".format(i))
                guilog.debug("\n{}".format(self.taskDF.loc[i]))

                self.repopulateProt.emit(casNumber,
                                      self.taskDF.loc[i,'progressNames'],
                                      self.taskDF.loc[i,'stepTimes'],
                                      otherVars)

            elif i in engagedCas:
                guilog.info('Emitting engages! {}'.format(i))
                self.casEngaged.emit(int(self.__get_key(i, self.convCas)))
        
        # guilog.debug("Restore connection with logger(s)......NOT IMPLEMENTED YET...")
        
        #restore connection with logger + rundetails.....
    
    
    # @wamp.subscribe('com.prepbot.prothandler.updateguitasks')
    # def update_tasks(self):
        
    
    def interpret(self, casNumber, protPath):
        #Convert casNumber to sample letter...
        cas = self.convCas[int(casNumber)]
        #Open/Read .json file as a list of dictionaries
        jsonprot = self.jHelper.openToRun(protPath)
        #Strings to execute for protocol->controller
        protstrings = list()
        #Strings for the progress bar
        progstrings = list()
        #Strings for keeping track of runtime
        stepTimes = list()
        #Need to pump out fluid in chamber before loading new fluid....
        #Check that JSON variables are indeed the expected variables... Help to protect from malicious code/wrong variable types.
        for i in range(len(jsonprot)):
            oper = jsonprot[i]
            #Check volume string
            # if oper['volume'].lower() == 'undefined':
            #     pass
            # elif oper['volume'][-2:].lower() == 'ul':
            #     mL = False
            # elif oper['volume'][-2:].lower() == 'ml':
            #     mL = True
            # else:
            #     guilog.error('Volume in protocol step {} is not defined ({})! Use "undefined", mL, or uL for volume'.format(i, oper['volume']))
            #     break

            if oper['opName'] == 'Incubation':
                inc = self.__incubate(cas, oper['opTime'], oper['mixAfterSecs'], oper['volume'], oper['extraVolOut'])
                protstrings.append(inc)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Mixing':
                mix = self.__mix(cas, oper['numCycles'], oper['volume'])
                protstrings.append(mix)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Purge':
                rem = self.__purge(cas)
                protstrings.append(rem)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load Formalin':
                load = self.__load_reagent(cas, oper['loadType'], oper['volume'], oper['inSpeed'], oper['chamberSpeed'],
                                           oper['lineSpeed'], oper['washSyr'], oper['washReagent'])
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load Stain':
                load = self.__load_reagent(cas, oper['loadType'], oper['volume'], oper['inSpeed'], oper['chamberSpeed'],
                                           oper['lineSpeed'], oper['washSyr'], oper['washReagent'])
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load BABB':
                load = self.__load_reagent(cas, oper['loadType'], oper['volume'], oper['inSpeed'], oper['chamberSpeed'],
                                           oper['lineSpeed'], oper['washSyr'], oper['washReagent'])
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load Dehydrant':
                load = self.__load_reagent(cas, oper['loadType'], oper['volume'], oper['inSpeed'], oper['chamberSpeed'],
                                           oper['lineSpeed'], oper['washSyr'], oper['washReagent'])
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            elif oper['opName'] == 'Load Custom':
                protstrings.append('print("Custom loading reagent....")')
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
            else:
                guilog.error('Operation "{}" not in protocol operations!'.format(oper['opName']))
        return(cas, protstrings, progstrings, stepTimes)
            
    

    def __get_key(self, val, my_dict): 
        for key, value in my_dict.items(): 
             if val == value: 
                 return key 
      
        return 0

    def convert_vol_to_mL(self, vol):
        if 'mL' in str(vol):
            vol = float(vol[:-2])
        elif 'uL' in str(vol):
            vol = float(vol[:-2]) / 1000
        else:
            # Check if vol is greater than MAX_PUMP_VOL
            if float(vol) > 5:
                # assume vol in uL
                vol = float(vol)/1000
            else:
                # assume vol in mL
                pass
        return vol

    #For each dictionary, case switch or if elif opName
    #to make strings to be executed
    def __get_sec(self, time_str):
        #Get Seconds from time.
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

    def __incubate(self, cas, runtime, mixAfter, mixVol=0.1, extraVolOut=0):
        #Convert runtime hh:mm:ss into seconds
        incubateTime = self.__get_sec(runtime)
        # Convert vol to mL
        mixVol = self.convert_vol_to_mL(mixVol)
        extraVolOut = self.convert_vol_to_mL(extraVolOut)
        if mixAfter == 'undefined':
            mixAfter = 0

        incStr = 'self.incubate(cas="{}",incTime={},mixAfter={},mixVol={},extraVolOut={})'.format(
            cas, incubateTime, mixAfter, mixVol, extraVolOut)
        return(incStr)
                
    def __mix(self, cas, numCycles, volume):
        # Convert vol to mL
        vol = self.convert_vol_to_mL(volume)

        mixStr = 'self.mix(cas="{}", numCycles={}, volume={})'.format(cas, numCycles, vol)
        return(mixStr)
        
    def __purge(self, cas):
        purgeStr = 'self.purge(cas="{}")'.format(cas)
        return(purgeStr)

    def __load_reagent(self, cas, loadType, volume, inSpeed=None, chamberSpeed=None, lineSpeed=None, washSyr='auto', washSyrReagent='Dehydrant'):
        # Convert vol to mL
        vol = self.convert_vol_to_mL(volume)


        if washSyr == 'true':
            washSyrBool = True
            loadStr = 'self.loadReagent(cas="{}",reagent="{}",ml={},inSpeed={},chamberSpeed={},lineSpeed={},washSyr={},washSyrReagent="{}")'.format(
                cas, self.reaConv[loadType], vol, inSpeed, chamberSpeed, lineSpeed, washSyrBool, self.reaConv[washSyrReagent])
        else:
            washSyrBool = 'auto'
            loadStr = 'self.loadReagent(cas="{}",reagent="{}",ml={},inSpeed={},chamberSpeed={},lineSpeed={},washSyr="{}",washSyrReagent="{}")'.format(
                cas, self.reaConv[loadType], vol, inSpeed, chamberSpeed, lineSpeed, washSyrBool,
                self.reaConv[washSyrReagent])

        return(loadStr)
    
