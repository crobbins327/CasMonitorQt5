# Changelog

## [0.0.1] - 09/30/2020
### Added
First Changelog entry and operational CasMonitor version!

**Controller and GUI WAMPHandler**
- Clean lines and shutdown procedure
- Task status 'stopping' and 'cleaning' can be used to repopulate the controller and GUI upon disconnection from router
- YAML adjustable parameters with functions to communicate to GUI and Debug screen
  - Send parameters when controller joins
  - Update parameters and write to config.yaml file from Debug screen
  - Communication with controller to receive config.yaml parameters and update Debug screen when GUI joins
- Density adjustment based on residual fluid and reagent
- Operation time log (opTimes.log) and timers on all controlNQ.py operations and machine.py functions
- Sample log in GUI should update more often and starts from the correct position

**GUI**
- Debug screen is fully functional.
  - Execute script and stop all terminal tasks (termTasks)
  - Use buttons to execute functions directly
  - Edit parameters and send to controller
  - Scroll view instead of swipe view
- Protocol editor
  - Wash line & syringe on load reagent operations
  
### TODO
- Test on prepbot
- Swipe view on cassette monitor to increase the number of samples that can be run
  - refactor corresponding machine functions to eliminate boilerplate code
- Save sample log button
- Past run/sample log history in GUI
- Add paths and preferences (default protocol, protocol folder, windowed/fullscreen) to config.yaml parameter file
- Update times for real operations using opTimes.log data
  - Determine operation bottlenecks and adjust parameters to speed up protocols


[0.0.1]: https://github.com/crobbins327/CasMonitor/tree/0.0.1 

