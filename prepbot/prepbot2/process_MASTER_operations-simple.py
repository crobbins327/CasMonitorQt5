import sys

sys.path.append('./prepbot/prepbot2')
from machine import *
from time import sleep
import datetime

syringeFluid = None
LINEVOL_1 = 1.0  # MAX is 1.0
LINEVOL_2 = 1.0
LINEVOL_3 = 1.0
# Could add more casette specific properties, save/load part as a JSON/YAML
casDict = {'CAS1': {'linevol': LINEVOL_1, 'currentFluid': None, 'volInLine': 0},
           'CAS2': {'linevol': LINEVOL_2, 'currentFluid': None, 'volInLine': 0},
           'CAS3': {'linevol': LINEVOL_3, 'currentFluid': None, 'volInLine': 0}, }

reagentDict = {'FORMALIN': {'pumpInWait': 1},
               'MEOH': {'pumpInWait': 0},
               'DYE': {'pumpInWait': 2},
               'BABB': {'pumpInWait': 4}}
volInLineFactor = 1.3
# The currentFluid must be the same and volInLine must be 1.3*pumpVol in order to pump from the line. This is a safety factor so not to pump bubbles/air into chamber.
# So if you wanted to pump 0.5ml into the chamber and the linevol was 1ml, 0.5*1.3 < 1 is true.
# However, for the next cycle to pump 0.5ml, the linevol is now 0.5ml, and 0.5*1.3 < 0.5 is false.
# Therefore, you have to purge the line before loading the new reagent.
formalin_secs = 20
meoh_secs = 30
dye_cycles = 6
dye_cycle_secs = 600
babb_secs = 500
# You can ignore this, for controller/GUI WAMP
def onJoin():
	connect()
	# acquire and home pump
	acquire()
	pass


# You can ignore this, for controller/GUI WAMP
def onDisconnect():
	release()
	pass


# incubate without mixing
def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		sleep(1)
		t -= 1


mixInSpeed = 500
mixOutSpeed = 50
# Can use this to ensure that linevolume is not depleted from pushing extra volume out
extraMixFactor = 1.1
def incubate(cas, incTime, mixAfter=None, mixVol=0.1, extraVolOut=0, earlyStopping=False):
	linevol = casDict[cas]['linevol']
	# Get start time
	start = datetime.datetime.now()
	if not incTime > 0:
		print('Inc time not > 0.... skipping incubation....')
		return

	if mixAfter == None or int(mixAfter) <= 0 or int(mixAfter) > int(incTime):
		waitI = int(incTime)
		# No washes/mixes, only one iteration
		washI = 1
		print('No washes for incubation. incTime={}, mixAfter={}'.format(incTime, mixAfter))
	else:
		washI = int(incTime / mixAfter)
		waitI = int(mixAfter)

	print('INCUBATING {}'.format(cas))

	for i in range(washI):
		countdown(waitI)
		# Can terminate early if you want
		diff = (datetime.datetime.now() - start).total_seconds()
		if earlyStopping and diff >= incTime:
			return

		if mixAfter == None or int(mixAfter) <= 0 or int(mixAfter) > int(incTime):
			return
		else:
			print('Mixing {}...'.format(cas))
			# If prior step was formalin, might want MEOH wash, but maybe dont need
			mux_to('AIR')
			pump_in(0.5, speed=mixInSpeed)
			sleep(1)
			mux_to(cas)
			pump_in(mixVol, speed=mixInSpeed)
			sleep(1)
			if extraVolOut * extraMixFactor < casDict[cas]['volInLine']:
				pump_out(mixVol + extraVolOut, speed=mixOutSpeed)
				casDict[cas]['volInLine'] -= extraVolOut
				print(cas, casDict[cas])
			else:
				print('Cannot pump extra volume out, linevol is nearly depleted {}ml.'.format(casDict[cas]['volInLine']))
				# Could load more into line..?
				pump_out(mixVol, speed=mixOutSpeed)
				print(cas, casDict[cas])
			# Reset pump
			mux_to('WASTE')
			pump_to_ml(0, speed=500)
			##################################################################################################################
			wait_move_done()
			##################################################################################################################
			print('CYCLE : {:02d} of {:02d}'.format(i + 1, washI))
	print('INCUBATION TOOK {}s'.format(diff))


