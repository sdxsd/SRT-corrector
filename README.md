# SRT-Corrector / Subtitle Corrector
This program aims to streamline the process of error checking automatically generated subtitles by leveraging ChatGPT.
## Usage:
You can invoke the program from the terminal as so:
```
Windows: python3 .\subtitle_corrector.py example.srt
macOS/GNU + Linux: ./subtitle_corrector.py example.srt
```
The program will then query ChatGPT and write it's response to a new file called output.srt, which will be located in the output directory.
### Notes:
This program is still a WIP and thusly cannot be considered entirely ready for use. As to what needs to be worked on, I give the following:
- Splitting the input into multiple queries thus getting the output for the entire file.
- GUI mode
- The production of a diff between the original and modified subtitles for easier error checking.

#### License:
This program is licensed under the GNU General Public License Version 3, and thus is Free Software. 
