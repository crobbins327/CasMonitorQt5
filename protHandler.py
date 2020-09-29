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

import asyncio

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import TransportLost
from autobahn import wamp


class protHandler(ApplicationSession, QtCore.QObject):
    
    #Globals...
    jHelper = jh.JSONHelper()
    convCas = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F'}
    #CasNumber, protStrings, progstrings, runtime, sampleName, protocolName
    setupProt = QtCore.pyqtSignal(str,'QVariantList','QVariantList',str,str,str)
    #To update progress bar. CasNumber of current sample to decrement.
    decrement = QtCore.pyqtSignal(str)
    deadspace = 1000 
    
    def __init__(self, cfg=None):
        ApplicationSession.__init__(self, cfg)
        QtCore.QObject.__init__(self)    
    
    async def onJoin(self, details):
        try:
            res = await self.subscribe(self)
            print("Subscribed to {0} procedure(s)".format(len(res)))
        except Exception as e:
            print("could not subscribe to procedure: {0}".format(e))

    
    # def __init__(self, DEADSPACE = 1000):
    #     self.deadspace = DEADSPACE
    #     self.Q = list()
    
    #Takes casNumber and protocol.json
    @QtCore.pyqtSlot(str, str, str, str, str)
    def startProtocol(self, casNumber, protPath, runtime, sampleName, protocolName):
        #Check current run status on cassette...
        #Error if run already in progress
        #Error if interpretter cannot interpret protocol
        #Interpret protocol and make list of strings to be executed
        protStrings, progStrings = self.interpret(casNumber, protPath)

        #Start progress bar and track steps completed in protocol for current sample...
        #Setup run by sending info to progress bar and sending protStrings
        self.setupProt.emit(casNumber,protStrings,progStrings,runtime,sampleName,protocolName)
        # #Send list to a Q or execute all at once....
        
        self.publish('com.prepbot.prothandler.start', casNumber, protStrings, progStrings, protPath)
        # #Send to Q or add to event loop....
        # # self.Q.append(protStrings)
        # #Event loop executes....
        # for i in range(len(protStrings)):
        #     #update progress bar steps and runtime...
        #     if i != 0:
        #         self.decrement.emit(casNumber)
        #     #Execute on contoller
        #     print(protStrings[i])            
        #     sleep(2)
        
    @wamp.subscribe('com.prepbot.prothandler.progress')
    def update_progress(self, n):
        # print("I know! {}".format(n))
        pass
        
    def interpret(self, casNumber, protPath):
        #Convert casNumber to sample letter...
        casL = self.convCas[int(casNumber)]
        #Open/Read .json file as a list of dictionaries
        jsonprot = self.jHelper.openToRun(protPath)
        #Strings to execute for protocol->controller
        protstrings = list()
        #Strings for the progress bar
        progstrings = list()
        #Need to pump out fluid in chamber before loading new fluid....
        for i in range(len(jsonprot)):
            oper = jsonprot[i]
            fluidType = 'undefined'
            # print(oper)
            if oper['opName'] == 'Incubation':
                inc = self.__incubate(casL, oper['opTime'])
                protstrings.append(inc)
                progstrings.append(oper['opName'])
            elif oper['opName'] == 'Mixing':
                protstrings.append('print("Mixing....")')
                progstrings.append(oper['opName'])
            elif oper['opName'] == 'Purge':
                rem = self.__purge(casL, oper['volume'])
                protstrings.append(rem)
                progstrings.append(oper['opName'])
            elif oper['opName'] == 'Load Formalin':
                rem = self.__purge(casL, oper['volume'])
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'])
                protstrings.append(rem+load)
                progstrings.append(oper['opName'])
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Stain':
                rem = self.__purge(casL, oper['volume'])
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'])
                protstrings.append(rem+load)
                progstrings.append(oper['opName'])
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load BABB':
                rem = self.__purge(casL, oper['volume'])
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'])
                protstrings.append(rem+load)
                progstrings.append(oper['opName'])
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Dehydrant':
                rem = self.__purge(casL, oper['volume'])
                load = self.__load_reagent(casL, oper['volume'], oper['pSpeed'], oper['loadType'])
                protstrings.append(rem+load)
                progstrings.append(oper['opName'])
                fluidType = oper['loadType']
            elif oper['opName'] == 'Load Custom':
                protstrings.append('print("Custom loading reagent....")')
                progstrings.append(oper['opName'])
                fluidType = oper['loadType']
            else:
                print('Operation "{}" not in protocol operations!'.format(oper['opName']))
        return(protstrings,progstrings)
            
        
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
        wash_interval = 600
        washF = int(incubateTime/wash_interval)
        incStr = '''
        print('INCUBATING DYE')
        for i in range({}):
            # print('i=',i)
            for j in range({}):
                sleep(1)
                print("Sample{} Seconds remaining: ", ({}-j-(i*{})))
            if ((i % 2) == 0):
                print('Mix')
                machine.pump_in(0.5)
                sleep(2)
                machine.pump_out(0.5)
        '''.format(washF,wash_interval,casL,incubateTime,wash_interval)
        return(incStr)
                
    # def mix(self, casL, numCycles, volume):
        
    def __purge(self, casL, volume):
        deVol = float(volume[:-2])/1000 + self.deadspace/1000
        purgeStr = '''
        print('PURGING CHAMBER')
        machine.goto_sample{}()
        machine.pump_in({})
        sleep(5)
        machine.empty_syringe()
        '''.format(casL,deVol)
        return(purgeStr)
        
    def __load_reagent(self, casL, volume, speed, loadType):
        reaConv = {'Dehydrant':'meoh','BABB':'babb',
                   'Formalin':'formalin','Stain':'vial'}
        #Check if volume is in uL or mL??
        #Assume uL
        vol = float(volume[:-2])/1000
        #Convert to mL for machine pump in/out command
        deVol = vol + self.deadspace/1000
        loadString = '''
        print('ADDING {}')
        machine.goto_{}()
        machine.pump_in({},{})
        sleep(5)
        machine.goto_sample{}()
        machine.pump_out({},{})
        '''.format(loadType,reaConv[loadType],vol,speed,casL,deVol,speed)
        return(loadString)
        
    
    