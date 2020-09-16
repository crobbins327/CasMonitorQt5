import os
import asyncio
from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn import wamp
import time
import datetime
import machine
import itertools
import namedTask as nTask

import pandas as pd
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import numpy as np
import re
import logging
import logging.config
from colorlog import ColoredFormatter
import sys
sys.setrecursionlimit(9000)

#Import logger config
logging.config.fileConfig(fname='./Log/init/ctrl-loggers.ini')
# Define all loggers
ctrl = logging.getLogger('ctrl')
casAlog = logging.getLogger('ctrl.casA')
casBlog = logging.getLogger('ctrl.casB')
casClog = logging.getLogger('ctrl.casC')
casDlog = logging.getLogger('ctrl.casD')
casElog = logging.getLogger('ctrl.casE')
casFlog = logging.getLogger('ctrl.casF')
machinelog = logging.getLogger('ctrl.machine')
rootlog = logging.getLogger('')

#Replace consoleHandler format with colorlog... can't pass the log_colors arg in the config file for some reason...
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
ctrl.handlers[0].setFormatter(colorFormat)
rootlog.handlers[0].setFormatter(colorFormat)
machinelog.handlers[0].setFormatter(colorFormat)

# Logger dictionary
casLogs = {'A' : casAlog,
           'B' : casBlog,
           'C' : casClog,
           'D' : casDlog,
           'E' : casElog,
           'F' : casFlog
           }

# Make the modifiable file handler for the machinelog
modHdl = logging.FileHandler('./Log/machine.log', mode='a')
modHdl.setLevel(logging.DEBUG)
textFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
modHdl.setFormatter(textFormatter)
machinelog.addHandler(modHdl)
#close file and do not write anything until needed
modHdl.close()

mixSpeed = 3
purgeSpeed = 3
purgeVol = 4
deadspace = 3
wasteSpeed = 8


