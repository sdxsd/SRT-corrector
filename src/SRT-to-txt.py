#!/usr/bin/env python3

import srt
import sys

print("Formatting: " + sys.argv[1])

SRT_file = open(sys.argv[1])
subtitles_TXT = srt.parse(SRT_FILE)
