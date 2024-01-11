import openai
import asyncio
from query import QueryException

# Handleable errors
Errors = {
    openai.APITimeoutError.__name__: "Query timed out.",
    openai.RateLimitError.__name__: "Query was rate limited.",
    openai.APIConnectionError.__name__: "Query failed due to connection error.",
    openai.BadRequestError.__name__: "Query failed due to request being bad.",
    "content_filter": "Response stopped due to content violation.",
    "ERR_generic": "Query failed due to error",
}

async def resend_failed_queries(failed_queries):
    tasks = []
    while (failed_queries):
        tasks.clear()
        await handle_failed_queries(failed_queries)
        for failed_query in failed_queries:
            tasks.append(asyncio.create_task(failed_query.query.run()))
        failed_queries.clear()
        failed_queries = await asyncio.gather(*tasks, return_exceptions=True)

async def handle_failed_queries(query_exceptions):
    for exception in query_exceptions:
        print(f"Query: {exception.query.idx} | {Errors[exception.error_type]}")
        if (exception.error_type == openai.APITimeoutError.__name__):
            handle_timeout(exception.query)
        elif (exception.error_type == openai.RateLimitError.__name__):
            handle_ratelimit(exception.query)
        elif (exception.error_type == "content_filter"):
            handle_content_violation(exception.query)
        elif (exception.error_type == "ERR_generic"):
            exception.query.should_run = False

def handle_content_violation(query):
    result = ""
    print(query.query_text)
    print("Explain how processing this text is not a content policy violation.") 
    print("Your explanation will be appended to the end of the prompt and the query will be resent.")
    while (result == ""):
        result = input("> ")
    query.content.prompt.instructions += result

def handle_timeout(query):
    query.timeouts_encountered += 1
    query.delay += 5
    if (query.timeouts_encountered > query.max_timeouts):
        print(f"Query: {query.idx} | Too many timeouts.")
        query.should_run = False
    else:
        query.should_run = True

def handle_ratelimit(query):
    if (query.query_delay > 256):
        print(f"Query: {query.idx} | Unable to overcome rate limit.")
        query.should_run = False
    if (query.query_delay == 0):
        query.query_delay = 30
    query.query_delay *= 2
    query.should_run = True
