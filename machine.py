import logging
import logging.config
from serial import Serial
from colorlog import ColoredFormatter
import fcntl
import sys
import os
#For debugging with only the machine file
# os.chdir('..')
# logging.config.fileConfig(fname='./Log/init/ctrl-loggers.ini')
# os.chdir('./prepbot')
# colorFormat = ColoredFormatter(
#     "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
#     datefmt=None,
#     reset=True,
#     log_colors={
#         'DEBUG':    'cyan',
#         'INFO':     'green',
#         'WARNING':  'yellow',
#         'ERROR':    'red',
#         'CRITICAL': 'red,bg_white',
#     },
#     secondary_log_colors={},
#     style='%'
# )
logger = logging.getLogger('ctrl.machine')
# logger.handlers[0].setFormatter(colorFormat)

homed = True

f = None

s = None
s_wheel = None

X_PARK = -70
X_SAMPLE_F = -85
X_VIAL = -97
X_FORMALIN = -109
X_MEOH = -121
X_SAMPLE_E = -133
X_SAMPLE_D = -145
X_WASTE = -156
X_SAMPLE_B = -143
X_BABB = -132
X_BABB_2 = -186

Z_SEPTUM = 66
Z_SAFE = 40
Z_WASTE = 80
Z_BABB = 72

#VIAL_X = -40
VIAL_Z = 73
VIAL_SCRAPE_Z = 10
VIAL_SCRAPE_X = -180
VIAL_OFFSET = -64           # degrees from sensor to needle position

S_ENGAGE_D = 8
S_ENGAGE_E = 8
S_ENGAGE_F = 11
S_DISENGAGE = 3

PUMP_SPEED = 1

LIMITS = {
    'x': [-190, 0],
    'z': [0, 100],
    'pump': [0, 40],
    'wheel': [float('-inf'), float('inf')],
    'sampleD': [0, 50],
    'sampleE': [0, 50],
    'sampleF': [0, 50],
}

def test_logger():
    logger.debug('Test debug')
    logger.info('Test info')
    logger.warning('Test warning')
    logger.error('Test error')
    logger.critical('Test critical')

def get_home_status():
    return(homed)

def acquire():
    global f, s
    logger.info('waiting to acquire machine lock')
    f = open('/tmp/machine.lock', 'w')
    fcntl.lockf(f, fcntl.LOCK_EX)
    s = Serial('/opt/klipper/printer', baudrate=250000, timeout=0.01)

def release():
    global f, s
    if s is None:
        return
    f = open('/tmp/machine.lock', 'w')
    fcntl.lockf(f, fcntl.LOCK_UN)
    logger.info('machine lock released')
    f = None
    s.close()
    s = None

def reset():
    global s, s_wheel, homed
    homed = False
    logger.info('connect to klipper')
    send('FIRMWARE_RESTART', read_response=False)
    wait_ok('Ready')
#    logger.info('connect to wheel arduino')
#    s_wheel = Serial('/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0', baudrate=115200, timeout=0.01)

def send(m, read_response=False):
    if s is None:
        acquire()
    logger.debug('send message: {}'.format(m))
    s.write((m+'\n').encode())
    if read_response:
        return s.readall().decode()

def wait_ok(msg='ok'):
    logger.debug('waiting for message: {}'.format(msg))
    while True:
        m = s.readall().decode()
        if m:
            logger.debug(m)
        if msg in m:
            logger.debug('message received')
            return

def wait_move_done():
    logger.debug('waiting for move to complete')
    _ = s.readall()
    send('M400', read_response=False)
    wait_ok()

def move(name, pos, wait=True, speed=None):
    if not homed:
        logger.warning('tried to move before homed!')
        raise RuntimeError

    logger.debug('move axis: {} {}'.format(name, pos))
    low, high = LIMITS[name]
    if pos < low or pos > high:
        logger.warning('move outside limits: {} {} {}'.format(name, pos, LIMITS[name]))
        return
    if speed is not None:
        send('MANUAL_STEPPER STEPPER={} MOVE={} SPEED={}'.format(name, pos, speed))
    else:
        send('MANUAL_STEPPER STEPPER={} MOVE={}'.format(name, pos))
    if wait:
        wait_move_done()
    motors_off()

def home_stepper(name, dist, wait=True):
    logger.info('home axis: {} {}'.format(name, dist))
    send('MANUAL_STEPPER STEPPER={} MOVE={} STOP_ON_ENDSTOP=1'.format(name, dist))
    wait_ok()
    if wait: 
        wait_move_done()
    send('MANUAL_STEPPER STEPPER={} SET_POSITION=0'.format(name))
    wait_ok()

