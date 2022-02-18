#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 11:24:35 2020

@author: jackr
"""

from PySide2 import QtCore
import json
import jsonschema
import os
# from jsonschema import validate

class JSONHelper(QtCore.QObject):
    # Can be redone with getters and setters for the stepModel property. This will be faster with less conversions on the data object.
    # https://qmlbook.github.io/ch18-python/python.html

    nextModel = QtCore.Signal(str, str, str)

    @QtCore.Slot(str, str)
    def saveProtocol(self, fileName, jString):
        # with open(fileName, "w") as outfile: 
        #     json.dump(jString, outfile) 
        with open(os.path.normpath(fileName), "w") as outfile:
            outfile.write(jString)

    @QtCore.Slot(str, str, str)
    def openProtocol(self, fileName, protocolName, pathSaved):
        # take accepted filename and check if it's .json
        jsondata=[]
        try:
            with open(os.path.normpath(fileName), encoding='utf-8') as data_file:
                jsondata = json.load(data_file)
        except Exception as e:
            print(e)
            print("An error has occurred with the file selected.")
            return

        # validate .json object?
        # check if json object has the propper keys for all elements?
        isValid = self.validateJson(jsondata)
        print('Is the jsondata valid: {}'.format(isValid))
        if not isValid:
            print('JSON has key value error. opName, opTime, volume, pSpeed, numCycles, and loadType are the only keys accepted.')
            return
        else:
            # Send JSON string with file info
            self.nextModel.emit(json.dumps(jsondata), protocolName, pathSaved)

    def openToRun(self, fileName):
        # take accepted filename and check if it's .json
        jsondata=[]
        try:
            with open(os.path.normpath(fileName), encoding='utf-8') as data_file:
                jsondata = json.load(data_file)
        except Exception as e:
            print(e)
            print("An error has occurred with the file selected.")
            return

        # validate .json object?
        # check if json object has the propper keys for all elements?
        isValid = self.validateJson(jsondata)
        print('Is the jsondata valid: {}'.format(isValid))
        if not isValid:
            print('JSON has key value error. opName, opTime, volume, pSpeed, numCycles, and loadType are the only keys accepted.')
            return
        else:
            # Send JSON string with file info
            return(jsondata)


    def validateJson(self, jsonData):
        # Describe what kind of json you expect.
        # Need to make this more functional with filter masks or regex
        protocolSchema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "opName": {"type": "string"},
                    "opTime": {"type": "string"},
                    "mixAfterSecs" : {"type": "string"},
                    "volume": {"type": "string"},
                    "pSpeed": {"type": "string"},
                    "numCycles": {"type": "string"},
                    "loadType": {"type": "string"},
                },
                "required": ["opName", "opTime","mixAfterSecs","volume","pSpeed","numCycles","loadType"]
            }
        }
        try:
            jsonschema.validate(instance=jsonData, schema=protocolSchema)
            return True
        except jsonschema.exceptions.ValidationError as err:
            return False

