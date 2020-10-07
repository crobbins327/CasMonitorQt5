#!/home/jackr/anaconda/envs/QML36/bin/python
import os
import sys
import subprocess

if __name__ == '__main__':
    processes = []
    processes.append(subprocess.Popen(['python3', './prepbot/controlNQ.py']))
    processes.append(subprocess.Popen(['python3', 'setupGUI.py']))

    
    
    
    while True:
        if any(p.poll() == 0 for p in processes):
            break
        continue


    processes[0].terminate()
    print('Controller poll: ', processes[0].poll())
    processes[1].terminate()
    print('GUI poll: ', processes[1].poll())
