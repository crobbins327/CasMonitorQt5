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
    
    
### Version 0.03 UI Demonstration:
Virtual keyboard demo

https://user-images.githubusercontent.com/28576964/183572020-357977ba-63bd-4c1e-ae71-2e55f5be016e.mp4

Temperature monitor

https://user-images.githubusercontent.com/28576964/183571838-403fcd68-21bb-4856-9eed-2fd87507e0a3.mp4

Tempterature monitor, grid swipe layout

https://user-images.githubusercontent.com/28576964/183571850-fc1c497b-1b5a-414f-a62e-01ef3f0ef64b.mp4

Testing multiple protocols

https://user-images.githubusercontent.com/28576964/183571984-76f1e3d2-41c0-42bb-90aa-c0eae710e6b7.mp4

1 Cassette

https://user-images.githubusercontent.com/28576964/183571662-a9f6303e-338c-4350-85f1-7ed05f10fe6e.mp4

Sample monitor swipe layout

https://user-images.githubusercontent.com/28576964/183571825-68eb6af4-fb38-41f2-88db-d5399dbf4ea3.mp4



#### Version 0.0.2 UI Demonstration:
![](examples/ProgressGIFs/10-07-UI-demonstration.gif)


#### Version 0.0.0 UI Demonstration:
![](examples/ProgressGIFs/9-11-UI-demonstration.gif)
