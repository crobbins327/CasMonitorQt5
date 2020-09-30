#!/usr/bin/env python3

import machine
from time import sleep

machine.move('x', -100)
sleep(5)
machine.move('x', 0)
sleep(5)