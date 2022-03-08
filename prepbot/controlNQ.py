#!/home/jackr/anaconda/envs/QML36/bin/python
import os
import sys
sys.path.append('/home/pi/CasMonitorQt5/')
# sys.path.append('F:/Torres/CasMonitorQt5/')
import asyncio
from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn import wamp
import time
import datetime
import machine_debug as machine
import itertools
import namedTask as nTask
# import confuse
import yaml
from collections import OrderedDict

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

# Import logger config
logging.config.fileConfig(fname='./Log/init/ctrl-loggers.ini')
# Define all loggers
ctrl = logging.getLogger('ctrl')
cas1log = logging.getLogger('ctrl.cas1')
cas2log = logging.getLogger('ctrl.cas2')
cas3log = logging.getLogger('ctrl.cas3')
cas4log = logging.getLogger('ctrl.cas4')
cas5log = logging.getLogger('ctrl.cas5')
cas6log = logging.getLogger('ctrl.cas6')
machinelog = logging.getLogger('ctrl.machine')
# machinelog.setLevel(logging.INFO)
opTimeslog = logging.getLogger('ctrl.opTimes')
rootlog = logging.getLogger('')

# Replace consoleHandler format with colorlog... can't pass the log_colors arg in the config file for some reason...
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
# Replace on each
ctrl.handlers[0].setFormatter(colorFormat)
rootlog.handlers[0].setFormatter(colorFormat)
machinelog.handlers[0].setFormatter(colorFormat)

# Logger dictionary
casLogs = {'CAS1' : cas1log,
           'CAS2' : cas2log,
           'CAS3' : cas3log,
           'CAS4' : cas4log,
           'CAS5' : cas5log,
           'CAS6' : cas6log
           }

# Make the modifiable file handler for the machinelog
modHdl = logging.FileHandler('./Log/machine.log', mode='a')
modHdl.setLevel(logging.DEBUG)
textFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
modHdl.setFormatter(textFormatter)
machinelog.addHandler(modHdl)
# close file and do not write anything until needed
modHdl.close()

# open YAML file with parameters....
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


