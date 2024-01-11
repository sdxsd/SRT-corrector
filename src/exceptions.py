import openai

# Handleable errors
Errors = {
    openai.APITimeoutError.__name__: "Request timed out.",
    openai.RateLimitError.__name__: "Request was rate limited.",
    "content_filter": "Response stopped due to content violation.",
    "ERR_generic": "Request failed due to error",
}

async def handle_failed_queries(query_exceptions):
    for exception in query_exceptions:
        print(f"#{exception.query.index}: {exception.error_type}")
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
        print("Too many timeouts encountered, returning orignal input.")
        query.should_run = False
    else:
        query.should_run = True

def handle_ratelimit(query):
    if (query.query_delay > 256):
        print("Unable to get past rate limit, returning original input")
        query.should_run = False
    if (query.query_delay == 0):
        query.query_delay = 30
    query.query_delay *= 2
    query.should_run = True
