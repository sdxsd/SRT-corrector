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

from const import API_prices
import tiktoken
import srt

def analyse_results(query_segments):
    failed = 0
    successful = 0
    for query_seg in query_segments:
        for query in query_seg.queries:
            if query.should_run is False:
                failed += 1
            else:
                successful += 1
    print(f"({successful}) Successful ({failed}) Failed")

def exit_message(query_segments, model):
    print("All queries resolved.")
    analyse_results(query_segments)
    print(f"Estimated cost: €{calculate_cost(query_segments, model)}")

# I <3 one line functions.
def count_subs(subs):
    return (sum(map(lambda sub: sub.rstrip().isdigit() is True, subs.splitlines())))

# Counts the number of tokens in a given string.
def num_tokens(raw_text):
    return (len(tiktoken.get_encoding("cl100k_base").encode(raw_text)))

# Estimates the total cost in api usage.
def calculate_cost(query_segments, model):
    input_usage = 0
    output_usage = 0
    for query_seg in query_segments:
        for query in query_seg.queries:
            input_usage += query.token_usage_input
            output_usage += query.token_usage_output
    return (round((API_prices[model]["input_price"] * input_usage) + (API_prices[model]["output_price"] * output_usage), 2))

# Globs all responses into single string.
def assemble_queries(queries):
    full_output = ""
    for query in queries:
        full_output += query.response.glob()
    return (full_output)

def failed_queries_from_list(results):
    failed = []
    for result in results:
        if (result is not True):
            failed.append(result)
    return (failed)

# Parses a given .SRT file and returns it's contents as an array.
def parse_subtitle_file(subtitle_file):
    slist = []
    encoding: str # TODO: Actually use this.
    try:
        with open(subtitle_file, encoding="utf-8") as f:
            print("File is utf-8")
            encoding = "utf-8"
            slist = list(srt.parse(f))
    except UnicodeError:
        with open(subtitle_file) as f:
            slist = list(srt.parse(f))
    if (not slist):
        print(f"Failed to parse {subtitle_file}, exiting...")
        exit()
    print(f"Parsed: {subtitle_file}")
    return (slist)

# Replaces the "content" variable of the original subtitle block list
# using the sum of the responses from GPT.
def replace_sub_content(rawlines, slist):
    i = 0
    for sub in slist:
        sub.content = ""
        digit_encountered = False
        while (i < len(rawlines)):
            if (rawlines[i].rstrip().isdigit() is True):
                if (digit_encountered is True):
                    digit_encountered = False
                    break
                else:
                    digit_encountered = True
            else:
                sub.content += ((" " if sub.content else "") + (rawlines[i] if rawlines[i].rstrip() != "" else ""))
            i += 1
    return (srt.compose(slist))

def report_status(idx, token_count):
    print(f"Sending query: {idx} Token count: {token_count}")