# Basic shutdown procedures when stopping a run before finishing
def shutdown(cas='CAS1'):
	print('Disengage {}...'.format(cas))
	cassette_eject(c=cas)
	clean(cas=cas)


# What are the cleaning parameters you want and where?
clnVol = 1
clnInSpeed = 200
washVol = 1.5
washInSpeed = 500
wasteSpeed = 500
# I gave up on trying to figure out what parameters you wanted to modify in this block
def clean(cas='CAS1'):
	global syringeFluid
	print('syringeFluid before:', syringeFluid)
	# Lookup properties in casDict
	linevol = casDict[cas]['linevol']
	print('CLEANING_PREP')
	mux_to(cas)
	pump_in(clnVol, speed=clnInSpeed)
	# pump_to_ml(-clnVol, speed=clnInSpeed) # drain reservoir semifast
	# wait_move_done()
	sleep(2)  # let residual babb settle
	mux_to('WASTE')
	pump_out(ml=clnVol, speed=wasteSpeed)
	# pump_to_ml(0, speed=clnOutSpeed) # clear fast
	# wait_move_done()

	print('WASHING LINE')
	mux_to('MEOH')
	pump_in(washVol, speed=washInSpeed)
	# Why is this in speed 500 when the others are 200... does this really need to be 500?
	# pump_to_ml(-1.5, speed=500) # extras meoh to clear syringe too
	# wait_move_done()
	mux_to(cas)
	# why so slow...
	pump_out(linevol, speed=50)
	# pump_to_ml((-1.5+linevol), speed=50)
	# wait_move_done()
	pump_in(2, speed=200)
	# pump_to_ml(-2, speed=200)
	# wait_move_done()
	mux_to('WASTE')
	pump_out(2, speed=wasteSpeed)
	# pump_to_ml(0, speed=500)
	# wait_move_done()
	# countdown(2)  Not enough time to do anything else...
	# Not sure why you want to wait here
	sleep(2)
	mux_to(cas)
	pump_in(1, speed=200)
	# pump_to_ml(-1, speed=200) # second suction to purge
	# wait_move_done()
	mux_to('WASTE')
	pump_out(1, speed=wasteSpeed)
	# pump_to_ml(0, speed=500)
	# wait_move_done()

	syringeFluid = 'MEOH'


def engage(cas='CAS1'):
	cassette_contact(cas)


def disengage(cas='CAS1'):
	cassette_eject(cas)

# washVol = 1.5
# washInSpeed = 500
# wasteSpeed = 500
def washSyringe(reagent='MEOH', washVol=washVol, washInSpeed=washInSpeed, wasteSpeed=wasteSpeed):
	global syringeFluid
	print('syringeFluid before:', syringeFluid)
	print('WASH SYRINGE WITH {}'.format(reagent))
	mux_to(reagent)
	pump_in(washVol, speed=washInSpeed)
	mux_to('WASTE')
	sleep(1)  # Why extra 1s?
	pump_out(washVol, speed=wasteSpeed)

	syringeFluid = reagent
	print('syringeFluid:', syringeFluid)


purgeInSpeed = 400
purgeOutSpeed = 50
# Shouldn't the purgeVol be the linevol + some extra so that you fully purge line and chamber?
purgeVol = 0.5
def purge(cas='CAS1'):
	print('PURGING LINE of {}'.format(cas))
	linevol = casDict[cas]['linevol']
	mux_to('AIR')
	pump_in(linevol + purgeVol, speed=purgeInSpeed)
	mux_to(cas)
	pump_out(linevol + purgeVol, speed=purgeOutSpeed)

	casDict[cas]['currentFluid'] = 'AIR'
	casDict[cas]['volInLine'] = 0
	print(cas, casDict[cas])

