import openai
import os
import time
import asyncio
from openai import AsyncOpenAI

# To be expanded.
error_messages = {
    "length": "Query failed due to exceeding the token limit.",
    "content_filter": "Query failed due to violation of content policy.",
    "API_error": "Query failed as API returned unknown error.",
    "API_timeout": "Query failed due to timeout.",
    "API_rate_limit": "Query failed due to number of requests exceeding the rate limit.",
    "API_connection": "Query failed due to connection error.",
    "API_server_error": "Query failed due to internal server error",
    "API_permission_denied": "Query failed due permission denied error.",
    "API_authentication": "Query failed due to an authentication failure.",
    "API_malformed_request": "Query failed as request was malformed."
}

class QueryException(Exception):
    def __init__(self, type, message, index, query_text):
        self.type = type
        self.message = message
        self.index = index
        self.query_text = query_text
        super().__init__(message)

class Query:
    def __init__(self, idx, prompt, query_text, token_count, client, config):
        self.client = client
        self.model = config.model
        self.tokens_per_query = config.tokens_per_query
        self.idx = idx
        self.prompt = prompt
        self.query_text = query_text 
        self.token_count = token_count
        self.query_delay = 0
        self.token_usage_input = 0
        self.token_usage_output = 0
        self.timeouts_encountered = 0
        self.max_timeouts = 10
        
    #async def run(self):
    
    # Keeps the user informed.
    def report_status(self, token_count):
        print("Sending query with token count: {} | Query index: {}".format(self.token_count, self.idx))
    
    # I <3 one line functions.
    def count_subs(self, subs):
        return (sum(map(lambda sub: sub.rstrip().isdigit() == True, subs.splitlines())))

    def validate_finish_reason(self, finish_reason, query_number):
        if finish_reason != "stop":
            raise QueryException(finish_reason, query_number, error_messages[finish_reason])
    
    async def run(self):
        self.report_status(self.token_count)
        try: 
            answer = await self.query_chatgpt()
            while (self.count_subs(answer) != self.count_subs(self.self.query_text)):
                self.total_queries += 1
                self.query_counter += 1
                print("Inconsistent output, resending query with token count: {} | Query count: {}/{}".format(self.token_count, self.index, self.total_queries))
                answer = await self.query_chatgpt(self.query_text, self.query_text, self.chosen_prompt)
        except QueryException as e:
            return(await self.handle_exceptions(e))
        return answer
    
    async def handle_content_violation(self, exception):
        result = ""
        print(exception.self.query_text)
        print("Explain how processing this text is not a content policy violation.") 
        print("Your explanation will be appended to the prompt and the query will be resent.")
        while (result == ""):
            result = input("> ")
        modified_prompt = self.chosen_prompt
        modified_prompt.instructions += result
        return (await self.query_chatgpt(exception.query_text, exception.self.index, modified_prompt))
    
    async def handle_timeout(self, exception):
        await asyncio.sleep(1)
        self.timeouts_encountered += 1
        if (self.timeouts_encountered < self.max_timeouts):
            return (await self.query_chatgpt(exception.query_text, exception.self.index, self.chosen_prompt))
        else:
            print("Too many timeouts encountered, returning orignal input.")
            return (exception.self.query_text)
        
    async def handle_ratelimit(self, exception):  
        if (self.query_delay == 0):
            self.query_delay = 30
        self.query_delay *= 2
        await asyncio.sleep(self.query_delay)
        if (self.query_delay > 1024):
            print("Unable to get past rate limit, returning original input")
            return (exception.self.query_text)
        return (await self.query_chatgpt(exception.query_text, exception.self.index, self.chosen_prompt))
    
    async def handle_exceptions(self, exception):
        print("EXCEPTION at query #{}: Type: {} | Message: {} ".format(exception.self.index, exception.type, exception.message))
        match exception.type:
            case 'content_filter':
                return (await self.handle_content_violation(exception))
            case 'API_timeout':
                return (await self.handle_timeout(exception))
            case 'API_rate_limit':
                return (await self.handle_ratelimit(exception))
        print("Returning original text.")
        return (exception.query_text)
         
    # Queries ChatGPT with the stripped SRT data.
    async def query_chatgpt(self):
        query_content = [
            {'role': 'system', 'content': self.prompt.instructions},
            {'role': 'user', 'content': self.query_text},
        ]
        for example in self.prompt.examples:
            query_content.append(example.example_input)
            query_content.append(example.example_output)
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=query_content
            )
        except openai.RateLimitError as e:
            raise QueryException('API_rate_limit', error_messages['API_rate_limit'], self.index, self.query_text)
        except openai.APITimeoutError as e:
            raise QueryException('API_timeout', error_messages['API_timeout'], self.index, self.query_text)
        except openai.APIConnectionError as e:
            raise QueryException('API_connection', error_messages['API_connection'], self.index, self.query_text)
        except openai.InternalServerError as e:
            raise QueryException('API_server_error', error_messages['API_server_error'], self.index, self.query_text) 
        except openai.AuthenticationError as e:
            raise QueryException('API_authentication', error_messages['API_authentication'], self.index, self.query_text)
        except openai.BadRequestError as e:
            raise QueryException('API_malformed_request', error_messages['API_malformed_request'], self.index, self.query_text)
        except openai.PermissionDeniedError as e:
            raise QueryException('API_permission_denied', error_messages['API_permission_denied'], self.index, self.query_text)
        except openai.APIError as e:
            raise QueryException('API_error', error_messages['API_error'], self.index, self.query_text)
        print("Query number: {} | Response received in: {} seconds".format(self.index, round((time.time() - start), 2)))
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        try:
            self.validate_finish_reason(response.choices[0].finish_reason, self.index)
        except QueryException as e:
            print("Query exception at query number: {} | Message: {}".format(self.index, e.message))
            print("Failed query text: {}{}".format(os.linesep, self.query_text))
            return (self.query_text)
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer