
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 14:11:29 2020

@author: Rick and Eben
"""

#!/usr/bin/env python3

from machine import *
from time import sleep
LINEVOL_1 = 1.0 # MAX is 1.0
LINEVOL_2 = 0.8
LINEVOL_3 = 1.0
formalin_secs = 10
meoh_secs = 30
dye_cycles = 6
dye_cycle_secs = 600
babb_secs = 500

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
cassette_contact('CAS2')
sleep(1)

#print('FORMALIN WASH')
#mux_to(FORMALIN)
#sleep(1)
#pump_to_ml(-1.5, speed=500)
#wait_move_done()
#mux_to(WASTE)
#sleep(2)
#pump_to_ml(-0, speed=400)
#wait_move_done()
#mux_to(FORMALIN)
#sleep(1)

#print('ADD FORMALIN')
#pump_to_ml(-1.3, speed=500)
#wait_move_done()
#sleep(1)
#mux_to(CAS2)
#sleep(1)
#pump_to_ml(-0, speed=50)
#wait_move_done()

#countdown(formalin_secs)

print('MEOH WASHING SAMPLE')
mux_to(MEOH)
sleep(1)
pump_to_ml(-1.5, speed=400)
wait_move_done()
sleep(2)
mux_to(CAS2)
pump_to_ml(-0.4, speed=50)
wait_move_done()
countdown(10)
pump_to_ml(0, speed=50)
wait_move_done()
countdown(meoh_secs)

mux_to(AIR)
sleep(1)
pump_to_ml(-2, speed=400)
wait_move_done()
sleep(1)
mux_to(CAS2)
sleep(1)
pump_to_ml(-0.5, speed=50)
wait_move_done()
countdown(4) #equilibrate

print('ADDING DYE')
mux_to(DYE) 
sleep(1)
pump_to_ml(0, speed=400)
wait_move_done()
pump_to_ml(-1.0, speed=200)
wait_move_done()
sleep(2)
mux_to(CAS2)
sleep(1)
pump_to_ml((-1.0+LINEVOL_3), speed=50)
wait_move_done()
sleep(1)
mux_to(AIR)
sleep(1)
pump_to_ml(-0.2, speed = 500)
wait_move_done()
mux_to(CAS2)
sleep(1)
pump_to_ml(0, speed=50)
wait_move_done()

#Equilibrate dye pressure
mux_to(AIR)
sleep(1)
pump_to_ml(-0.5, speed=500)
wait_move_done()
mux_to(DYE)
sleep(1)
pump_to_ml(0, speed=400)
wait_move_done()

print('INCUBATING DYE')
countdown(dye_cycle_secs)
for x in range(dye_cycles):
    print ('CYCLE : {:02d}'.format(x+1))
    mux_to(AIR)
    sleep(1)
    pump_to_ml(-0.5, speed=500)
    wait_move_done()
    sleep(1)
    mux_to(CAS2)
    sleep(1)
    pump_to_ml(-0.6, speed=400)
    wait_move_done()
    sleep(1)
    pump_to_ml(-0.4, speed=100)
    wait_move_done()
    print('CYCLE : {:02d} of {:02d}'.format(x+1, dye_cycles))
    sleep(1)
    countdown(dye_cycle_secs)

print('DONE WITH DYE')
mux_to(WASTE)
pump_to_ml(0, speed=400)
wait_move_done()
sleep(1)

print('ADDING BABB')
mux_to(BABB)
pump_to_ml(-2, speed=200)
wait_move_done()
sleep(4)
mux_to(CAS2)
sleep(1)
pump_to_ml(-2.1+LINEVOL_3, speed=200)
wait_move_done()
pump_to_ml(-0.6, speed = 50)
wait_move_done()
countdown(babb_secs)
pump_to_ml(0, speed=50)
wait_move_done()
sleep(1)
countdown(30)
connect() # NEED DUE TO STAGE MALFUNCTIONING
print('Specimen ejecting')
cassette_eject('CAS2')

print('CLEANING_PREP')
mux_to(CAS2)
sleep(1)
pump_to_ml(-1, speed=100)
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
pump_to_ml((-1.5+LINEVOL_3), speed=50)
wait_move_done()
countdown(8)
pump_to_ml(-2, speed=200)
wait_move_done()
mux_to(WASTE)
sleep(1)
pump_to_ml(0, speed=500)
wait_move_done()
countdown(2)
mux_to(CAS2)
sleep(1)
pump_to_ml(-1, speed=200)
wait_move_done()
mux_to(WASTE)
pump_to_ml(0, speed=500)
wait_move_done()

print('READY FOR NEW SAMPLE')
