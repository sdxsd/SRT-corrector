#!/usr/bin/env python3

import subtitlecorrector as stc
import argparse
import os
import platform

# Creates the argument parser.
# These python libraries are actually pretty cool.
def arg_parser_init():
    parser = argparse.ArgumentParser(
        prog="subtitle-corrector",
        description="Corrects subtitles by using ChatGPT",
        epilog="subtitle-corrector")
    parser.add_argument('input_srt')
    parser.add_argument('--ofile', action='store', required=True)
    return (parser)

# Main.
def main():
    parser = arg_parser_init()
    args = parser.parse_args()
    stc.correct_subtitles(args.input_srt, args.ofile)

main()