def check_vial_sensor():
    m = s_wheel.readall().decode()
    return m[-1]

def vial_find():
    return
    home_stepper('wheel', -360)
    for n in range(30):
        logger.debug('check for vial in position {}'.format(n))
        if check_vial_sensor() == 'Y':
            break
        else:
            move('wheel', -12*n)
    else:
        logger.warning('No vial found!')
    move('wheel', -12*n + VIAL_OFFSET)

def vial_engage():
    move('z', Z_SAFE)
    move('x', VIAL_X)
    move('z', VIAL_Z)

def vial_discard():
    move('z', Z_SAFE)
    return
    move('x', VIAL_SCRAPE_X)
    move('z', VIAL_SCRAPE_Z)
    move('z', Z_SAFE)
    move('x', X_PARK)

def pump_vent():
    send('SET_PIN PIN=vent VALUE=1')
    send('SET_PIN PIN=syringe VALUE=0')

def pump_syringe():
    send('SET_PIN PIN=vent VALUE=0')
    send('SET_PIN PIN=syringe VALUE=1')

def pump_off():
    send('SET_PIN PIN=vent VALUE=0')
    send('SET_PIN PIN=syringe VALUE=0')

def pump_in(ml, speed=PUMP_SPEED):
    while ml:
        pump_vent()
        move('pump', 0)
        pump_syringe()
        if ml >= 3:
            move('pump', 45*3/5, speed=speed)
            ml -= 3
        else:
            move('pump', 45*ml/5, speed=speed)
            ml -= ml
        pump_off()

def pump_out(ml, speed=PUMP_SPEED):
    while ml:
        pump_vent()
        if ml >= 3:
            move('pump', 45*3/5)
            ml -= 3
        else:
            move('pump', 45*ml/5)
            ml -= ml
        pump_syringe()
        move('pump', 0, speed=speed)
        pump_off()

def goto_waste():
    move('z', Z_SAFE)
    move('x', X_WASTE)
    move('z', Z_WASTE)

def goto_meoh():
    move('z', Z_SAFE)
    move('x', X_MEOH)
    move('z', Z_SEPTUM)

def goto_park():
    move('z', Z_SAFE)
    move('x', X_PARK)

def goto_babb():
    move('z', Z_SAFE)
    move('x', X_BABB_2)
    move('z', Z_BABB)

def goto_sampleD():
    move('z', Z_SAFE)
    move('x', X_SAMPLE_D)
    move('z', Z_SEPTUM)
    
def goto_sampleE():
    move('z', Z_SAFE)
    move('x', X_SAMPLE_E)
    move('z', Z_SEPTUM)

def goto_sampleF():
    move('z', Z_SAFE)
    move('x', X_SAMPLE_F)
    move('z', Z_SEPTUM)

def goto_formalin():
    move('z', Z_SAFE)
    move('x', X_FORMALIN)
    move('z', Z_SEPTUM)

def goto_vial():
    move('z', Z_SAFE)
    move('x', X_VIAL)
    move('z', Z_SEPTUM)

def purge_syringe():
    empty_syringe()
    goto_meoh()
    pump_in(3)
    empty_syringe()

def empty_syringe(speed=1):
    goto_waste()
    pump_out(5, speed=speed)
    move('z', Z_SAFE)

def dye_process():
    empty_syringe()
    vial_find()
    vial_engage()
    pump_in(4)
    vial_discard()

def engage_sampleD():
    move('sampleD', S_ENGAGE_D)

def disengage_sampleD():
    move('sampleD', S_DISENGAGE)

def engage_sampleE():
    move('sampleE', S_ENGAGE_E)

def disengage_sampleE():
    move('sampleE', S_DISENGAGE)

def engage_sampleF():
    move('sampleF', S_ENGAGE_F)

def disengage_sampleF():
    move('sampleF', S_DISENGAGE)

def motors_off():
    send('M84')

def home():
    global homed
    home_stepper('z', -100, wait=False)
    home_stepper('pump', -50, wait=False)
    home_stepper('x', 300, wait=False)
    home_stepper('sampleD', -50, wait=False)
    home_stepper('sampleE', -50, wait=False)
    home_stepper('sampleF', -50, wait=False)
    wait_move_done()
    motors_off()
    homed = True