def washSyringeLogic(reagent, washSyr='auto', washSyrReagent='MEOH'):
	if reagent not in ['FORMALIN','MEOH','DYE','BABB']:
		# stop protocol
		raise ValueError('CANNOT LOAD {}....'.format(reagent))

	global syringeFluid
	print('syringeFluid before:', syringeFluid)
	if washSyr == 'auto':
		if reagent in ['FORMALIN', 'MEOH']:
			# Check if last reagent in syringe was BABB, then need to wash syringe with MEOH first
			if syringeFluid == 'BABB':
				washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
		elif reagent in ['DYE']:
			# If prior step was not MEOH, should wash syringe with MEOH
			if syringeFluid != 'MEOH':
				washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
		elif reagent in ['BABB']:
			# If prior step was formalin, should do MEOH wash of syringe
			if syringeFluid == 'FORMALIN':
				washSyringe(reagent=washSyrReagent)  # Should I give you the ability to change the washSyrReagent?
		else:
			# The load reagent would never be None or AIR so this does nothing
			pass

	elif washSyr == True:
		# Force washing syringe
		washSyringe(reagent=washSyrReagent)
	else:
		#Do not wash the syringe
		pass


def reuseOrPurgeLine(cas, reagent, ml, inSpeed, chamberSpeed):
	if reagent not in ['FORMALIN','MEOH','DYE','BABB']:
		# stop protocol
		raise ValueError('CANNOT LOAD {}....'.format(reagent))

	# Reuse linevol if it is reagent and has sufficient volInLine for pumping
	if casDict[cas]['currentFluid'] == reagent and ml * volInLineFactor < casDict[cas]['volInLine']:
		print('ADDING {}, REUSING {} linevol {}'.format(reagent, cas, casDict[cas]['volInLine']))
		mux_to('AIR')
		pump_in(ml, speed=inSpeed)
		mux_to(cas)
		pump_out(ml, speed=chamberSpeed)

		casDict[cas]['currentFluid'] = reagent
		casDict[cas]['volInLine'] -= ml
		print(cas, casDict[cas])

		# This process doesn't change the last syringe fluid
		print('syringeFluid:', syringeFluid)
		#Is the operation completed? Yes, because you are reusing the reagent in the line.
		return True
	elif casDict[cas]['currentFluid'] not in [None, 'AIR', reagent]:
		# Purge the line with AIR before starting
		print('{} LINE has {}, not {}'.format(cas, casDict[cas]['currentFluid'], reagent))
		purge(cas=cas)
		# Is the operation completed? No, you just purged the line so that the reagent could be loaded using specific load parameters...
		####### goto reagent specific protocol #######
		return False
	else:
		#It's okay to fill the line with new fluid, do not reuse linevol
		# Is the operation completed? No, you can't reuse the linevol for the load operation. You need to continue.
		####### goto reagent specific protocol #######
		return False


# reagentDict = {'FORMALIN': {'pumpInWait': 1},
#                'MEOH': {'pumpInWait': 0},
#                'DYE': {'pumpInWait': 2},
#                'BABB': {'pumpInWait': 4}}
# What do you want to modify here as parameters in a config file?
stainAirVol = 1
stainAirInSpeed = 500
stainAirOutSpeed = 200
def loadFreshReagent(cas, reagent, ml, inSpeed, chamberSpeed, lineSpeed, pumpInWait='auto'):
	global syringeFluid
	if reagent not in ['FORMALIN','MEOH','DYE','BABB']:
		# stop protocol
		raise ValueError('CANNOT LOAD {}....'.format(reagent))
	if pumpInWait is None or pumpInWait == 'auto':
		#Get parameter from dictionary
		pumpInWait = reagentDict[reagent]['pumpInWait']

	####### reagent specific protocol #######
	# What do you want to modify here as parameters in a config file?
	if reagent == 'DYE':
		linevol = casDict[cas]['linevol']
		print('ADDING DYE')
		# First get air into dye bottle to prevent neg pressure
		# May need to do in two steps of 0.5ml if pressure gets too high with 1
		mux_to('AIR')
		pump_in(stainAirVol + linevol + ml, speed=stainAirInSpeed)
		mux_to('DYE')
		# This doesn't make sense, shouldn't you completely pump out and then draw in the same volume?
		# If anything, pump out a little more air into the dye container?
		# Why have air in the pump at in this step all?
		pump_out(linevol + ml, speed=stainAirOutSpeed) # not too fast so there is no leakage
		pump_in(linevol + ml, speed=inSpeed) # draw dye back into syringe, dead vol small, ~0.1 ml?
		sleep(pumpInWait) #2s
		mux_to(cas)
		pump_out(linevol, speed=lineSpeed) # Fast fill of reservoir
		pump_out(ml, speed=chamberSpeed) # Slow fill of chamber
		# May need to adjust the 0.2 depending on dead volume of dye bottle connector
		sleep(1) #Why sleep here??
		# Need to reset the pump to 0 because it still has stainAirVol inside....
		mux_to('WASTE')
		# Perhaps the pump should be zeroed at the end of every fluid operation to prevent accumulation of rounding errors?
		pump_to_ml(0, speed=stainAirOutSpeed)
		##################################################################################################################
		wait_move_done()
		##################################################################################################################
	elif reagent in ['FORMALIN','MEOH','BABB']:
		linevol = casDict[cas]['linevol']
		print('ADDING {}'.format(reagent))
		mux_to(reagent)
		pump_in(linevol + ml, speed=inSpeed)
		# BABB = 4s
		# FORMALIN = 1s
		# MEOH = 0s
		sleep(pumpInWait) # give time to equilibrate pressure because reagent can be viscous
		mux_to(cas)
		pump_out(linevol, speed=lineSpeed)
		pump_out(ml, speed=chamberSpeed)
	else:
		raise ValueError('{} loading is not implemented...'.format(reagent))

	#Update globals and casDict
	casDict[cas]['currentFluid'] = reagent
	casDict[cas]['volInLine'] = linevol
	print(cas, casDict[cas])
	syringeFluid = reagent
	print('syringeFluid:', syringeFluid)


