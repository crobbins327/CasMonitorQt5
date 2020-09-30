from os import environ
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import time
import machine


class Component(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.halted = True
        self.homed = False

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
        except ConnectionRefusedError:
            time.sleep(2)
