#!/usr/bin/env python3

from utils import num_tokens
from os import linesep
import re

# Dyse funktion makt yn array bloks ut yn glob teckst an et response fan GPT.
# Yn glob ar yn forsamlen tekst ymakt ut subtitle blokken yglobt dur
# et glob() metod. Worhem dyse funktion? Wo ybruken dyse funktion far
# et hereancoderen fan et SRT yskryve.
def blocks_from_response(response):
    blank_line_regex = r"(?:\r?\n){2,}" # Incomprehensible.
    raw_blocks = re.split(blank_line_regex, response.strip())
    blocks = []
    for rblock in raw_blocks:
        lines = rblock.splitlines()
        idx = int(lines[0]) # 1st element will always be the index (hopefully).
        content = linesep.join(lines[1:]) # From the 2nd element in the list to the end.
        blocks.append(Block(idx, content))
    return (blocks)

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
        self.chunks = chunks
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
        self.blocks = blocks
        self.tokens = (sum(map(lambda block: block.tokens, blocks)))

    def append_to_chunk(self, block: Block):
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
