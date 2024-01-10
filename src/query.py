import openai
import os
import time
from typing import Optional

class QueryException(Exception):
    def __init__(self, query, error: Optional[openai.APIError], finish_reason="") -> None:
        self.query = query
        self.error = error
        self.finish_reason = finish_reason 
        
class QueryContent:
    def __init__(self, prompt, query_text, config, token_count):
        self.query_text = query_text
        self.model = config.model
        self.messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query_text}
        ]
        for example in self.prompt.examples:
            self.content.append(example.example_input)
            self.content.append(example.example_output)
        self.token_count = token_count
 
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
        print("Sending query with token count: {} | Query index: {}".format(self.content.token_count, self.idx))
    
    # I <3 one line functions.
    def count_subs(self, subs):
        return (sum(map(lambda sub: sub.rstrip().isdigit() == True, subs.splitlines())))
    
    async def run(self):
        self.report_status()
        answer = await self.query_chatgpt()
        while (self.count_subs(answer) != self.count_subs(self.content.query_text)):
            print("Inconsistent output, resending: {}".format(self.idx))
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
            raise QueryException(self, e)
        if (response.choices[0].finish_reason != "stop"):
            raise QueryException(self, None, response.choices[0].finish_reason)
        print("Query index: {} | Response received in: {} seconds".format(self.idx, round((time.time() - start), 2)))
        self.token_usage_input += response.usage.prompt_tokens
        self.token_usage_output += response.usage.completion_tokens
        answer = response.choices[0].message.content
        if (answer[-1] != os.linesep):
            answer += os.linesep
        return answer