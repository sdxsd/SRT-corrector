#!/usr/bin/env python3

import subtitlecorrector as stc
import argparse
import os
import platform

prompt_shorthand_names = {
    'SCR': 1,
    'DTE': 2,
    'ETD': 3
}

# Creates the argument parser.
# These python libraries are actually pretty cool.
def arg_parser_init():
    parser = argparse.ArgumentParser(
        prog="subtitle-corrector",
        description="Corrects subtitles by using ChatGPT",
        epilog="subtitle-corrector")
    parser.add_argument('input_srt')
    parser.add_argument('--ofile', action='store', required=True)
    parser.add_argument('--prompt', action='store')
    return (parser)

# Main.
def main():
    parser = arg_parser_init()
    args = parser.parse_args()
    if (args.prompt != "" and (args.prompt != 'SCR' or args.prompt != 'DTE' or args.prompt != 'ETD')):
        stc.correct_subtitles(args.input_srt, args.ofile, prompt_shorthand_names[args.prompt])
    else:
        stc.correct_subtitles(args.input_srt, args.ofile, prompt_shorthand_names['SCR'])

main()
