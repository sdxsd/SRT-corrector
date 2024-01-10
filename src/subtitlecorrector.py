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
import math
import prompts as prompts
from config import Config
from query import Query

# Models and their different prices per token.
API_prices = {
    "gpt-4-1106-preview": {
        "input_price": 0.01 / 1000,
        "output_price": 0.03 / 1000
    },
    "gpt-4": {
        "input_price": 0.03 / 1000,
        "output_price": 0.06 / 1000
    },
    "gpt-4-32k": {
        "input_price": 0.06 / 1000,
        "output_price": 0.12 / 1000
    },
    "gpt-3.5-turbo-1106": {
        "input_price": 0.0010 / 1000,
        "output_price": 0.0020 / 1000
    },
    "gpt-3.5-turbo": {
        "input_price": 0.0010 / 1000,
        "output_price": 0.0020 / 1000
    }
}

class SubtitleCorrector:
    def __init__(self, chosen_prompt):
        self.client = AsyncOpenAI()
        self.config = Config()
        self.model = self.config.model
        self.tokens_per_query = self.config.tokens_per_query
        self.chosen_prompt = chosen_prompt
        self.prompt_token_count = self.num_tokens(self.chosen_prompt.instructions)
        self.queries = []
        self.query_tasks = []
             
    # Counts the number of tokens in a given string.
    def num_tokens(self, raw_text):
        return (len(tiktoken.get_encoding("cl100k_base").encode(raw_text)))

    # Estimates the total cost in api usage.
    def calculate_cost(self):
        input_usage = 0
        output_usage = 0
        for query in self.queries:
            input_usage += query.token_usage_input
            output_usage += query.token_usage_output
        return (round((API_prices[self.model]["input_price"] * input_usage) + (API_prices[self.model]["output_price"] * output_usage), 2))
        
    # Replaces the "content" variable of the original subtitle block list
    # using the sum of the responses from GPT.
    def replace_sub_content(self, rawlines, slist):
        i = 0
        for sub in slist:
            sub.content = ""
            digit_encountered = False
            while (i < len(rawlines)):
                if (rawlines[i].rstrip().isdigit() == True):
                    if (digit_encountered == True):
                        digit_encountered = False
                        break
                    else:
                        digit_encountered = True
                else:
                    sub.content += ((" " if sub.content else "") + (rawlines[i] if rawlines[i].rstrip() != "" else ""))
                i += 1
        return (srt.compose(slist))
   
    # This function creates a list of queries (tasks)
    # which will later be executed by asyncio.gather()
    def prepare_queries(self, slist):
        query_str = ""
        query_tasks = []
        idx = 0
        for sub in slist: 
            query_str += (os.linesep.join([str(sub.index), sub.content]) + os.linesep)
            token_count = self.num_tokens(query_str)
            if (token_count > self.tokens_per_query or (slist[-1].index == sub.index)):
                self.queries.append(Query(idx, self.chosen_prompt, query_str, token_count + self.prompt_token_count, self.client, self.config))
                query_tasks.append(asyncio.create_task(self.queries[idx].run()))
                query_str = ""
                idx += 1
        return (query_tasks)
    
    # raw subtitle data -> array of sub blocks -> array of tasks to be executed -> modified subtitle data -> ??? -> profit              
    async def process_subs(self, subtitle_file):
        with open(subtitle_file, "r") as f:
            slist = list(srt.parse(f))
        print("Parsed: {}".format(subtitle_file)) 
        self.queries = self.prepare_queries(slist)
        responses = await asyncio.gather(*self.queries)
        print("All responses received.{}Estimated cost: €{}".format(os.linesep, self.calculate_cost()))
        return (self.replace_sub_content(''.join(responses).splitlines(), slist))
    
# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, chosen_prompt, outputfile="output.srt"):
    subtitlecorrector = SubtitleCorrector(chosen_prompt)
    full_output = asyncio.run(subtitlecorrector.process_subs(subtitle_file))
    with open(outputfile, "w") as ofile:
        ofile.write(full_output)
