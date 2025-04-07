# README #

This is my project to create a system giving full access to people with severe limitations on their mobility by allowing them to interact with a computer through only blinks.  This version of the system is in Python while I continue to develop it and figure out the functionality, however eventually once this is all locked down I plan to convert it to C++ (that is why I have mostly limited myself to external libraries which exist for both languages).  

It was also intentionally written to be robust, simple to use and extremely low demand in terms of both system resources and the quality of the camera required. This was to keep the costs low and make it as accessible as possible.

## Explanation of Approach ## 

[Note - this is reconstructed from my own notes written 10 years ago, as a result there may be inaccuracies]

There is an initialization process which is used to capture unambiguous images of the eyes both open and closed. After initialization it uses a haarcascade to find an initial position of the face and from that a rough estimate of where the eyes will be, then it uses template matching with the previously captured images of the eyes to detect whether they are open or closed. Future frames after the first use the previous position of the eyes to match the next eyes (meaning the costlier haar cascade only needs to be done once).
When the eyes are closed for longer than 100ms and then re-opened then it is considered a purposeful blink and a command is sent. Additionally if a long enough period has passed since the initialization or last recording, then updated images of the eyes are recorded.
The commands are used to either target a point on the screen or to select a type of interaction from a grid (double click, single click, scroll up etc.) to send to that point on the screen

An example of all of the part of this process can be found here:
https://youtu.be/cDzmFX5loTY 


### How do I get set up? ###
 
[Note - below here these notes are ~10 years out of date, it may well be possible to simply update libraries, but I expect many of the links will be obsolete and the libraries are 

Currently the system is initialised by running the BlinkController.py file which contains the main wx app object.  The requirements to use it are:

* Python 2.7 (found here https://www.python.org/download/releases/2.7/ )
* wxPython (found here http://www.wxpython.org/download.php )
* OpenCV-Python (found here http://docs.opencv.org/trunk/doc/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html )
* PYUserInput (found here https://github.com/SavinaRoja/PyUserInput )

The system also requires that you have a working webcam and the files blink.png and open.png will need to be replaced with an image of your own eyes (you can capture one more easily using the script save_eyes_to_file.py in the folder of the same name in this repository https://bitbucket.org/adam-barnett/blink_detection_experiments/src )

### Current Status ###

Currently the system allows for clicking on the screen using blinks as inputs to specify the position.  A short video of me using it can be found here https://www.youtube.com/watch?v=KZ74LAR_lME (recorded on the 16/01/15).

### Future work ###

Future developments of the system will:

* Alter the interaction method for clicking to allow moving in any direction and multiple types of mouse input (double click, right click etc.)
* Add  a keyboard such that a user can type using blinks
* Add a menu system for navigating between these different sections and configuring the system to personal preferences
