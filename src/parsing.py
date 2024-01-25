#!/usr/bin/env python3

from utils import num_tokens
from os import linesep
import srt

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

# Dyse funktion makt yn array bloks ut yn glob teckst an et response fan GPT.
# Yn glob ar yn forsamlen tekst ymakt ut subtitle blokken yglobt dur
# et glob() metod. Worhem dyse funktion? Wo ybruken dyse funktion far
# et hereancoderen fan et SRT yskryve.
def blocks_from_response(response, block):
    lines = response.splitlines()
    i = 0
    for block in blocks:
        block.text = ""
        while (i < len(lines)):
            content = ""
            index = 0
            if (lines[i].rstrip() == ""):

                break
            if (lines[i].rstrip().isdigit() is True):
                index = int(lines[i].rstrip().isdigit())
            content += ((" " if sub.content else "") + (lines[i] if lines[i].rstrip() != "" else ""))
            i += 1
    return (srt.compose(slist))

# Displays a whole file stored as segments.
def display_sub_file(segments):
    for segment in segments:
        segment.display_chunks()

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
    def __init__(self, idx, text):
        self.idx = idx
        self.text = text
        self.tokens = num_tokens(str(self.idx) + linesep + self.text + linesep)

    def display(self):
        print(f"Index: {self.idx}")
        print(f"Token count: {self.tokens}")
        print(f"Text:{linesep}{self.text}")