# Define application session class for controller
class Component(ApplicationSession):
    
    '''protFuncs = {
    'self.incubate': self.incubate,
    'self.mix': self.mix,
    'self.'}'''

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.halted = True
        self.homed = False
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','engaged','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName','startlog','endlog'] ,
                                   index=['casA','casB','casC','casD','casE','casF'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        self.guiStatus = 'disconnected'
    
    # @wamp.subscribe('com.prepbot.prothandler.heartbeat-ctrl')
    async def heartbeat(self):
        if self.guiStatus == 'disconnected':
            self.guiStatus = 'connected'
    
    async def update(self):
        while True:
            #Send updates of activate cassette logs
            try:
                await self.call('com.prepbot.prothandler.heartbeat-gui')
                if self.guiStatus == 'disconnected':
                    self.guiStatus = 'connected'
                    ctrl.info('GUI is connected!')
                for i in self.activeTasks:
                    start = self.taskDF.loc[i,'endlog'] + 1
                    linesToSend, currentEnd = self.get_caslogchunk(i[-1], start, end=0)
                    if len(linesToSend) > 0:
                        self.taskDF.loc[i, 'endlog'] = currentEnd
                        self.publish('com.prepbot.prothandler.update-cas-log', i[-1], linesToSend, currentEnd)
                        ctrl.debug('Sent updated {} cassette log!'.format(i))
                await asyncio.sleep(10)
            except Exception as e:
                if self.guiStatus == 'connected':
                    self.guiStatus = 'disconnected'
                    ctrl.warning('GUI is disconnected!')
                    ctrl.warning(e)
                await asyncio.sleep(1)
                

    async def onJoin(self, details):
        #Trying to check if there was a disconnection recently
        #If disconnection occured, load in taskDF from file
        ctrl.info(sys.getrecursionlimit())
        ctrl.info('Loading last controller state...')
        disconnectDir = os.listdir('./Log/disconnect')
        if 'disconnect-state.pkl' in disconnectDir:
            dcTask = pd.read_pickle('./Log/disconnect/disconnect-state.pkl')
            ctrl.info('Checking disonnect-state for last controller state...')
            ctrl.debug('\n{}'.format(dcTask))
            #Remove that file so that it would not disrupt a new controller instance
        else:
            dcTask = []
        #Else, new controller instance with no taskDF
        #Register so that GUI can get_tasks when reconnecting/joining
        try:
            self.register(self.get_tasks, 'com.prepbot.prothandler.controller-tasks')
            self.register(self.heartbeat, 'com.prepbot.prothandler.heartbeat-ctrl')
            self.register(self.get_caslogchunk, 'com.prepbot.prothandler.caslog-chunk')
            ctrl.info('Registered to all procedures!')
        except Exception as e:
            ctrl.error('Could not register get_tasks to router...')
            ctrl.error(e)
        try:
            res = await self.subscribe(self)
            ctrl.info("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            ctrl.error("could not subscribe to procedure: {0}".format(e))
        asyncio.ensure_future(self.update())
        #After connecting, home the machine and make sure it's connected
        #Prime the reagent lines
        #Formalin ~3mL, 10speed
        #MeOH ~3mL, 10speed
        try:
            machine.reset()
            machine.home()
        except Exception as e:
            ctrl.critical('Could not reset and home machine!')
            ctrl.critical(e)
            self.leave()
            self.disconnect()
        
        if len(dcTask):
            #Convert strings back to lists...
            if pd.notna(dcTask.status).sum() > 0 or dcTask.engaged.sum() > 0:
                self.taskDF = dcTask
                ctrl.info('Repopulating controller tasks from contoller state...')
                self.repopulateController()
                ctrl.info('Sending tasks to GUI to repopulate it...')
                self.publish('com.prepbot.prothandler.tasks-to-gui', self.taskDF.to_json())
            else:
                self.taskDF = dcTask
                ctrl.info('dcTask has no engaged cassettes nor running/finished processes.')
                pass
        else:
            ctrl.info('No dcTask file was found, starting controller in null state.')
            
            
    def onDisconnect(self):
        ctrl.warning("Disconnected, {}".format(self.activeTasks))
        #Write the last state of the controller taskDF to a file
        ctrl.info('Writing disconnect-state to file...')
        self.taskDF.to_pickle('./Log/disconnect/disconnect-state.pkl')
        try:
            machine.goto_park()
            ctrl.info('Parking machine...')
        except Exception as e:
            ctrl.critical('Could not park machine!')
            ctrl.critical(e)
        
        
        
    def get_tasks(self):
        return(self.taskDF.to_json())
    
    def get_caslogchunk(self, casL, start, end=0, limit=10000):
        #Get log filename from handler
        fn = casLogs[casL].handlers[0].baseFilename
        linesToSend = []
        if start <= end:
            with open(fn, 'r') as logfile:
                for i, line in enumerate(logfile):
                    if i >= start and i <= end:
                        linesToSend.append(line)
                    elif i > end:
                        break
        else:
            with open(fn, 'r') as logfile:
                for i, line in enumerate(logfile):
                    if i >= start and i <= start + limit:
                        linesToSend.append(line)
                        end = i
                    elif i > start+limit:
                        break
                    
        #Make a string that can be displayed/written to file
        linesToSend = ''.join(linesToSend)
        return(linesToSend, end)
                    
    async def get_lastline(self, fn):
        with open(fn, 'r') as logfile:
                for i, line in enumerate(logfile):
                    pass
                last_line_num = i
        return(last_line_num)
                    
    
    def repopulateController(self):
        running = self.taskDF[self.taskDF.status.isin(['running'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running'])].index
        
        for i in self.taskDF.index:
            ctrl.debug(i)
            if i in engagedCas:
                self.engage(i[-1])
            elif i in running:
                ctrl.info('{}, Restarting run!'.format(i))
                asyncio.ensure_future(self.startProtocol(casL=i[-1], taskJSON=None, restart=True))
                # self.publish('com.prepbot.prothandler.start', i[-1], None, True)
                
                
        
        ctrl.info("Restore connection with logger(s)......NOT IMPLEMENTED YET...")
    # @wamp.subscribe('com.prepbot.prothandler.request-tasks-gui')
    # def sendTasks(self):
    #     self.publish('com.prepbot.prothandler.tasks-to-gui', self.taskDF.to_json())
    
    
    @wamp.subscribe('com.prepbot.prothandler.engage')
    def engage(self, casL):
        #How to check if cassette already is engaged....?
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info('Engage Cas{}...'.format(casL))
        # machine.test_logger()
        try:
            eval('machine.engage_sample{}()'.format(casL))
#             time.sleep(1)
            self.publish('com.prepbot.prothandler.ready', casL, True)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = True

        except Exception as e:
            ctrl.critical('Machine could not engage cas{}. Does it exist?'.format(casL))
            ctrl.critical(e)
            self.taskDF.loc['cas{}'.format(casL)] = np.nan
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            self.publish('com.prepbot.prothandler.ready', casL, False)
            
    @wamp.subscribe('com.prepbot.prothandler.disengage')
    def disengage(self, casL):
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info('Disengage Cas{}...'.format(casL))
        try:
            eval('machine.disengage_sample{}()'.format(casL))
#             time.sleep(1)
            self.publish('com.prepbot.prothandler.ready', casL, False)
            self.taskDF.loc['cas{}'.format(casL)] = np.nan
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
        except Exception as e:
            ctrl.critical('Machine could not disengage cas{}. Does it exist?'.format(casL))
            ctrl.critical(e)
            self.taskDF.loc['cas{}'.format(casL)] = np.nan
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            self.publish('com.prepbot.prothandler.ready', casL, False)

        
    @wamp.subscribe('com.prepbot.prothandler.start')
    async def startProtocol(self, casL, taskJSON, restart = False):
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        if self.halted:
            # self.connect()
            self.halted = False
        if not self.homed:
            # self.home()
            self.homed = True
        casName = 'cas{}'.format(casL)
        #Check if a task with that CasL name already exists
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Create task with CasL as the name
        if casName in self.activeTasks:
            casLogs[casL].info(self.activeTasks)
            casLogs[casL].info('Already running task on {}!'.format(casName))
            #Repopulate GUI because it must be wrong!
            await self.publish('com.prepbot.prothandler.one-task-to-gui', casName, self.taskDF.loc[casName].to_json())
            pass
        else:
            if restart:
                casLogs[casL].warning('Restarting Run...\n{}'.format(self.taskDF.loc[casName,['sampleName','protocolName','protocolPath']]))
                #Start at current stepNum and if the step is an incubate step,
                stepNum = int(self.taskDF.loc[casName,'stepNum'])
                # casLogs[casL].debug(stepNum)
                casLogs[casL].info('{}: Restarting at step # {}...'.format(casName, stepNum))
                #update the runtime using secsRemaining
                if self.taskDF.loc[casName,'progressNames'][stepNum-1] == 'Incubation':
                    casLogs[casL].info('{}: Restarting incubate timer'.format(casName))
                    incStr = self.taskDF.loc[casName,'protocolList'][stepNum-1]
                    #Get parameters betwen parantheses
                    incParam = re.search('\(([^)]+)', incStr).group(1).split(',')
                    casLogs[casL].debug(incParam)
                    #Find incTime
                    j = [ i for i, word in enumerate(incParam) if word.startswith('incTime=') ][0]
                    casLogs[casL].debug(j)
                    #Change incTime
                    incParam[j] = 'incTime={}'.format(self.taskDF.loc[casName,'secsRemaining'])
                    #Change incStr and protocolList
                    self.taskDF.loc[casName,'protocolList'][stepNum-1] = 'self.incubate({})'.format(','.join(incParam))
                    casLogs[casL].debug(self.taskDF.loc[casName,'protocolList'][stepNum-1])
            else:
                #When the protocol is starting
                #Add step to taskDF
                self.taskDF.loc[casName] = pd.read_json(taskJSON, typ='series', dtype=object)
                #update taskDF to show that it was received by controller and started
                self.taskDF.loc[casName,'stepNum'] = 1
                #Make some space in log
                casLogs[casL].info('\n\n\n')
                #Get starting line number for the log
                fn = casLogs[casL].handlers[0].baseFilename
                start = await self.get_lastline(fn)
                self.taskDF.loc[casName,'startlog'] = start 
                #Set end number to 0 until the protocol is completed or stopped
                self.taskDF.loc[casName,'endlog'] = start
                casLogs[casL].info('Starting Run!\n{}'.format(self.taskDF.loc[casName,['sampleName','protocolName','protocolPath','startlog']]))
                stepNum = 1
                self.taskDF.loc[casName,'secsRemaining'] = self.taskDF.loc[casName,'stepTimes'][0]
            #get the protocol functions to be executed
            protStrings = self.taskDF.loc[casName,'protocolList']
            progStrings = self.taskDF.loc[casName,'progressNames']
            exec('self.{} = nTask.create_task(self.evalProtocol(casL, protStrings, progStrings, stepNum), name="{}")'.format(casName,casName,stepNum))
            #update the activeTasks
            self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
            casLogs[casL].info('Starting task on {}'.format(casName))
            casLogs[casL].info(self.activeTasks)
            if not restart:
                samplelog, currentEnd = self.get_caslogchunk(casL, start, end=0)
                self.publish('com.prepbot.prothandler.started', casName, self.taskDF.loc[casName].to_json(), samplelog, currentEnd)
                
            
    async def evalProtocol(self, casL, protStrings, progStrings, stepNum=1):
        casName = 'cas{}'.format(casL)
        fn = casLogs[casL].handlers[0].baseFilename
        # i=stepNum-1
        # while i < len(protStrings):
        for i in range(stepNum-1, len(protStrings)):
            #Break up blocks of code, exec cannot be used because it does not return values
            #Eval() has poor security!!!! Should at least filter protStrings before evaluating...
            toEval = protStrings[i].split('\n')
            casLogs[casL].info('{}: Evaluating step {}'.format(casName,i))
            casLogs[casL].info(toEval)
            # if len(toEval) > 1:
            #     #Need to gather functions so that the protocol step is completed synchronously
            #     #Important for synchronous sample purging then loading
            #     await asyncio.gather(eval(toEval[0]),eval(toEval[1]))
            # else:
            # if progStrings[i] not in ['Incubation','Mixing']:
            #     ctrl.debug('Gathering steps for {}...'.format(progStrings[i]))
            #     await asyncio.gather(eval(protStrings[i]))
            # else:
            await eval(protStrings[i])
                
            #Once step has been evaluated, publish to update progress bar, update taskDF again
            if i+2 <= len(protStrings):
                #advance taskDF for next step
                self.taskDF.loc[casName,'secsRemaining'] = self.taskDF.loc[casName,'stepTimes'][i+1]
                self.taskDF.loc[casName,'stepNum'] = i+2
            else:
                #this is the last step when it is completed
                self.taskDF.loc[casName,'secsRemaining'] = 0
                self.taskDF.loc[casName,'stepNum'] = i+1
                self.taskDF.loc[casName,'status'] = 'finished'
                casLogs[casL].info('Finished {} task!'.format(casName))
            #Send updated log
            start = self.taskDF.loc[casName,'endlog'] + 1
            linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
            if len(linesToSend) > 0:
                self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
            #Update end line number of log
            self.taskDF.loc[casName,'endlog'] = currentEnd
            #wampHandler will send a corresponding signal to QML to update the progress bar, GUI taskDF, and cassette log
            self.publish('com.prepbot.prothandler.progress', casL, self.taskDF.loc[casName].to_json())
            casLogs[casL].info('Updating progress on cas{}...'.format(casL))
            await asyncio.sleep(0.05)
            # i+= 1
            
    @wamp.subscribe('com.prepbot.prothandler.stop')
    async def stopProtocol(self, casL):
        casName = 'cas{}'.format(casL)
        casLogs[casL].info('Trying to cancel {}, getting active tasks...'.format(casName))
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        casLogs[casL].info(self.activeTasks)
        if casName in self.activeTasks:
            eval('self.{}.cancel()'.format(casName))
            self.taskDF.loc[casName,'status'] = 'stopping'
            try:
                eval('self.{}'.format(casName))
            except asyncio.CancelledError:
                casLogs[casL].info("The run on {} has been cancelled.".format(casName))
            self.publish('com.prepbot.prothandler.start-shutdown', casL)
            #Shutdown procedures...
            await self.shutdown(casL)
            #Clearing taskDF, getting end of log, and publishing it
            self.taskDF.loc[casName,'status'] = 'shutdown'
            # self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
            fn = casLogs[casL].handlers[0].baseFilename
            end = await self.get_lastline(fn)
            self.taskDF.loc[casName,'endlog'] = end
            self.publish('com.prepbot.prothandler.finish-shutdown', casL, self.taskDF.loc[casName].to_json())
        else:
            casLogs[casL].warning('{} is not running a protocol...'.format(casName))
            self.taskDF.loc[casName,'status'] = 'idle'
            #self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
            self.publish('com.prepbot.prothandler.finish-shutdown', casL, self.taskDF.loc[casName].to_json())
            
            
    # @wamp.subscribe('com.prepbot.prothandler.next')
    # async def nextProtocol(self, casL):
    #     casName = 'cas{}'.format(casL)
    #     casLogs[casL].info('Trying to setup next run on {}, getting active tasks...'.format(casName))
    #     self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
    #     casLogs[casL].info(self.activeTasks)
    #     if casName in self.activeTasks:
    #         eval('self.{}.cancel()'.format(casName))
    #         self.taskDF.loc[casName,'status'] = 'stopped'
    #         try:
    #             eval('self.{}'.format(casName))
    #         except asyncio.CancelledError:
    #             casLogs[casL].info("The run on {} has been cancelled.".format(casName))
    #         self.publish('com.prepbot.prothandler.start-shutdown', casL)
    #         #Shutdown procedures...
    #         await self.shutdown(casL)
    #         #Clearing taskDF and publishing it
    #         self.taskDF.loc[casName,'status'] = 'shutdown'
    #         self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
    #         self.publish('com.prepbot.prothandler.finish-shutdown', casL, self.taskDF.loc[casName].to_json())
    #     else:
    #         casLogs[casL].info('{} is idle and ready for next run.'.format(casName))
    #         self.taskDF.loc[casName,'status'] = 'idle'
    #         self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
    #         self.publish('com.prepbot.prothandler.finish-shutdown', casL, self.taskDF.loc[casName].to_json(), True)
            
    async def shutdown(self, casL):
        #Basic shutdown procedures when stopping a run before finishing.....
        casLogs[casL].info('SHUTDOWN Cas{}'.format(casL))
        try:
            machine.goto_park()
        except Exception as e:
            casLogs[casL].critical(e)
            
    #Perhaps make this an async function that is awaited on as a named task for the debug screen
    @wamp.subscribe('com.prepbot.prothandler.exec-script')
    async def execScript(self, linesToExec):
        try:
            ctrl.info('{}'.format(linesToExec))
            #get current line of ctrl logger to send to debug screen...
            ctrl.info('Starting to execute lines from script editor!')
            #split the lines by \n, make a list
            execList = linesToExec.split('\n')
            ctrl.debug('{}'.format(execList))
            #make a for loop through list
            for i in range(len(execList)):
                if execList[i]!='' and not execList[i].isspace():
                    ctrl.debug(execList[i])
                    #string evaluate each line
                    if execList[i][0:4] == 'self':
                        await eval(execList[i])
                    else:
                        eval(execList[i])
        except Exception as e:
            ctrl.critical('Cannot evaluate script! Please check that function called exists and formatting is correct.')
            ctrl.critical(e)
    
    async def incubate(self, casL, incTime, mixAfter=600):
        casName = 'cas{}'.format(casL)
        #Get start time
        start = datetime.datetime.now()
        incSleep  = 10
        if mixAfter=='undefined' or int(mixAfter)<=0:
            waitI= int(incTime/incSleep)
            #No washes/mixes, only one iteration
            washI = 0
        else:
            mixMod = int(mixAfter/2)
            if mixMod < 1:
                mixMod=1
            washI = int(incTime/mixMod)
            #Divide mixMod by the incSleep to get the iterator for how many times to asyncio.sleep
            #wait iterator
            waitI = int(mixMod/incSleep)
        casLogs[casL].info('INCUBATING Cas{}'.format(casL))
        #Want to break out of this loop if timediff exceeds incTime
        exceedInc = False
        #Publish index
        p=1
        for i in range(washI):
            #mix at end of 2*waitI
            i+=1
            if exceedInc:
                break
            for j in range(waitI):
                #Sleep for incSleep=10
                await asyncio.sleep(incSleep)
                diff = (datetime.datetime.now() - start).total_seconds()
                if diff >= incTime:
                    exceedInc = True
                    break
                ctrl.debug("Cas{} Incubation Seconds remaining: {}".format(casL,int(incTime - diff)))
                self.taskDF.loc[casName,'secsRemaining'] = int(incTime - diff)
                #This interupts the processes on the wampHandler by publishing every second
                #Send a publish every 30 seconds?
                if diff > 30*p:
                    casLogs[casL].info('Cas{} publishing secs-remaining!'.format(casL))
                    self.publish('com.com.prepbot.prothandler.secs-remaining',casL,int(incTime - diff))
                    p += 1
            if ((i % 2) == 0):
                await asyncio.sleep(0.1)
                modHdl.close()
                modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
                casLogs[casL].info('Mixing Cas{}...'.format(casL))
                #Goto last fluidtype???
                try:
                    eval('machine.goto_sample{}()'.format(casL))
                    machine.pump_in(0.5, mixSpeed)
                    time.sleep(2)
                    machine.pump_out(0.5, mixSpeed)
                except Exception as e:
                    casLogs[casL].critical(e)
        
    async def mix(self, casL, numCycles, volume):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info("MIXING Cas{}, {} TIMES, {} VOLUME".format(casL, numCycles, volume))
        try:
            eval('machine.goto_sample{}()'.format(casL))
            for i in range(int(numCycles)):
                # await asyncio.sleep(0.01)
                casLogs[casL].info('Mixing {}, #{} of {} cycles...'.format(casL,i+1,int(numCycles)))
                # Goto last fluidtype???
                machine.pump_in(volume, mixSpeed)
                time.sleep(2)
                machine.pump_out(volume, mixSpeed)
        except Exception as e:
            casLogs[casL].critical(e)
        
    async def purge(self, casL, deadvol=deadspace):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info('PURGING CHAMBER, Cas{}'.format(casL))
        # Goto last fluidtype???
        try:
            eval('machine.goto_sample{}()'.format(casL))
            machine.pump_in(deadvol, purgeSpeed)
            time.sleep(1)
            machine.empty_syringe(wasteSpeed)
        except Exception as e:
            casLogs[casL].critical(e)
        
    async def loadReagent(self, casL, loadstr, reagent, vol, speed, deadvol=deadspace):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        try:
            casLogs[casL].info('PURGING CHAMBER, Cas{}'.format(casL))
            eval('machine.goto_sample{}()'.format(casL))
#             machine.pump_in(deadvol, purgeSpeed)
#             time.sleep(1)
#             machine.empty_syringe(wasteSpeed)
            flowThru = purgeVol + deadvol
            machine.pump_out(flowThru, purgeSpeed)
            

            casLogs[casL].info('ADDING {} TO Cas{}'.format(loadstr, casL))
            eval('machine.goto_{}()'.format(reagent))
            deVol = vol + deadvol
            machine.pump_in(deVol,speed)
            if reagent == 'babb':
                time.sleep(3)
            else:
                time.sleep(1)
            eval('machine.goto_sample{}()'.format(casL))
            machine.pump_out(vol,speed)
        except Exception as e:
            casLogs[casL].critical(e)

    @wamp.subscribe('com.prepbot.button.btn_halt')
    async def halt(self):
        machine.send('M112', read_response=False)
        self.halted = True
        self.homed = False

    @wamp.subscribe('com.prepbot.button.btn_connect')
    def connect(self):
        machine.connect()
        self.halted = False

    @wamp.subscribe('com.prepbot.button.btn_home')
    def home(self):
        machine.home()
        self.homed = True

    # @wamp.subscribe('com.prepbot.button.btn_engage')
    # def enage(self):
    #     machine.engage_sampleD()

    # @wamp.subscribe('com.prepbot.button.btn_disengage')
    # def disengage(self):
    #     machine.disengage_sampleD()

    @wamp.subscribe('com.prepbot.button.btn_waste')
    def btn_waste(self):
        machine.goto_waste()

    @wamp.subscribe('com.prepbot.button.btn_formalin')
    def btn_formalin(self):
        machine.goto_formalin()

    @wamp.subscribe('com.prepbot.button.btn_meoh')    
    def btn_meoh(self):
        machine.goto_meoh()

    @wamp.subscribe('com.prepbot.button.btn_babb')    
    def btn_babb(self):
        machine.goto_babb()

    @wamp.subscribe('com.prepbot.button.btn_sample')    
    def btn_sample(self):
        machine.goto_sampleD()

    @wamp.subscribe('com.prepbot.button.btn_vial')    
    def btn_vial(self):
        machine.goto_vial()

    @wamp.subscribe('com.prepbot.button.btn_park')    
    def btn_park(self):
        machine.goto_park()

    @wamp.subscribe('com.prepbot.button.btn_pumpin')
    def btn_pumpin(self, vol=None):
        machine.pump_in(vol)

    @wamp.subscribe('com.prepbot.button.btn_pumpout')    
    def btn_pumpout(self, vol=None):
        machine.pump_out(vol)

    @wamp.subscribe('com.prepbot.button.btn_dyeprocess')
    def btn_dyeprocess(self):
        machine.dye_process()

    @wamp.subscribe('com.prepbot.button.btn_purge')
    def btn_purge(self):
        machine.purge_syringe()

if __name__ == '__main__':
    while True:
        runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1")
        try:
            runner.run(Component)
            loop = asyncio.get_event_loop()
            loop.run_forever()
        except ConnectionRefusedError:
            time.sleep(2)
