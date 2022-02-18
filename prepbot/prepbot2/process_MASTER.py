
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 14:11:29 2020

@author: Rick and Eben
"""

#!/usr/bin/env python3

from machine import *
from time import sleep
LINEVOL_1 = 1.0 # MAX is 1.0
LINEVOL_3 = 1.0
formalin_secs = 20
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
set_heater('CAS1',47)
cassette_contact('CAS1')
sleep(1)

# Skip for ARF
# If last step was BABB in syringe, need to wash syringe with MEOH first
# If last step was dye, should be ok to go direct to here
print('FORMALIN WASH')
mux_to(FORMALIN)
sleep(1)
pump_to_ml(-(LINEVOL_1+0.5), speed=500)
wait_move_done()
mux_to(WASTE)
sleep(2)
pump_to_ml(-0, speed=400)
wait_move_done()
mux_to(FORMALIN)
sleep(1)
print('ADD FORMALIN')
pump_to_ml(-(LINEVOL_1+0.5), speed=500)
wait_move_done()
sleep(1)
mux_to(CAS1)
sleep(1)
pump_to_ml(-0, speed=50)
wait_move_done()
countdown(formalin_secs)
#OK TO DO OTHER THINGS

# If last step was BABB in syringe, need to wash syringe with MEOH first
print('MEOH WASHING SAMPLE')
mux_to(MEOH)
sleep(1)
pump_to_ml(-(LINEVOL_1+0.5), speed=400)
wait_move_done()
mux_to(CAS1)
sleep(1)
pump_to_ml(-0.7, speed=200) #Fill reservoir quickly
wait_move_done()
pump_to_ml(0, speed=50) #Fill chamber slow to keep laminar
countdown(meoh_secs)
#OK TO DO OTHER THINGS

# If last step was BABB in syringe, need to wash syringe with MEOH first (probably)
# Second brief dehydration
mux_to(AIR)
sleep(1)
pump_to_ml(-0.5, speed = 500)
wait_move_done()
pump_to_ml(0, speed=50)
wait_move_done()
countdown(meoh_secs)
#OK TO DO OTHER THINGS

# If last step was BABB in syringe, need to wash syringe with MEOH first (probably)
# Purge-like step
mux_to(AIR)
sleep(1)
pump_to_ml(-(LINEVOL_1), speed=400)
wait_move_done()
mux_to(CAS1)
sleep(1)
pump_to_ml(0, speed=50)
wait_move_done()
countdown(4) #equilibrate

# If prior step was not MEOH, should wash syringe with MEOH
print('ADDING DYE')
# First get air into dye bottle to prevent neg pressure
# May need to do in two steps of 0.5ml if pressure gets too high with 1
mux_to(AIR)
sleep(1)
pump_to_ml(-2, speed=500)
mux_to(DYE)
sleep(1)
pump_to_ml(-1.0, speed=200) # not too fast so there is no leakage
wait_move_done()
pump_to_ml(-2, speed=200) # draw dye back into syringe, dead vol small, ~0.1 ml?
sleep(2)
mux_to(CAS1)
sleep(1)
pump_to_ml(-(2-LINEVOL_1), speed=200) # Fast fill of reservoir 
wait_move_done()
pump_to_ml(-(2-LINEVOL_1-0.2), speed=50) # Slow fill of chamber
# May need to adjust the 0.2 depending on dead volume of dye bottle connector 
sleep(1)
countdown(dye_cycle_secs)
# Actual first dye cycle
#OK TO DO SOMETHING ELSE
print('INCUBATING DYE')
for x in range(dye_cycles-1):
    print ('CYCLE : {:02d}'.format(x+2)) # Now counting pre-loop cycle as well
    # If prior step was formalin, might want MEOH wash, but maybe dont need
    mux_to(AIR)
    sleep(1)
    pump_to_ml(-0.5, speed=500)
    wait_move_done()
    sleep(1)
    mux_to(CAS1)
    sleep(1)
    pump_to_ml(-0.6, speed=500) # draw in a bit quickly to dislodge
    wait_move_done()
    sleep(1)
    pump_to_ml(-0.4, speed=50) # refil slow
    wait_move_done()
    print('CYCLE : {:02d} of {:02d}'.format(x+1, dye_cycles))
    countdown(dye_cycle_secs)
    #OK TO DO SOMETHING ELSE


print('DONE WITH DYE')
# Empty syring and set to 0
mux_to(WASTE)
pump_to_ml(0, speed=400)
wait_move_done()

# If prior step was formalin, should do MEOH wash of syringe
print('ADDING BABB')
mux_to(BABB)
pump_to_ml(-2, speed=200) # a bit slower because viscous
wait_move_done()
sleep(4) # give time to equilibrate pressure because viscous
mux_to(CAS1)
sleep(1)
pump_to_ml(-2+LINEVOL_1, speed=200) # fast but less fast than MEOH
wait_move_done()
pump_to_ml(0, speed = 25) # very slow push through for clearing 1
wait_move_done()
countdown(babb_secs)
# OK TO DO SOMETHING ELSE

# Should be ok no matter what prior was
mux_to(AIR)
sleep(1)
pump_to_ml(-0.5, speed=500)
wait_move_done()
mux_to(CAS1)
sleep(1)
pump_to_ml(0, speed=25) # very slow push through
wait_move_done()
sleep(1)
countdown(babb_secs) # second clearing
# OK TO DO SOMETHING ELSE

print('Specimen ejecting')
cassette_eject('CAS1') # Should minimize delay for eject when ready

# Should be ok no matter what prior
print('CLEANING_PREP')
mux_to(CAS1)
sleep(1)
pump_to_ml(-1, speed=200) # drain reservoir semifast
wait_move_done()
sleep(2) # let residual babb settle
mux_to(WASTE)
sleep(1)
pump_to_ml(0, speed=500) # clear fast
wait_move_done()

print('WASHING LINE')
mux_to(MEOH)
pump_to_ml(-1.5, speed=500) # extras meoh to clear syringe too
wait_move_done()
mux_to(CAS1)
sleep(1)
pump_to_ml((-1.5+LINEVOL_3), speed=50)
wait_move_done()
pump_to_ml(-2, speed=200)
wait_move_done()
mux_to(WASTE)
sleep(1)
pump_to_ml(0, speed=500)
wait_move_done()
countdown(2)
mux_to(CAS1)
sleep(1)
pump_to_ml(-1, speed=200) # second suction to purge
wait_move_done()
mux_to(WASTE)
pump_to_ml(0, speed=500)
wait_move_done()

print('READY FOR NEW SAMPLE')
