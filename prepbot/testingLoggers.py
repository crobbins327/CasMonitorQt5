#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 01:57:39 2020

@author: jackr
"""


import logging
import logging.config
import os

logging.config.fileConfig(fname='./Log/init/ctrl-loggers.ini')

ctrl = logging.getLogger('ctrl')
casAlog = logging.getLogger('ctrl.casA')
machinelog = logging.getLogger('ctrl.machine')
logger = logging.getLogger('')

logger.info('testing root')
ctrl.info('testing ctrl')
casAlog.info('testing casAlog')
machinelog.info('testing machinelog')


textFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
casName = 'casA'
# Make the modifiable file handler for the machinelog
modHdl = logging.FileHandler('./Log/{}.log'.format(casName), mode='a')
modHdl.setLevel(logging.DEBUG)
modHdl.setFormatter(textFormatter)
machinelog.addHandler(modHdl)

machinelog.info('testing in casA')

casName = 'casB'
modHdl.close()
modHdl.baseFilename = os.path.abspath('./Log/{}.log'.format(casName))

machinelog.info('testing in casB')