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

import argparse
import openai
import srt
import sys
import os
import platform
import tiktoken

ORAW_TEXT = ""
OFILE = ""
if (platform.system() == "Linux" or platform.system() == "Darwin"):
    ORAW_TEXT = "./output/raw_SRT_text.txt"
    OFILE = "./output/output.srt"
elif (platform.system() == 'Windows'):
    ORAW_TEXT = 'output/raw_SRT_text.txt'
    OFILE = 'output/output.srt'

subtitle_correction_prompt = '''You are going to help correct the subtitles for a talk given at a
programming school. You will be provided with an input, each newline is a new subtitle.
Your job is to remove redundant words, fix grammar, and make sure that sentences make sense in the context.
You are going to output the modified subtitles in the same format as it was given.
You MUST preserve the newlines.'''

# Parses the SRT file into raw text data delimited by newlines.
def srt_to_text(file_name):
    print("Formatting: " + file_name)
    srt_file = open(file_name, encoding="utf-8")
    subtitles_list = list(srt.parse(srt_file.read()))
    ofile_raw_text = open(ORAW_TEXT, "w", encoding="utf-8")
    for sub in subtitles_list:
        ofile_raw_text.write(sub.content + "\n")
    print("Formatted: " + file_name)
    return (subtitles_list)

def output_SRT(answer, subtitles_list):
    print("Response received. Processing response into SRT and outputting")
    outputfile = open(OFILE, "w", encoding="utf-8")
    new_content_lines = answer.splitlines()
    i = 0
    for sub in subtitles_list:
        if (i > len(new_content_lines) - 1):
            sub.content = sub.content
        else:
            sub.content = new_content_lines[i]
            i += 1
    outputfile.write(srt.compose(subtitles_list))
    print("Done!")

# Queries ChatGPT with the stripped SRT data.
def query_chatgpt(question):
    print("Querying ChatGPT")
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    client = openai.ChatCompletion()
    chat_log = [{
        'role': 'system',
        'content': subtitle_correction_prompt,
    }]
    chat_log.append({'role': 'user', 'content': question})
    response = client.create(model='gpt-3.5-turbo-16k', messages=chat_log)
    answer = response.choices[0]['message']['content']
    chat_log.append({'role': 'assistant', 'content': answer})
    return answer, chat_log

def num_tokens_from_string(raw_text):
    print("Calculating number of tokens")
    encoding = tiktoken.get_encoding("gpt2")
    num_tokens = len(encoding.encode(raw_text))
    return num_tokens

# Reads the raw SRT data and passes it to ChatGPT to be processed.
def auto_process(subtitles_list):
    query = open(ORAW_TEXT, "r", encoding="utf-8")
    raw_text = query.read()
    token_num = num_tokens_from_string(raw_text)
    print("Number of tokens:", token_num)
    query_count = 0
    while (token_num > 1250):
        token_num /= 2
        query_count += 1
    print(query_count)
    # answer, log = query_chatgpt(raw_text);
    # output_SRT(answer, subtitles_list)
