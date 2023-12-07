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

from openai import AsyncOpenAI
import asyncio
import srt
import os
import tiktoken
import time

class QueryException(Exception):
    def __init___(self, type, message):
        self.type = type
        self.message = message
        print(self.message)
        super().__init__(message)

class SubtitleCorrector:
    def __init__(self, chosen_prompt=1):
        self.prompt_list = {
            1:
'''You are going to act as a program designed to help correct subtitles. 
You will be correcting automatically generated subtitles from a talk at a programming school.
You will be given an input in the .srt format
You will be doing the following: Please correct out of place words. Removing redundant and or filler words.
Keep the content of the sentences consistent with the input. Your goal is correction not replacement.
The number of lines in the output must be the same as the number of lines in the input.
Make sure to preserve the subtitle id.
Please do not use overly formal language.''',
            2:
'''Je gaat optreden als een programma ontworpen om ondertitels naar het Engels te vertalen.
Je zult automatisch gegenereerde ondertitels vertalen.
Je krijgt een invoer in het .srt-formaat.
Je gaat het volgende doen: Foutief geplaatste woorden corrigeren. Overbodige en/of vulwoorden verwijderen.
Het aantal regels in de uitvoer moet hetzelfde zijn als het aantal regels in de invoer.
Zorg ervoor dat je de ondertitel-ID behoudt''',
            3:
'''You are going to act as a program designed to help translate subtitles.
You will be translating automatically generated subtitles from English to Dutch.
You will be given an input in the .srt format.
You will be doing the following: Translating English sentences into Dutch. Correcting out of place words. Removing redundant and or filler words.
Keep the content of the sentences consistent with the input.
The number of lines in the output must be the same as the number of lines in the input.
Make sure to preserve the subtitle id.
Please do not use overly formal language.'''
        }
         
        self.chosen_prompt = chosen_prompt
        self.prompt_token_count = self.num_tokens(self.prompt_list[int(chosen_prompt)])
        self.query_counter = 0
        self.total_queries = 0
        self.queries = []
        self.token_usage = 0
    
    def validate_finish_reason(self, finish_reason):
        if (finish_reason == "stop"):
            return 
        elif (finish_reason == "length"):
            raise QueryException(finish_reason, "Query failed due to exceeding the token limit.")
        elif (finish_reason == "content_filter"):
            raise QueryException(finish_reason, "Query failed due to violation of content policy")
         
    # Queries ChatGPT with the stripped SRT data.
    async def query_chatgpt(self, query_str, query_number):
        client = AsyncOpenAI()
        start = time.time()
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {'role': 'system', 'content': self.prompt_list[int(self.chosen_prompt)]},
                {'role': 'user', 'content': query_str},
            ]
        )
        print("Query number: ", query_number, " | ", "Response received in: ", round((time.time() - start), 2), " seconds")
        self.token_usage += response.usage.total_tokens
        self.validate_finish_reason(response.choices[0].finish_reason)
        answer = response.choices[0].message.content
        if (answer[-1] != '\n'):
            answer += '\n' 
        return answer
    
    # Counts the number of tokens in a given string.
    def num_tokens(self, raw_text):
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(raw_text))
        return num_tokens
    
    # Counts the number of subtitle blocks in a given string.
    def count_subs(self, subs):
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
    
    # Estimates the total queries required for the file using token counts.
    def estimate_total_queries(self, slist):
        query = ""
        for sub in slist:
            query += (str(sub.index) + os.linesep + sub.content + os.linesep)
        token_count = self.num_tokens(query)
        query_count = 0
        while (token_count > 300):
            token_count -= 300
            query_count += 1
        if (token_count > 0):
            query_count += 1
        return (query_count)
    
    # Keeps the user informed.
    def report_status(self, token_count):
        print("Sending query with token count: ", (token_count + self.prompt_token_count), " | Query count: ", self.query_counter, "/", self.total_queries)
    
    # Replaces the "content" variable of the original subtitle block list
    # using the sum of the responses from GPT.
    def replace_sub_content(self, full_output, slist):
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
                    if (sub.content != ""):
                        sub.content += " "
                    sub.content += rawlines[i]
                    i += 1
        return (srt.compose(slist))
    
    async def send_and_receive(self, query_str, token_count):
        self.query_counter += 1
        self.report_status(token_count)
        answer = await self.query_chatgpt(query_str, self.query_counter)
        while (self.count_subs(answer) != self.count_subs(query_str)):
            self.total_queries += 1
            self.query_counter += 1
            print("Inconsistent output, resending query: ", token_count, " | Query count: ", self.query_counter)
            answer = await self.query_chatgpt(query_str, self.query_counter)
        return answer
    
    def handle_exception(self, exception):
        print(exception.message)
        for query in self.queries:
             query.cancel()
        
    async def query_loop(self, subtitle_file):
        slist = list(srt.parse(open(subtitle_file, "r", encoding="utf-8")))
        self.total_queries = self.estimate_total_queries(slist)
        print("Parsed: ", subtitle_file, " | ", "Estimated number of queries: ", self.total_queries)
        query_str = ""
        for sub in slist:
            query_str += (str(sub.index) + os.linesep + sub.content + os.linesep)
            token_count = self.num_tokens(query_str)
            if (token_count > 300 or (slist[-1].index == sub.index)):
                self.queries.append(asyncio.create_task(self.send_and_receive(query_str, token_count)))
                query_str = ""
        try:
            responses = await asyncio.gather(*self.queries)
        except QueryException as e:
            self.handle_exception(e)
        print("Queries sent & responses received")
        return (self.replace_sub_content(''.join(responses), slist))
    
# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, outputfile="output.srt", chosen_prompt=1):
    subtitlecorrector = SubtitleCorrector(chosen_prompt)
    full_output = asyncio.run(subtitlecorrector.query_loop(subtitle_file))
    ofile = open(outputfile, "w", encoding="utf-8")
    ofile.write(full_output)
        