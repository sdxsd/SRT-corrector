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
import utils

class QueryException(Exception):
    def __init__(self, query, error_type):
        self.query: Query = query
        self.error_type = error_type

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

# This class can be thought of as a package which contains the data to allow a request to
# be sent to the OpenAI API. A given query contains a prompt, and the chunk of the original subtitle
# being sent. This allows a query to be run() multiple times if an error has occurred.
# The class also contains error information such as how many timeouts have been encountered and
# the current query delay.
# The should_run boolean indicates if enough errors have been encountered such that a query
# should not be re-run but instead returns the original text from the subtitle file.
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
        self.should_run = True
        
    # Keeps the user informed.
    def report_status(self):
        print(f"Sending query: {self.idx} | Token count: {self.content.token_count}")

    # This function is a wrapper over query_chatgpt()
    # It runs query_chatgpt() and checks if the response
    # from GPT has the same number of lines as the input
    # that was given.
    # In addition, if self.should_run is False it indicates
    # that this query is almost guaranteed to fail. Hence the input
    # text should be returned rather than carelessly wasting API usage
    # by resending the query.
    async def run(self):
        if (self.should_run is False):
            print(f"Query: {self.idx} failed unrecoverably.")
            self.response = self.content.query_text
            return
        self.report_status()
        answer = await self.query_chatgpt()
        while (utils.count_subs(answer) != utils.count_subs(self.content.query_text)):
            print(f"Inconsistent output, resending: {self.idx}")
            answer = await self.query_chatgpt()
        self.response = answer

    # This functions sends the query TO and receives the response
    # FROM the OpenAI API.
    # A QueryException object is raised if either the finish_reason does not
    # equal stop, or if the API itself has returned an exception.
    # If the API does not return an exception, the token input and token output
    # are recorded for later cost calculation.
    # If all is good, the output is finally returned in the form of a string.
    # A newline is appended if required.
    async def query_chatgpt(self):
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.content.model, 
                messages=self.content.messages
            )
        except openai.APIError as e:
            raise QueryException(self, type(e).__name__)
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        if (response.choices[0].finish_reason != "stop"):
            raise QueryException(self, response.choices[0].finish_reason)
        print(f"Query: {self.idx} | Response received in: {round((time.time() - start), 2)} seconds")
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer
