# Subtitle Corrector
This program is a general purpose subtitle modifier powered by GPT4.

You can use this program for any number of purposes for example:
- Correcting error filled subtitles from a faulty transcript.
- Translating a given subtitle from language X to language Y.
- Turning a horror film into a comedy by making every character speak in outdated slang.

## Documentation:
### Installing OpenAI API key:
Before you can use the program, your OpenAI api key needs to be present within your environment variables.
The following are instructions on how to add your API key to your respective operating system.
#### Windows:
Press the start key and type in environment. You will then see the option "Edit the system environment variables".
Click it and a GUI will appear, at the bottom there is a button which says "Environment variables..."
Click this button and it will take you to a new menu, below the user variables list click "new" and create a new variable
with the name "OPENAI_API_KEY" and with its value being the key itself. Click OK, and now you're done.
#### MacOS/GNU + Linux
Open your terminal and run the following commands:
```
echo 'export OPENAI_API_KEY="insert your key here between the parentheses"' >> ~/.zshrc (.bashrc if on GNU + Linux)
```
### Using the program:
#### GUI
![Screenshot](icns/screenshot.png)

Double click the executable as with any other program.
Select a prompt, then an input file, and finally an output directory. Then click process and wait.
The program is finished when the terminal outputs: "Queries sent and responses received."
#### TUI
You can invoke the program in TUI mode as so:
```
Windows: python3 .\SRT-tui.py example.srt --ofile example_output.srt --prompt SCR
macOS/GNU + Linux: ./SRT-tui.py example.srt --ofile example_output.srt --prompt DTE
```
The program will then query ChatGPT and write it's response to the outputfile.

### Errors:
Since the program queries the OpenAI API asynchronously if a query encounters an exception it will not
halt the processing of the subtitle file. In the case of an exception, the original input of the failed query will
be written to the output file in place of the response that would have been recorded had the query not failed.

### License:
This program is licensed under the GNU General Public License Version 3, and thus is Free Software. 
