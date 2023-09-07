#!/usr/bin/env python3

import srt
import sys

print("Formatting: " + sys.argv[1])

srtFile = open(sys.argv[1])
subtitlesText = srtFile.read()
subtitlesGenerator = srt.parse(srtFile)
outputFileText = open("../output/separatedText.txt", "w")
for sub in srt.parse(subtitlesText):
    outputFileText.write(sub.content + "\n")
