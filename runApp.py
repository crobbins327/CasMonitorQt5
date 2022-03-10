#!/home/jackr/anaconda/envs/QML36/bin/python
import os
import sys
import psutil
#sys.path.append('~/CasMonitorQt5/')
import subprocess
import time

def isPIDRunning(pid):
    print('Checking if PID {} is running...'.format(pid))
    try:
        if psutil.pid_exists(int(pid)):
            print ('PID {} already exists!'.format(pid))
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def checkPIDFile(pidfile):
    if os.path.isfile(pidfile):
        pid = open(pidfile, 'r').read()
        #print(pid)
        if isPIDRunning(pid):
            return True, int(pid)
        else:
            return False, None
    else:
        return False, None



if __name__ == '__main__':
    #Check if SampleMonitor is running...
    pid = str(os.getpid())
    pidfile = '/tmp/SampleMonitor.pid'
    #Saving gui and ctrl subprocess PIDs to also kill if running
    guipidf = '/tmp/SampleMonitor_GUI.pid'
    ctrlpidf = '/tmp/SampleMonitor_Controller.pid'
#     pidfile = 'F:/Torres/CasMonitorQt5/SampleMonitor.pid'
    #If it is running, warn the user and do not start the app
    #Could also terminate the active processes and give the user an option to do that
    runRunning, runPID = checkPIDFile(pidfile)
    guiRunning, guiPID = checkPIDFile(guipidf)
    ctrlRunning, ctrlPID = checkPIDFile(ctrlpidf)
    if runRunning or guiRunning or ctrlRunning:
        print('SampleMonitor with PID {},{},{} is still running. Use task manager to terminate runApp.py, controlNQ.py, and setupGUI.py processes'.format(runPID, ctrlPID, guiPID))
        while True:
            terminate = input("Do you wish to terminate existing process? yes|no    ")
            if terminate == "yes" or terminate == "y":
                try:
                    if runPID is not None:
                        psutil.Process(runPID).terminate()
                    if guiPID is not None:
                        psutil.Process(guiPID).terminate()
                    if ctrlPID is not None:
                        psutil.Process(ctrlPID).terminate()
                except Exception as e:
                    print(e)
                break
            elif terminate == "no" or terminate == "n":
                print('Goodbye!')
                time.sleep(5)
                sys.exit()
        
    open(pidfile, 'w').write(pid)
    
    try:
        processes = []

        ctrl = subprocess.Popen(['python3', 'prepbot/controlNQ.py'])
        # ctrl = subprocess.Popen([sys.executable, 'prepbot/controlNQ.py'])
        open(ctrlpidf,'w').write(str(ctrl.pid))
        time.sleep(1)
        gui = subprocess.Popen(['python3', 'setupGUI.py'])
        # gui = subprocess.Popen([sys.executable, 'setupGUI.py'])
        open(guipidf,'w').write(str(gui.pid))
        processes.append(gui)
        processes.append(ctrl)
    
        
        while True:
            if any(p.poll() == 0 for p in processes):
                break
            time.sleep(0.5)
            continue
    
        processes[0].terminate()
        print('Controller poll: {}'.format(processes[0].poll()))
        processes[1].terminate()
        print('GUI poll: {}'.format(processes[1].poll()))
     
    finally:
        os.unlink(pidfile)
