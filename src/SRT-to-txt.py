#!/usr/bin/env python3

import srt
import sys

print("Formatting: " + sys.argv[1])
srtFile = open(sys.argv[1])
subtitlesText = srtFile.read()
subtitlesList = list(srt.parse(subtitlesText))
outputFileText = open("../output/separatedText.txt", "w")
for i in subtitlesList:
    outputFileText.write(i.content + "\n")
print("Formatted: " + sys.argv[1])
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
finalOutputFile = open("../output/processedOutput.srt", "w")
finalOutputFile.write(srt.compose(subtitlesList))
