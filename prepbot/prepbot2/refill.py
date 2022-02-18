# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 14:11:29 2020

@author: Rick
"""

#!/usr/bin/env python3

# PUMP conversion factor 1 ~ 50ul  ?
from machine import *
from time import sleep

LINEVOL_A = 5

def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		sleep(1)
		t -=1

print('STARTING...')
connect()
home()
set_heater(45)
cassette_contact()

mux_to(AIR)
move('pump', 40, speed=10)
wait_move_done()
mux_to(SAMPLE_A)
move('pump', 0, speed=1)
wait_move_done()


print('ADDING BABB')
#mux_to(AIR)
#move('pump', 2, speed=10)
mux_to(BABB)
move('pump', 25, speed=1)
wait_move_done()
sleep(15)
mux_to(SAMPLE_A)
move('pump', 5, speed=1)
wait_move_done()
#sleep(15)
#mux_to(WASTE)
#sleep(3)
#move('pump', 0, speed=0.3)
countdown(10)
#mux_to(SAMPLE_A)
#move('pump', 20, speed=1)
#wait_move_done()
#countdown(10)
#mux_to(WASTE)
#move('pump', 0, speed=10)
#wait_move_done()
#countdown(5)
#mux_to(BABB)
#move('pump', 3, speed=1)
#wait_move_done()
#sleep(5)
#mux_to(SAMPLE_A)
#wait_move_done()
move('pump', 2, speed=0.3)
wait_move_done()
sleep(3)
#mux_to(MEOH)
#move('pump', 0, speed=0.3)
#wait_move_done()
#mux_to(MEOH)
countdown(10)
print('Specimen ejecting')
connect()
cassette_eject()

print('CLEANING_PREP')
move('pump', 20, speed=10)
wait_move_done()
mux_to(WASTE)
home()
wait_move_done()
move('pump', 0, speed=10)

print('REMOVING BABB')
mux_to(SAMPLE_A)
move('pump', 40, speed=10)
wait_move_done()
sleep(3)
mux_to(WASTE)
move('pump', 0, speed=10)
wait_move_done()
sleep(2)

print('WASHING LINE')
mux_to(MEOH)
move('pump', 20, speed=10)
wait_move_done()
sleep(1)
mux_to(SAMPLE_A)
move('pump', 15, speed=0.3)
wait_move_done()
sleep(1)
move('pump', 30, speed=5)
wait_move_done()
mux_to(WASTE)
move('pump', 0, speed=10)

print('READY FOR NEW SAMPLE')


