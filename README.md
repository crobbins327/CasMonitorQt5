# CasMonitor
### PyQt GUI and python controller tissue sample monitor 
__1)__ Start _crossbario_ docker image in a new terminal. There is a text file that is named "start docker". Copy and paste that code into the terminal.

**IF on raspberry pi or other device, use appropriate docker image for _crossbario_!** (https://github.com/crossbario/crossbar)

__2)__ Open SampleMonitor.desktop launcher. This will launch controlNQ.py and setupGUI.py simultaneously as subprocesses.



### OLD METHOD TO START

__1)__ Start _crossbario_ docker image in a new terminal. There is a text file that is named "start docker". Copy and paste that code into the terminal.

**IF on raspberry pi or other device, use appropriate docker image for _crossbario_!** (https://github.com/crossbario/crossbar)

__2)__ Open a second terminal. Make sure all casettes and the syringe needle are removed just incase. Activate the base environment for python and run the controlNQ.py file.

    cd CasMonitor/
    source activate base
    python ./prepbot/controlNQ.py

__3)__ Open another terminal or use the docker terminal to open the gui.

    cd CasMonitor/
    source activate base
    python setupGUI.py
    

#### Version 0.0.2 UI Demonstration:



#### Version 0.0.0 UI Demonstration:
![](examples/ProgressGIFs/9-11-UI-demonstration.gif)
