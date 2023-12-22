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
from openai import AsyncOpenAI
import asyncio
import srt
import os
import tiktoken
import math
import time
import prompts as prompts
from config import Config

# Globals:
encoding = "iso-8859-1" if os.name == "posix" else "utf-8"

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

# To be expanded.
error_messages = {
    "length": "Query failed due to exceeding the token limit.",
    "content_filter": "Query failed due to violation of content policy.",
    "API_error": "Query failed as API returned unknown error.",
    "API_timeout": "Query failed due to timeout.",
    "API_rate_limit": "Query failed due to number of requests exceeding the rate limit."
}

class QueryException(Exception):
    def __init__(self, type, message, query_number, query_str):
        self.type = type
        self.message = message
        self.query_number = query_number
        self.query_str = query_str
        super().__init__(message)

class SubtitleCorrector:
    def __init__(self, chosen_prompt):
        self.client = AsyncOpenAI()
        config = Config()
        self.model = config.model
        self.tokens_per_query = config.tokens_per_query
        self.chosen_prompt = chosen_prompt
        self.prompt_token_count = self.num_tokens(self.chosen_prompt.instructions)
        self.queries = []
        self.query_counter = 0
        self.total_queries = 0
        self.query_delay = 0
        self.token_usage_input = 0
        self.token_usage_output = 0
        self.timeouts_encountered = 0
        self.max_timeouts = 10        
    
    async def handle_exception(self, exception):
        print("EXCEPTION at query #{1}: Type: {2} | Message: {3} ".format(exception.query_number, exception.type, exception.message))
        match exception.type:
            case 'length': # TODO: Instead of returning original content send sub by sub.
                print("Returning original sub content.")
                return (exception.query_str)
            case 'content_filter':
                result = ""
                print(exception.query_str)
                print("Explain how processing this text is not a content policy violation.") 
                print("Your explanation will be appended to the prompt and the query will be resent.")
                while (result == ""):
                    result = input("> ")
                modified_prompt = self.chosen_prompt
                modified_prompt.instructions += result
                return (self.query_chatgpt(exception.query_str, exception.query_number, modified_prompt))
            case 'API_error':
                print("Unable to handle exception: {}, program will now exit.".format(exception.type)) 
                for query in self.queries:
                    query.cancel()
            case 'API_timeout':
                await asyncio.sleep(1)
                self.timeouts_encountered += 1
                if (self.timeouts_encountered < self.max_timeouts):
                    return (self.query_chatgpt(exception.query_str, exception.query_number, self.chosen_prompt))
                else:
                    print("Too many timeouts encountered, exiting.")
                    for query in self.queries:
                        query.cancel()
            case 'API_rate_limit':
                self.query_delay *= 2
                return (self.query_chatgpt(exception.query_str, exception.query_number, self.chosen_prompt))
             
    def validate_finish_reason(self, finish_reason):
        if finish_reason != "stop":
            raise QueryException(finish_reason, error_messages[finish_reason])
    
    # Counts the number of tokens in a given string.
    def num_tokens(self, raw_text):
        return (len(tiktoken.get_encoding("cl100k_base").encode(raw_text)))

    # I <3 one line functions.
    def count_subs(self, subs):
        return (sum(map(lambda sub: sub.rstrip().isdigit() == True, subs.splitlines())))

    # Estimates the total queries required for the file using token counts.
    def estimate_total_queries(self, slist):
        return (math.ceil(self.num_tokens(''.join(map(lambda sub: str(sub.index) + os.linesep + sub.content + os.linesep, slist))) / self.tokens_per_query))
    
    # Estimates the total cost in api usage.
    def calculate_cost(self):
        return (round((API_prices[self.model]["input_price"] * self.token_usage_input) + (API_prices[self.model]["output_price"] * self.token_usage_output), 2))
    
    # Keeps the user informed.
    def report_status(self, token_count):
        print("Sending query with token count: {1} | Query count: {2}/{3}".format((token_count + self.prompt_token_count), self.query_counter, self.total_queries))
    
    # Queries ChatGPT with the stripped SRT data.
    async def query_chatgpt(self, query_str, query_number, prompt):
        query_content = [
            {'role': 'system', 'content': prompt.instructions},
            {'role': 'user', 'content': query_str},
        ]
        for example in prompt.examples:
            query_content.append(example.example_input)
            query_content.append(example.example_output)
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=query_content
            )
        except openai.RateLimitError as e:
            raise QueryException('API_rate_limit', error_messages['API_rate_limit'], query_number, query_str)
        except openai.APITimeoutError as e:
            raise QueryException('API_timeout', error_messages['API_timeout'], query_number, query_str)
        except openai.APIError as e:
            raise QueryException('API_error', error_messages['API_error'], query_number, query_str)
        print("Query number: {1} | Response received in: {2} seconds".format(query_number, round((time.time() - start), 2)))
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        try:
            self.validate_finish_reason(response.choices[0].finish_reason, query_number)
        except QueryException as e:
            print("Query exception at query number: {1} | Message: {2}".format(query_number, e.message))
            print("Failed query text: {}{}".format(os.linesep, query_str))
            return (query_str)
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer
    
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
    
    async def send_and_receive(self, query_str, token_count, query_number):
        self.query_counter += 1
        self.report_status(token_count)
        if (self.query_delay > 0):
            await asyncio.sleep(self.query_delay) 
        try: 
            answer = await self.query_chatgpt(query_str, self.query_counter, self.chosen_prompt)
            while (self.count_subs(answer) != self.count_subs(query_str)):
                self.total_queries += 1
                self.query_counter += 1
                print("Inconsistent output, resending query with token count: {1} | Query count: {2}/{3}".format(token_count, query_number, self.total_queries))
                answer = await self.query_chatgpt(query_str, query_number, self.chosen_prompt)
        except QueryException as e:
            return(self.handle_exception(e))
        return answer
   
    # This function creates a list of queries (tasks)
    # which will later be executed by asyncio.gather()
    def prepare_queries(self, slist):
        queries = []
        idx = 0
        for sub in slist: 
            query_str += (os.linesep.join([str(sub.index), sub.content]) + os.linesep)
            token_count = self.num_tokens(query_str)
            if (token_count > self.tokens_per_query or (slist[-1].index == sub.index)):
                idx += 1
                queries.append(asyncio.create_task(self.send_and_receive(query_str, token_count, idx)))
                query_str = ""
        return (queries)
    
    # raw subtitle data -> array of sub blocks -> array of tasks to be executed -> modified subtitle data -> ??? -> profit              
    async def process_subs(self, subtitle_file):
        with open(subtitle_file, "r", encoding=encoding) as f:
            slist = list(srt.parse(f))
        print("Parsed: {}".format(subtitle_file)) 
        self.total_queries = self.estimate_total_queries(slist)
        self.queries = self.prepare_queries(slist)
        self.total_queries = len(self.queries)
        responses = await asyncio.gather(*self.queries)
        print("All responses received. {} Estimated cost: €{}".format(os.linesep, self.calculate_cost()))
        return (self.replace_sub_content(''.join(responses).splitlines(), slist))
    
# Reads the raw SRT data and passes it to ChatGPT to be processed.
def correct_subtitles(subtitle_file, chosen_prompt, outputfile="output.srt"):
    subtitlecorrector = SubtitleCorrector(chosen_prompt)
    full_output = asyncio.run(subtitlecorrector.process_subs(subtitle_file))
    with open(outputfile, "w", encoding=encoding) as ofile:
        ofile.write(full_output)
