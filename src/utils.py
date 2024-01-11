#!/usr/bin/env python3

import tiktoken

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

# I <3 one line functions.
def count_subs(subs):
    return (sum(map(lambda sub: sub.rstrip().isdigit() is True, subs.splitlines())))

# Counts the number of tokens in a given string.
def num_tokens(raw_text):
    return (len(tiktoken.get_encoding("cl100k_base").encode(raw_text)))

# Estimates the total cost in api usage.
def calculate_cost(queries, model):
    input_usage = 0
    output_usage = 0
    for query in queries:
        input_usage += query.token_usage_input
        output_usage += query.token_usage_output
    return (round((API_prices[model]["input_price"] * input_usage) + (API_prices[model]["output_price"] * output_usage), 2))
