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

from utils import assemble_queries, report_status, failed_queries_from_list
from error import resend_failed_queries
from parsing import Chunk, blocks_from_response
import asyncio
import openai
import time
import os

def prepare_queries(chunks, client, config):
    queries = []
    query_tasks = []
    for idx, chunk in enumerate(chunks):
        queries.append(Query(idx, client, config, chunk))
        query_tasks.append(asyncio.create_task(queries[idx].run()))
    return (queries, query_tasks)

class QueryException(Exception):
    def __init__(self, query, error_type):
        self.query: Query = query # Query object which has failed.
        self.error_type = error_type # Type of error which caused Query object to fail.

class QuerySegment:
    def __init__(self, segment, client, config):
        self.config = config
        self.segment = segment
        self.queries, self.query_tasks = prepare_queries(self.segment.chunks, client, config)
        self.tokens = segment.tokens

    async def run(self):
        result = await asyncio.gather(*self.query_tasks, return_exceptions=True)
        failed_queries = failed_queries_from_list(result)
        if (len(failed_queries) > 0):
            await resend_failed_queries(failed_queries)
        responses = assemble_queries(self.queries)
        return (responses)

# This class can be thought of as a package which contains the data to allow a request to
# be sent to the OpenAI API. A given query contains a prompt, and the chunk of the original subtitle
# being sent. This allows a query to be run() multiple times if an error has occurred.
# The class also contains error information such as how many timeouts have been encountered and
# the current query delay.
# The should_run boolean indicates if enough errors have been encountered such that a query
# should not be re-run but instead return the original text from the subtitle file.
class Query:
    def __init__(self, idx, client, config, chunk):
        self.prompt = config.prompt # Prompt object containing instructions for GPT.
        self.input_chunk = chunk # Contains the chunk of subtitle data to be modified.
        self.model = config.model # Model to be used for subtitle modification.
        self.token_count = (chunk.tokens + config.prompt.tokens) # Total token count of Query to be sent.
        self.messages = [ # Dictionary in format required by the OpenAI client. (sent as JSON eventually)
            {"role": "system", "content": config.prompt.instructions},
            {"role": "user", "content": self.input_chunk.glob()}
        ]
        # Data required for sending query:
        self.client = client # Client object used for communication with the API.
        self.idx = idx # Index of Query, later can be used to reconstruct valid .SRT file.
        # Usage data for cost calculation:
        self.token_usage_input = 0 # Sum of input tokens sent.
        self.token_usage_output = 0 # Sum of output tokens received.
        # Error specific data
        self.delay = 0 # Amount of time to wait before sending API request.
        self.timeouts_encountered = 0 # Number of timeouts encountered.
        self.max_timeouts = 10 # Maximum tolerable timeouts before giving up on request.
        self.response: Chunk # Response from GPT (or original text in case of unrecoverable failure).
        self.should_run = True # If the Query should run or simply return the original text.

    # This function is a wrapper over query_chatgpt()
    # It runs query_chatgpt() and checks if the response
    # from GPT has the same number of lines as the input
    # that was given.
    # In addition, if self.should_run is False it indicates
    # that this query is almost guaranteed to fail. Hence the input
    # text should be returned rather than carelessly wasting API usage
    # by resending the query.
    async def run(self):
        time.sleep(self.delay)
        if (self.should_run is False):
            print(f"Query: {self.idx} failed unrecoverably.")
            self.response = self.input_chunk
            return True
        report_status(self.idx, self.token_count)
        self.response = Chunk(blocks_from_response(await self.query_chatgpt())) # String -> Blocks[] -> Chunk
        while (len(self.response.blocks) != len(self.input_chunk.blocks)):
            time.sleep(self.delay)
            print(f"Inconsistent output, resending: {self.idx}")
            self.response = Chunk(blocks_from_response(await self.query_chatgpt()))
        return True

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
                model=self.model, 
                messages=self.messages
            )
        except openai.APIError as e:
            raise QueryException(self, type(e).__name__)
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        if (response.choices[0].finish_reason != "stop"):
            raise QueryException(self, response.choices[0].finish_reason)
        print(f"Query: {self.idx} Response received in: {round((time.time() - start), 2)} seconds")
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer
