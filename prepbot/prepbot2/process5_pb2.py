
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 14:11:29 2020

@author: Rick and Eben
"""

#!/usr/bin/env python3

from machine import *
from time import sleep
LINEVOL_1 = 0.8

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        sleep(1)
        t -=1


print('STARTING...')
connect()
set_heater('CAS2',47)
mux_to(CAS2)
sleep(1)
pump_to_ml(-1, speed=50)
wait_move_done()
mux_to(WASTE)
cassette_contact('CAS2')
sleep(1)
pump_to_ml(0, speed=500)
wait_move_done()

print('ADDING FORMALIN')
mux_to(FORMALIN)
sleep(1)
pump_to_ml(-1.3, speed=500)
wait_move_done()
sleep(5)
mux_to(CAS2)
sleep(1)
pump_to_ml(-0, speed=100)
wait_move_done()
mux_to(AIR)
sleep(1)
pump_to_ml(-0.5, speed=500)
wait_move_done()
mux_to(CAS2)
sleep(1)
pump_to_ml(-0, speed=100)
wait_move_done()
countdown(12)

print('MEOH WASHING SAMPLE')
mux_to(MEOH)
sleep(1)
pump_to_ml(-1.5, speed=400)
wait_move_done()
sleep(2)
mux_to(CAS2)
pump_to_ml(-0.4, speed=100)
wait_move_done()
countdown(6)
pump_to_ml(0, speed=100)
wait_move_done()
countdown(6)

mux_to(AIR)
sleep(1)
pump_to_ml(-2, speed=400)
wait_move_done()
sleep(1)
mux_to(CAS2)
sleep(1)
pump_to_ml(0, speed=400)
wait_move_done()
countdown(4) #equilibrate

print('ADDING DYE')
mux_to(DYE) 
sleep(1)
pump_to_ml(-1.0, speed=100)
wait_move_done()
sleep(5)
mux_to(CAS2)
sleep(2)
pump_to_ml(-0.2, speed=100)
wait_move_done()
sleep(1)
countdown(6) # x100

print('INCUBATING DYE')
num_cycles = 4
cycle_secs = 6 # x100
for x in range(num_cycles):
    print ('CYCLE : {:02d}'.format(x+1))
    mux_to(AIR)
    sleep(1)
    pump_to_ml(-0.5, speed=100)
    wait_move_done()
    sleep(1)
    mux_to(CAS2)
    sleep(1)
    pump_to_ml(-0.4, speed=100)
    wait_move_done()
    print('CYCLE : {:02d} of {:02d}'.format(x+1, num_cycles))
    countdown(cycle_secs)

print('DONE WITH DYE')
mux_to(WASTE)
pump_to_ml(0, speed=400)
wait_move_done()
sleep(1)

print('ADDING BABB')
mux_to(BABB)
pump_to_ml(-2, speed=100)
wait_move_done()
sleep(5)
mux_to(CAS2)
sleep(1)
pump_to_ml(-1, speed=100)
wait_move_done()
countdown(60)
pump_to_ml(0, speed=100)
wait_move_done()
sleep(1)
countdown(24)
print('Specimen ejecting')
cassette_eject('CAS2')

print('CLEANING_PREP')
mux_to(CAS2)
sleep(1)
pump_to_ml(-1, speed=50)
wait_move_done()
sleep(2)
mux_to(WASTE)
sleep(1)
pump_to_ml(0, speed=500)
wait_move_done()
sleep(5)

print('WASHING LINE')
mux_to(MEOH)
pump_to_ml(-1.5, speed=500)
wait_move_done()
sleep(1)
mux_to(CAS2)
pump_to_ml((-1.5+LINEVOL_1), speed=100)
wait_move_done()
countdown(5)
pump_to_ml(-2, speed=50)
wait_move_done()
mux_to(WASTE)
sleep(1)
pump_to_ml(0, speed=500)
wait_move_done()

print('READY FOR NEW SAMPLE')
