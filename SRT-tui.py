#!/usr/bin/env python3

import subtitlecorrector as stc
import argparse
import os
import platform

ORAW_TEXT = ""
OFILE = ""
if (platform.system() == "Linux" or platform.system() == "Darwin"):
    ORAW_TEXT = "./output/raw_SRT_text.txt"
    OFILE = "./output/output.srt"
elif (platform.system() == 'Windows'):
    ORAW_TEXT = 'output/raw_SRT_text.txt'
    OFILE = 'output/output.srt'

# Creates the argument parser.
# These python libraries are actually pretty cool.
def arg_parser_init():
    parser = argparse.ArgumentParser(
        prog="subtitle-corrector",
        description="Corrects subtitles by using ChatGPT",
        epilog="subtitle-corrector")
    parser.add_argument('input_srt')
    parser.add_argument('--ofile', action='store', default=OFILE)
    return (parser)

# Main.
def main():
    parser = arg_parser_init()
    args = parser.parse_args()
    stc.correct_subtitles(args.input_srt, args.ofile)

main()
