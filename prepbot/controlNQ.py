#!/home/jackr/anaconda/envs/QML36/bin/python
import os
import sys
sys.path.append('/home/pi/CasMonitorQt5/')
import asyncio
from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn import wamp
import time
import datetime
import machine
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
#machinelog.setLevel(logging.INFO)
opTimeslog = logging.getLogger('ctrl.opTimes')
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



#open YAML file with parameters....
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


param = confY['parameters']

# mixSpeed = 1
# incSpeed = 0.2
# removeSpeed = 1
# wasteSpeed = 4
# fillLineSpeed = 1
# fillSyrSpeed = 1
# washSyrSpeed = 1

# # sample deadspace
# LINEVOL = 0.75
# removeVol = 4
# purgeVol = 5

# #Dictionary for density adjustments
# #vial==stain
# #unk or unknown for first fluid in chamber. It adjusts like if it were water in the chamber
# reaDensOrder = {'meoh':0,'vial':0,'formalin':1,'babb':2, 'unk': 1}
# #Density column adjustment volume and speed
# densVol = 0.1
# densSpeed = 0.2
# #Time to let fluid layers settle before density adjustment (secs)
# settleTime = 15

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
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','currentFluid','engaged','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName','startlog','endlog'] ,
                                   index=['casA','casB','casC','casD','casE','casF'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        self.guiStatus = 'disconnected'
        self.taskIter = 1
    
    # @wamp.subscribe('com.prepbot.prothandler.heartbeat-ctrl')
    async def heartbeat(self):
        if self.guiStatus == 'disconnected':
            self.guiStatus = 'connected'
            
    async def halt(self):
        machine.send('M112', read_response=False)
        self.halted = True
        self.homed = False

    def send_mStatus(self):
        return(self.homed)
    
    
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
        #Set global param
        self.set_param(paramDict)
        #Write to YAML file...
        with open('./prepbot/config.yaml', 'w') as f:
            # yaml.dump(confY, f, default_flow_style=False, sort_keys=False)
            ordered_dump(confY, f, Dumper=yaml.SafeDumper)
            
        ctrl.debug('Wrote parameters to config.yaml!')
        #Confirm GUI is updated...
        self.publish('com.prepbot.prothandler.send-param-gui', param)
    
    def set_param(self, paramDict):
        global confY, param
        for k in paramDict.keys():
            param[k] = paramDict[k]
        confY['parameters'] = param
            
    def send_param(self):
        self.publish('com.prepbot.prothandler.send-param-gui', param)
        
                
    async def onJoin(self, details):
        #Trying to check if there was a disconnection recently
        #If disconnection occured, load in taskDF from file
        ctrl.info(sys.getrecursionlimit())
        ctrl.info('Loading last controller state...')
        disconnectDir = os.listdir('./Log/disconnect')
        if 'disconnect-state.pkl' in disconnectDir:
            dcTask = pd.read_pickle('./Log/disconnect/disconnect-state.pkl')
            ctrl.info('Checking disconnect-state for last controller state...')
            ctrl.debug('\n{}'.format(dcTask))
            self.taskDF = dcTask
            #Remove that file so that it would not disrupt a new controller instance
        else:
            dcTask = []
        #Else, new controller instance with no taskDF
        #Register so that GUI can get_tasks when reconnecting/joining
        try:
            self.register(self.get_tasks, 'com.prepbot.prothandler.controller-tasks')
            self.register(self.heartbeat, 'com.prepbot.prothandler.heartbeat-ctrl')
            self.register(self.get_caslogchunk, 'com.prepbot.prothandler.caslog-chunk')
            self.register(self.send_mStatus, 'com.prepbot.prothandler.gui-get-machine-homed')
            self.register(self.send_param, 'com.prepbot.prothandler.gui-get-param')
            ctrl.info('Registered to all procedures!')
        except Exception as e:
            ctrl.error('Could not register functions to router...')
            ctrl.error(e)
        try:
            res = await self.subscribe(self)
            ctrl.info("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            ctrl.error("could not subscribe to procedure: {0}".format(e))

        asyncio.ensure_future(self.update())
        #After connecting to router, make sure machine is connected and check if it should be homed
        if self.halted == True:
        	try:
        		# machine.acquire()
        		self.halted = False
        	except Exception as e:
        		ctrl.critical('Could not acquire machine lock!')
        		ctrl.critical(e)
        		self.writeDCstate = False
        		self.leave()
        		self.disconnect()

        #Check if GUI says that machine has been homed. If GUI is not responsive, timeput
        ctrl.info('Checking if GUI says that machine is homed...')
        try:
            # mstat = asyncio.ensure_future(self.call('com.prepbot.prothandler.is-machine-homed'))
            self.homed = await asyncio.wait_for(self.call('com.prepbot.prothandler.is-machine-homed'), timeout=3.5)
            ctrl.info('Machine is homed? : {}'.format(self.homed))
        except Exception as e:
        	ctrl.warning('GUI may not be connected! Setting machine homed status to False.')
        	ctrl.warning(e)
        	self.homed = False

        if self.homed == False:
            try:
                ctrl.info('Resetting and homing machine...')
                # machine.reset()
                # machine.home()
                self.homed = True
                self.halted = False
                try:
                    await asyncio.wait_for(self.call('com.prepbot.prothandler.set-machine-homed', True), timeout=3.5)
                except Exception as e:
                    ctrl.warning('GUI may not be connected! Machine has been homed.')
                    ctrl.warning(e)
            except Exception as e:
	            ctrl.critical('Could not reset and home machine!')
	            ctrl.critical(e)
	            self.writeDCstate = False
	            self.leave()
	            self.disconnect()
                
        ctrl.info('Sending parameters to GUI...')
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
                time.sleep(5)
                # machine.goto_park()
                ctrl.info('Parking machine...')
            except Exception as e:
	            ctrl.critical('Could not park machine!')
	            ctrl.critical(e)
	        

    async def connectNHome(self):
        if self.halted == True:
            try:
                # machine.acquire()
                self.halted = False 
            except Exception as e:
                ctrl.critical(e)
                
        ctrl.info('Checking if machine is connected and homed....')

        if self.homed == False:
            try:
                # machine.reset()
                # machine.home()
                self.homed = True
                await self.call('com.prepbot.prothandler.set-machine-homed', True)
            except Exception as e:
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
        
    
    # def update_caslogchunk(self, casL):
    #     #Send updated log
    #     start = self.taskDF.loc['cas{}'.format(casL),'endlog'] + 1
    #     linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
    #     if len(linesToSend) > 0:
    #         self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
    #     #Update end line number of log
    #     self.taskDF.loc['cas{}'.format(casL),'endlog'] = currentEnd
                    
    async def get_lastline(self, fn):
        with open(fn, 'r') as logfile:
                for i, line in enumerate(logfile):
                    pass
                last_line_num = i
        return(last_line_num)
                    
    
    async def repopulateController(self):
        running = self.taskDF[self.taskDF.status.isin(['running'])].index
        cleanStop = self.taskDF[self.taskDF.status.isin(['cleaning','stopping'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running','cleaning','stopping'])].index
        
        for i in self.taskDF.index:
            ctrl.debug(i)
            if i in engagedCas:
                await self.engage(i[-1])
            elif i in running:
                await self.engage(i[-1])
                ctrl.info('{}, Restarting run!'.format(i))
                asyncio.ensure_future(self.startProtocol(casL=i[-1], taskJSON=None, restart=True))
                # self.publish('com.prepbot.prothandler.start', i[-1], None, True)
            elif i in cleanStop:
                ctrl.info('{}, Restarting clean/shutdown!'.format(i))
                asyncio.ensure_future(self.startProtocol(casL=i[-1], taskJSON=None, restart=True))
                
                
                
    
    
    @wamp.subscribe('com.prepbot.prothandler.engage')
    async def engage(self, casL):
        #How to check if cassette already is engaged....?
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        #Check if machine is connected and homed
        await self.connectNHome()
        casLogs[casL].info('Engage Cas{}...'.format(casL))
        try:
            # time.sleep(5)
            # eval('machine.engage_sample{}()'.format(casL))
            self.publish('com.prepbot.prothandler.ready', casL, True)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = True

        except Exception as e:
            ctrl.critical('Machine could not engage cas{}. Does it exist?'.format(casL))
            ctrl.critical(e)
            self.taskDF.loc['cas{}'.format(casL)] = np.nan
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            self.publish('com.prepbot.prothandler.ready', casL, False)
            
    @wamp.subscribe('com.prepbot.prothandler.disengage')
    async def disengage(self, casL):
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        #Check if machine is connected and homed
        await self.connectNHome()
        casLogs[casL].info('Disengage Cas{}...'.format(casL))
        try:
            # time.sleep(5)
            # eval('machine.disengage_sample{}()'.format(casL))
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
        casName = 'cas{}'.format(casL)
        #Check if a task with that CasL name already exists
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Create task with CasL as the name
        if casName in self.activeTasks:
            casLogs[casL].info(self.activeTasks)
            casLogs[casL].info('Already running task on {}!'.format(casName))
            #Repopulate GUI because it must be wrong!
            self.publish('com.prepbot.prothandler.one-task-to-gui', casName, self.taskDF.loc[casName].to_json())
            pass
        else:
        	#Check if machine is connected and homed
            await self.connectNHome()
            
            if restart:
                casLogs[casL].debug(self.taskDF.loc[casName, 'status'])
                if self.taskDF.loc[casName, 'status'] == 'cleaning':
                    progStrings = self.taskDF.loc[casName,'progressNames']
                    stepNum = len(progStrings)
                    
                    exec('self.{} = nTask.create_task(self.restartClean(casL, stepNum), name="{}")'.format(casName,casName))
                    
                elif self.taskDF.loc[casName, 'status'] == 'stopping':
                    exec('self.{} = nTask.create_task(self.restartShutdown(casL), name="{}")'.format(casName,casName))

                elif self.taskDF.loc[casName, 'status'] == 'running':
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
                    #get the protocol functions to be executed
                    protStrings = self.taskDF.loc[casName,'protocolList']
                    progStrings = self.taskDF.loc[casName,'progressNames']
                    exec('self.{} = nTask.create_task(self.evalProtocol(casL, protStrings, progStrings, stepNum), name="{}")'.format(casName,casName))
                    #update the activeTasks
                    self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
                    casLogs[casL].info('Starting task on {}'.format(casName))
                    casLogs[casL].info(self.activeTasks)

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
                # self.taskDF.loc[casName,'endlog'] = start
                casLogs[casL].info('Starting Run!\n{}'.format(self.taskDF.loc[casName,['sampleName','protocolName','protocolPath','startlog']]))
                stepNum = 1
                self.taskDF.loc[casName,'secsRemaining'] = self.taskDF.loc[casName,'stepTimes'][0]
                #get the protocol functions to be executed
                protStrings = self.taskDF.loc[casName,'protocolList']
                progStrings = self.taskDF.loc[casName,'progressNames']
                exec('self.{} = nTask.create_task(self.evalProtocol(casL, protStrings, progStrings, stepNum), name="{}")'.format(casName,casName))
                #update the activeTasks
                self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
                casLogs[casL].info('Starting task on {}'.format(casName))
                casLogs[casL].info(self.activeTasks)
                #publish that task was started to GUI
                samplelog, currentEnd = self.get_caslogchunk(casL, start, end=0)
                self.taskDF.loc[casName,'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.started', casName, self.taskDF.loc[casName].to_json(), samplelog, currentEnd)
                # self.publish('com.prepbot.prothandler.one-task-to-gui', casName, self.taskDF.loc[casName].to_json())
                
            
    async def evalProtocol(self, casL, protStrings, progStrings, stepNum=1):
        casName = 'cas{}'.format(casL)
        # fn = casLogs[casL].handlers[0].baseFilename
        # i=stepNum-1
        # while i < len(protStrings):
        casLogs[casL].debug(protStrings)
        casLogs[casL].debug(progStrings)
        casLogs[casL].debug(stepNum)
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
            else:
                #this is the last step when it is completed
                #Disengage sample and clean the line using finishedRun()
                self.taskDF.loc[casName,'secsRemaining'] = 0
                self.taskDF.loc[casName,'stepNum'] = i+1
                #Send updated log
                start = self.taskDF.loc[casName,'endlog'] + 1
                linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
                if len(linesToSend) > 0:
                    self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
                #Update end line number of log
                self.taskDF.loc[casName,'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.progress', casL, self.taskDF.loc[casName].to_json())
                casLogs[casL].info('Finished all steps, starting to clean cas{}...'.format(casL))
                
                #start cleaning
                self.taskDF.loc[casName,'status'] = 'cleaning'
                self.publish('com.prepbot.prothandler.start-clean', casL)
                await self.clean(casL)
                
                self.taskDF.loc[casName,'status'] = 'finished'
                casLogs[casL].info('Finished {} task!'.format(casName))
                #Send updated log
                start = self.taskDF.loc[casName,'endlog'] + 1
                linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
                if len(linesToSend) > 0:
                    self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
                #Update end line number of log
                self.taskDF.loc[casName,'endlog'] = currentEnd
                self.publish('com.prepbot.prothandler.finish-clean', casL, self.taskDF.loc[casName].to_json())
                
            
            
    @wamp.subscribe('com.prepbot.prothandler.stop')
    async def stopProtocol(self, casL):
        casName = 'cas{}'.format(casL)
        casLogs[casL].info('Trying to cancel {}, getting active tasks...'.format(casName))
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        casLogs[casL].info(self.activeTasks)
        if casName in self.activeTasks:
            self.taskDF.loc[casName,'status'] = 'stopping'
            eval('self.{}.cancel()'.format(casName))
            self.publish('com.prepbot.prothandler.start-shutdown', casL)
            #Shutdown procedures...
            await self.shutdown(casL)
            self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
            casLogs[casL].info(self.activeTasks)
            try:
                eval('self.{}'.format(casName))
                cancelBool = eval('self.{}.cancelled()'.format(casName))
                casLogs[casL].info("The run on {} has been cancelled? {}.".format(casName, cancelBool))
            except asyncio.CancelledError:
                casLogs[casL].info("The run on {} has been cancelled.".format(casName))
            #Getting log, sending updated log chunk, and publishing taskDF
            self.taskDF.loc[casName,'status'] = 'shutdown'
            # self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
            # fn = casLogs[casL].handlers[0].baseFilename
            #Send updated log
            start = self.taskDF.loc[casName,'endlog'] + 1
            linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
            if len(linesToSend) > 0:
                self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
            #Update end line number of log
            self.taskDF.loc[casName,'endlog'] = currentEnd
            
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
            
    
    
    async def restartClean(self, casL, stepNum):
        self.publish('com.prepbot.prothandler.start-clean', casL)
        await self.clean(casL)
        casName = 'cas{}'.format(casL)
        self.taskDF.loc[casName,'secsRemaining'] = 0
        self.taskDF.loc[casName,'stepNum'] = stepNum
        self.taskDF.loc[casName,'status'] = 'finished'
        casLogs[casL].info('Finished {} task!'.format(casName))
        #Send updated log
        start = self.taskDF.loc[casName,'endlog'] + 1
        linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
        if len(linesToSend) > 0:
            self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
        #Update end line number of log
        self.taskDF.loc[casName,'endlog'] = currentEnd
        self.publish('com.prepbot.prothandler.finish-clean', casL, self.taskDF.loc[casName].to_json())
        
    
    
    async def clean(self, casL, deadvol=param['LINEVOL']):
        await asyncio.sleep(0.1)
        #Basic cleaning procedures when finishing a run
        try:
        #Start time
            t0 = time.time()
            casLogs[casL].info('Disengage Cas{}...'.format(casL))
            # eval('machine.disengage_sample{}'.format(casL))
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            
            casLogs[casL].info('Cleaning line for Cas{}'.format(casL))
            casLogs[casL].info('PURGING LINE, Cas{}'.format(casL))
            # eval('machine.goto_sample{}()'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            
            await asyncio.sleep(5)
            
            casLogs[casL].info('MEOH WASH of Cas{} LINE'.format(casL))
            # machine.goto_meoh()
            # machine.pump_in(deadvol, param['washSyrSpeed'])
            #wash the line
            # eval('machine.goto_sample{}()'.format(casL))
            #fill linevol
            # machine.pump_out(deadvol, param['fillLineSpeed'])
            #remove from line
            casLogs[casL].info('REMOVING MEOH WASH from LINE, Cas{}'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            
            #Stop time
            casLogs[casL].info('Clean Time: {:0.2f}s'.format(time.time()-t0))
            opTimeslog.info('Clean Time: {:0.2f}s'.format(time.time()-t0))
            
        except Exception as e:
            casLogs[casL].critical(e)
            
    async def restartShutdown(self, casL):
        self.publish('com.prepbot.prothandler.start-shutdown', casL)
        #Shutdown procedures...
        await self.shutdown(casL)
        casName = 'cas{}'.format(casL)
        #Getting log, sending updated log chunk, and publishing taskDF
        self.taskDF.loc[casName,'status'] = 'shutdown'
        # self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
        # fn = casLogs[casL].handlers[0].baseFilename
        #Send updated log
        start = self.taskDF.loc[casName,'endlog'] + 1
        linesToSend, currentEnd = self.get_caslogchunk(casL, start, end=0)
        if len(linesToSend) > 0:
            self.publish('com.prepbot.prothandler.update-cas-log', casL, linesToSend, currentEnd)
        #Update end line number of log
        self.taskDF.loc[casName,'endlog'] = currentEnd
        self.publish('com.prepbot.prothandler.finish-shutdown', casL, self.taskDF.loc[casName].to_json())
    
    
    async def shutdown(self, casL, deadvol=param['LINEVOL']):
        await asyncio.sleep(0.1)
        #Basic shutdown procedures when stopping a run before finishing.....
        casLogs[casL].info('SHUTDOWN Cas{}'.format(casL))
        try:
        #Start time
            t0 = time.time()
            
            casLogs[casL].info('Disengage Cas{}...'.format(casL))
            # eval('machine.disengage_sample{}'.format(casL))
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            
            casLogs[casL].info('Cleaning line for Cas{}'.format(casL))
            casLogs[casL].info('PURGING LINE, Cas{}'.format(casL))
            # eval('machine.goto_sample{}()'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            
            await asyncio.sleep(5)
            
            casLogs[casL].info('MEOH WASH of Cas{} LINE'.format(casL))
            # machine.goto_meoh()
            # machine.pump_in(deadvol, param['washSyrSpeed'])
            #wash the line
            # eval('machine.goto_sample{}()'.format(casL))
            #fill linevol
            # machine.pump_out(deadvol, param['fillLineSpeed'])
            #remove from line
            casLogs[casL].info('REMOVING MEOH WASH from LINE, Cas{}'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            
            #Stop time
            casLogs[casL].info('Shutdown Time: {:0.2f}s'.format(time.time()-t0))
            opTimeslog.info('Shutdown Time: {:0.2f}s'.format(time.time()-t0))

        except Exception as e:
            casLogs[casL].critical(e)
            
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
            
    
    async def incubate(self, casL, incTime, mixAfter=600, incSleep=10):
        casName = 'cas{}'.format(casL)
        #Get start time
        start = datetime.datetime.now()
        fn = casLogs[casL].handlers[0].baseFilename
        try:
            if not incTime > 0:
                casLogs[casL].warning('Inc. time not > 0: {}'.format(incTime))
                casLogs[casL].warning('Skipping incubation...')
                return
        except Exception as e:
            casLogs[casL].critical(e)
            casLogs[casL].critical('Skipping incubation...')
            return
        
        try:
            if mixAfter=='undefined' or int(mixAfter)<=0 or int(mixAfter) > int(incTime):
                waitI= int(incTime/incSleep)
                if waitI < 1:
                    waitI=1
                #No washes/mixes, only one iteration
                washI = 1
                casLogs[casL].info('No washes for incubation. incTime={}, mixAfter={}'.format(incTime, mixAfter))
            else:
                mixMod = int(mixAfter/2)
                if mixMod < 1:
                    mixMod=1
                washI = int(incTime/mixMod)
                #Divide mixMod by the incSleep to get the iterator for how many times to asyncio.sleep
                #wait iterator
                if mixMod < incSleep:
                    incSleep = mixMod
                    waitI = 1
                else:
                    waitI = int(mixMod/incSleep)
                
        except Exception as e:
            casLogs[casL].critical(e)
            casLogs[casL].critical('Skipping incubation...')
            return
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
                    casLogs[casL].info('Cas{} publishing secs-remaining and new task DF!'.format(casL))
                    self.taskDF.loc['cas{}'.format(casL),'endlog'] = await self.get_lastline(fn)
                    self.taskDF.loc[casName,'secsRemaining'] = int(incTime - diff)
                    self.publish('com.prepbot.prothandler.update-taskdf',casL,self.taskDF.loc[casName].to_json())
                    p += 1
            if ((i % 2) == 0):
                await asyncio.sleep(0.1)
                modHdl.close()
                modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
                casLogs[casL].info('Mixing Cas{}...'.format(casL))
                #Goto last fluidtype???
                try:
                    t0 = time.time()
                    # eval('machine.goto_sample{}()'.format(casL))
                    # machine.pump_in(0.6, param['incSpeed'])
                    time.sleep(1)
                    # machine.pump_out(0.6, param['incSpeed'])
                    self.taskDF.loc['cas{}'.format(casL),'endlog'] = await self.get_lastline(fn)
                    self.publish('com.prepbot.prothandler.update-taskdf',casL,self.taskDF.loc[casName].to_json())
                    casLogs[casL].info('Inc. Mix Time: {:0.2f}s'.format(time.time()-t0))
                    opTimeslog.info('Inc. Mix Time: {:0.2f}s'.format(time.time()-t0))
                except Exception as e:
                    casLogs[casL].critical(e)
                    # await self.stopProtocol(casL)
        
        casLogs[casL].info('FINISHED INCUBATION of Cas{}'.format(casL))
        
    async def mix(self, casL, numCycles, volume):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info("MIXING Cas{}, {} TIMES, {} VOLUME".format(casL, numCycles, volume))
        try:
            # eval('machine.goto_sample{}()'.format(casL))
            tStart = time.time()
            for i in range(int(numCycles)):
                # await asyncio.sleep(0.01)
                casLogs[casL].info('Mixing {}, #{} of {} cycles...'.format(casL,i+1,int(numCycles)))
                t0 = time.time()
                # machine.pump_in(volume, param['mixSpeed'])
                # machine.pump_out(volume, param['mixSpeed'])
                opTimeslog.info('Mix cycle {} of {} Time: {:0.2f}s'.format(i+1, int(numCycles), time.time()-t0))
                
            opTimeslog.info('Mix Finished, {} cycles Time: {:0.2f}s'.format(int(numCycles), time.time()-tStart))
        except Exception as e:
            casLogs[casL].critical(e)
            # await self.stopProtocol(casL)
        
    async def purge(self, casL, deadvol=param['LINEVOL']):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        casLogs[casL].info('PURGING CHAMBER, Cas{}'.format(casL))
        # Goto last fluidtype???
        try:
            t0 = time.time()
            # eval('machine.goto_sample{}()'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            opTimeslog.info('Purge, {} mL, {} removeSpeed, {} wasteSpeed, Time: {:0.2f}s'.format(param['removeVol'], param['removeSpeed'], param['wasteSpeed'], time.time()-t0))
        except Exception as e:
            casLogs[casL].critical(e)
            # await self.stopProtocol(casL)
        
    async def loadReagent(self, casL, reagent, vol, speed, deadvol=param['LINEVOL'], washSyr=False, loadstr=None):
        await asyncio.sleep(0.1)
        modHdl.close()
        modHdl.baseFilename = os.path.abspath('./Log/cas{}.log'.format(casL))
        if loadstr==None:
            loadstr = reagent
            
        try:
            tStart = time.time()
            t0 = time.time()
            casLogs[casL].info('PURGING CHAMBER, Cas{}'.format(casL))
            # eval('machine.goto_sample{}()'.format(casL))
            # machine.pump_in(param['removeVol'], param['removeSpeed'])
            
            # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
            opTimeslog.info('Purge, {} mL, {} removeSpeed, {} wasteSpeed, Time: {:0.2f}s'.format(param['removeVol'], param['removeSpeed'], param['wasteSpeed'], time.time()-t0))
            # #flowThru = param['purgeVol'] + deadvol
            # #machine.pump_out(flowThru, purgeSpeed)
            
            if washSyr == True:
                t0 = time.time()
                casLogs[casL].info('WASHING SYRINGE WITH {}'.format(loadstr))
                # eval('machine.goto_{}()'.format(reagent))
                deVol = vol + deadvol
                # machine.pump_in(deVol, param['washSyrSpeed'])
                #wash the line
                # eval('machine.goto_sample{}()'.format(casL))
                #fill linevol
                # machine.pump_out(deadvol, param['fillLineSpeed'])
                #remove from line
                # machine.pump_in(param['removeVol'], param['removeSpeed'])
                
                # machine.empty_syringe(param['purgeVol'], param['wasteSpeed'])
                opTimeslog.info('Wash Syringe, {} mL, {} washSyrSpeed, {} fillLineSpeed, Time: {:0.2f}s'.format(deVol, param['washSyrSpeed'], param['fillLineSpeed'], time.time()-t0))
                
            t0 = time.time()    
            casLogs[casL].info('ADDING {} TO Cas{}'.format(loadstr, casL))
            # eval('machine.goto_{}()'.format(reagent))
            deVol = vol + deadvol
    #            assume lines are primed....
            # machine.pump_in(deVol, param['fillSyrSpeed'])
            # eval('machine.goto_sample{}()'.format(casL))
            #pump out to LINEVOL at fillLineSpeed
            # machine.pump_out(deadvol, param['fillLineSpeed'])
            if reagent == 'babb':
                time.sleep(2)
            #pump out remaining fluid to fill the cassette depending on adjustable volume and speed
            # machine.pump_out(vol, speed)
            opTimeslog.info('Adding {}, {} mL, {} fillLineSpeed, {} speed, Time: {:0.2f}s'.format(loadstr, vol, param['fillLineSpeed'], speed, time.time()-t0))
        
        except Exception as e:
            casLogs[casL].citical('Load Reagent, 1st block error...')
            casLogs[casL].citical(e)
        
        #adjust for last fluid density
        #meoh < formalin/water < babb
        residualFluid = self.taskDF.loc['cas{}'.format(casL),'currentFluid']
        reaDen = param['reagentDensOrder'][reagent]
        try:
            residualDen = param['reagentDensOrder'][residualFluid]
        except Exception as e:
            casLogs[casL].warning('Residual fluid may not be inside of density adjustment dictionary: {}'.format(residualFluid))
            casLogs[casL].warning(e)
            casLogs[casL].info('Setting residual fluid to unknown (unk)')
            residualDen = param['reagentDensOrder']['unk']
            
        #update current fluid in taskDF
        self.taskDF.loc['cas{}'.format(casL),'currentFluid'] = reagent
        casLogs[casL].info('Cas{} CURRENT FLUID: {}'.format(casL, reagent))
        
        t0 = time.time()
        if reaDen > residualDen:
            #if reagent density > currentFluid density
            #pump out a little more reagent to push out the last fluid
            #Allow fluid density column to settle
            casLogs[casL].info('Cas{} SETTLE TIME: {}'.format(casL, param['settleTime']))
            await asyncio.sleep(param['settleTime'])
            casLogs[casL].info('Cas{}: Reagent ({}) is denser than residual fluid ({}). Pump out {}mL to push out residual fluid.'.format(casL, reagent, residualFluid, param['densVol']))
            try:
                # eval('machine.goto_sample{}()'.format(casL))
                # machine.pump_out(param['densVol'], param['densSpeed'])
                opTimeslog.info('Reagent denser than resid., adjusting, {}s settleTime, {} densVol, {} densSpeed, Time: {:0.2f}s'.format(param['settleTime'], param['densVol'], param['densSpeed'], time.time()-t0))
            except Exception as e:
                casLogs[casL].citical('Load Reagent, Density adjustment reaDen > residualDen error...')
                casLogs[casL].citical(e)
            
        elif reaDen < residualDen:
            #else if reagent density < currentFluid density
            #pump in a little to suck in last fluid
            #Pump out a little more to give room to suck in after fluid column settles
            try:
                # machine.pump_out(param['densVol'], param['densSpeed'])
                casLogs[casL].info('Pump out ({}mL) to give room for sucking residual fluid in...'.format(param['densVol']))
            except Exception as e:
                casLogs[casL].citical('Load Reagent, Density adjustment reaDen < residualDen error...')
                casLogs[casL].citical(e)
            #Allow fluid density column to settle
            casLogs[casL].info('Cas{} SETTLE TIME: {}'.format(casL, param['settleTime']))
            await asyncio.sleep(param['settleTime'])
            casLogs[casL].info('Cas{}: Reagent ({}) is less dense than residual fluid ({}). Pump in {}mL to suck in residual fluid.'.format(casL, reagent, residualFluid, param['densVol']))
            try:
                # eval('machine.goto_sample{}()'.format(casL))
                # machine.pump_in(param['densVol'], param['densSpeed'])
                opTimeslog.info('Reagent less dense than resid., adjusting, {}s settleTime, {} densVol, {} densSpeed, Time: {:0.2f}s'.format(param['settleTime'], param['densVol'], param['densSpeed'], time.time()-t0))
            except Exception as e:
                casLogs[casL].citical('Load Reagent, Density adjustment reaDen < residualDen error...')
                casLogs[casL].citical(e)
                
        else:
            #else None is currentFluid or reagent == current fluid density
            #no adjustment
            casLogs[casL].info('Cas{}: Reagent ({}) and residual fluid ({}) do not require a density adjustment.'.format(casL, reagent, residualFluid))
        
                
            casLogs[casL].info('FINISHED LOADING {} TO Cas{}, Time: {:0.2f}s'.format(loadstr, casL, time.time()-tStart))
            opTimeslog.info('FINISHED LOADING {} TO Cas{}, Time: {:0.2f}s'.format(loadstr, casL, time.time()-tStart))


if __name__ == '__main__':
    while True:
        runner = ApplicationRunner(url="ws://127.0.0.1:8080/ws", realm="realm1", auto_ping_timeout=120)
        try:
            runner.run(Component)
            loop = asyncio.get_event_loop()
            # loop.run_forever()
        except ConnectionRefusedError:
            time.sleep(2)
