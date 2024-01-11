from query import Query, QueryContent, QueryException

async def resend_failed_queries(queries: QueryException):
    while queries:
        for query in queries[:]:
            if query.error is not None:
                
async def handle_content_violation(self, exception):
    result = ""
    print(exception.query_text)
    print("Explain how processing this text is not a content policy violation.") 
    print("Your explanation will be appended to the prompt and the query will be resent.")
    while (result == ""):
        result = input("> ")
    self.prompt += result
    return (await self.query_chatgpt())

async def handle_timeout(self, exception):
    await asyncio.sleep(1)
    self.timeouts_encountered += 1
    if (self.timeouts_encountered < self.max_timeouts):
        return (await self.query_chatgpt())
    else:
        print("Too many timeouts encountered, returning orignal input.")
        return (exception.query_text)
    
async def handle_ratelimit(self, exception):  
    if (self.query_delay == 0):
        self.query_delay = 15
    self.query_delay *= 2
    await asyncio.sleep(self.query_delay)
    if (self.query_delay > 1024):
        print("Unable to get past rate limit, returning original input")
        return (exception.query_text)
    return (await self.query_chatgpt())