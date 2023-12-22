# Project blueprints

### Files (in order of importance):
#### **subtitlecorrector.py**
This file contains the main functionality of the program. It handles the queries to OpenAI, the parsing and
formatting of the .srt, and the exception handling along with a number of smaller features such as cost calculation
and displaying logs.
#### **prompts.py**
This file defines the Prompt object and a number of functions to instantiate Prompts out of json files.
The Prompt object contains all the information that the program needs to modify a subtitle in the desired way.
#### **config.py** 
This file defines a Config object which is generated from the config.json located in an operating system specific 
configuration directory.
#### **SRT-tui.py**
This file can be called from the shell in order to process the subtitle file.
It is the recommended way of using the program.
#### **SRT-gui.py**
This file is responsible for the GUI of the program.
#### **setup.py**
Makes accessible all the information needed by py2app in order to create a MacOS .app file.