with open(r'./prepbot/config.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    # confY = yaml.safe_load(file)
    confY = ordered_load(file, yaml.SafeLoader)
    ctrl.debug(confY)


loadParam = confY['load']
reagParam = confY['reagents']
# specifies where reagent settings are from
# config or protocol
reagSettings = 'config'
# reagSettings = 'protocol'
casParam = confY['cassettes']

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
        self.writeDCstate = True
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','currentFluid','volInLine','engaged','protocolList','progressNames',
                                              'stepTimes','sampleName','protocolPath','protocolName','startlog','endlog'] ,
                                   index=['CAS1','CAS2','CAS3','CAS4','CAS5','CAS6'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        self.guiStatus = 'disconnected'
        self.taskIter = 1
        self.syringeFluid = None
    
    # @wamp.subscribe('com.prepbot.prothandler.heartbeat-ctrl')
    async def heartbeat(self):
        if self.guiStatus == 'disconnected':
            self.guiStatus = 'connected'
            
    # async def halt(self):
    #     machine.send('M112', read_response=False)
    #     self.halted = True
    #     self.homed = False

    def send_mStatus(self):
        return self.homed
    
    
    async def update(self):
        while True:
            # Send updates of activated cassette logs
            try:
                await self.call('com.prepbot.prothandler.heartbeat-gui')
                if self.guiStatus == 'disconnected':
                    self.guiStatus = 'connected'
                    ctrl.info('GUI is connected!')
                for i in self.activeTasks:
                    start = self.taskDF.loc[i, 'endlog'] + 1
                    linesToSend, currentEnd = self.get_caslogchunk(i, start, end=0)
                    if len(linesToSend) > 0:
                        self.taskDF.loc[i, 'endlog'] = currentEnd
                        self.publish('com.prepbot.prothandler.update-cas-log', i, linesToSend, currentEnd)
                        ctrl.debug('Sent updated {} cassette log!'.format(i))
                await asyncio.sleep(10)
            except Exception as e:
                if 'termTask' in str(e):
                    await self.stopTermTasks()
                if self.guiStatus == 'connected':
                    self.guiStatus = 'disconnected'
                    ctrl.warning('GUI is disconnected!')
                    ctrl.warning(e)
                await asyncio.sleep(1)
                
    @wamp.subscribe('com.prepbot.prothandler.send-param-controller')
    async def update_param(self, paramDict):
        ctrl.debug(paramDict)
        # Set global param
        self.set_param(paramDict)
        # Write to YAML file...
        with open('./prepbot/config.yaml', 'w') as f:
            # yaml.dump(confY, f, default_flow_style=False, sort_keys=False)
            ordered_dump(confY, f, Dumper=yaml.SafeDumper)
            
        ctrl.debug('Wrote parameters to config.yaml!')
        # Confirm GUI is updated...
        self.publish('com.prepbot.prothandler.send-param-gui', confY)
    
    def set_param(self, paramDict):
        global confY, loadParam, reagParam, casParam

        for i in paramDict.keys():
            for k in paramDict[i].keys():
                confY[i][k] = paramDict[i][k]
        loadParam = confY['load']
        reagParam = confY['reagents']
        casParam = confY['cassettes']
            
    def send_param(self):
        self.publish('com.prepbot.prothandler.send-param-gui', confY)

        
                
    async def onJoin(self, details):
        # Register so that GUI can get_tasks when reconnecting/joining
        try:
            self.register(self.get_tasks, 'com.prepbot.prothandler.controller-tasks')
            self.register(self.heartbeat, 'com.prepbot.prothandler.heartbeat-ctrl')
            self.register(self.get_caslogchunk, 'com.prepbot.prothandler.caslog-chunk')
            self.register(self.send_mStatus, 'com.prepbot.prothandler.gui-get-machine-homed')
            self.register(self.send_param, 'com.prepbot.prothandler.gui-get-param')
            ctrl.info('Registered all procedures!')
        except Exception as e:
            ctrl.error('Could not register functions to router...')
            ctrl.error(e)
        try:
            res = await self.subscribe(self)
            ctrl.info("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            ctrl.error("could not subscribe to procedure: {0}".format(e))
        
        asyncio.ensure_future(self.update())
        
        # Trying to check if there was a disconnection recently
        # If disconnection occured, load in taskDF from file
        ctrl.info(sys.getrecursionlimit())
        ctrl.info('Loading last controller state...')
        disconnectDir = os.listdir('./Log/disconnect')
        if 'disconnect-state.pkl' in disconnectDir:
            dcTask = pd.read_pickle('./Log/disconnect/disconnect-state.pkl')
            ctrl.info('Checking disconnect-state for last controller state...')
            ctrl.debug('\n{}'.format(dcTask))
            self.taskDF = dcTask
            # Remove that file so that it would not disrupt a new controller instance
        else:
            dcTask = []
        # Else, new controller instance with no taskDF

        # After connecting to router, make sure machine is connected and check if it should be homed
        # Need to release the lock to reset the pump homing file when the controller is first opened
        try:
            machine.release()
            time.sleep(1)
            machine.acquire()
            ctrl.info('Checking if machine is homed...')
            self.homed = machine.pump_is_homed()
            self.halted = False
            ctrl.info('Machine is homed? : {}'.format(self.homed))
            if not self.homed:
                machine.pump_home()
                self.homed = machine.pump_is_homed()
            try:
                await asyncio.wait_for(self.call('com.prepbot.prothandler.set-machine-homed', self.homed), timeout=3.5)
            except Exception as e:
                ctrl.warning('GUI may not be connected! Machine has been homed.')
                ctrl.warning(e)
        except Exception as e:
            ctrl.critical('Could not acquire machine lock!')
            ctrl.critical(e)
            self.writeDCstate = False
            self.leave()
            self.disconnect()

        ctrl.info('Sending parameters to GUI...')
        ctrl.debug(self.taskDF)
        self.send_param()
        #Warn GUI to prime the reagent lines
        #Formalin ~3mL, 10speed
        #MeOH ~3mL, 10speed

        if len(dcTask):
            #Convert strings back to lists...
            if pd.notna(self.taskDF.status).sum() > 0 or self.taskDF.engaged.sum() > 0:
                ctrl.info('Repopulating controller tasks from contoller state...')
                await self.repopulateController()
                ctrl.info('Sending tasks to GUI to repopulate it...')
                self.publish('com.prepbot.prothandler.tasks-to-gui', self.taskDF.to_json())
            else:
                ctrl.info('dcTask has no engaged cassettes nor running/finished processes.')
                pass
        else:
            ctrl.info('No dcTask file was found, starting controller in null state.')
            
            
    def onDisconnect(self):
        ctrl.warning("Disconnected, {}".format(self.activeTasks))
        if self.writeDCstate == True:
            #Write the last state of the controller taskDF to a file
            ctrl.info('Writing disconnect-state to file...')
            self.taskDF.to_pickle('./Log/disconnect/disconnect-state.pkl')
            try:
                machine.release()
                ctrl.info('Releasing machine hardware lock...')
                time.sleep(5)
            except Exception as e:
                ctrl.critical('Could not release machine!')
                ctrl.critical(e)

    async def connectNHome(self):
        ctrl.info('Checking if machine is homed....')
        if self.halted or not self.homed:
            try:
                machine.release()
                time.sleep(1)
                machine.acquire()
                self.homed = machine.pump_is_homed()
                self.halted = False
                if not self.homed:
                    machine.pump_home()
                    self.homed = machine.pump_is_homed()
                try:
                    await asyncio.wait_for(self.call('com.prepbot.prothandler.set-machine-homed', self.homed),
                                           timeout=3.5)
                except Exception as e:
                    ctrl.warning('GUI may not be connected! Machine has been homed.')
                    ctrl.warning(e)
            except Exception as e:
                ctrl.critical(e)


    def get_tasks(self):
        return(self.taskDF.to_json())
    
    def get_caslogchunk(self, cas, start, end=0, limit=10000):
        #Get log filename from handler
        fn = casLogs[cas].handlers[0].baseFilename
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
        
    
    # def update_caslogchunk(self, cas):
    #     #Send updated log
    #     start = self.taskDF.loc[cas, 'endlog'] + 1
    #     linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
    #     if len(linesToSend) > 0:
    #         self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
    #     #Update end line number of log
    #     self.taskDF.loc[cas, 'endlog'] = currentEnd
                    
    async def get_lastline(self, fn):
        with open(fn, 'r') as logfile:
                for i, line in enumerate(logfile):
                    pass
                last_line_num = i
        return(last_line_num)
                    
    
    async def repopulateController(self):
        running = self.taskDF[self.taskDF.status.isin(['running'])].index
        cleanStop = self.taskDF[self.taskDF.status.isin(['cleaning', 'stopping'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running', 'cleaning', 'stopping'])].index
        
        for i in self.taskDF.index:
            ctrl.debug(i)
            if i in engagedCas:
                await self.engage(i[-1])
            elif i in running:
                await self.engage(i[-1])
                ctrl.info('{}, Restarting run!'.format(i))
                asyncio.ensure_future(self.startProtocol(cas=i[-1], taskJSON=None, restart=True))
                # self.publish('com.prepbot.prothandler.start', i[-1], None, True)
            elif i in cleanStop:
                ctrl.info('{}, Restarting clean/shutdown!'.format(i))
                asyncio.ensure_future(self.startProtocol(cas=i[-1], taskJSON=None, restart=True))
                

    @wamp.subscribe('com.prepbot.prothandler.engage')
    async def engage(self, cas):
        #How to check if cassette is inserted to be engaged?
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas.lower()))
        #Check if machine is connected and homed
        await self.connectNHome()
        casLogs[cas].info('Engage {}...'.format(cas))
        try:
            if machine.cassette_inserted(cas):
                machine.cassette_contact(cas)
                self.publish('com.prepbot.prothandler.ready', cas, True)
                self.taskDF.loc[cas, 'engaged'] = True
            else:
                #Send to notify gui?
                self.taskDF.loc[cas] = np.nan
                self.taskDF.loc[cas, 'engaged'] = False
                self.publish('com.prepbot.prothandler.ready', cas, False, True)

        except Exception as e:
            ctrl.critical('Machine could not engage {}. Does it exist?'.format(cas))
            ctrl.critical(e)
            self.taskDF.loc[cas] = np.nan
            self.taskDF.loc[cas, 'engaged'] = False
            self.publish('com.prepbot.prothandler.ready', cas, False)
            
    @wamp.subscribe('com.prepbot.prothandler.disengage')
    async def disengage(self, cas):
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas.lower()))
        #Check if machine is connected and homed
        await self.connectNHome()
        casLogs[cas].info('Disengage {}...'.format(cas))
        try:
            if machine.cassette_inserted(cas):
                machine.cassette_eject(cas)
                self.publish('com.prepbot.prothandler.ready', cas, False)
                self.taskDF.loc[cas] = np.nan
                self.taskDF.loc[cas,'engaged'] = False
            else:
                #Send to notify gui?
                self.taskDF.loc[cas] = np.nan
                self.taskDF.loc[cas, 'engaged'] = False
                self.publish('com.prepbot.prothandler.ready', cas, False, True)
            
        except Exception as e:
            ctrl.critical('Machine could not disengage {}. Does it exist?'.format(cas))
            ctrl.critical(e)
            self.taskDF.loc[cas] = np.nan
            self.taskDF.loc[cas, 'engaged'] = False
            self.publish('com.prepbot.prothandler.ready', cas, False)

        
    @wamp.subscribe('com.prepbot.prothandler.start')
    async def startProtocol(self, cas, taskJSON, restart=False):
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas))
        #Check if a task with that Cas name already exists
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Create task with Cas as the name
        if cas in self.activeTasks:
            casLogs[cas].info(self.activeTasks)
            casLogs[cas].info('Already running task on {}!'.format(cas))
            #Repopulate GUI because it must be wrong!
            self.publish('com.prepbot.prothandler.one-task-to-gui', cas, self.taskDF.loc[cas].to_json())
            pass
        else:
            #Check if machine is connected and homed
            await self.connectNHome()
            
            if restart:
                casLogs[cas].debug(self.taskDF.loc[cas, 'status'])
                if self.taskDF.loc[cas, 'status'] == 'cleaning':
                    progStrings = self.taskDF.loc[cas, 'progressNames']
                    stepNum = len(progStrings)
                    
                    exec('self.{} = nTask.create_task(self.restartClean(cas, stepNum), name="{}")'.format(cas, cas))
                    
                elif self.taskDF.loc[cas, 'status'] == 'stopping':
                    exec('self.{} = nTask.create_task(self.restartShutdown(cas), name="{}")'.format(cas, cas))

                elif self.taskDF.loc[cas, 'status'] == 'running':
                    casLogs[cas].warning('Restarting Run...\n{}'.format(self.taskDF.loc[cas, ['sampleName','protocolName','protocolPath']]))
                    #Start at current stepNum and if the step is an incubate step,
                    stepNum = int(self.taskDF.loc[cas, 'stepNum'])
                    # casLogs[cas].debug(stepNum)
                    casLogs[cas].info('{}: Restarting at step # {}...'.format(cas, stepNum))
                    #update the runtime using secsRemaining
                    if self.taskDF.loc[cas, 'progressNames'][stepNum-1] == 'Incubation':
                        casLogs[cas].info('{}: Restarting incubate timer'.format(cas))
                        incStr = self.taskDF.loc[cas, 'protocolList'][stepNum-1]
                        #Get parameters betwen parantheses
                        incParam = re.search('\(([^)]+)', incStr).group(1).split(',')
                        casLogs[cas].debug(incParam)
                        #Find incTime
                        j = [ i for i, word in enumerate(incParam) if word.startswith('incTime=') ][0]
                        casLogs[cas].debug(j)
                        #Change incTime
                        incParam[j] = 'incTime={}'.format(self.taskDF.loc[cas, 'secsRemaining'])
                        #Change incStr and protocolList
                        self.taskDF.loc[cas, 'protocolList'][stepNum-1] = 'self.incubate({})'.format(','.join(incParam))
                        casLogs[cas].debug(self.taskDF.loc[cas, 'protocolList'][stepNum-1])
                    #get the protocol functions to be executed
                    protStrings = self.taskDF.loc[cas, 'protocolList']
                    progStrings = self.taskDF.loc[cas, 'progressNames']
                    exec('self.{} = nTask.create_task(self.evalProtocol(cas, protStrings, progStrings, stepNum), name="{}")'.format(cas, cas))
                    #update the activeTasks
                    self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
                    casLogs[cas].info('Starting task on {}'.format(cas))
                    casLogs[cas].info(self.activeTasks)

            else:
                #When the protocol is starting
                #Add step to taskDF
                self.taskDF.loc[cas] = pd.read_json(taskJSON, typ='series', dtype=object)
                #update taskDF to show that it was received by controller and started
                self.taskDF.loc[cas,'stepNum'] = 1
                #Make some space in log
                casLogs[cas].info('\n\n\n')
                #Get starting line number for the log
                fn = casLogs[cas].handlers[0].baseFilename
                start = await self.get_lastline(fn)
                self.taskDF.loc[cas, 'startlog'] = start
                #Set end number to 0 until the protocol is completed or stopped
                # self.taskDF.loc[cas, 'endlog'] = start
                casLogs[cas].info('Starting Run!\n{}'.format(self.taskDF.loc[cas, ['sampleName','protocolName','protocolPath','startlog']]))
                stepNum = 1
                self.taskDF.loc[cas, 'secsRemaining'] = self.taskDF.loc[cas, 'stepTimes'][0]
                #get the protocol functions to be executed
                protStrings = self.taskDF.loc[cas, 'protocolList']
                progStrings = self.taskDF.loc[cas, 'progressNames']
                exec('self.{} = nTask.create_task(self.evalProtocol(cas, protStrings, progStrings, stepNum), name="{}")'.format(cas, cas))
                #update the activeTasks
                self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
                casLogs[cas].info('Starting task on {}'.format(cas))
                casLogs[cas].info(self.activeTasks)
                #publish that task was started to GUI
                samplelog, currentEnd = self.get_caslogchunk(cas, start, end=0)
                self.taskDF.loc[cas, 'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.started', cas, self.taskDF.loc[cas].to_json(), samplelog, currentEnd)
                # self.publish('com.prepbot.prothandler.one-task-to-gui', cas, self.taskDF.loc[cas].to_json())
                
            
    async def evalProtocol(self, cas, protStrings, progStrings, stepNum=1):
        # fn = casLogs[cas].handlers[0].baseFilename
        # i=stepNum-1
        # while i < len(protStrings):
        casLogs[cas].debug(protStrings)
        casLogs[cas].debug(progStrings)
        casLogs[cas].debug(stepNum)
        for i in range(stepNum-1, len(protStrings)):
            #Break up blocks of code, exec cannot be used because it does not return values
            #Eval() has poor security!!!! Should at least filter protStrings before evaluating...
            toEval = protStrings[i].split('\n')
            casLogs[cas].info('{}: Evaluating step {}'.format(cas,i))
            casLogs[cas].info(toEval)
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
                self.taskDF.loc[cas, 'secsRemaining'] = self.taskDF.loc[cas, 'stepTimes'][i+1]
                self.taskDF.loc[cas, 'stepNum'] = i+2
                #Send updated log
                start = self.taskDF.loc[cas, 'endlog'] + 1
                linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
                if len(linesToSend) > 0:
                    self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
                #Update end line number of log
                self.taskDF.loc[cas, 'endlog'] = currentEnd
                #wampHandler will send a corresponding signal to QML to update the progress bar, GUI taskDF, and cassette log
                self.publish('com.prepbot.prothandler.progress', cas, self.taskDF.loc[cas].to_json())
                casLogs[cas].info('Updating progress on {}...'.format(cas))
                await asyncio.sleep(0.05)
                # i+= 1
            else:
                #this is the last step when it is completed
                #Disengage sample and clean the line
                self.taskDF.loc[cas, 'secsRemaining'] = 0
                self.taskDF.loc[cas, 'stepNum'] = i+1
                #Send updated log
                start = self.taskDF.loc[cas, 'endlog'] + 1
                linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
                if len(linesToSend) > 0:
                    self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
                #Update end line number of log
                self.taskDF.loc[cas, 'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.progress', cas, self.taskDF.loc[cas].to_json())

                #Currently checked inside of clean()
                # casLogs[cas].info('Disengage {}...'.format(cas))
                # machine.cassette_eject(cas)
                # self.taskDF.loc[cas, 'engaged'] = False
                #
                casLogs[cas].info('Finished all steps, starting to clean {}...'.format(cas))
                
                #start cleaning
                self.taskDF.loc[cas, 'status'] = 'cleaning'
                self.publish('com.prepbot.prothandler.start-clean', cas)
                await self.clean(cas)
                
                self.taskDF.loc[cas, 'status'] = 'finished'
                casLogs[cas].info('Finished {} task!'.format(cas))
                #Send updated log
                start = self.taskDF.loc[cas, 'endlog'] + 1
                linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
                if len(linesToSend) > 0:
                    self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
                #Update end line number of log
                self.taskDF.loc[cas, 'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.finish-clean', cas, self.taskDF.loc[cas].to_json())
                
            
            
    @wamp.subscribe('com.prepbot.prothandler.stop')
    async def stopProtocol(self, cas):
        casLogs[cas].info('Trying to cancel {}, getting active tasks...'.format(cas))
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        casLogs[cas].info(self.activeTasks)
        if cas in self.activeTasks:
            self.taskDF.loc[cas, 'status'] = 'stopping'
            eval('self.{}.cancel()'.format(cas))
            self.publish('com.prepbot.prothandler.start-shutdown', cas)
            #Shutdown procedures...
            await self.shutdown(cas)
            self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
            casLogs[cas].info(self.activeTasks)
            try:
                eval('self.{}'.format(cas))
                cancelBool = eval('self.{}.cancelled()'.format(cas))
                casLogs[cas].info("The run on {} has been cancelled? {}.".format(cas, cancelBool))
            except asyncio.CancelledError:
                casLogs[cas].info("The run on {} has been cancelled.".format(cas))
            #Getting log, sending updated log chunk, and publishing taskDF
            self.taskDF.loc[cas, 'status'] = 'shutdown'
            # self.taskDF.loc[cas, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
            # fn = casLogs[cas].handlers[0].baseFilename
            #Send updated log
            start = self.taskDF.loc[cas, 'endlog'] + 1
            linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
            if len(linesToSend) > 0:
                self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
            #Update end line number of log
            self.taskDF.loc[cas, 'endlog'] = currentEnd
            
            self.publish('com.prepbot.prothandler.finish-shutdown', cas, self.taskDF.loc[cas].to_json())
        else:
            casLogs[cas].warning('{} is not running a protocol...'.format(cas))
            self.taskDF.loc[cas, 'status'] = 'idle'
            #self.taskDF.loc[cas, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
            self.publish('com.prepbot.prothandler.finish-shutdown', cas, self.taskDF.loc[cas].to_json())
            
            
    # @wamp.subscribe('com.prepbot.prothandler.next')
    # async def nextProtocol(self, cas):
    #     casLogs[cas].info('Trying to setup next run on {}, getting active tasks...'.format(cas))
    #     self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
    #     casLogs[cas].info(self.activeTasks)
    #     if cas in self.activeTasks:
    #         eval('self.{}.cancel()'.format(cas))
    #         self.taskDF.loc[cas,'status'] = 'stopped'
    #         try:
    #             eval('self.{}'.format(cas))
    #         except asyncio.CancelledError:
    #             casLogs[cas].info("The run on {} has been cancelled.".format(cas))
    #         self.publish('com.prepbot.prothandler.start-shutdown', cas)
    #         #Shutdown procedures...
    #         await self.shutdown(cas)
    #         #Clearing taskDF and publishing it
    #         self.taskDF.loc[cas,'status'] = 'shutdown'
    #         self.taskDF.loc[cas, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
    #         self.publish('com.prepbot.prothandler.finish-shutdown', cas, self.taskDF.loc[cas].to_json())
    #     else:
    #         casLogs[cas].info('{} is idle and ready for next run.'.format(cas))
    #         self.taskDF.loc[cas,'status'] = 'idle'
    #         self.taskDF.loc[cas, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
    #         self.publish('com.prepbot.prothandler.finish-shutdown', cas, self.taskDF.loc[cas].to_json(), True)
            
    
    
    async def restartClean(self, cas, stepNum):
        self.publish('com.prepbot.prothandler.start-clean', cas)
        await self.clean(cas)
        self.taskDF.loc[cas,'secsRemaining'] = 0
        self.taskDF.loc[cas,'stepNum'] = stepNum
        self.taskDF.loc[cas,'status'] = 'finished'
        casLogs[cas].info('Finished {} task!'.format(cas))
        #Send updated log
        start = self.taskDF.loc[cas,'endlog'] + 1
        linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
        if len(linesToSend) > 0:
            self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
        #Update end line number of log
        self.taskDF.loc[cas,'endlog'] = currentEnd
        self.publish('com.prepbot.prothandler.finish-clean', cas, self.taskDF.loc[cas].to_json())

    async def clean(self, cas):
        await asyncio.sleep(0.05)
        t0 = time.time()
        casLogs[cas].info('Cleaning {}'.format(cas))
        try:
            #The pump should always be at 0 for the beginning of every protocol step based on the asyncio.sleeps
            ctrl.info('syringeFluid before: {}'.format(self.syringeFluid))
            linevol = casParam[cas]['linevol']

            casLogs[cas].info('Disengage {}...'.format(cas))
            machine.cassette_eject(cas)
            self.taskDF.loc[cas, 'engaged'] = False

            casLogs[cas].info('CLEANING_PREP')
            machine.mux_to(cas)
            machine.pump_in(loadParam['clnVol'], speed=loadParam['clnInSpeed'])
            time.sleep(2)  # let residual babb settle
            #Settle where? the fluid that will be sent to waste has already been sucked up by the syringe...
            machine.mux_to('WASTE')
            machine.pump_out(loadParam['clnVol'], speed=loadParam['wasteSpeed'])

            await asyncio.sleep(0.05)
            casLogs[cas].info('WASHING LINE')
            machine.mux_to('MEOH')
            machine.pump_in(loadParam['washVol'], speed=loadParam['washInSpeed'])
            machine.mux_to(cas)
            # slow for the line speed because there is no drain attached once the cassette is ejected.
            machine.pump_out(linevol, speed=loadParam['clnOutSpeed'])
            machine.pump_in(linevol+loadParam['washVol'], speed=loadParam['clnInSpeed'])
            machine.mux_to('WASTE')
            machine.pump_out(linevol+loadParam['washVol'], speed=loadParam['wasteSpeed'])

            #Drain line again after residual fluid settles
            await asyncio.sleep(2)
            # time.sleep(2)
            machine.mux_to(cas)
            machine.pump_in(linevol, speed=loadParam['clnInSpeed'])
            machine.mux_to('WASTE')
            machine.pump_out(linevol, speed=loadParam['wasteSpeed'])

            self.syringeFluid = 'MEOH'
            ctrl.info('syringeFluid: {}'.format(self.syringeFluid))
            opTimeslog.info('Clean Time: {:0.2f}s'.format(time.time() - t0))

        except Exception as e:
            casLogs[cas].critical(e)
            
    async def restartShutdown(self, cas):
        self.publish('com.prepbot.prothandler.start-shutdown', cas)
        #Shutdown procedures...
        await self.shutdown(cas)
        #Getting log, sending updated log chunk, and publishing taskDF
        self.taskDF.loc[cas, 'status'] = 'shutdown'
        # self.taskDF.loc[cas, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
        # fn = casLogs[cas].handlers[0].baseFilename
        #Send updated log
        start = self.taskDF.loc[cas, 'endlog'] + 1
        linesToSend, currentEnd = self.get_caslogchunk(cas, start, end=0)
        if len(linesToSend) > 0:
            self.publish('com.prepbot.prothandler.update-cas-log', cas, linesToSend, currentEnd)
        #Update end line number of log
        self.taskDF.loc[cas, 'endlog'] = currentEnd
        self.publish('com.prepbot.prothandler.finish-shutdown', cas, self.taskDF.loc[cas].to_json())
    
    
    async def shutdown(self, cas):
        await asyncio.sleep(0.1)
        #Basic shutdown procedures when stopping a run before finishing.....
        casLogs[cas].info('SHUTDOWN {}'.format(cas))
        try:
            #Start time
            t0 = time.time()
            
            casLogs[cas].info('Disengage {}...'.format(cas))
            machine.cassette_eject(cas)
            self.taskDF.loc[cas, 'engaged'] = False

            #empty syringe
            #What if pump is already at 0? Should this be skipped?
            #Can this step accidentally happen in the middle of a load step for another cassette? I don't think so based off of the asyncio.sleeps
            casLogs[cas].info('EMPTYING SYRINGE')
            ctrl.info('EMPTYING SYRINGE')
            machine.mux_to('WASTE')
            machine.pump_to_ml(0, speed=loadParam['wasteSpeed'])
            machine.wait_move_done()

            #clean line
            await self.clean(cas)

            #Stop time
            opTimeslog.info('Shutdown Time: {:0.2f}s'.format(time.time()-t0))

        except Exception as e:
            casLogs[cas].critical(e)
            
    #Perhaps make this an async function that is awaited on as a named task for the debug screen
    @wamp.subscribe('com.prepbot.prothandler.exec-script')
    async def createTerminalTask(self, linesToSend):
        self.termTask = nTask.create_task(self.execScript(linesToSend), name='termTask-{}'.format(self.taskIter))
        self.taskIter += 1
        
    @wamp.subscribe('com.prepbot.prothandler.exec-stop')
    async def stopTermTasks(self):
        pending = [task for task in nTask.namedTask.all_tasks() if not task.done()]
        # ctrl.debug(pending)
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Find the tasks that have termTask in the name
        indices = [i for i, s in enumerate(self.activeTasks) if 'termTask' in s]
        # ctrl.debug(indices)
        termTasks = [pending[i] for i in indices]
        #Cancel all the termTasks
        for task in termTasks:
            ctrl.warning('Stopping {}'.format(task.get_name()))
            task.cancel()
        
        
    async def execScript(self, linesToExec):
        #Check if machine is connected and homed
        await self.connectNHome()
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
            if len(str(e))>0:
                ctrl.critical('Cannot evaluate script! Please check that function called exists and formatting is correct.')
                ctrl.critical(e)
            else:
                ctrl.warning('Canceling all termTasks...')
                asyncio.ensure_future(self.stopTermTasks())
                # await self.stopTermTasks()


    async def incubate(self, cas, incTime, mixAfter=None, mixVol=0.1, extraVolOut=0, earlyStopping=False, incSleep=10):
        # Get start time
        start = datetime.datetime.now()
        fn = casLogs[cas].handlers[0].baseFilename
        try:
            if not incTime > 0:
                casLogs[cas].warning('Inc. time not > 0: {}'.format(incTime))
                casLogs[cas].warning('Skipping incubation...')
                return
        except Exception as e:
            casLogs[cas].critical(e)
            casLogs[cas].critical('Skipping incubation...')
            return

        try:
            if mixAfter == 'undefined' or int(mixAfter) <= 0 or int(mixAfter) > int(incTime):
                waitI = int(incTime / incSleep)
                if waitI < 1:
                    waitI = 1
                # No washes/mixes, only one iteration
                washI = 1
                casLogs[cas].info('No washes for incubation. incTime={}, mixAfter={}'.format(incTime, mixAfter))
            else:
                #how many times to wash based on incubation time
                washI = int(incTime / mixAfter)
                # Divide mixAfter by incSleep to get the iterator for how many times to asyncio.sleep
                # wait iterator
                if mixAfter < incSleep:
                    incSleep = mixAfter
                    waitI = 1
                else:
                    waitI = int(mixAfter / incSleep)

        except Exception as e:
            casLogs[cas].critical(e)
            casLogs[cas].critical('Skipping incubation...')
            return
        casLogs[cas].info('INCUBATING {}'.format(cas))

        # Want to break out of this loop if timediff exceeds incTime
        exceedInc = False
        # Publish index
        p = 1
        for i in range(washI):
            if exceedInc:
                break
            for j in range(waitI):
                # Sleep for incSleep=10
                await asyncio.sleep(incSleep)
                diff = (datetime.datetime.now() - start).total_seconds()
                if earlyStopping and diff >= incTime:
                    exceedInc = True
                    break
                ctrl.debug("{} Incubation Seconds remaining: {}".format(cas, int(incTime - diff)))
                self.taskDF.loc[cas, 'secsRemaining'] = int(incTime - diff)
                # This interupts the processes on the wampHandler by publishing every second
                # Send a publish every 30 seconds?
                if diff > 30 * p:
                    casLogs[cas].info('{} publishing secs-remaining and new task DF!'.format(cas))
                    self.taskDF.loc[cas, 'endlog'] = await self.get_lastline(fn)
                    self.taskDF.loc[cas, 'secsRemaining'] = int(incTime - diff)
                    self.publish('com.prepbot.prothandler.update-taskdf', cas, self.taskDF.loc[cas].to_json())
                    p += 1

            if mixAfter == 'undefined' or int(mixAfter) <= 0 or int(mixAfter) > int(incTime):
                diff = (datetime.datetime.now() - start).total_seconds()
                casLogs[cas].info('FINISHED INCUBATION of {} for {}s'.format(cas, diff))
                return
            else:
                await asyncio.sleep(0.1)
                modHdl.close()
                modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas.lower()))
                casLogs[cas].info('Mixing {}...'.format(cas))
                t0 = time.time()
                try:
                    # If prior step was formalin, might want MEOH wash, but maybe dont need
                    machine.mux_to('AIR')
                    machine.pump_in(0.5, speed=loadParam['mixInSpeed'])
                    time.sleep(1)
                    machine.mux_to(cas)
                    machine.pump_in(mixVol, speed=loadParam['mixInSpeed'])
                    time.sleep(1)
                    if extraVolOut * loadParam['extraMixFactor'] < self.taskDF.loc[cas, 'volInLine']:
                        machine.pump_out(mixVol + extraVolOut, speed=loadParam['mixOutSpeed'])
                        self.taskDF.loc[cas, 'volInLine'] -= extraVolOut
                    else:
                        ctrl.info('Cannot pump extra volume out, linevol is nearly depleted {}ml.'.format(
                            self.taskDF.loc[cas, 'volInLine']))
                        # Could load more into line..?
                        machine.pump_out(mixVol, speed=loadParam['mixOutSpeed'])
                    # Reset pump
                    machine.mux_to('WASTE')
                    machine.pump_to_ml(0, speed=500)
                    machine.wait_move_done()

                    self.taskDF.loc[cas, 'endlog'] = await self.get_lastline(fn)
                    self.publish('com.prepbot.prothandler.update-taskdf', cas, self.taskDF.loc[cas].to_json())
                    casLogs[cas].info('Inc. Mix Time: {:0.2f}s'.format(time.time() - t0))
                    opTimeslog.info('Inc. Mix Time: {:0.2f}s'.format(time.time() - t0))

                except Exception as e:
                    casLogs[cas].critical(e)
                    # await self.stopProtocol(cas)
        diff = (datetime.datetime.now() - start).total_seconds()
        casLogs[cas].info('FINISHED INCUBATION of {} for {}s'.format(cas, diff))
        return
        
    async def mix(self, cas, numCycles, volume):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas.lower()))
        casLogs[cas].info("MIXING {}, {} TIMES, {} VOLUME".format(cas, numCycles, volume))
        try:
            machine.mux_to(cas)
            tStart = time.time()
            for i in range(int(numCycles)):
                # await asyncio.sleep(1)
                casLogs[cas].info('Mixing {}, #{} of {} cycles...'.format(cas,i+1,int(numCycles)))
                t0 = time.time()
                machine.pump_in(volume, speed=loadParam['mixInSpeed'])
                time.sleep(1)
                machine.pump_out(volume, speed=loadParam['mixOutSpeed'])
                opTimeslog.info('Mix cycle {} of {} Time: {:0.2f}s'.format(i+1, int(numCycles), time.time()-t0))
                
            opTimeslog.info('Mix Finished, {} cycles Time: {:0.2f}s'.format(int(numCycles), time.time()-tStart))
        except Exception as e:
            casLogs[cas].critical(e)
            # await self.stopProtocol(cas)

    async def purge(self, cas):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(cas.lower()))
        casLogs[cas].info('PURGING CHAMBER, {}'.format(cas))
        try:
            t0 = time.time()
            linevol = casParam[cas]['linevol']
            machine.mux_to('AIR')
            machine.pump_in(linevol + loadParam['purgeVol'], speed=loadParam['purgeInSpeed'])
            machine.mux_to(cas)
            machine.pump_out(linevol + loadParam['purgeVol'], speed=loadParam['purgeOutSpeed'])

            self.taskDF.loc[cas, 'currentFluid'] = 'AIR'
            self.taskDF.loc[cas, 'volInLine'] = 0
            opTimeslog.info('Purge, {} mL, {} purgeInSpeed, {} purgeOutSpeed, Time: {:0.2f}s'.format(loadParam['purgeVol'],
                                                                                             loadParam['purgeInSpeed'],
                                                                                             loadParam['purgeOutSpeed'],
                                                                                             time.time() - t0))
        except Exception as e:
            casLogs[cas].critical(e)
            # await self.stopProtocol(cas)

    ####################################################################################################################
    # Do not async/await these because I wan't these steps to be performed within a load reagent step without stopping
    ####################################################################################################################
    def washSyringe(self, reagent='MEOH', washVol=loadParam['washVol'], washInSpeed=loadParam['washInSpeed'], wasteSpeed=loadParam['wasteSpeed']):
        ctrl.info('syringeFluid before: {}'.format(self.syringeFluid))
        ctrl.info('WASH SYRINGE WITH {}'.format(reagent))
        machine.mux_to(reagent)
        machine.pump_in(washVol, speed=washInSpeed)
        machine.mux_to('WASTE')
        time.sleep(1)  # Why extra 1s?
        machine.pump_out(washVol, speed=wasteSpeed)

        self.syringeFluid = reagent
        ctrl.info('syringeFluid: {}'.format(self.syringeFluid))

    def washSyringeLogic(self, reagent, washSyr='auto', washSyrReagent='MEOH'):
        if reagent not in ['FORMALIN', 'MEOH', 'DYE', 'BABB']:
            # stop protocol
            raise ValueError('CANNOT LOAD {}....'.format(reagent))

        ctrl.info('syringeFluid before: {}'.format(self.syringeFluid))
        if washSyr == 'auto':
            if reagent in ['FORMALIN', 'MEOH']:
                # Check if last reagent in syringe was BABB, then need to wash syringe with MEOH first
                if self.syringeFluid == 'BABB':
                    self.washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
            elif reagent in ['DYE']:
                # If prior step was not MEOH, should wash syringe with MEOH
                if self.syringeFluid != 'MEOH':
                    self.washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
            elif reagent in ['BABB']:
                # If prior step was formalin, should do MEOH wash of syringe
                if self.syringeFluid == 'FORMALIN':
                    self.washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
            else:
                # The load reagent would never be None or AIR so this does nothing
                pass

        elif washSyr == True:
            # Force washing syringe
            self.washSyringe(reagent=washSyrReagent)
        else:
            # Do not wash the syringe
            pass

    def reuseOrPurgeLine(self, cas, reagent, ml, inSpeed, chamberSpeed):
        if reagent not in ['FORMALIN', 'MEOH', 'DYE', 'BABB']:
            # stop protocol
            raise ValueError('CANNOT LOAD {}....'.format(reagent))

        # Reuse linevol if it is reagent and has sufficient volInLine for pumping
        currentFluid = self.taskDF.loc[cas, 'currentFluid']
        volInLine = self.taskDF.loc[cas, 'volInLine']
        if currentFluid == reagent and ml * loadParam['volInLineFactor'] < volInLine:
            casLogs[cas].info('ADDING {}, REUSING {} linevol {}'.format(reagent, cas, volInLine))
            machine.mux_to('AIR')
            machine.pump_in(ml, speed=inSpeed)
            machine.mux_to(cas)
            machine.pump_out(ml, speed=chamberSpeed)

            self.taskDF.loc[cas, 'currentFluid'] = reagent
            self.taskDF.loc[cas, 'volInLine'] -= ml

            # Is the operation completed? Yes, because you are reusing the reagent in the line.
            return True
        elif currentFluid not in [None, 'AIR', reagent]:
            # Purge the line with AIR before starting
            casLogs[cas].info('{} LINE has {}, not {}'.format(cas, currentFluid, reagent))
            #Purge is an async function, cannot be run in this function
            # self.purge(cas=cas)
            casLogs[cas].info('PURGING CHAMBER, {}'.format(cas))
            linevol = casParam[cas]['linevol']
            machine.mux_to('AIR')
            machine.pump_in(linevol + loadParam['purgeVol'], speed=loadParam['purgeInSpeed'])
            machine.mux_to(cas)
            machine.pump_out(linevol + loadParam['purgeVol'], speed=loadParam['purgeOutSpeed'])

            self.taskDF.loc[cas, 'currentFluid'] = 'AIR'
            self.taskDF.loc[cas, 'volInLine'] = 0

            # Is the operation completed? No, you just purged the line so that the reagent could be loaded using specific load parameters...
            ####### goto reagent specific protocol #######
            return False
        else:
            # It's okay to fill the line with new fluid, do not reuse linevol
            # Is the operation completed? No, you can't reuse the linevol for the load operation. You need to continue.
            ####### goto reagent specific protocol #######
            return False

    def loadFreshReagent(self, cas, reagent, ml, inSpeed, chamberSpeed, lineSpeed, pumpInWait='auto'):
        if reagent not in ['FORMALIN', 'MEOH', 'DYE', 'BABB']:
            # stop protocol
            raise ValueError('CANNOT LOAD {}....'.format(reagent))
        if pumpInWait is None or pumpInWait == 'auto':
            # Get parameter from dictionary
            pumpInWait = reagParam[reagent]['pumpInWait']

        ####### reagent specific protocol #######
        # What do you want to modify here as parameters in a config file?
        if reagent == 'DYE':
            linevol = casParam[cas]['linevol']
            casLogs[cas].info('ADDING DYE to {}'.format(cas))
            # First get air into dye bottle to prevent neg pressure
            # May need to do in two steps of 0.5ml if pressure gets too high with 1
            machine.mux_to('AIR')
            machine.pump_in(loadParam['stainAirVol'] + linevol + ml, speed=loadParam['stainAirInSpeed'])
            machine.mux_to('DYE')
            # This doesn't make sense, shouldn't you completely pump out and then draw in the same volume?
            # If anything, pump out a little more air into the dye container?
            # Why have air in the pump at in this step all?
            machine.pump_out(linevol + ml, speed=loadParam['stainAirOutSpeed'])  # not too fast so there is no leakage
            machine.pump_in(linevol + ml, speed=inSpeed)  # draw dye back into syringe, dead vol small, ~0.1 ml?
            time.sleep(pumpInWait)  # 2s
            machine.mux_to(cas)
            machine.pump_out(linevol, speed=lineSpeed)  # Fast fill of reservoir
            machine.pump_out(ml, speed=chamberSpeed)  # Slow fill of chamber
            # May need to adjust the 0.2 depending on dead volume of dye bottle connector
            time.sleep(1)  # Why sleep here??
            # Need to reset the pump to 0 because it still has stainAirVol inside....
            machine.mux_to('WASTE')
            # Perhaps the pump should be zeroed at the end of every fluid operation to prevent accumulation of rounding errors?
            machine.pump_to_ml(0, speed=loadParam['stainAirOutSpeed'])
            machine.wait_move_done()
        elif reagent in ['FORMALIN', 'MEOH', 'BABB']:
            linevol = casParam[cas]['linevol']
            casLogs[cas].info('ADDING {} to {}'.format(reagent, cas))
            machine.mux_to(reagent)
            machine.pump_in(linevol + ml, speed=inSpeed)
            # BABB = 4s
            # FORMALIN = 1s
            # MEOH = 0s
            time.sleep(pumpInWait)  # give time to equilibrate pressure because reagent can be viscous
            machine.mux_to(cas)
            machine.pump_out(linevol, speed=lineSpeed)
            machine.pump_out(ml, speed=chamberSpeed)
        else:
            raise ValueError('{} loading is not implemented...'.format(reagent))

        # Update globals and taskDF
        self.taskDF.loc[cas, 'currentFluid'] = reagent
        self.taskDF.loc[cas, 'volInLine'] = linevol
        self.syringeFluid = reagent
        ctrl.info('syringeFluid: {}'.format(self.syringeFluid))

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    async def loadReagent(self, cas, reagent, ml, inSpeed=None, chamberSpeed=None, lineSpeed=None, washSyr='auto', washSyrReagent='MEOH'):
        await asyncio.sleep(0.1)
        #Setting reagent parameters according to config file or protocol
        if inSpeed is None or inSpeed == 'undefined' or reagSettings == 'config':
            inSpeed = reagParam[reagent]['inSpeed']
        if chamberSpeed is None or chamberSpeed == 'undefined' or reagSettings == 'config':
            chamberSpeed = reagParam[reagent]['chamberSpeed']
        if lineSpeed is None or lineSpeed == 'undefined' or reagSettings == 'config':
            lineSpeed = reagParam[reagent]['lineSpeed']

        try:
            t0 = time.time()
            self.washSyringeLogic(reagent=reagent, washSyr=washSyr, washSyrReagent=washSyrReagent)
            opTimeslog.info('FINISHED WASHING SYRINGE, Time: {:0.2f}s'.format(time.time() - t0))
            await asyncio.sleep(0.1)
            t0 = time.time()
            completed = self.reuseOrPurgeLine(cas=cas, reagent=reagent, ml=ml, inSpeed=inSpeed, chamberSpeed=chamberSpeed)
            if completed:
                # Finished with operation because the reagent within the line volume was used for the loading operation
                opTimeslog.info('FINISHED REUSING {} in {}, Time: {:0.2f}s'.format(reagent, cas, time.time() - t0))
                return
            else:
                await asyncio.sleep(0.1)
                t0 = time.time()
                self.loadFreshReagent(cas=cas, reagent=reagent, ml=ml, inSpeed=inSpeed,
                                      chamberSpeed=chamberSpeed, lineSpeed=lineSpeed,
                                      pumpInWait='auto')
                opTimeslog.info('FINISHED LOADING FRESH {} to {}, Time: {:0.2f}s'.format(reagent, cas, time.time() - t0))
        except Exception as e:
            casLogs[cas].critical(e)
            # await self.stopProtocol(cas)



if __name__ == '__main__':
    while True:
        runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1", auto_ping_timeout=120)
        try:
            runner.run(Component)
            loop = asyncio.get_event_loop()
            # loop.run_forever()
        except ConnectionRefusedError:
            time.sleep(2)
