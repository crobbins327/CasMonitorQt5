#!/home/jackr/anaconda/envs/QML36/bin/python
import os
import sys
import subprocess
import time

if __name__ == '__main__':
    
    pid = str(os.getpid())
    pidfile = '/tmp/SampleMonitor.pid'
    if os.path.isfile(pidfile):
        print ("{} already exists, exiting".format(pidfile ))
        time.sleep(1)
        sys.exit()
    
    open(pidfile, 'w').write(pid)
    
    try:
        processes = []
        #Only start controller if a controller is not already open....
        processes.append(subprocess.Popen(['python3', './prepbot/controlNQ.py']))
        processes.append(subprocess.Popen(['python3', 'setupGUI.py']))
    
        
        while True:
            if any(p.poll() == 0 for p in processes):
                break
            continue
    
    
        processes[0].terminate()
        print('Controller poll: {}'.format(processes[0].poll()))
        processes[1].terminate()
        print('GUI poll: {}'.format(processes[1].poll()))
     
    finally:
        os.unlink(pidfile)