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


dutch_to_english_prompt = '''
Je gaat optreden als een programma ontworpen om ondertitels naar het Engels te vertalen.
Je zult automatisch gegenereerde ondertitels vertalen.
Je krijgt een invoer in het .srt-formaat.
Je gaat het volgende doen: Foutief geplaatste woorden corrigeren. Overbodige en/of vulwoorden verwijderen.
Het aantal regels in de uitvoer moet hetzelfde zijn als het aantal regels in de invoer.
Zorg ervoor dat je de ondertitel-ID behoudt
'''

english_to_dutch_prompt = '''
You are going to act as a program designed to help translate subtitles.
You will be translating automatically generated subtitles from Dutch to English.
You will be given an input in the .srt format.
You will be doing the following: Translating Dutch sentences into English. Correcting out of place words. Removing redundant and or filler words.
Keep the content of the sentences consistent with the input.
The number of lines in the output must be the same as the number of lines in the input.
Make sure to preserve the subtitle id.
Please do not use overly formal language.
'''

subtitle_correction_prompt = '''
You are going to act as a program designed to help correct subtitles.
You will be correcting automatically generated subtitles from a talk at a programming school.
You will be given an input in the .srt format.
You will be doing the following: Please correct out of place words. Removing redundant and or filler words.
Keep the content of the sentences consistent with the input. Your goal is correction not replacement.
The number of lines in the output must be the same as the number of lines in the input.
Make sure to preserve the subtitle id.
Please do not use overly formal language.
'''

prompt_list = {
    1: subtitle_correction_prompt,
    2: dutch_to_english_prompt,
    3: english_to_dutch_prompt
}

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
def query_chatgpt(query_str, chosen_prompt):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    client = openai.ChatCompletion()
    chat_log = [{
        'role': 'system',
        'content': prompt_list[int(chosen_prompt)],
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

def count_subs(subs):
    rawlines = subs.splitlines()
    subcount = 0
    i = 0
    while (i < len(rawlines)):
            if (rawlines[i].rstrip() == ""):
                i += 1
            if (rawlines[i].rstrip().isdigit() == True):
                    subcount += 1
                    i += 1
            elif (rawlines[i] != ""):
                i += 1
    return (subcount)


def query_loop(subtitle_file, chosen_prompt):
    full_output = ""
    query_str = ""
    query_counter = 0
    slist = srt_to_text(subtitle_file)
    raw_outputfile = open("raw_output.txt", "w", encoding="utf-8")
    
    for sub in slist:
        query_str += (str(sub.index) + os.linesep + sub.content + os.linesep)
        token_count = num_tokens(query_str)
        if (token_count > 300):
            query_counter += 1
            print("Sending query with token count: ", token_count, " | Query count: ", query_counter)
            answer, log = query_chatgpt(query_str, chosen_prompt)
            if (answer[-1] != '\n'):
                answer += '\n' 
            while (count_subs(answer) != count_subs(query_str)):
                query_counter += 1
                print("Inconsistent output, resending query: ", token_count, " | Query count: ", query_counter)
                answer, log = query_chatgpt(query_str, chosen_prompt)
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
    rawlines = full_output.splitlines()
    i = 0
    for sub in slist:
        sub.content = ""
        digit_encountered = False
        while (i < len(rawlines)):
            if (rawlines[i].rstrip() == ""):
                sub.content += "Zhazhek was here!"
                i += 1
            if (rawlines[i].rstrip().isdigit() == True):
                if (digit_encountered == True):
                    digit_encountered = False
                    break
                else:
                    i += 1
                    digit_encountered = True
            elif (rawlines[i] != ""):
                sub.content += rawlines[i]
                i += 1
    return (srt.compose(slist))

# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, outputfile="output.srt", chosen_prompt=1):
    full_output = query_loop(subtitle_file, chosen_prompt)
    ofile = open(outputfile, "w", encoding="utf-8")
    ofile.write(full_output)
