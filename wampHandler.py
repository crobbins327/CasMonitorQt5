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
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
import numpy as np
import asyncio

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp


class wampHandler(ApplicationSession, QtCore.QObject):
    
    #Globals...
    jHelper = jh.JSONHelper()
    convCas = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F'}
    #CasNumber, protStrings, progstrings, runtime, sampleName, protocolName
    setupProt = QtCore.pyqtSignal(str,'QVariantList','QVariantList',str,str,str)
    # To repopulate the progress bars when there is a GUI disconnection and rejoin
    # repopulateProt = QtCore.pyqtSignal(str,'QVariantList','QVariantList',int,int,int,int,str,str,str)
    repopulateProt = QtCore.pyqtSignal(int, 'QVariantList','QVariantList', 'QVariantList')
    #To update GUI that cassette is engaged and ready
    casEngaged = QtCore.pyqtSignal(int)
    casDisengaged = QtCore.pyqtSignal(int)
    #To update progress bar. CasNumber of current sample to decrement.
    updateProg = QtCore.pyqtSignal(int)
    deadspace = 1000 
    
    def __init__(self, cfg=None):
        ApplicationSession.__init__(self, cfg)
        QtCore.QObject.__init__(self)
        self.taskDF = pd.DataFrame(columns = ['status','stepNum','secsRemaining','engaged','protocolList','progressNames','stepTimes','sampleName','protocolPath','protocolName'] ,
                                   index=['casA','casB','casC','casD','casE','casF'], dtype=object)
        self.taskDF.engaged = False
        self.taskDF.engaged = self.taskDF.engaged.astype(object)
    
    
    async def update(self):
        while True:
    #            self.publish('com.prepbot.window.progress', self.progress)
            await asyncio.sleep(0.1)
        
    async def onJoin(self, details):
        print("Getting controller task dataframe..")
        # self.publish('com.prepbot.prothandler.request-tasks-gui')
        try:
            taskJSON = await self.call('com.prepbot.prothandler.controller-tasks')
            # print(taskJSON)
        except Exception as e:
            print("Waiting until controller is connected...")
            print(e)
            await asyncio.sleep(5)
            self.disconnect()
            self.leave()
            
        self.set_tasks_repopulate(taskJSON)
        print('\nFinished setting tasks and repopulating GUI!\n')
        
        try:
            res = await self.subscribe(self)
            print("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            print("could not subscribe to procedure: {0}".format(e))
        
        print('\nFINISHED JOIN!\n')
    
    @wamp.subscribe('com.prepbot.prothandler.tasks-to-gui')
    def set_tasks_repopulate(self, taskJSON):
        cTasks = pd.read_json(taskJSON, typ='frame', dtype=object)
        if cTasks.equals(self.taskDF):
            print('Controller has same taskDF as GUI')
            #Repopulate anyways??
            self.repopulateGUI()
        else:
            print('Repopulating GUI with controller procedures!')
            # print(cTasks)
            self.taskDF = cTasks
            self.repopulateGUI()
     
        
    # def onLeave(self, details):
    #     print("Left")
    #     print(self.taskDF)
    
    def onDisconnect(self):
        print("Disconnected")
        print(self.taskDF)
    
    
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
        print(protStrings)
        print(progStrings)
        print(stepTimes)
        self.taskDF.loc['cas{}'.format(casL)] = np.array(['running',0,np.nan,True,protStrings, progStrings, stepTimes, sampleName,protPath,protocolName],dtype=object)
        print(self.taskDF)
        #Send protocol to controller to add to Q
        self.publish('com.prepbot.prothandler.start', casL, self.taskDF.loc['cas{}'.format(casL)].to_json())
    
    #Separate start of gui when protocol is actually started on controller???
    #Hang until the start signal is actually received?
    
    @QtCore.pyqtSlot(str)
    def stopProtocol(self, casNumber):
        casL = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.stop', casL)
    
    #GUI waits until cassette is actually engaged before able to start a protocol
    @QtCore.pyqtSlot(str)
    def engageCas(self, casNumber):
        casL = self.convCas[int(casNumber)]
        self.publish('com.prepbot.prothandler.engage', casL)
    
    @wamp.subscribe('com.prepbot.prothandler.ready')
    def casReady(self, casL, engageBool):
        casNumber = int(self.__get_key(casL, self.convCas))
        if engageBool:
            self.casEngaged.emit(casNumber)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = True
            print('Cas{} engage complete'.format(casNumber))
        else:
            self.casDisengaged.emit(casNumber)
            self.taskDF.loc['cas{}'.format(casL),'engaged'] = False
            print('Cas{} disengage complete'.format(casNumber))
    
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
        print(self.taskDF.loc['cas{}'.format(casL)])
    
    @wamp.subscribe('com.prepbot.prothandler.progress')
    async def update_progress(self, casL, taskJSON):
        await asyncio.sleep(1)
        casNumber = int(self.__get_key(casL, self.convCas))
        self.updateProg.emit(casNumber)
        #Replace entry in taskDF
        self.taskDF.loc['cas{}'.format(casL)] = pd.read_json(taskJSON, typ='series', dtype=object)
        print(self.taskDF.loc['cas{}'.format(casL)])
    
    
    def repopulateGUI(self):
        runfin = self.taskDF[self.taskDF.status.isin(['running','finished'])].index
        engagedCas = self.taskDF[self.taskDF.engaged==True & ~self.taskDF.status.isin(['running','finished'])].index
        
        for i in self.taskDF.index:
            print(i)
            print(i in runfin)
            if i in runfin:
                casNumber = int(self.__get_key(i[-1], self.convCas))
                # stepNum = self.taskDF.loc[i,'stepNum']
                # secsRem = self.taskDF.loc[i,'secsRemaining']
                # totalSecs = sum(self.taskDF.loc[i,'stepTimes'])
                # tremSecs = sum(self.taskDF.loc[i,'stepTimes'][stepNum:]) + secsRem
                otherVars = self.taskDF.loc[i,['stepNum','secsRemaining','sampleName','protocolName','status']].tolist()
                # otherVars.append(totalSecs)
                # otherVars.append(tremSecs)
                print('\npre-Emitted???')
                print(i, casNumber)
                print(self.taskDF.loc[i])
                print(self.taskDF.loc[i,'progressNames'])
                print(self.taskDF.loc[i,'stepTimes'])
                print(otherVars)
                self.repopulateProt.emit(casNumber,
                                      self.taskDF.loc[i,'progressNames'],
                                      self.taskDF.loc[i,'stepTimes'],
                                      otherVars)
                print('Emitted???')
            elif i in engagedCas:
                print('Emitting engages! {}'.format(i))
                self.casEngaged.emit(int(self.__get_key(i[-1], self.convCas)))
        
        print("Restore connection with logger(s)......NOT IMPLEMENTED YET...")
        
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
                print('Volume in protocol step {} is not defined ({})! Use "undefined", mL, or uL for volume'.format(i,oper['volume']))
                break
                    
            fluidType = 'undefined'
            # print(oper)
            if oper['opName'] == 'Incubation':
                inc = self.__incubate(casL, oper['opTime'])
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
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Stain':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load BABB':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], mL=mL)
#                protstrings.append(rem+'\n'+load)
                protstrings.append(load)
                progstrings.append(oper['opName'])
                stepTimes.append(self.__get_sec(oper['opTime']))
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Dehydrant':
#                rem = self.__purge(casL, oper['volume'], mL=mL)
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'], mL=mL)
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
                print('Operation "{}" not in protocol operations!'.format(oper['opName']))
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

    def __incubate(self, casL, runtime):
        #Convert runtime hh:mm:ss into seconds
        incubateTime = self.__get_sec(runtime)
        # incubate_time_sec =  10
        #Mix every 2x seconds
        wash_interval = 2
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
        incStr = 'self.incubate(casL="{}",incTime={},mixAfter={})'.format(casL,incubateTime,wash_interval)
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
        deVol = vol + self.deadspace/1000
        # purgeStr = '''
        # print('PURGING CHAMBER')
        # machine.goto_sample{}()
        # machine.pump_in({})
        # sleep(5)
        # machine.empty_syringe()
        # '''.format(casL,deVol)
        purgeStr = 'self.purge(casL="{}",deadvol={})'.format(casL,deVol)
        return(purgeStr)
        
    def __load_reagent(self, casL, volume, speed, loadType, mL=False):
        reaConv = {'Dehydrant':'meoh','BABB':'babb',
                   'Formalin':'formalin','Stain':'vial'}
        #Check if volume is in uL or mL??
        if mL:
            vol = float(volume[:-2])
        else:
            vol = float(volume[:-2])/1000
        #Convert to mL for machine pump in/out command
        deVol = vol + self.deadspace/1000
        # loadString = '''
        # print('ADDING {}')
        # machine.goto_{}()
        # machine.pump_in({},{})
        # sleep(5)
        # machine.goto_sample{}()
        # machine.pump_out({},{})
        # '''.format(loadType,reaConv[loadType],vol,speed,casL,deVol,speed)
        loadStr= 'self.loadReagent(casL="{}",loadstr="{}",reagent="{}",vol={},speed={},deadvol={})'.format(casL,loadType, reaConv[loadType], vol, speed, deVol)
        return(loadStr)
        
    
    