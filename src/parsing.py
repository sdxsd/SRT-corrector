#!/usr/bin/env python3

from utils import num_tokens
from os import linesep

# Tiers and their respective rate limits for GPT models.
Tiers = {
    0: {
        "gpt-3.5-turbo": {
            "RPM": 3,
            "TPM": 40000
        }
    },
    1: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 60000
        },
        "gpt-4": {
            "RPM": 500,
            "TPM": 10000
        },
        "gpt-4-1106-preview": {
            "RPM": 500,
            "TPM": 150000
        }
    },
    2: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 80000
        },
        "gpt-4": {
            "RPM": 5000,
            "TPM": 40000
        },
        "gpt-4-1106-preview": {
            "RPM": 5000,
            "TPM": 300000
        }
    },
    3: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 160000
        },
        "gpt-4": {
            "RPM": 5000,
            "TPM": 80000
        },
        "gpt-4-1106-preview": {
            "RPM": 5000,
            "TPM": 300000
        }
    },
    4: {
        "gpt-3.5-turbo": {
            "RPM": 10000,
            "TPM": 1000000
        },
        "gpt-4": {
            "RPM": 10000,
            "TPM": 300000
        },
        "gpt-4-1106-preview": {
            "RPM": 10000,
            "TPM": 450000
        }
    },
    5: {
        "gpt-3.5-turbo": {
            "RPM": 10000,
            "TPM": 2000000
        },
        "gpt-4": {
            "RPM": 10000,
            "TPM": 300000
        },
        "gpt-4-1106-preview": {
            "RPM": 10000,
            "TPM": 600000
        }
    },
}

def display_sub_file(segments):
    for segment in segments:
        segment.display_chunks()

# Loads a whole sub file as an array of Segment objects.
def load_subs(subs, tokens_per_query, tier, model):
    segments = []
    chunks = []
    blocks = []
    for sub in subs:
        blocks.append(Block(sub))
        if (sum(map(lambda b: b.tokens, blocks)) >= tokens_per_query):
            chunks.append(Chunk(blocks))
            blocks.clear()
        if (sum(map(lambda c: c.tokens, chunks)) >= Tiers[tier][model]['TPM']):
            segments.append(Segment(chunks))
            chunks.clear()
    chunks.append(Chunk(blocks))
    segments.append(Segment(chunks))
    return (segments)

# Segment is a collection of Chunks.
# The number of Chunks will depend on the rate limit which is
# dependent on the "tier" of the organisation as specified in the Config
# object.
class Segment:
    def __init__(self, chunks):
        self.chunks = []
        for chunk in chunks:
            self.chunks.append(chunk)
        self.tokens = (sum(map(lambda chunk: chunk.tokens, chunks)))

    def append_to_segment(self, chunk):
        self.chunks.append(chunk)
        self.tokens += chunk.tokens

    def display(self):
        print(f"Number of Chunks: {len(self.chunks)}")
        print(f"Total tokens in segment: {self.tokens}")

    def display_chunks(self):
        for chunk in self.chunks:
            chunk.display_blocks()

# Chunk is a collection of Block objects with a token count
# roughly equivalent to tokens_per_query as specified in the config.
class Chunk:
    def __init__(self, blocks):
        self.blocks = []
        for block in blocks:
            self.blocks.append(block)
        self.tokens = (sum(map(lambda block: block.tokens, blocks)))

    def append_to_chunk(self, block):
        self.blocks.append(block)
        self.tokens += block.tokens

    def display(self):
        print(f"Number of blocks: {len(self.blocks)}")
        print(f"Total tokens in chunk: {self.tokens}")

    def display_blocks(self):
        for block in self.blocks:
            block.display()

    def glob(self):
        glob = ""
        for block in self.blocks:
            glob += str(block.idx) + linesep + block.text + linesep
        return (glob)

# Class representation of .SRT block with time stripped i.e
# 125
# Blah blah blah I am the person
# who dies in this movie.
class Block:
    def __init__(self, sub):
        self.idx = sub.index
        self.text = sub.content
        self.tokens = num_tokens(str(self.idx) + linesep + self.text + linesep)

    def display(self):
        print(f"Index: {self.idx}")
        print(f"Token count: {self.tokens}")
        print(f"Text:{linesep}{self.text}")
