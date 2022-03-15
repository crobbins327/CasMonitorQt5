#!/home/jackr/anaconda/envs/QML36/bin/python
import sys
sys.path.append('~/CasMonitorQt5')
import subprocess
import time

if __name__ == '__main__':
    processes = []
    processes.append(subprocess.Popen([sys.executable, './prepbot/controlNQ.py']))
    processes.append(subprocess.Popen([sys.executable, 'setupGUI.py']))

    while True:
        time.sleep(10)
#        print(processes)
#        for p in processes:
#            print(p)
#            print(p.poll())
        if any(p.poll() != None for p in processes):
            break
        continue


    processes[0].terminate()
    print('Controller poll: ', processes[0].poll())
    processes[1].terminate()
    print('GUI poll: ', processes[1].poll())