def formalin(cas='CAS1', ml=0.5, inSpeed=500, chamberSpeed=50, lineSpeed=400, washSyr='auto', washSyrReagent='MEOH'):
	washSyringeLogic(reagent='FORMALIN', washSyr=washSyr, washSyrReagent=washSyrReagent)
	completed = reuseOrPurgeLine(cas=cas, reagent='FORMALIN', ml=ml, inSpeed=inSpeed, chamberSpeed=chamberSpeed)
	if completed:
		#Finished with operation because the reagent within the line volume was used for the loading operation
		return
	else:
		loadFreshReagent(cas=cas, reagent='FORMALIN', ml=ml, inSpeed=inSpeed,
		                 chamberSpeed=chamberSpeed, lineSpeed=lineSpeed,
		                 pumpInWait='auto')


def meoh(cas='CAS1', ml=0.5, inSpeed=500, chamberSpeed=50, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH'):
	washSyringeLogic(reagent='MEOH', washSyr=washSyr, washSyrReagent=washSyrReagent)
	completed = reuseOrPurgeLine(cas=cas, reagent='MEOH', ml=ml, inSpeed=inSpeed, chamberSpeed=chamberSpeed)
	if completed:
		# Finished with operation because the reagent within the line volume was used for the loading operation
		return
	else:
		loadFreshReagent(cas=cas, reagent='MEOH', ml=ml, inSpeed=inSpeed,
		                 chamberSpeed=chamberSpeed, lineSpeed=lineSpeed,
		                 pumpInWait='auto')


def stain(cas='CAS1', ml=0.2, inSpeed=200, chamberSpeed=50, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH'):
	washSyringeLogic(reagent='DYE', washSyr=washSyr, washSyrReagent=washSyrReagent)
	completed = reuseOrPurgeLine(cas=cas, reagent='DYE', ml=ml, inSpeed=inSpeed, chamberSpeed=chamberSpeed)
	if completed:
		# Finished with operation because the reagent within the line volume was used for the loading operation
		return
	else:
		loadFreshReagent(cas=cas, reagent='DYE', ml=ml, inSpeed=inSpeed,
		                 chamberSpeed=chamberSpeed, lineSpeed=lineSpeed,
		                 pumpInWait='auto')


def babb(cas='CAS1', ml=1, inSpeed=200, chamberSpeed=25, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH'):
	washSyringeLogic(reagent='BABB', washSyr=washSyr, washSyrReagent=washSyrReagent)
	completed = reuseOrPurgeLine(cas=cas, reagent='BABB', ml=ml, inSpeed=inSpeed, chamberSpeed=chamberSpeed)
	if completed:
		# Finished with operation because the reagent within the line volume was used for the loading operation
		return
	else:
		loadFreshReagent(cas=cas, reagent='BABB', ml=ml, inSpeed=inSpeed,
		                 chamberSpeed=chamberSpeed, lineSpeed=lineSpeed,
		                 pumpInWait='auto')

# CURRENT STATIC PARAMETERS
# syringeFluid = None
# LINEVOL_1 = 1.0 # MAX is 1.0
# LINEVOL_2 = 1.0
# LINEVOL_3 = 1.0
# #Could add more casette specific properties, save/load part as a JSON/YAML
# casDict = {'CAS1':{'linevol': LINEVOL_1, 'currentFluid': None, 'volInLine': 0},
# 		'CAS2': {'linevol': LINEVOL_2, 'currentFluid': None, 'volInLine': 0},
# 		'CAS3': {'linevol': LINEVOL_3, 'currentFluid': None, 'volInLine': 0},}
# volInLineFactor = 1.3
# #The currentFluid must be the same and volInLine must be 1.3*pumpVol in order to pump from the line. This is a safety factor so not to pump bubbles/air into chamber.
# #So if you wanted to pump 0.5ml into the chamber and the linevol was 1ml, 0.5*1.3 < 1 is true.
# #However, for the next cycle to pump 0.5ml, the linevol is now 0.5ml, and 0.5*1.3 < 0.5 is false.
# #Therefore, you have to purge the line before loading the new reagent.
formalin_secs = 5
meoh_secs = 5
dye_cycles = 6
dye_cycle_secs = 10
babb_secs = 5
# mixInSpeed=500
# mixOutSpeed = 50
# #Can use this to ensure that linevolume is not depleted from pushing extra volume out
# extraMixFactor = 1.1
# clnVol = 1
# clnInSpeed = 200
# washVol = 1.5
# washInSpeed = 500
# wasteSpeed = 500
# purgeInSpeed = 400
# purgeOutSpeed = 50
# #Shouldn't the purgeVol be the linevol + some extra so that you fully purge line and chamber?
# purgeVol = 0.5
# stainAirVol = 1
# stainAirInSpeed = 500
# stainAirOutSpeed = 200

# This part will be done mainly by the onJoin command
print('STARTING...')
connect()
# Is this where acquire goes?
acquire()
# Do you want to have an option to set the heater temp in the protocol or GUI defaults? There a heater setting for each cassette?
set_heater('CAS1', 47)
# Should you wait until the heater is at the right temperature before starting the protocol? If so, how do you check the heater temperature?
# Is it just cassette_temp('CAS1')?
# engage('CAS1')  # same thing for now
cassette_contact('CAS1')
sleep(1)  # Can I move this sleep into the machine.py code?

# Skip for ARF
# If last step was BABB in syringe, need to wash syringe with MEOH first
# If last step was dye, should be ok to go direct to here
# Do you want to do this everytime you draw formalin? Or just when the current reagent in the syringe isn't formalin?
washSyringe(reagent='FORMALIN', washVol=casDict['CAS1']['linevol'] + 0.5,
            washInSpeed=500, wasteSpeed=400)

formalin(cas='CAS1', ml=0.5, inSpeed=500, chamberSpeed=50, lineSpeed=50, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=formalin_secs, mixAfter=None)
# OK TO DO OTHER THINGS

meoh(cas='CAS1', ml=0.5, inSpeed=400, chamberSpeed=50, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=meoh_secs, mixAfter=None)
# OK TO DO OTHER THINGS

meoh(cas='CAS1', ml=0.5, inSpeed=500, chamberSpeed=50, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=meoh_secs, mixAfter=None)
# OK TO DO OTHER THINGS

purge(cas='CAS1')
countdown(4)  # equilibrate

stain(cas='CAS1', ml=0.2, inSpeed=200, chamberSpeed=50, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=dye_cycle_secs * dye_cycles, mixAfter=dye_cycle_secs, mixVol=0.1, extraVolOut=0.1, earlyStopping=False)

print('DONE WITH DYE')

babb(cas='CAS1', ml=1, inSpeed=200, chamberSpeed=25, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=babb_secs, mixAfter=None)
# OK TO DO SOMETHING ELSE

babb(cas='CAS1', ml=0.5, inSpeed=200, chamberSpeed=25, lineSpeed=200, washSyr='auto', washSyrReagent='MEOH')
incubate(cas='CAS1', incTime=babb_secs, mixAfter=None)
# OK TO DO SOMETHING ELSE

print('Specimen ejecting')
cassette_eject('CAS1')  # Should minimize delay for eject when ready
# disengage(cas='CAS1')

clean(cas='CAS1')

print('READY FOR NEW SAMPLE')
