from os import environ
import asyncio
from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner
from autobahn import wamp
import time
import datetime
import machine
import itertools
import namedTask as nTask


class Component(ApplicationSession):
    
    '''protFuncs = {
    'self.incubate': self.incubate,
    'self.mix': self.mix,
    'self.'}'''

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.halted = True
        self.homed = False
        self.allTasks = [task.get_name() for task in nTask.namedTask.all_tasks()]
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]

    async def update(self):
        while True:
#            self.publish('com.prepbot.window.progress', self.progress)
            await asyncio.sleep(0.1)

    async def onJoin(self, details):
        try:
            res = await self.subscribe(self)
            print("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            print("could not subscribe to procedure: {0}".format(e))
        asyncio.ensure_future(self.update())
        
        
    @wamp.subscribe('com.prepbot.prothandler.start')
    async def startProtocol(self, casL, protStrings, progStrings, protPath):
        if self.halted:
            # self.connect()
            self.halted = False
        if not self.homed:
            # self.home()
            self.homed = True
        casName = 'cas{}'.format(casL)
        # print(protStrings)
        print(progStrings)
        # print(protPath)
        #Check if a task with that CasL name already exists
        self.allTasks = [task.get_name() for task in nTask.namedTask.all_tasks()]
        self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
        #Create task with CasL as the name
        if casName in self.activeTasks:
            print(self.activeTasks)
            print('Already running task on {}!'.format(casName))
            pass
        else:
            exec('self.{} = nTask.create_task(self.evalProtocol(casL, protStrings), name="{}")'.format(casName,casName))
            self.allTasks = [task.get_name() for task in nTask.namedTask.all_tasks()]
            self.activeTasks = [task.get_name() for task in nTask.namedTask.all_tasks() if not task.done()]
            print(self.activeTasks)
            print('Starting task on {}'.format(casName))
        
    
    async def evalProtocol(self, casL, protStrings):
        for i in range(len(protStrings)):
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
            #Once step has been evaluated, publish to update progress bar
            #wampHandler will send a corresponding signal to QML to update the progress bar
            self.publish('com.prepbot.prothandler.progress', casL)
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
                await eval('self.{}'.format(casName))
            except asyncio.CancelledError:
                print("The run on {} has been cancelled.".format(casName))
            #Shutdown procedures...
            await self.shutdown(casL)
        else:
            print('{} is not running a protocol...'.format(casName))
    
    
    async def shutdown(self, casL):
        #Basic shutdown procedures when stopping a run before finishing.....
        print('SHUTDOWN Cas{}'.format(casL))
        time.sleep(2)
    
    async def incubate(self, casL, incTime, mixAfter=600):
        #Get start time
        start = datetime.datetime.now()
        mixMod = int(mixAfter/2)
        washF = int(incTime/mixMod)
        print('INCUBATING Cas{}'.format(casL))
        #Want to break out of this loop if timediff exceeds incTime
        exceedInc = False
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
            await asyncio.sleep(0.01)
            print('Mixing {}, #{} of {} cycles...'.format(casL,i+1,int(numCycles)))
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

    @wamp.subscribe('com.prepbot.button.btn_engage')
    def enage(self):
        machine.engage_sampleD()

    @wamp.subscribe('com.prepbot.button.btn_disengage')
    def disengage(self):
        machine.disengage_sampleD()

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
