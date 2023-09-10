<img src="icns/Icon1024.png" width="256"/>

# Subtitle Corrector
This program aims to streamline the process of error checking automatically generated subtitles by leveraging ChatGPT.
## Usage:
### Installing openai API key:
#### Windows:
Press START (The Windows button) and type in environment, you will see the option "edit the system environment variables".
Click it and a GUI will appear, at the bottom there is a button which says "Environment variables..."
Click this button and it will take you to a new menu, below the user variables list click "New" and create new variable
with the name "OPENAI_API_KEY" and with its value being the key itself. Click OK, and now you're done.
#### macOS/GNU + Linux
Open your terminal and run the following commands:
```
echo 'export OPENAI_API_KEY="[insert your key here between the brackets]"' >> ~/.zshrc (.bashrc if on GNU + Linux)
```
### Using the program:
#### GUI
![Screenshot](icns/screenshot.png)
To invoke the program in GUI mode, run the following command:
```
Windows: python3 .\SRT-gui.py
macOS/GNU + Linux: ./SRT-gui.py
```
With the GUI you can specify the output folder and the input subtitle file to be corrected.
When both are selected, simply click the "Process subtitle" button.
#### TUI
You can invoke the program in TUI mode as so:
```
Windows: python3 .\SRT-tui.py example.srt
macOS/GNU + Linux: ./SRT-tui.py example.srt
```
The program will then query ChatGPT and write it's response to a new file called output.srt, which will be located in the output directory.
### Notes:
This program is still a WIP and thusly cannot be considered entirely ready for use. As to what needs to be worked on, I give the following:
- Splitting the input into multiple queries thus getting the output for the entire file.
- The production of a diff between the original and modified subtitles for easier error checking.

#### License:
This program is licensed under the GNU General Public License Version 3, and thus is Free Software. 
