#!/home/jackr/anaconda/envs/QML36/bin/python
import sys
sys.path.append('F:/Torres/CasMonitorQt5')
import subprocess

if __name__ == '__main__':
    processes = []
    processes.append(subprocess.Popen([sys.executable, './prepbot/controlNQ.py']))
    processes.append(subprocess.Popen([sys.executable, 'setupGUI.py']))

    while True:
        if any(p.poll() == 0 for p in processes):
            break
        continue


    processes[0].terminate()
    print('Controller poll: ', processes[0].poll())
    processes[1].terminate()
    print('GUI poll: ', processes[1].poll())
