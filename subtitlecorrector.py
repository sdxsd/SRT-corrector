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

import openai
import srt
import sys
import os
import platform
import tiktoken

subtitle_correction_prompt = '''
You are going to act as a program designed to help modify subtitles.
You will be given an input in the .srt format.
The number of lines in the output must be the same as the number of lines in the input.
Make sure to preserve the subtitle id.
You will be transforming the subtitles of the film "Downfall" from 2004, so that each character is alternating between speaking in one of three ways, these being: extremely exaggerated and obnoxious generation z slang such as "bussin', for real for real, no cap, on god, rizz, fire, lit, zamn, bussy, cringe, based, soy, chad, blackpilled, redpilled" + making references to contemporary meme culture. Or is speaking in an exaggerated gangster-like dialect utilising lots of outdated slang, or is speaking as a hypothetical soyjak from meme culture and is completely obsessed with marvel/star wars movies and pop media i.e. "oh my science this is just like when I lost my funkopops".
You must not include any emojis.
'''

def srt_to_text(file_name):
    print("Formatting: " + file_name)
    srt_file = open(file_name, encoding="utf-8")
    subtitles_list = list(srt.parse(srt_file.read()))
    ofile_raw_text = open("stripped_srt.txt", "w", encoding="utf-8")
    for sub in subtitles_list:
        ofile_raw_text.write(str(sub.index) + os.linesep)
        ofile_raw_text.write(sub.content + os.linesep)
        ofile_raw_text.write(os.linesep)
    print("Formatted: " + file_name)
    return (subtitles_list)

# Queries ChatGPT with the stripped SRT data.
def query_chatgpt(query_str):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    client = openai.ChatCompletion()
    chat_log = [{
        'role': 'system',
        'content': subtitle_correction_prompt,
    }]
    chat_log.append({'role': 'user', 'content': query_str})
    response = client.create(model='gpt-4', messages=chat_log)
    answer = response.choices[0]['message']['content']
    chat_log.append({'role': 'assistant', 'content': answer})
    return answer, chat_log

def num_tokens(raw_text):
    encoding = tiktoken.get_encoding("gpt2")
    num_tokens = len(encoding.encode(raw_text))
    return num_tokens

def query_loop(subtitle_file):
    full_output = ""
    query_str = ""
    query_counter = 0
    slist = srt_to_text(subtitle_file)
    raw_outputfile = open("raw_output.txt", "w", encoding="utf-8")
    
    for sub in slist:
        query_str += (str(sub.index) + os.linesep + sub.content + os.linesep)
        token_count = num_tokens(query_str)
        if (token_count > 150):
            query_counter += 1
            print("Sending query with token count: ", token_count, " | Query count: ", query_counter)
            answer, log = query_chatgpt(query_str)
            if (answer[-1] != '\n'):
                answer += '\n' 
            print(answer)
            full_output += (answer)
            raw_outputfile.write(answer)
            raw_outputfile.flush()
            query_str = ""
    if (query_str != ""):
        query_counter += 1
        print("Sending query with token count: ", token_count, " | Query count: ", query_counter)
        answer, log = query_chatgpt(query_str)
        raw_outputfile.write(answer)
        raw_outputfile.flush()
        full_output += (answer)

    print("Queries sent & responses received")
    outputlines = full_output.splitlines()
    i = -1
    for sub in slist:
        sub.content = ""
    for line in outputlines:
        if (line.isdigit() == True):
            i += 1
        elif (line != ""): 
            if (slist[i].content != ""):
                slist[i].content += " "
            slist[i].content += line
        elif (line == ""):
            continue 
    return (srt.compose(slist))

# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, outputfile="output.srt"):
    full_output = query_loop(subtitle_file)
    ofile = open(outputfile, "w", encoding="utf-8")
    ofile.write(full_output)
