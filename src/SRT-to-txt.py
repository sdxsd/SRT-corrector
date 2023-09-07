#!/usr/bin/env python3

import pychatgpt
import srt
import sys

ORAW_TEXT_UNIX = "../output/raw_SRT_text.txt"
OSRT_UNIX = "../output/output.srt"

# Parses the SRT file into raw text data delimited by newlines.
def srt_to_text(file_name):
    print("Formatting: " + file_name)
    srt_file = open(sys.argv[1])
    subtitles_list = list(srt.parse(srt_file.read()))
    ofile_raw_text = open(ORAW_TEXT_UNIX, "w")
    for sub in subtitles_list:
        ofile_raw_text.write(sub.content + "\n")
    print("Formatted: " + filename)
    return (subtitles_list)

# Requires the user to manually access chatgpt and get the required output. Program will
# be paused until user confirms that the replacement subtitles are available.
def manual_process(subtitles_list):
    input("Press enter when processed data is placed into output/newContent.txt...")
    newContentFile = open("../input/newContent.txt", "r")
    newContentLines = newContentFile.readlines()
    i = 0
    for sub in subtitlesList:
        if (i > len(newContentLines) - 1):
            sub.content = sub.content
        else:
            sub.content = newContentLines[i]
            i += 1
    finalOutputFile = open(OSRT_UNIX, "w")
    finalOutputFile.write(srt.compose(subtitlesList))

# Uses the pychatgpt library to automatically query chatgpt for subtitle correction.
def auto_processing():



def main():
    if (len(sys.argv) < 3):
        print("Please enter the path to a valid SRT file.")
    subtitles_list = srt_to_text(sys.argv[1])
    if (sys.argv[2] == 'a'):
        auto_processing()
    else if (sys.argv[2] == 'm'):
        manual_process(subtitles_list)
    else:
        print("Please enter either a or m to indicate whether you will use the automatic or manual process")
