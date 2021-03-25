# GB-Boundary-Generator
This is a program used to convert special objects imported into Golf Blitz courses into real boundaries for course making.

##### NOTE: This program is only compatible with MacOS 10.14 and higher. Please see the OPENING ON DIFFERENT OS section for info on running the python script.

### Video Tutorial: https://www.youtube.com/watch?v=X6mAMkMpwQ8

## USAGE:

1. Download the newest release of Boundary Generator from https://github.com/Blakiemon/GB-Boundary-Generator/releases

2. Open up your Golf Blitz course then drag and drop 'LeftBoundary.png' into the editor.

3. VERY IMPORTANT: In the 'Terrain' category dropdown rename the object you just imported to 'LeftBoundary' (Obviously without the quotes)

4. Save your course then open BoundaryGenerator.app (If you are on an older version of MacOS or on a different operating system please see the OPENING ON DIFFERENT OS section for info on with your device.)

5. Select your course within the program and ONLY select the holes with terrain objects named "LeftBoundary"

6. IMPORTANT: I have not added a way to reverse this process, if you accidently misplaced a boundary after processing you will have to edit the .plist files yourself. (HINT: they are in JSON. Just use a JSON editor and remove all Boundaries at the end of the JSON file.)

7. You are DONE! Go ahead and open the course, please note that you will not be able to visually see the boundaries unless you turn on the debug view during play-mode

## BUT WHY?:

*Welll.... "Why would you event WANT to add boundaries to your course?" I hear.*
1. Boundaries are invisible, and so you can create a kaizo / troll course to terrorize people :-)
 
2. Spider and Tunnel ball cannot stick to / tunnel through the boundary. (Again good for trolling)

3. You can make certain areas that are blocked off and cannot be tunneled into (E.G decoration or some other crap)

## OPENING ON DIFFERENT OS:

*REQUIREMENTS: Python3, and the PySimpleGUI package.*
1. Please download the latest version of Python here https://www.python.org/downloads/

2. Then install pip using this guide https://www.makeuseof.com/tag/install-pip-for-python/

3. Once you have python and pip installed, open CMD, Terminal or whatever bash/shell program you use and type `pip install PySimpleGUI`

4. Download or clone this github project to your computer (NOT DOWNLOAD A RELEASE, you can tell because the download will have BoundaryGenerator.py in it.)

5. Then, you need to change your directory in your bash/shell (Terminal or Command Prompt) to the folder that you download (Which contains BoundaryGenerator.py)
An easy way to do this is to type `cd ` then drag and drop the folder onto the bash/shell.


***AND FINALLY***

6. Once you're in the directory with Boundary Generator (😩 Yes I know these instructions were so hard to follow....) type in `python BoundaryGenerator.py` if that doesn't work type in `python3 BoundaryGenerator.py` if that doesn't work either try running `pip3 install PySimpleGUI` THEN run `python3 BoundaryGenerator.py`

AND YOU ARE DONE! Enjoy using the program :P

