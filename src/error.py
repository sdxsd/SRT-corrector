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

# General structure of error handling:
# resend_failed_queries(failed_queries) takes a list
# of QueryExceptions objects, each QueryException contains a Query object.
# A loop is entered that continues until the failed_queries list is empty of QueryExceptions.
# handle_failed_queries is called and modifies each Query according to the error_type of the QueryException.
# Queries are modified such that they have a chance of succeeding the next time they are run().
# For example, in the case of encountering a rate limit, a delay is added so the request sleeps
# before querying the OpenAI API thus hopefully allowing enough time to pass for the rate limit to expire.
# After handle_failed_queries returns, for every Query a asyncio task object is created
# which will later be run by asyncio.gather().
# The list of query.run() tasks is then executed asynchronously by asyncio.gather() with the flag
# return_exceptions equalling True.
# In the case that return_exceptions is True, asyncio.gather() will return each exception within
# the array that it returns. In this case, since a successful Query does not return any value; the contents
# of the list will only ever be QueryExceptions, hence we can consider
# the result of asyncio.gather() as a list of the queries that have once again failed thus
# allowing us to repeat the process of resending them.
# In the case that handle_failed_queries() detects that a given Query will likely not succeed when resent
# it will set a flag within the Query object such that upon the next run() the object will return the original
# chunk of subtitle data it was initialised with. This will count as a "successful" query and thus
# will not appear in the results of asyncio.gather().
# Because of this, the loop within resend_failed_queries() will continue until all the queries
# have been resolved (either failed unrecoverably) or returned successful output from the API.

import openai
import asyncio

# Mapping of error names to messages.
Errors = {
    openai.APITimeoutError.__name__: "Query timed out.",
    openai.RateLimitError.__name__: "Query was rate limited.",
    openai.APIConnectionError.__name__: "Query failed due to connection error.",
    openai.BadRequestError.__name__: "Query failed due to request being bad.",
    openai.AuthenticationError.__name__: "Query failed due to auth error (check API key).",
    openai.InternalServerError.__name__: "Query failed due to API returning an internal server error.",
    "content_filter": "Response stopped due to content violation.",
    "ERR_generic": "Query failed due to error",
}

def list_empty(list_to_check):
    if (sum(map(lambda x: x is True, list_to_check)) == 0):
        return True
    else:
        return (False)

# Modify and run() again till all Queries are either succesful or have failed unrecoverably.
async def resend_failed_queries(failed_queries):
    if (list_empty(failed_queries) is True):
        return
    tasks = []
    while (True):
        tasks.clear()
        await handle_failed_queries(failed_queries)
        for failed_query in failed_queries:
            tasks.append(asyncio.create_task(failed_query.query.run()))
        failed_queries.clear()
        failed_queries = await asyncio.gather(*tasks, return_exceptions=True)
        if (list_empty(failed_queries) is True):
            return

# Modify state of failed queries.
async def handle_failed_queries(query_exceptions):
    for exception in query_exceptions:
        print(f"Query: {exception.query.idx} {Errors[exception.error_type]}")
        if (exception.error_type == openai.APITimeoutError.__name__):
            handle_timeout(exception.query)
        elif (exception.error_type == openai.RateLimitError.__name__):
            handle_ratelimit(exception.query)
        elif (exception.error_type == "content_filter"):
            handle_content_violation(exception.query)
        else:
            exception.query.should_run = False

# Your negotiation skills better be good.
def handle_content_violation(query):
    result = ""
    print(query.query_text)
    print("Explain how processing this text is not a content policy violation.") 
    print("Your explanation will be appended to the end of the prompt and the query will be resent.")
    while (result == ""):
        result = input("> ")
    query.prompt.instructions += result

# Linear backoff.
def handle_timeout(query):
    query.timeouts_encountered += 1
    query.delay += 5
    if (query.timeouts_encountered > query.max_timeouts):
        print(f"Query: {query.idx} Too many timeouts.")
        query.should_run = False
    else:
        query.should_run = True

# Exponential backoff.
def handle_ratelimit(query):
    if (query.query_delay > 256):
        print(f"Query: {query.idx} Unable to overcome rate limit.")
        query.should_run = False
    if (query.query_delay == 0):
        query.query_delay = 30
    query.query_delay *= 2
    query.should_run = True
