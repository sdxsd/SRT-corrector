#!/usr/bin/env python3

# SUBTITLE-CORRECTOR IS LICENSED UNDER THE GNU GPLv3
# Copyright (C) 2023 Will Maguire

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

# The definition of Free Software is as follows:
# 	- The freedom to run the program, for any purpose.
# 	- The freedom to study how the program works, and adapt it to your needs.
# 	- The freedom to redistribute copies so you can help your neighbor.
# 	- The freedom to improve the program, and release your improvements
#   - to the public, so that the whole community benefits.

# A program is free software if users have all of these freedoms.

import subtitlecorrector as stc
import argparse
import prompts as prompts

# Creates the argument parser.
# These python libraries are actually pretty cool.
def arg_parser_init():
    parser = argparse.ArgumentParser(
        prog="subtitle-corrector",
        description="Modifies subtitles by using ChatGPT",
        epilog="subtitle-corrector")
    parser.add_argument('input_srt')
    parser.add_argument('--ofile', action='store', required=True)
    parser.add_argument('--prompt', action='store', required=True)
    return (parser)

# Main.
def main():
    parser = arg_parser_init()
    args = parser.parse_args()
    stc.correct_subtitles(args.input_srt, prompts.load_prompt(args.prompt), args.ofile)
    
main()
