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
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
import numpy as np
import re


class Component(ApplicationSession):
    
    '''protFuncs = {
    'self.incubate': self.incubate,
    'self.mix': self.mix,
    'self.'}'''

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.halted = True
        self.homed = False
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','engaged','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName'] ,
                                   index=['casA','casB','casC','casD','casE','casF'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        

    async def update(self):
        while True:
#            self.publish('com.prepbot.window.progress', self.progress)
            await asyncio.sleep(0.1)

    async def onJoin(self, details):
        #Trying to check if there was a disconnection recently
        #If disconnection occured, load in taskDF from file
        print('Loading last controller state...')
        disconnectDir = os.listdir('./Log/Disconnect')
        if 'disconnect-state.pkl' in disconnectDir:
            dcTask = pd.read_pickle('./Log/Disconnect/disconnect-state.pkl')
            print('Checking disonnect-state for last controller state...')
            print(dcTask)
            #Remove that file so that it would not disrupt a new controller instance
        else:
            dcTask = []
        #Else, new controller instance with no taskDF
        #Register so that GUI can get_tasks when reconnecting/joining
        try:
            self.register(self.get_tasks, 'com.prepbot.prothandler.controller-tasks')
        except Exception as e:
            print('Could not register get_tasks to router...')
            print(e)
        try:
            res = await self.subscribe(self)
            print("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            print("could not subscribe to procedure: {0}".format(e))
        asyncio.ensure_future(self.update())
        if len(dcTask):
            #Convert strings back to lists...
            if pd.notna(dcTask.status).sum() > 0 or dcTask.engaged.sum() > 0:
                self.taskDF = dcTask
                print('Repopulating controller tasks from contoller state...')
                self.repopulateController()
                print('Sending tasks to GUI to repopulate it...')
                self.publish('com.prepbot.prothandler.tasks-to-gui', self.taskDF.to_json())
            else:
                self.taskDF = dcTask
                print('dcTask has no engaged cassettes nor running/finished processes.')
                pass
        else:
            print('No dcTask file was found, starting controller in null state.')
            
        
    
    # def onLeave(self, details):
    #     print("Left, {}".format(self.activeTasks))
    
    def onDisconnect(self):
        print("Disconnected, {}".format(self.activeTasks))
        #Write the last state of the controller taskDF to a file
        print('Writing disconnect-state to file...')
        self.taskDF.to_pickle('./Log/Disconnect/disconnect-state.pkl')
        #Send signal to GUI that contoller was disconnected and to wait
        
        
    
    def get_tasks(self):
        return(self.taskDF.to_json())
    
    
    def repopulateController(self):
        runfin = self.taskDF[self.taskDF.status.isin(['running','finished'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running','finished'])].index
        
        for i in self.taskDF.index:
            print(i)
            if i in engagedCas:
                self.engage(i[-1])
            elif i in runfin:
                print(i, 'Restarting run!')
                self.startProtocol(casL=i[-1], taskJSON=None, restart=True)
                # self.publish('com.prepbot.prothandler.start', i[-1], None, True)
                
                
        
        print("Restore connection with logger(s)......NOT IMPLEMENTED YET...")
    # @wamp.subscribe('com.prepbot.prothandler.request-tasks-gui')
    # def sendTasks(self):
    #     self.publish('com.prepbot.prothandler.tasks-to-gui', self.taskDF.to_json())
    
    
    @wamp.subscribe('com.prepbot.prothandler.engage')
    def engage(self, casL):
        #How to check if cassette already is engaged....?
        print('Engage Cas{}...'.format(casL))
        #eval('machine.engage_sample{}()'.format(casL))
        time.sleep(1)
        self.publish('com.prepbot.prothandler.ready', casL, True)
        self.taskDF.loc['cas{}'.format(casL),'engaged'] = True
    
    @wamp.subscribe('com.prepbot.prothandler.disengage')
    def disengage(self, casL):
        print('Disengage Cas{}...'.format(casL))
        #eval('machine.disengage_sample{}()'.format(casL))
        time.sleep(1)
        self.publish('com.prepbot.prothandler.ready', casL, False)
        self.taskDF.loc['cas{}'.format(casL)] = np.nan
        self.taskDF.loc['cas{}'.format(casL),'engaged'] = False

        
    @wamp.subscribe('com.prepbot.prothandler.start')
    def startProtocol(self, casL, taskJSON, restart = False):
        if self.halted:
            # self.connect()
            self.halted = False
        if not self.homed:
            # self.home()
            self.homed = True
        casName = 'cas{}'.format(casL)
        # print(protPath)
        #Check if a task with that CasL name already exists
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Create task with CasL as the name
        if casName in self.activeTasks:
            print(self.activeTasks)
            print('Already running task on {}!'.format(casName))
            pass
        else:
            if restart:
                #Start at current stepNum and if the step is an incubate step,
                stepNum = int(self.taskDF.loc[casName,'stepNum'])
                print(stepNum)
                print('Restarting...')
                #update the runtime using secsRemaining
                if self.taskDF.loc[casName,'progressNames'][stepNum-1] == 'Incubation':
                    print('{}: Restarting incubate timer'.format(casName))
                    incStr = self.taskDF.loc[casName,'protocolList'][stepNum-1]
                    #Get parameters betwen parantheses
                    incParam = re.search('\(([^)]+)', incStr).group(1).split(',')
                    print(incParam)
                    #Find incTime
                    j = [ i for i, word in enumerate(incParam) if word.startswith('incTime=') ][0]
                    print(j)
                    #Change incTime
                    incParam[j] = 'incTime={}'.format(self.taskDF.loc[casName,'secsRemaining'])
                    #Change incStr and protocolList
                    self.taskDF.loc[casName,'protocolList'][stepNum-1] = 'self.incubate({})'.format(','.join(incParam))
                    print(self.taskDF.loc[casName,'protocolList'][stepNum-1])
            else:
                #Add step to taskDF
                self.taskDF.loc[casName] = pd.read_json(taskJSON, typ='series', dtype=object)
                #update taskDF to show that it was received by controller and started
                self.taskDF.loc[casName,'stepNum'] = 1
                stepNum = 1
                self.taskDF.loc[casName,'secsRemaining'] = self.taskDF.loc[casName,'stepTimes'][0]
            #get the protocol functions to be executed
            protStrings = self.taskDF.loc[casName,'protocolList']
            # print(protStrings)
            exec('self.{} = nTask.create_task(self.evalProtocol(casL, protStrings, stepNum), name="{}")'.format(casName,casName,stepNum))
            #update the activeTasks
            self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
            print(self.activeTasks)
            print('Starting task on {}'.format(casName))
        
    
    async def evalProtocol(self, casL, protStrings, stepNum=1):
        casName = 'cas{}'.format(casL)
        for i in range(stepNum-1, len(protStrings)):
            #Break up blocks of code, exec cannot be used because it does not return values
            #Eval() has poor security!!!! Should at least filter protStrings before evaluating...
            toEval = protStrings[i].split('\n')
            print(toEval)
            if len(toEval) > 1:
                #Need to gather functions so that the protocol step is completed synchronously
                #Important for synchronous sample purging then loading
                await asyncio.gather(eval(toEval[0]),eval(toEval[1]))
            else:
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
                print('Finished {} task!'.format(casName))
            #wampHandler will send a corresponding signal to QML to update the progress bar and GUI taskDF
            self.publish('com.prepbot.prothandler.progress', casL, self.taskDF.loc[casName].to_json())
            print('Updating progress on cas{}...'.format(casL))
            
    @wamp.subscribe('com.prepbot.prothandler.stop')
    async def stopProtocol(self, casL):
        casName = 'cas{}'.format(casL)
        print('Trying to cancel {}, getting active tasks...'.format(casName))
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        print(self.activeTasks)
        if casName in self.activeTasks:
            eval('self.{}.cancel()'.format(casName))
            try:
                eval('self.{}'.format(casName))
            except asyncio.CancelledError:
                print("The run on {} has been cancelled.".format(casName))
            #Shutdown procedures...
            await self.shutdown(casL)
            #Clearing taskDF and publishing it
            self.taskDF.loc[casName,'status'] = 'canceled'
            self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
        else:
            print('{} is not running a protocol...'.format(casName))
            self.taskDF.loc[casName,'status'] = 'idle'
            self.taskDF.loc[casName, ['stepNum','secsRemaining','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName']] = np.nan
    
    
    async def shutdown(self, casL):
        #Basic shutdown procedures when stopping a run before finishing.....
        print('SHUTDOWN Cas{}'.format(casL))
        time.sleep(2)
    
    async def incubate(self, casL, incTime, mixAfter=600):
        casName = 'cas{}'.format(casL)
        #Get start time
        start = datetime.datetime.now()
        mixMod = int(mixAfter/2)
        washF = int(incTime/mixMod)
        print('INCUBATING Cas{}'.format(casL))
        #Want to break out of this loop if timediff exceeds incTime
        exceedInc = False
        #Publish index
        p=1
        for i in range(washF):
            if exceedInc:
                break
            for j in range(mixMod):
                #Do I really have to check every second? or can I sleep for longer?
                await asyncio.sleep(1)
                diff = (datetime.datetime.now() - start).total_seconds()
                if diff >= incTime:
                    exceedInc = True
                    break
                print("Cas{} Incubation Seconds remaining: {}".format(casL,int(incTime - diff)))
                self.taskDF.loc[casName,'secsRemaining'] = int(incTime - diff)
                #This interupts the processes on the wampHandler by publishing every second
                #Send a publish every 30 seconds?
                if diff > 30*p:
                    print('Cas{} publishing secs-remaining!'.format(casL))
                    self.publish('com.com.prepbot.prothandler.secs-remaining',casL,int(incTime - diff))
                    p += 1
            if ((i % 2) == 0):
                await asyncio.sleep(0.01)
                print('Mixing {}...'.format(casL))
                #Goto last fluidtype???
                # eval('machine.goto_sample{}()'.format(casL))
                # machine.pump_in(0.5)
                time.sleep(2)
                # machine.pump_out(0.5)
    
    async def mix(self, casL, numCycles, volume):
        await asyncio.sleep(0.01)
        print("MIXING Cas{}, {} TIMES, {} VOLUME".format(casL, numCycles, volume))
        # eval('machine.goto_sample{}()'.format(casL))
        for i in range(int(numCycles)):
            # await asyncio.sleep(0.01)
            print('Mixing {}, #{} of {} cycles...'.format(casL,i+1,int(numCycles)))
            # Goto last fluidtype???
            # machine.pump_in(volume)
            time.sleep(2)
            # machine.pump_out(volume)
    
    async def purge(self, casL, deadvol):
        await asyncio.sleep(0.01)
        print('PURGING CHAMBER, Cas{}'.format(casL))
        # Goto last fluidtype???
        # eval('machine.goto_sample{}()'.format(casL))
        # machine.pump_in(deadvol)
        time.sleep(5)
        #machine.empty_syringe()
    
    async def loadReagent(self, casL, loadstr, reagent, vol, speed, deadvol):
        await asyncio.sleep(0.01)
        print('PURGING CHAMBER, Cas{}'.format(casL))
        # eval('machine.goto_sample{}()'.format(casL))
        # machine.pump_in(deadvol)
        time.sleep(5)
        #machine.empty_syringe()

        print('ADDING {} TO Cas{}'.format(loadstr, casL))
        # eval('machine.goto_{}()'.format(reagent))
        # machine.pump_in(vol,speed)
        time.sleep(5)
        # eval('machine.goto_sample{}()'.format(casL))
        # machine.pump_out(vol,speed)

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
