#!/usr/bin/env python3

import srt
import sys

ORAW_TEXT_UNIX = "../output/raw_SRT_text.txt"
OSRT_UNIX = "../output/output.srt"

def srt_to_text(file_name):
    print("Formatting: " + file_name)
    srtFile = open(sys.argv[1])
    subtitlesList = list(srt.parse(srtFile.read()))
    outputFileText = open(ORAW_TEXT_UNIX, "w")
    for i in subtitlesList:
        outputFileText.write(i.content + "\n")
    print("Formatted: " + filename)

def main():
    if (len(sys.argv) < 2):
        print("Please enter the path to a valid SRT file.")
    srt_to_text(sys.argv[1])

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
