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
import os
import time
from typing import Optional
import utils

class QueryException(Exception):
    def __init__(self, query, error_type) -> None:
        self.query: Query = query
        self.error_type: str = error_type

class QueryContent:
    def __init__(self, prompt, query_text, config, token_count):
        self.prompt = prompt
        self.query_text = query_text
        self.model = config.model
        self.messages = [
            {"role": "system", "content": prompt.instructions},
            {"role": "user", "content": query_text}
        ]
        for example in self.prompt.examples:
            self.messages.append(example.example_input)
            self.messages.append(example.example_output)
        self.token_count = (token_count + utils.num_tokens(prompt.instructions))
 
class Query:
    def __init__(self, idx, client, content):
        # Data required for sending query:
        self.client = client
        self.content = content
        self.idx = idx
        # Usage data for cost calculation:
        self.token_usage_input = 0
        self.token_usage_output = 0
        # Error specific data
        self.query_delay = 0
        self.timeouts_encountered = 0
        self.max_timeouts = 10
        self.response = ""
        
    # Keeps the user informed.
    def report_status(self):
        print(f"Sending query with token count: {self.content.token_count} | Query index: {self.idx}")

    async def run(self):
        self.report_status()
        answer = await self.query_chatgpt()
        while (utils.count_subs(answer) != utils.count_subs(self.content.query_text)):
            print(f"Inconsistent output, resending: {self.idx}")
            answer = await self.query_chatgpt()
        self.response = answer
                 
    # Queries ChatGPT with the stripped SRT data.
    async def query_chatgpt(self):
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.content.model, 
                messages=self.content.messages
            )
        except openai.APIError as e:
            raise QueryException(self, type(e).__name__)
        if (response.choices[0].finish_reason != "stop"):
            raise QueryException(self, response.choices[0].finish_reason)
        print(f"Query index: {self.idx} | Response received in: {round((time.time() - start), 2)} seconds")
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer
